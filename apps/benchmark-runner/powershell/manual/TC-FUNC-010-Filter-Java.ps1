# ==============================================================================
# File: apps/benchmark-runner/powershell/manual/TC-FUNC-010-Filter-Java.ps1
# Purpose: Thin case — SearchByFilter on grpc-java.
# SOLID: SRP — bind TestId + language only.
# Gherkin: docs/gherkin/person-filter.feature (@functional)
# ==============================================================================
& (Join-Path $PSScriptRoot '..\Invoke-ManualTest.ps1') -TestId 'TC-FUNC-002' -Language java
