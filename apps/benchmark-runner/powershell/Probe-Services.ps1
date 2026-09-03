# ==============================================================================
# File: apps/benchmark-runner/powershell/Probe-Services.ps1
# Purpose: TCP health of each language port; append one service_runs row each.
# SOLID: SRP — module-run history only (separate from test history).
# Usage: .\Probe-Services.ps1
# ==============================================================================

[CmdletBinding()]
param()

$ErrorActionPreference = 'Continue'
. (Join-Path $PSScriptRoot 'ReportWriter.ps1')

$cfgPath = Join-Path (Get-OpnRunnerRoot) 'config\services.json'
$cfg = Get-Content -LiteralPath $cfgPath -Raw | ConvertFrom-Json
$rows = @()

foreach ($prop in $cfg.languages.PSObject.Properties) {
    $lang = $prop.Name
    $meta = $prop.Value
    $hostName = $meta.host
    $port = [int]$meta.port
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    $up = $false
    $err = ''
    try {
        $client = New-Object System.Net.Sockets.TcpClient
        $iar = $client.BeginConnect($hostName, $port, $null, $null)
        $up = $iar.AsyncWaitHandle.WaitOne(400)
        if ($up) { $client.EndConnect($iar) }
        else { $err = 'connection timed out' }
        $client.Close()
    }
    catch {
        $up = $false
        $err = "$_"
    }
    $sw.Stop()
    $rows += Write-OpnServiceRun -Language $lang -Port $port -Up $up -LatencyMs $sw.Elapsed.TotalMilliseconds -ErrorMessage $err
}

Write-Host '=== Service run history (TCP) ===' -ForegroundColor Green
$rows | Format-Table -AutoSize language, port, up, latency_ms, error_message | Out-Host
return $rows
