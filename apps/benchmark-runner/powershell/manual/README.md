# powershell/manual

Thin ISTQB-style wrappers. Each file sets `-TestId` and `-Language` and calls `Invoke-ManualTest.ps1`. The 4×6 matrix lives in `Invoke-AllManualTests.ps1` (loops), not as 24 large copies here.

| Script | TestId | Language | RPC (via catalog) |
|--------|--------|----------|-------------------|
| `TC-FUNC-001-ReadAll-Python.ps1` | TC-FUNC-001 | python | ReadAllPersons |
| `TC-FUNC-002-ReadAll-Go.ps1` | TC-FUNC-001 | go | ReadAllPersons |
| `TC-FUNC-003-ReadAll-Csharp.ps1` | TC-FUNC-001 | csharp | ReadAllPersons |
| `TC-FUNC-004-ReadAll-Java.ps1` | TC-FUNC-001 | java | ReadAllPersons |
| `TC-FUNC-005-ReadAll-Node.ps1` | TC-FUNC-001 | node | ReadAllPersons |
| `TC-FUNC-006-ReadAll-Cpp.ps1` | TC-FUNC-001 | cpp | ReadAllPersons |
| `TC-FUNC-007-Filter-Python.ps1` | TC-FUNC-002 | python | SearchByFilter |
| `TC-FUNC-008-Vector-Go.ps1` | TC-FUNC-003 | go | SearchByVector |
| `TC-FUNC-009-Create-Csharp.ps1` | TC-FUNC-004 | csharp | CreatePerson |
| `TC-FUNC-010-Filter-Java.ps1` | TC-FUNC-002 | java | SearchByFilter |
| `TC-EDGE-001-EmptyFilter-Python.ps1` | TC-EDGE-001 | python | empty filter |
| `TC-EDGE-002-HugeLimit-Go.ps1` | TC-EDGE-002 | go | huge limit |
| `TC-EDGE-003-TopKZero-Java.ps1` | TC-EDGE-003 | java | top_k=0 |
