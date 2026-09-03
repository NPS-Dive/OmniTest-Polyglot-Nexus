# ==============================================================================
# File: apps/benchmark-runner/powershell/ReportWriter.ps1
# Purpose: Append-only CSV + JSONL history. Never overwrites prior runs.
# SOLID: SRP — persist one result row. Callers compute metrics and pass/fail.
# Dependencies: Common.ps1 (paths). Files under reports/history/.
# Columns (locked): timestamp_utc,test_name,test_type,language,p90_ms,p95_ms,
#   p98_ms,p99_ms,ttl_ms,p50_ms,avg_ms,max_ms,iterations,vus,fail_rate,pass,
#   error_message
# Service-run columns: timestamp_utc,language,port,up,latency_ms,error_message
# ==============================================================================

. (Join-Path $PSScriptRoot 'Common.ps1')

function Get-OpnHistoryHeader {
    <#
    .SYNOPSIS
        Canonical CSV header. Must match the header-only files in reports/history.
    #>
    return 'timestamp_utc,test_name,test_type,language,p90_ms,p95_ms,p98_ms,p99_ms,ttl_ms,p50_ms,avg_ms,max_ms,iterations,vus,fail_rate,pass,error_message'
}

function Get-OpnServiceRunHeader {
    <#
    .SYNOPSIS
        Canonical header for service_runs.csv (liveness / probe rows).
    #>
    return 'timestamp_utc,language,port,up,latency_ms,error_message'
}

function Get-OpnHistoryPaths {
    <#
    .SYNOPSIS
        Pair of append targets for a test_type bucket.
    #>
    param(
        [Parameter(Mandatory = $true)]
        [ValidateSet('manual', 'automated', 'performance', 'security')]
        [string]$TestType
    )
    $dir = Join-Path (Get-OpnRunnerRoot) 'reports\history'
    $stem = switch ($TestType) {
        'manual' { 'manual_results' }
        'automated' { 'automated_results' }
        default { 'performance_results' }  # performance + security share perf history
    }
    return [pscustomobject]@{
        Csv   = Join-Path $dir "$stem.csv"
        Jsonl = Join-Path $dir "$stem.jsonl"
    }
}

function Get-OpnServiceRunPaths {
    <#
    .SYNOPSIS
        Append targets for service_runs.csv / .jsonl.
    #>
    $dir = Join-Path (Get-OpnRunnerRoot) 'reports\history'
    return [pscustomobject]@{
        Csv   = Join-Path $dir 'service_runs.csv'
        Jsonl = Join-Path $dir 'service_runs.jsonl'
    }
}

function ConvertTo-OpnCsvField {
    <#
    .SYNOPSIS
        RFC-ish CSV escape: quote when the value contains comma, quote, or newline.
    #>
    param([AllowNull()][object]$Value)
    if ($null -eq $Value) { return '' }
    $s = [string]$Value
    if ($s -match '[,"\r\n]') {
        return '"' + ($s.Replace('"', '""')) + '"'
    }
    return $s
}

function Write-OpnTestResult {
    <#
    .SYNOPSIS
        Append one row to the matching CSV and one object to the matching JSONL.
        Creates files with header if they are missing (does not truncate existing).
    #>
    param(
        [Parameter(Mandatory = $true)]
        [string]$TestName,

        [Parameter(Mandatory = $true)]
        [ValidateSet('manual', 'automated', 'performance', 'security')]
        [string]$TestType,

        [Parameter(Mandatory = $true)]
        [string]$Language,

        [double]$P90Ms = 0,
        [double]$P95Ms = 0,
        [double]$P98Ms = 0,
        [double]$P99Ms = 0,
        [double]$TtlMs = 0,
        [double]$P50Ms = 0,
        [double]$AvgMs = 0,
        [double]$MaxMs = 0,
        [int]$Iterations = 1,
        [int]$Vus = 1,
        [double]$FailRate = 0,
        [bool]$Pass = $false,
        [string]$ErrorMessage = ''
    )

    $ts = [DateTime]::UtcNow.ToString('o')
    $paths = Get-OpnHistoryPaths -TestType $TestType

    $row = [ordered]@{
        timestamp_utc = $ts
        test_name     = $TestName
        test_type     = $TestType
        language      = $Language.ToLowerInvariant()
        p90_ms        = [math]::Round($P90Ms, 3)
        p95_ms        = [math]::Round($P95Ms, 3)
        p98_ms        = [math]::Round($P98Ms, 3)
        p99_ms        = [math]::Round($P99Ms, 3)
        ttl_ms        = [math]::Round($TtlMs, 3)
        p50_ms        = [math]::Round($P50Ms, 3)
        avg_ms        = [math]::Round($AvgMs, 3)
        max_ms        = [math]::Round($MaxMs, 3)
        iterations    = $Iterations
        vus           = $Vus
        fail_rate     = [math]::Round($FailRate, 4)
        pass          = $Pass
        error_message = $ErrorMessage
    }

    if (-not (Test-Path -LiteralPath $paths.Csv)) {
        $dir = Split-Path -Parent $paths.Csv
        if (-not (Test-Path -LiteralPath $dir)) {
            New-Item -ItemType Directory -Path $dir | Out-Null
        }
        Set-Content -LiteralPath $paths.Csv -Value (Get-OpnHistoryHeader) -Encoding utf8
    }

    $csvLine = @(
        $row.timestamp_utc
        $row.test_name
        $row.test_type
        $row.language
        $row.p90_ms
        $row.p95_ms
        $row.p98_ms
        $row.p99_ms
        $row.ttl_ms
        $row.p50_ms
        $row.avg_ms
        $row.max_ms
        $row.iterations
        $row.vus
        $row.fail_rate
        $row.pass
        $row.error_message
    ) | ForEach-Object { ConvertTo-OpnCsvField $_ }

    Add-Content -LiteralPath $paths.Csv -Value ($csvLine -join ',') -Encoding utf8

    $json = ($row | ConvertTo-Json -Compress -Depth 4)
    Add-Content -LiteralPath $paths.Jsonl -Value $json -Encoding utf8

    return [pscustomobject]$row
}

function Write-OpnServiceRun {
    <#
    .SYNOPSIS
        Append one liveness/probe row to service_runs.csv and service_runs.jsonl.
        Creates the CSV with header if missing; never truncates existing files.
    #>
    param(
        [Parameter(Mandatory = $true)]
        [string]$Language,

        [Parameter(Mandatory = $true)]
        [int]$Port,

        [bool]$Up = $false,
        [double]$LatencyMs = 0,
        [string]$ErrorMessage = ''
    )

    $ts = [DateTime]::UtcNow.ToString('o')
    $paths = Get-OpnServiceRunPaths

    $row = [ordered]@{
        timestamp_utc = $ts
        language      = $Language.ToLowerInvariant()
        port          = $Port
        up            = $Up
        latency_ms    = [math]::Round($LatencyMs, 3)
        error_message = $ErrorMessage
    }

    if (-not (Test-Path -LiteralPath $paths.Csv)) {
        $dir = Split-Path -Parent $paths.Csv
        if (-not (Test-Path -LiteralPath $dir)) {
            New-Item -ItemType Directory -Path $dir | Out-Null
        }
        Set-Content -LiteralPath $paths.Csv -Value (Get-OpnServiceRunHeader) -Encoding utf8
    }

    $csvLine = @(
        $row.timestamp_utc
        $row.language
        $row.port
        $row.up
        $row.latency_ms
        $row.error_message
    ) | ForEach-Object { ConvertTo-OpnCsvField $_ }

    Add-Content -LiteralPath $paths.Csv -Value ($csvLine -join ',') -Encoding utf8

    $json = ($row | ConvertTo-Json -Compress -Depth 4)
    Add-Content -LiteralPath $paths.Jsonl -Value $json -Encoding utf8

    return [pscustomobject]$row
}

function Write-OpnCliSummary {
    <#
    .SYNOPSIS
        Human-readable table for one or more result objects (manager + CLI).
    #>
    param(
        [Parameter(Mandatory = $true, ValueFromPipeline = $true)]
        [object[]]$Results
    )
    $Results | Format-Table -AutoSize test_name, language, pass, ttl_ms, p90_ms, p95_ms, p98_ms, p99_ms, error_message | Out-Host
}
