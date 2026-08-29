# ==============================================================================
# File: apps/benchmark-runner/powershell/Invoke-AllManualTests.ps1
# Purpose: Loop 4 RPCs × 6 languages (+ edges) instead of 24+ copied scripts.
# SOLID: OCP — add a TestId to the list below; do not duplicate runners.
# ==============================================================================

[CmdletBinding()]
param(
    [string[]]$Languages = @('cpp', 'python', 'java', 'go', 'csharp', 'node'),
    [string[]]$TestIds = @(
        'TC-FUNC-001',
        'TC-FUNC-002',
        'TC-FUNC-003',
        'TC-FUNC-004',
        'TC-EDGE-001',
        'TC-EDGE-002',
        'TC-EDGE-003'
    )
)

$ErrorActionPreference = 'Continue'
. (Join-Path $PSScriptRoot 'ReportWriter.ps1')

$runner = Join-Path $PSScriptRoot 'Invoke-ManualTest.ps1'
$results = @()

foreach ($lang in $Languages) {
    foreach ($id in $TestIds) {
        Write-Host "=== $id / $lang ===" -ForegroundColor Cyan
        try {
            $results += & $runner -TestId $id -Language $lang
        }
        catch {
            Write-Warning $_
            $results += [pscustomobject]@{
                test_name     = "$id-$lang"
                language      = $lang
                pass          = $false
                ttl_ms        = 0
                p90_ms        = 0
                p95_ms        = 0
                p98_ms        = 0
                error_message = "$_"
            }
        }
    }
}

Write-Host ''
Write-Host '=== Manual suite summary ===' -ForegroundColor Green
Write-OpnCliSummary -Results $results
$failed = @($results | Where-Object { -not $_.pass }).Count
Write-Host ("Passed {0}/{1}" -f ($results.Count - $failed), $results.Count)
return $results
