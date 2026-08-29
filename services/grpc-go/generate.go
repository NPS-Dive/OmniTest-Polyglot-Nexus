//go:build generate

// ============================================================================
// File: services/grpc-go/generate.go
// Purpose: Host //go:generate so `go generate ./...` rebuilds gRPC stubs from
//          the shared proto. This file is excluded from normal builds.
// SOLID: SRP — codegen entry only; no runtime types.
// Dependencies: scripts/generate.ps1 (Windows) or make generate (Make).
// ============================================================================

// Package generate exists solely as an anchor for go:generate directives.
package generate

// Rebuild personpb stubs from shared/proto/person_service.proto.
// Requires protoc, protoc-gen-go, and protoc-gen-go-grpc on PATH.
//
//go:generate powershell -NoProfile -ExecutionPolicy Bypass -File scripts/generate.ps1
