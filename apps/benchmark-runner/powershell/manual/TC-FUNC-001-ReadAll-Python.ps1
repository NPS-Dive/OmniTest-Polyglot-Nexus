# ==============================================================================
# File: apps/benchmark-runner/powershell/manual/TC-FUNC-001-ReadAll-Python.ps1
# Purpose: Thin case — ReadAllPersons on api-python (:50052 / persons_python).
# SOLID: SRP — bind TestId + language only. Execution is Invoke-ManualTest.ps1.
# Gherkin: docs/gherkin/person-readall.feature (@functional)
# ==============================================================================
& (Join-Path $PSScriptRoot '..\Invoke-ManualTest.ps1') -TestId 'TC-FUNC-001' -Language python
