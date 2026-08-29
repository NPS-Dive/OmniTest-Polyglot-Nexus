# ==============================================================================
# File: apps/benchmark-runner/powershell/manual/TC-FUNC-008-Vector-Go.ps1
# Purpose: Thin case — SearchByVector on grpc-go.
# SOLID: SRP — bind TestId + language only.
# Gherkin: docs/gherkin/person-vector.feature (@functional @performance)
# ==============================================================================
& (Join-Path $PSScriptRoot '..\Invoke-ManualTest.ps1') -TestId 'TC-FUNC-003' -Language go
