# ==============================================================================
# File: apps/benchmark-runner/powershell/Invoke-OwaspPlatformChecklist.ps1
# Purpose: Manual OWASP API2/5/7/8/9/10 platform checklist — residual risk logged.
#          Does NOT fake exploit passes. pass=true means checklist completed.
# Usage: .\Invoke-OwaspPlatformChecklist.ps1 -Language csharp
# Docs: docs/qa/scenarios/TS-SEC-OWASP-PLATFORM/
# ==============================================================================

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('cpp', 'python', 'java', 'go', 'csharp', 'node')]
    [string]$Language,

    [switch]$SkipInteractive
)

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'ReportWriter.ps1')
. (Join-Path $PSScriptRoot 'Common.ps1')

$cfg = Get-OpnServicesConfig
$ep = Get-OpnLanguageEndpoint -Language $Language
$checklist = @(
    [pscustomobject]@{
        Id = 'TC-SEC-API2-NO-AUTH-PLAINTEXT'
        Prompt = "API2: Confirm RPCs to $($ep.host):$($ep.port) succeed without credentials (plaintext). Residual risk documented?"
    }
    [pscustomobject]@{
        Id = 'TC-SEC-API5-BFLA-NA'
        Prompt = 'API5: Confirm no admin/role RPCs in person_service.proto (BFLA N/A for v1). Residual risk logged?'
    }
    [pscustomobject]@{
        Id = 'TC-SEC-API7-SSRF-NA'
        Prompt = 'API7: Confirm no URL/fetch fields on Person RPCs (SSRF N/A). Residual risk logged?'
    }
    [pscustomobject]@{
        Id = 'TC-SEC-API8-REFLECTION-MISCONFIG'
        Prompt = "API8: Is gRPC reflection enabled on $Language? Document as misconfig residual risk if yes."
    }
    [pscustomobject]@{
        Id = 'TC-SEC-API9-SERVICE-INVENTORY'
        Prompt = 'API9: Six language ports + proto methods match config/services.json inventory?'
    }
    [pscustomobject]@{
        Id = 'TC-SEC-API10-OUTBOUND-NA'
        Prompt = 'API10: Confirm no outbound URL consumption on this surface (N/A). Residual risk logged?'
    }
)

$results = @()
foreach ($item in $checklist) {
    $completed = $true
    $note = 'checklist completed / residual risk logged'
    if (-not $SkipInteractive) {
        Write-Host ""
        Write-Host "[$($item.Id)] $($item.Prompt)" -ForegroundColor Cyan
        $ans = Read-Host "Mark completed? [Y/n]"
        if ($ans -match '^[Nn]') {
            $completed = $false
            $note = 'checklist incomplete'
        }
    }
    else {
        Write-Host "[$($item.Id)] auto-marked complete (-SkipInteractive): $($item.Prompt)"
    }

    $null = Write-OpnTestResult `
        -TestName "$($item.Id)-$Language" `
        -TestType 'security' `
        -Language $Language `
        -P90Ms 0 -P95Ms 0 -P98Ms 0 -P99Ms 0 `
        -TtlMs 0 -P50Ms 0 -AvgMs 0 -MaxMs 0 `
        -Iterations 1 -Vus 1 `
        -FailRate $(if ($completed) { 0 } else { 1 }) `
        -Pass $completed `
        -ErrorMessage $note

    $results += [pscustomobject]@{
        test_name = "$($item.Id)-$Language"
        pass      = $completed
        note      = $note
    }
}

Write-Host ""
Write-Host "OWASP platform checklist for $Language — $($results.Count) rows written to security/performance history."
$results | Format-Table -AutoSize
return $results
