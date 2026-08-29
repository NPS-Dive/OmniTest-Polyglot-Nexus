# ==============================================================================
# File: apps/benchmark-runner/powershell/Invoke-AutomatedTests.ps1
# Purpose: Automated wrapper around the same functional catalog (and optional
#          k6 smoke). Writes automated_results history, not manual_results.
# SOLID: SRP — orchestration + report type. RPC work stays in Invoke-FunctionalRpc.
# Usage: .\Invoke-AutomatedTests.ps1 -TestId TC-FUNC-001 -Language go
#        .\Invoke-AutomatedTests.ps1 -SmokeK6 -Language go
# ==============================================================================

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$TestId,

    [Parameter(Mandatory = $true)]
    [ValidateSet('cpp', 'python', 'java', 'go', 'csharp', 'node')]
    [string]$Language,

    [switch]$SmokeK6
)

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'Common.ps1')
. (Join-Path $PSScriptRoot 'ReportWriter.ps1')

$Catalog = @{
    'TC-FUNC-001' = @{ Rpc = 'ReadAllPersons'; PayloadKind = 'readall_default' }
    'TC-FUNC-002' = @{ Rpc = 'SearchByFilter'; PayloadKind = 'filter_name' }
    'TC-FUNC-003' = @{ Rpc = 'SearchByVector'; PayloadKind = 'vector_dummy' }
    'TC-FUNC-004' = @{ Rpc = 'CreatePerson'; PayloadKind = 'create_minimal' }
    'TC-EDGE-001' = @{ Rpc = 'SearchByFilter'; PayloadKind = 'filter_empty' }
    'TC-EDGE-002' = @{ Rpc = 'ReadAllPersons'; PayloadKind = 'readall_huge_limit' }
    'TC-EDGE-003' = @{ Rpc = 'SearchByVector'; PayloadKind = 'vector_topk_zero' }
    'TC-EDGE-004' = @{ Rpc = 'SearchByFilter'; PayloadKind = 'filter_sql_name' }
}

$key = $TestId.ToUpperInvariant()
$spec = $Catalog[$key]
if (-not $spec) {
    throw "Unknown TestId '$TestId'"
}

$fn = Join-Path $PSScriptRoot 'Invoke-FunctionalRpc.ps1'
$result = & $fn `
    -Language $Language `
    -Rpc $spec.Rpc `
    -PayloadKind $spec.PayloadKind `
    -TestName "AUTO-$key-$Language" `
    -TestType 'automated'

if ($SmokeK6) {
    $k6 = Get-Command k6 -ErrorAction SilentlyContinue
    if (-not $k6) {
        $null = Write-OpnTestResult `
            -TestName "AUTO-K6-SMOKE-$Language" `
            -TestType 'automated' `
            -Language $Language `
            -Pass $false `
            -ErrorMessage 'k6 is not on PATH. Install https://k6.io/docs/get-started/installation/ (Windows). Smoke was not executed.'
        Write-Warning 'k6 missing — smoke skipped (recorded as fail).'
    }
    else {
        $script = Join-Path (Get-OpnRunnerRoot) 'k6\load.js'
        Write-Host "k6 smoke: this script invokes k6; it does not claim a prior run succeeded."
        $k6Out = & k6 run -e LANG=$Language --vus 1 --duration 5s $script 2>&1
        $ok = ($LASTEXITCODE -eq 0)
        $null = Write-OpnTestResult `
            -TestName "AUTO-K6-SMOKE-$Language" `
            -TestType 'performance' `
            -Language $Language `
            -Pass $ok `
            -ErrorMessage $(if ($ok) { '' } else { ($k6Out | Out-String).Trim() })
    }
}

Write-OpnCliSummary -Results @($result)
return $result
