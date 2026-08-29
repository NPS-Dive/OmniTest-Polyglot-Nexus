# ============================================================================
# File: services/grpc-go/scripts/generate.ps1
# Purpose: Generate Go gRPC stubs from the shared Person proto.
# SOLID: SRP — codegen only. Does not start the server or touch the database.
# ============================================================================

$ErrorActionPreference = "Stop"

$ApiGoRoot = Split-Path -Parent $PSScriptRoot
$RepoRoot = (Resolve-Path (Join-Path $ApiGoRoot "..\..")).Path
$ProtoDir = Join-Path $RepoRoot "shared\proto"
$ProtoFile = Join-Path $ProtoDir "person_service.proto"
$OutDir = Join-Path $ApiGoRoot "internal\gen"

if (-not (Test-Path $ProtoFile)) {
    throw "Proto not found: $ProtoFile"
}

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

function Find-Protoc {
    $cmd = Get-Command protoc -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }

    $temp = Join-Path $env:TEMP "protoc-29.3\bin\protoc.exe"
    if (Test-Path $temp) { return $temp }

    throw @"
protoc is not on PATH.

Install Protocol Buffers (https://github.com/protocolbuffers/protobuf/releases)
and re-run this script. Example (v29.3 win64):

  Invoke-WebRequest https://github.com/protocolbuffers/protobuf/releases/download/v29.3/protoc-29.3-win64.zip -OutFile `$env:TEMP\protoc.zip
  Expand-Archive `$env:TEMP\protoc.zip -DestinationPath `$env:TEMP\protoc-29.3
  `$env:PATH = "`$env:TEMP\protoc-29.3\bin;`$env:PATH"

Then install plugins:

  go install google.golang.org/protobuf/cmd/protoc-gen-go@v1.36.5
  go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@v1.5.1
"@
}

$protoc = Find-Protoc
Write-Host "Using protoc: $protoc"

$pluginDir = Join-Path (go env GOPATH) "bin"
if ($pluginDir -and (Test-Path $pluginDir)) {
    $env:PATH = "$pluginDir;$env:PATH"
}

$genGo = Get-Command protoc-gen-go -ErrorAction SilentlyContinue
$genGrpc = Get-Command protoc-gen-go-grpc -ErrorAction SilentlyContinue
if (-not $genGo -or -not $genGrpc) {
    throw @"
Missing protoc plugins. Install:

  go install google.golang.org/protobuf/cmd/protoc-gen-go@v1.36.5
  go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@v1.5.1

Ensure `$(go env GOPATH)\bin` is on PATH.
"@
}

# paths=source_relative keeps stubs next to this module (internal/gen).
# M mapping matches option go_package in the shared proto.
& $protoc `
    -I $ProtoDir `
    --go_out=$OutDir `
    --go_opt=paths=source_relative `
    --go_opt=Mperson_service.proto=github.com/omnitest/grpc-go/internal/gen `
    --go-grpc_out=$OutDir `
    --go-grpc_opt=paths=source_relative `
    --go-grpc_opt=Mperson_service.proto=github.com/omnitest/grpc-go/internal/gen `
    $ProtoFile

if ($LASTEXITCODE -ne 0) {
    throw "protoc failed with exit code $LASTEXITCODE"
}

Write-Host "Generated stubs in $OutDir"
Get-ChildItem $OutDir -Filter "*.pb.go" | ForEach-Object { Write-Host "  $($_.Name)" }
