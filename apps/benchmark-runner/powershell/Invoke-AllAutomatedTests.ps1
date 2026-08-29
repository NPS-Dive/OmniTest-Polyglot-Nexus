# ==============================================================================
# File: apps/benchmark-runner/powershell/Invoke-AllAutomatedTests.ps1
# Purpose: Run the automated catalog for every language (loop, not copies).
# SOLID: OCP — extend TestIds; do not fork this file per language.
# ==============================================================================

[CmdletBinding()]
param(
    [string[]]$Languages = @('cpp', 'python', 'java', 'go', 'csharp', 'node'),
    [string[]]$TestIds = @('TC-FUNC-001', 'TC-FUNC-002', 'TC-FUNC-003', 'TC-FUNC-004'),
    [switch]$SmokeK6
)

$ErrorActionPreference = 'Continue'
. (Join-Path $PSScriptRoot 'ReportWriter.ps1')

$runner = Join-Path $PSScriptRoot 'Invoke-AutomatedTests.ps1'
$results = @()

foreach ($lang in $Languages) {
    foreach ($id in $TestIds) {
        Write-Host "=== AUTO $id / $lang ===" -ForegroundColor Cyan
        try {
            $args = @{ TestId = $id; Language = $lang }
            if ($SmokeK6) { $args.SmokeK6 = $true }
            $results += & $runner @args
        }
        catch {
            Write-Warning $_
        }
    }
}

Write-Host ''
Write-Host '=== Automated suite summary ===' -ForegroundColor Green
if ($results.Count -gt 0) {
    Write-OpnCliSummary -Results $results
}
return $results
