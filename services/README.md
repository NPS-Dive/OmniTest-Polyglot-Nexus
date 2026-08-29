# services

| Folder | Port | Role |
|--------|------|------|
| `api-cpp` | 50051 | Person gRPC → `persons_cpp` |
| `api-python` | 50052 | Person gRPC → `persons_python` |
| `api-java` | 50053 | Person gRPC → `persons_java` |
| `api-go` | 50054 | Person gRPC → `persons_golang` |
| `api-csharp` | 5078 | Person gRPC → `persons_csharp` |
| `api-node` | 5079 | Person gRPC → `persons_node` |
| `ai-gateway` | 5082 | FastAPI `/rag/query` `/agent/run` |
| `ai-agents` | — | OpenClaw + Hermes + MCP + LangGraph scaffolding |
