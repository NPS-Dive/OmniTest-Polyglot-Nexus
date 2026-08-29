# ==============================================================================
# File: apps/benchmark-runner/powershell/manual/TC-EDGE-002-HugeLimit-Go.ps1
# Purpose: Thin edge — ReadAllPersons limit=999999 (expect clamp to max 500).
# SOLID: SRP — bind TestId + language only.
# Gherkin: docs/gherkin/person-security.feature (@security)
# ==============================================================================
& (Join-Path $PSScriptRoot '..\Invoke-ManualTest.ps1') -TestId 'TC-EDGE-002' -Language go
