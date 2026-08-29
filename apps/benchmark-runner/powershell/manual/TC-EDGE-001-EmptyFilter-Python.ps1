# ==============================================================================
# File: apps/benchmark-runner/powershell/manual/TC-EDGE-001-EmptyFilter-Python.ps1
# Purpose: Thin edge — empty SearchByFilter (expect a page, not a crash).
# SOLID: SRP — bind TestId + language only.
# Gherkin: docs/gherkin/person-filter.feature (@functional)
# ==============================================================================
& (Join-Path $PSScriptRoot '..\Invoke-ManualTest.ps1') -TestId 'TC-EDGE-001' -Language python
