# ==============================================================================
# File: apps/benchmark-runner/powershell/Invoke-ManualTest.ps1
# Purpose: Run one catalogued functional / edge case against one language.
# SOLID: SRP — map TestId → RPC + payload, then delegate to Invoke-FunctionalRpc.
# Usage: .\Invoke-ManualTest.ps1 -TestId TC-FUNC-001 -Language python
# ==============================================================================

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$TestId,

    [Parameter(Mandatory = $true)]
    [ValidateSet('cpp', 'python', 'java', 'go', 'csharp', 'node')]
    [string]$Language
)

$ErrorActionPreference = 'Stop'

# Catalog: TestId → RPC + payload. Thin scripts under manual/ call this file.
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
    $known = ($Catalog.Keys | Sort-Object) -join ', '
    throw "Unknown TestId '$TestId'. Known: $known"
}

$script = Join-Path $PSScriptRoot 'Invoke-FunctionalRpc.ps1'
$result = & $script `
    -Language $Language `
    -Rpc $spec.Rpc `
    -PayloadKind $spec.PayloadKind `
    -TestName "$key-$Language" `
    -TestType 'manual'

Write-OpnCliSummary -Results @($result)
return $result
