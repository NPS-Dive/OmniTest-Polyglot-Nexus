# ==============================================================================
# File: apps/benchmark-runner/powershell/manual/TC-FUNC-005-ReadAll-Node.ps1
# Purpose: Thin case — ReadAllPersons on api-node (:5079 / persons_node).
# SOLID: SRP — bind TestId + language only.
# Gherkin: docs/gherkin/person-readall.feature (@functional)
# ==============================================================================
& (Join-Path $PSScriptRoot '..\Invoke-ManualTest.ps1') -TestId 'TC-FUNC-001' -Language node
