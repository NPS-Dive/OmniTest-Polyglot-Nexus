# ==============================================================================
# File: apps/benchmark-runner/powershell/manual/TC-FUNC-006-ReadAll-Cpp.ps1
# Purpose: Thin case — ReadAllPersons on grpc-cpp (:50051 / persons_cpp).
# SOLID: SRP — bind TestId + language only.
# Gherkin: docs/gherkin/person-readall.feature (@functional)
# ==============================================================================
& (Join-Path $PSScriptRoot '..\Invoke-ManualTest.ps1') -TestId 'TC-FUNC-001' -Language cpp
