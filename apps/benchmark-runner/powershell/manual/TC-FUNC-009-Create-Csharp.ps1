# ==============================================================================
# File: apps/benchmark-runner/powershell/manual/TC-FUNC-009-Create-Csharp.ps1
# Purpose: Thin case — CreatePerson on grpc-csharp.
# SOLID: SRP — bind TestId + language only.
# Gherkin: docs/gherkin/person-readall.feature (create precondition / @functional)
# ==============================================================================
& (Join-Path $PSScriptRoot '..\Invoke-ManualTest.ps1') -TestId 'TC-FUNC-004' -Language csharp
