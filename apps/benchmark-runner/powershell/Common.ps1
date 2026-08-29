# ==============================================================================
# File: apps/benchmark-runner/powershell/Common.ps1
# Purpose: Shared path + services.json helpers for every runner script.
# SOLID: SRP — resolve roots and load config. No I/O to report files.
# Dependencies: config/services.json
# ==============================================================================

function Get-OpnRunnerRoot {
    <#
    .SYNOPSIS
        Absolute path of apps/benchmark-runner (parent of this powershell folder).
    #>
    return (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
}

function Get-OpnRepoRoot {
    <#
    .SYNOPSIS
        Repository root (OmniTest-Polyglot-Nexus).
    #>
    return (Resolve-Path (Join-Path (Get-OpnRunnerRoot) '..\..')).Path
}

function Get-OpnServicesConfig {
    <#
    .SYNOPSIS
        Parsed services.json object (languages + grpc proto paths).
    #>
    $path = Join-Path (Get-OpnRunnerRoot) 'config\services.json'
    if (-not (Test-Path -LiteralPath $path)) {
        throw "Missing services map: $path"
    }
    return (Get-Content -LiteralPath $path -Raw -Encoding UTF8 | ConvertFrom-Json)
}

function Get-OpnLanguageEndpoint {
    <#
    .SYNOPSIS
        One language entry (host, port, table) or throw.
    #>
    param(
        [Parameter(Mandatory = $true)]
        [string]$Language
    )
    $cfg = Get-OpnServicesConfig
    $key = $Language.ToLowerInvariant()
    $entry = $cfg.languages.$key
    if (-not $entry) {
        $known = ($cfg.languages.PSObject.Properties.Name) -join ', '
        throw "Unknown language '$Language'. Known: $known"
    }
    return $entry
}

function Test-OpnGrpcurlPresent {
    <#
    .SYNOPSIS
        $true if grpcurl is on PATH (needed for live gRPC functional calls).
    #>
    return [bool](Get-Command grpcurl -ErrorAction SilentlyContinue)
}

function Get-OpnGrpcurlInstallHint {
    <#
    .SYNOPSIS
        Fail-message text when grpcurl is missing. No RPC is sent in that case.
    #>
    return 'grpcurl is not on PATH. Mock-safe skip: no request was sent to any API. Install from https://github.com/fullstorydev/grpcurl/releases (Windows amd64 zip) and re-run. Example after install: grpcurl -plaintext 127.0.0.1:50054 list'
}
