# grpc-node

TypeScript gRPC Person service on **port 5079**, table **`persons_node` only**.

```powershell
cd services/grpc-node
npm install
npm start
```

Env: `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `PORT`.

Layers: `domain/` (typed `Person` + `IPersonRepository`) → `infrastructure/db` (L2) → `presentation/PersonController` (full filter + `top_k` + `inserted_id`).
