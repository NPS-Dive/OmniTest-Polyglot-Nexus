# docs/gherkin

BDD view of the ISTQB / OWASP cases under [docs/qa/scenarios/](../qa/scenarios/). Step automation is PowerShell (`Invoke-ManualTest.ps1` / `Invoke-FunctionalRpc.ps1` / `Invoke-OwaspPlatformChecklist.ps1`), not a separate Cucumber JVM.

Security feature uses `@owasp` plus `@api1`…`@api10` tags aligned to OWASP API Security Top 10:2023.

See [docs/qa/README.md](../qa/README.md) and [docs/qa/catalog.md](../qa/catalog.md). Feature → script map: [docs/README.md](../README.md).
