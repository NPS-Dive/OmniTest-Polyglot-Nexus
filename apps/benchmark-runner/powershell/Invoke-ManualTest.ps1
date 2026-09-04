# ==============================================================================
# File: apps/benchmark-runner/powershell/Invoke-ManualTest.ps1
# Purpose: Run one catalogued functional / edge / OWASP SEC case against one language.
# SOLID: SRP — map TestId → RPC + payload, then delegate to Invoke-FunctionalRpc.
# Usage: .\Invoke-ManualTest.ps1 -TestId TC-FUNC-001 -Language python
# Docs: docs/qa/catalog.md and docs/qa/scenarios/TS-*/
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
. (Join-Path $PSScriptRoot 'ReportWriter.ps1')

# Catalog: TestId → RPC + payload. Keys normalized to upper for lookup.
$Catalog = @{
    'TC-FUNC-001' = @{ Rpc = 'ReadAllPersons'; PayloadKind = 'readall_default' }
    'TC-FUNC-002' = @{ Rpc = 'SearchByFilter'; PayloadKind = 'filter_name' }
    'TC-FUNC-003' = @{ Rpc = 'SearchByVector'; PayloadKind = 'vector_dummy' }
    'TC-FUNC-004' = @{ Rpc = 'CreatePerson'; PayloadKind = 'create_minimal' }
    'TC-EDGE-001' = @{ Rpc = 'SearchByFilter'; PayloadKind = 'filter_empty' }
    'TC-EDGE-002' = @{ Rpc = 'ReadAllPersons'; PayloadKind = 'readall_huge_limit' }
    'TC-EDGE-003' = @{ Rpc = 'SearchByVector'; PayloadKind = 'vector_topk_zero' }
    'TC-EDGE-004' = @{ Rpc = 'SearchByFilter'; PayloadKind = 'filter_sql_name' }
    # OWASP API Security Top 10:2023 — executable safe cases
    'TC-SEC-API4-READALL-RESOURCE' = @{ Rpc = 'ReadAllPersons'; PayloadKind = 'readall_huge_limit' }
    'TC-SEC-API3-FILTER-INJECTION' = @{ Rpc = 'SearchByFilter'; PayloadKind = 'filter_sql_name' }
    'TC-SEC-API4-VECTOR-TOPK' = @{ Rpc = 'SearchByVector'; PayloadKind = 'vector_topk_huge' }
    'TC-SEC-API1-CREATE-ID-TAMPER' = @{ Rpc = 'CreatePerson'; PayloadKind = 'create_bad_uuid' }
    'TC-SEC-API3-CREATE-MASS-ASSIGNMENT' = @{ Rpc = 'CreatePerson'; PayloadKind = 'create_extra_fields' }
    'TC-SEC-API8-VERBOSE-ERRORS' = @{ Rpc = 'SearchByVector'; PayloadKind = 'vector_bad_dims' }
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
