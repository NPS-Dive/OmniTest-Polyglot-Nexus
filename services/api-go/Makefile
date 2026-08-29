# ============================================================================
# File: services/api-go/Makefile
# Purpose: Proto codegen and local run helpers for the Go Person gRPC API.
# SOLID: SRP — build/run entrypoints only. Runtime wiring stays in cmd/server.
# ============================================================================

PROTO_DIR := ../../shared/proto
PROTO := $(PROTO_DIR)/person_service.proto
GEN_DIR := internal/gen
MODULE := github.com/omnitest/api-go/internal/gen

.PHONY: generate run tidy build

# Exact protoc command (Linux/macOS/Make). Windows: scripts/generate.ps1
generate:
	mkdir -p $(GEN_DIR)
	protoc -I $(PROTO_DIR) \
		--go_out=$(GEN_DIR) --go_opt=paths=source_relative \
		--go_opt=Mperson_service.proto=$(MODULE) \
		--go-grpc_out=$(GEN_DIR) --go-grpc_opt=paths=source_relative \
		--go-grpc_opt=Mperson_service.proto=$(MODULE) \
		$(PROTO)

run:
	go run ./cmd/server

build:
	go build -o bin/api-go ./cmd/server

tidy:
	go mod tidy
