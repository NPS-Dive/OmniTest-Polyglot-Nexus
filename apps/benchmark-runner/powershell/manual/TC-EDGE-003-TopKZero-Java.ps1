# ==============================================================================
# File: apps/benchmark-runner/powershell/manual/TC-EDGE-003-TopKZero-Java.ps1
# Purpose: Thin edge — SearchByVector top_k=0 (expect default 10, not an abort).
# SOLID: SRP — bind TestId + language only.
# Gherkin: docs/gherkin/person-vector.feature (@functional)
# ==============================================================================
& (Join-Path $PSScriptRoot '..\Invoke-ManualTest.ps1') -TestId 'TC-EDGE-003' -Language java
