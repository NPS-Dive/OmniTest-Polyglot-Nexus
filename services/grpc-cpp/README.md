# C++ Person gRPC service (`api-cpp`)

gRPC Person API for OmniTest-Polyglot-Nexus. Listens on **0.0.0.0:50051** and reads/writes **only** `persons_cpp` in `opn_db`.

## Layout (SOLID)

| Path | Role |
|------|------|
| `src/domain/Person.hpp` | Entity (data only) |
| `src/domain/IPersonRepository.hpp` | Persistence port (DIP) |
| `src/infrastructure/db/` | libpqxx adapter — SQL stays here |
| `src/infrastructure/telemetry/Otel.hpp` | OTLP stub (logs if `OTEL_EXPORTER_OTLP_ENDPOINT` is set) |
| `src/presentation/grpc/` | Proto ↔ domain mapping, no SQL |
| `src/main.cpp` | Composition root: env → repo → service → server |

Contract: `shared/proto/person_service.proto` (package `omnitest.polyglot.nexus`). Generated files are `person_service.pb.h` and `person_service.grpc.pb.h`.

## Environment

| Variable | Default |
|----------|---------|
| `POSTGRES_HOST` | `localhost` |
| `POSTGRES_PORT` | `5432` |
| `POSTGRES_USER` | `opn_admin` |
| `POSTGRES_PASSWORD` | `opn_secret` |
| `POSTGRES_DB` | `opn_db` |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | unset (stub idle) |

Start Postgres from `shared/infrastructure/docker-compose.yml` before running the binary.

## Windows (vcpkg)

Install [vcpkg](https://github.com/microsoft/vcpkg) and the C++ toolchain (Visual Studio or Build Tools).

```powershell
$env:VCPKG_ROOT = "C:\src\vcpkg"   # your clone
& $env:VCPKG_ROOT\vcpkg install grpc protobuf libpqxx --triplet x64-windows

cmake -S . -B build `
  -DCMAKE_TOOLCHAIN_FILE="$env:VCPKG_ROOT\scripts\buildsystems\vcpkg.cmake" `
  -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release
.\build\Release\api_cpp.exe
```

If you prefer a manifest, create `vcpkg.json` next to this README with dependencies `grpc`, `protobuf`, and `libpqxx`, then configure with the same toolchain file (`VCPKG_FEATURE_FLAGS=manifests` is the default in current vcpkg).

## Linux

Debian/Ubuntu-style packages (names vary by distro):

```bash
sudo apt-get update
sudo apt-get install -y \
  cmake g++ pkg-config \
  protobuf-compiler libprotobuf-dev \
  libgrpc++-dev protobuf-compiler-grpc \
  libpqxx-dev libpq-dev
```

Arch: `pacman -S cmake gcc protobuf grpc libpqxx postgresql-libs`.

```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build -j
./build/api_cpp
```

Fedora/RHEL package names differ (`grpc-devel`, `protobuf-devel`, `libpqxx-devel`); the CMake `find_package` names stay `Protobuf`, `gRPC`, and `pqxx`.

## RPCs

All four proto RPCs are implemented against `persons_cpp`:

- `CreatePerson` — returns `success`, `message`, `inserted_id`
- `ReadAllPersons` — `limit` default 50, max 500; `total_count` is `COUNT(*)`
- `SearchByFilter` — `first_name`, `last_name`, `min_age`, `max_age`, `gender`, `national_code`
- `SearchByVector` — L2 distance (`embedding <-> query`), `top_k` default 10, max 100

Wire mapping: `gender`↔`sex`, `job_category`↔`occupation`, `embedding_vector`↔`embedding`. `birth_date` is `(current_year - age)-01-01`. Seed CSV labels (`male`, `full-time`, `single parent`) are mapped flexibly onto proto enums.
