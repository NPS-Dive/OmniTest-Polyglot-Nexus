# ==============================================================================
# File: apps/benchmark-runner/powershell/Invoke-AllLanguagePerf.ps1
# Purpose: Loop six languages × k6 profiles and append performance/security
#          history (including p99). Smoke mode runs only load.js for 10s.
# SOLID: SRP — orchestration. Metrics persist via ReportWriter.ps1.
# Dependencies: Common.ps1, ReportWriter.ps1, k6 on PATH, apps/benchmark-runner/k6
# ==============================================================================

[CmdletBinding()]
param(
    [string[]]$Languages = @('cpp', 'python', 'java', 'go', 'csharp', 'node'),
    [string[]]$Scripts = @(
        'load',
        'stress',
        'spike',
        'concurrency',
        'endurance',
        'scalability',
        'security',
        'compare'
    ),
    [switch]$Smoke
)

$ErrorActionPreference = 'Continue'
. (Join-Path $PSScriptRoot 'Common.ps1')
. (Join-Path $PSScriptRoot 'ReportWriter.ps1')

function Get-OpnK6TrendValue {
    <#
    .SYNOPSIS
        Read a named trend stat from a k6 --summary-export metrics object.
        k6 nests values under .values ('p(90)', avg, …); older shapes are flat.
    #>
    param(
        [AllowNull()][object]$Metric,
        [Parameter(Mandatory = $true)][string]$Stat
    )
    if ($null -eq $Metric) { return 0 }
    $bag = $Metric
    if ($null -ne $Metric.values) { $bag = $Metric.values }
    $prop = $bag.PSObject.Properties | Where-Object { $_.Name -eq $Stat } | Select-Object -First 1
    if ($null -eq $prop -or $null -eq $prop.Value) { return 0 }
    try { return [double]$prop.Value } catch { return 0 }
}

function ConvertFrom-OpnK6Summary {
    <#
    .SYNOPSIS
        Map k6 JSON summary metrics to Write-OpnTestResult arguments.
        Returns $null when the file is missing or not JSON.
    #>
    param([string]$Path)
    if (-not $Path -or -not (Test-Path -LiteralPath $Path)) { return $null }
    try {
        $doc = Get-Content -LiteralPath $Path -Raw -Encoding UTF8 | ConvertFrom-Json
    }
    catch {
        return $null
    }
    if (-not $doc -or -not $doc.metrics) { return $null }

    $m = $doc.metrics
    $dur = $m.grpc_req_duration
    $iterations = 0
    if ($m.iterations) {
        $iterations = [int](Get-OpnK6TrendValue -Metric $m.iterations -Stat 'count')
    }
    $vus = 0
    if ($m.vus_max) {
        $vus = [int](Get-OpnK6TrendValue -Metric $m.vus_max -Stat 'value')
        if ($vus -le 0) { $vus = [int](Get-OpnK6TrendValue -Metric $m.vus_max -Stat 'max') }
    }
    if ($vus -le 0 -and $m.vus) {
        $vus = [int](Get-OpnK6TrendValue -Metric $m.vus -Stat 'max')
        if ($vus -le 0) { $vus = [int](Get-OpnK6TrendValue -Metric $m.vus -Stat 'value') }
    }
    $failRate = 0.0
    if ($m.checks) {
        $rate = Get-OpnK6TrendValue -Metric $m.checks -Stat 'rate'
        if ($rate -gt 0 -or $rate -eq 0) { $failRate = [math]::Max(0, 1.0 - $rate) }
    }
    if ($m.grpc_req_failed) {
        $grpcFail = Get-OpnK6TrendValue -Metric $m.grpc_req_failed -Stat 'rate'
        if ($grpcFail -gt $failRate) { $failRate = $grpcFail }
    }

    return [pscustomobject]@{
        P90Ms      = (Get-OpnK6TrendValue -Metric $dur -Stat 'p(90)')
        P95Ms      = (Get-OpnK6TrendValue -Metric $dur -Stat 'p(95)')
        P98Ms      = (Get-OpnK6TrendValue -Metric $dur -Stat 'p(98)')
        P99Ms      = (Get-OpnK6TrendValue -Metric $dur -Stat 'p(99)')
        P50Ms      = (Get-OpnK6TrendValue -Metric $dur -Stat 'med')
        AvgMs      = (Get-OpnK6TrendValue -Metric $dur -Stat 'avg')
        MaxMs      = (Get-OpnK6TrendValue -Metric $dur -Stat 'max')
        Iterations = $iterations
        Vus        = $vus
        FailRate   = $failRate
    }
}

$k6Dir = Join-Path (Get-OpnRunnerRoot) 'k6'
$k6cmd = Get-Command k6 -ErrorAction SilentlyContinue
$results = @()

if ($Smoke) {
    $Scripts = @('load')
}

$prevDuration = $env:K6_DURATION
if ($Smoke) {
    $env:K6_DURATION = '10s'
}

try {
    foreach ($lang in $Languages) {
        foreach ($name in $Scripts) {
            $testType = if ($name -eq 'security') { 'security' } else { 'performance' }
            $testName = "K6-$name-$lang"
            Write-Host "=== $testName ===" -ForegroundColor Cyan

            if (-not $k6cmd) {
                $row = Write-OpnTestResult `
                    -TestName $testName `
                    -TestType $testType `
                    -Language $lang `
                    -Pass $false `
                    -ErrorMessage 'k6 is not on PATH. Install https://k6.io/docs/get-started/installation/ (Windows). Suite was not executed.'
                $results += $row
                continue
            }

            $js = Join-Path $k6Dir "$name.js"
            if (-not (Test-Path -LiteralPath $js)) {
                $row = Write-OpnTestResult `
                    -TestName $testName `
                    -TestType $testType `
                    -Language $lang `
                    -Pass $false `
                    -ErrorMessage "Missing k6 script: $js"
                $results += $row
                continue
            }

            $summaryPath = Join-Path ([System.IO.Path]::GetTempPath()) ("opn-k6-{0}-{1}-{2}.json" -f $lang, $name, [DateTime]::UtcNow.ToString('yyyyMMddHHmmssfff'))
            $k6Args = @(
                'run'
                '-e', "LANG=$lang"
                '--summary-export', $summaryPath
                '--summary-trend-stats', 'avg,min,med,max,p(90),p(95),p(98),p(99)'
                '--tag', "lang=$lang"
            )
            # Push live series to Prometheus so Grafana test-comparison panels fill.
            if ($env:K6_PROMETHEUS_RW_SERVER_URL) {
                if (-not $env:K6_PROMETHEUS_RW_TREND_STATS) {
                    $env:K6_PROMETHEUS_RW_TREND_STATS = 'p(90),p(95),p(98),p(99),avg'
                }
                $k6Args += @('--out', 'experimental-prometheus-rw')
            }
            if ($Smoke) {
                $k6Args += @('--duration', '10s')
            }
            $k6Args += $js

            Write-Host "k6 $($k6Args -join ' ')"
            $sw = [System.Diagnostics.Stopwatch]::StartNew()
            $k6Out = & k6 @k6Args 2>&1
            $exit = $LASTEXITCODE
            $sw.Stop()
            $parsed = ConvertFrom-OpnK6Summary -Path $summaryPath

            $pass = ($exit -eq 0)
            $err = ''
            if (-not $pass) {
                $err = (($k6Out | Out-String).Trim())
                if (-not $err) { $err = "k6 exit $exit" }
            }

            $write = @{
                TestName     = $testName
                TestType     = $testType
                Language     = $lang
                TtlMs        = $sw.Elapsed.TotalMilliseconds
                Pass         = $pass
                ErrorMessage = $err
            }
            if ($parsed) {
                $write.P90Ms = $parsed.P90Ms
                $write.P95Ms = $parsed.P95Ms
                $write.P98Ms = $parsed.P98Ms
                $write.P99Ms = $parsed.P99Ms
                $write.P50Ms = $parsed.P50Ms
                $write.AvgMs = $parsed.AvgMs
                $write.MaxMs = $parsed.MaxMs
                $write.Iterations = $parsed.Iterations
                $write.Vus = $parsed.Vus
                $write.FailRate = $parsed.FailRate
            }
            else {
                # No JSON summary: pass follows exit code; percentiles stay 0.
                $write.Iterations = 0
                $write.Vus = 0
                if (-not $err -and -not $pass) {
                    $write.ErrorMessage = "k6 exit $exit (summary JSON not parsed)"
                }
            }

            $results += Write-OpnTestResult @write
        }
    }
}
finally {
    if ($null -eq $prevDuration) {
        Remove-Item Env:K6_DURATION -ErrorAction SilentlyContinue
    }
    else {
        $env:K6_DURATION = $prevDuration
    }
}

Write-Host ''
Write-Host '=== Language performance summary ===' -ForegroundColor Green
if ($results.Count -gt 0) {
    Write-OpnCliSummary -Results $results
}
$failed = @($results | Where-Object { -not $_.pass }).Count
Write-Host ("Passed {0}/{1}" -f ($results.Count - $failed), $results.Count)
return $results
