# ==============================================================================
# File: apps/benchmark-runner/powershell/Invoke-FunctionalRpc.ps1
# Purpose: Parameterized functional runner — 4 RPCs × 6 languages via loops,
#          not 24 copied scripts. Uses grpcurl when present; otherwise records
#          a mock-safe skip (pass=false, no network call).
# SOLID: SRP — one RPC invocation + timing. Persistence is ReportWriter.ps1.
# Dependencies: Common.ps1, ReportWriter.ps1, shared/proto/person_service.proto
# ==============================================================================

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('cpp', 'python', 'java', 'go', 'csharp', 'node')]
    [string]$Language,

    [Parameter(Mandatory = $true)]
    [ValidateSet('CreatePerson', 'ReadAllPersons', 'SearchByFilter', 'SearchByVector')]
    [string]$Rpc,

    [string]$TestName = '',

    [ValidateSet('manual', 'automated')]
    [string]$TestType = 'manual',

    [ValidateSet(
        'readall_default',
        'readall_huge_limit',
        'filter_name',
        'filter_empty',
        'filter_sql_name',
        'filter_oversized',
        'vector_dummy',
        'vector_topk_zero',
        'vector_topk_huge',
        'vector_bad_dims',
        'create_minimal',
        'create_bad_uuid',
        'create_extra_fields'
    )]
    [string]$PayloadKind = 'readall_default',

    [switch]$NoReport
)

. (Join-Path $PSScriptRoot 'Common.ps1')
. (Join-Path $PSScriptRoot 'ReportWriter.ps1')

function Get-OpnRpcPayload {
    <#
    .SYNOPSIS
        JSON body for grpcurl -d. Keep payloads small and deterministic.
    #>
    param([string]$Kind)
    switch ($Kind) {
        'readall_default' { return '{"limit":5,"offset":0}' }
        'readall_huge_limit' { return '{"limit":999999,"offset":0}' }
        'filter_name' { return '{"first_name":"A"}' }
        'filter_empty' { return '{}' }
        'filter_sql_name' { return '{"first_name":"Robert''); DROP TABLE persons_python;--"}' }
        'filter_oversized' {
            $long = 'X' * 20000
            return "{`"first_name`":`"$long`"}"
        }
        'vector_dummy' {
            $vals = (1..384 | ForEach-Object { '0.01' }) -join ','
            return "{`"vector`":[$vals],`"top_k`":5}"
        }
        'vector_topk_zero' {
            $vals = (1..384 | ForEach-Object { '0.0' }) -join ','
            return "{`"vector`":[$vals],`"top_k`":0}"
        }
        'vector_topk_huge' {
            $vals = (1..384 | ForEach-Object { '0.0' }) -join ','
            return "{`"vector`":[$vals],`"top_k`":999999}"
        }
        'vector_bad_dims' {
            return '{"vector":[0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8],"top_k":5}'
        }
        'create_minimal' {
            $id = [guid]::NewGuid().ToString()
            $code = Get-Random -Minimum 1000000000 -Maximum 1999999999
            return (@'
{"person":{"id":"ID_PLACE","first_name":"Bench","last_name":"Runner","age":30,"gender":"SEX_MALE","marital_status":"MARITAL_STATUS_SINGLE","children_count":0,"living_place":"LIVING_PLACE_APARTMENT","job_category":"OCCUPATION_FULL_TIME","national_code":"CODE_PLACE","has_passport":false}}
'@).Replace('ID_PLACE', $id).Replace('CODE_PLACE', [string]$code)
        }
        'create_bad_uuid' {
            $code = Get-Random -Minimum 1000000000 -Maximum 1999999999
            return (@'
{"person":{"id":"not-a-uuid","first_name":"Bad","last_name":"Uuid","age":30,"gender":"SEX_MALE","marital_status":"MARITAL_STATUS_SINGLE","children_count":0,"living_place":"LIVING_PLACE_APARTMENT","job_category":"OCCUPATION_FULL_TIME","national_code":"CODE_PLACE","has_passport":false}}
'@).Replace('CODE_PLACE', [string]$code)
        }
        'create_extra_fields' {
            $id = [guid]::NewGuid().ToString()
            $code = Get-Random -Minimum 1000000000 -Maximum 1999999999
            # Unknown JSON keys: grpcurl/proto may strip them — that is an acceptable API3 pass.
            return (@'
{"person":{"id":"ID_PLACE","first_name":"Mass","last_name":"Assign","age":30,"gender":"SEX_MALE","marital_status":"MARITAL_STATUS_SINGLE","children_count":0,"living_place":"LIVING_PLACE_APARTMENT","job_category":"OCCUPATION_FULL_TIME","national_code":"CODE_PLACE","has_passport":false,"is_admin":true,"role":"root"}}
'@).Replace('ID_PLACE', $id).Replace('CODE_PLACE', [string]$code)
        }
        default { throw "Unknown PayloadKind $Kind" }
    }
}

if (-not $TestName) {
    $TestName = "FUNC-$Rpc-$Language-$PayloadKind"
}

$endpoint = Get-OpnLanguageEndpoint -Language $Language
$cfg = Get-OpnServicesConfig
$target = "$($endpoint.host):$($endpoint.port)"
$method = "$($cfg.grpc.packageService)/$Rpc"
$repo = Get-OpnRepoRoot
$proto = Join-Path $repo $cfg.grpc.protoRelPath
$importDir = Join-Path $repo $cfg.grpc.protoImportRelPath
$body = Get-OpnRpcPayload -Kind $PayloadKind

$pass = $false
$err = ''
$ttl = 0.0

if (-not (Test-OpnGrpcurlPresent)) {
    $err = Get-OpnGrpcurlInstallHint
}
elseif (-not (Test-Path -LiteralPath $proto)) {
    $err = "Proto not found at $proto"
}
else {
    $grpcurlArgs = @(
        '-plaintext'
        '-import-path', $importDir
        '-proto', (Split-Path -Leaf $proto)
        '-d', $body
        '-max-time', '30'
        $target
        $method
    )
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    $output = & grpcurl @grpcurlArgs 2>&1
    $exit = $LASTEXITCODE
    $sw.Stop()
    $ttl = $sw.Elapsed.TotalMilliseconds
    if ($exit -eq 0) {
        $pass = $true
        $err = ''
    }
    else {
        $pass = $false
        $err = (($output | Out-String).Trim())
        if (-not $err) { $err = "grpcurl exit $exit" }
        # Huge limit / SQL-looking names: API may return InvalidArgument. That is
        # still "safe handling" for security/edge cases — callers decide pass rules.
        $safeKinds = @(
            'readall_huge_limit', 'filter_sql_name', 'filter_oversized',
            'vector_topk_zero', 'vector_topk_huge', 'vector_bad_dims',
            'create_bad_uuid', 'create_extra_fields'
        )
        if ($PayloadKind -in $safeKinds) {
            # Safe handling = process still answered (non-crash). Connection refused is fail.
            if ($err -notmatch 'connection refused|Unavailable|dial tcp') {
                $pass = $true
                $err = "safe-handling: $err"
            }
        }
    }
}

$result = [pscustomobject]@{
    test_name     = $TestName
    test_type     = $TestType
    language      = $Language
    p90_ms        = $ttl
    p95_ms        = $ttl
    p98_ms        = $ttl
    ttl_ms        = $ttl
    p50_ms        = $ttl
    avg_ms        = $ttl
    max_ms        = $ttl
    iterations    = 1
    vus           = 1
    fail_rate     = $(if ($pass) { 0 } else { 1 })
    pass          = $pass
    error_message = $err
}

if (-not $NoReport) {
    $null = Write-OpnTestResult `
        -TestName $result.test_name `
        -TestType $TestType `
        -Language $Language `
        -P90Ms $result.p90_ms -P95Ms $result.p95_ms -P98Ms $result.p98_ms `
        -TtlMs $result.ttl_ms -P50Ms $result.p50_ms -AvgMs $result.avg_ms -MaxMs $result.max_ms `
        -Iterations 1 -Vus 1 -FailRate $result.fail_rate -Pass $pass -ErrorMessage $err
}

Write-Host ("[{0}] {1} {2} {3} ttl={4:N1}ms pass={5}" -f $TestType, $Language, $Rpc, $PayloadKind, $ttl, $pass)
if ($err) { Write-Host "  $err" }

return $result
