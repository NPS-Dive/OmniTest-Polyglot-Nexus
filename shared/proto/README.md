# Shared gRPC contract

## Purpose

Single source of truth for all six Person services. Do not copy this `.proto` into each language except as generated stubs.

**File:** `person_service.proto`  
**Package:** `omnitest.polyglot.nexus`  
**RPCs:** `CreatePerson`, `ReadAllPersons`, `SearchByFilter`, `SearchByVector`

## Persistence mapping (do not rename proto fields)

| Proto field | Postgres `persons_*` column |
|-------------|-----------------------------|
| `gender` | `sex` |
| `job_category` | `occupation` |
| `embedding_vector` | `embedding` (vector 384, L2 `<->`) |
| `has_passport` | `has_passport` |
| `birth_date` | not stored; derived from `age` on read |

## Codegen

- C# / Java: project files point at this folder
- Python: `services/grpc-python/generate_proto.py`
- Go: `services/grpc-go/scripts/generate.ps1` (`option go_package` = `github.com/omnitest/grpc-go/internal/gen;personpb`)
- C++: CMake `protoc` from this path
- Node: runtime load via `@grpc/proto-loader`
