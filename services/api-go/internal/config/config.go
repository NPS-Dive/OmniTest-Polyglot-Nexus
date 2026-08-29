// ============================================================================
// File: services/api-go/internal/config/config.go
// Purpose: Load listen port and Postgres settings from the environment.
// SOLID: SRP — configuration only. Composition root calls Load(); nothing else.
// Dependencies: os, strconv, net/url. Defaults match docker-compose opn_db.
// ============================================================================

// Package config loads PORT and POSTGRES_* from the environment with local defaults.
package config

import (
	"fmt"
	"net/url"
	"os"
	"strconv"
)

// DefaultPort is the locked Go Person API port (C++ 50051 … Go 50054).
const DefaultPort = 50054

// Config is the process configuration assembled from env vars.
type Config struct {
	// Port is the gRPC listen port (PORT overrides DefaultPort).
	Port int
	// PostgresHost is POSTGRES_HOST (default localhost).
	PostgresHost string
	// PostgresPort is POSTGRES_PORT (default 5432).
	PostgresPort int
	// PostgresDB is POSTGRES_DB or POSTGRES_DATABASE (default opn_db).
	PostgresDB string
	// PostgresUser is POSTGRES_USER (default opn_admin).
	PostgresUser string
	// PostgresPassword is POSTGRES_PASSWORD (default opn_secret).
	PostgresPassword string
	// PostgresSSLMode is POSTGRES_SSLMODE (default disable) for local Docker.
	PostgresSSLMode string
	// ServiceName is OTEL_SERVICE_NAME (default api-go).
	ServiceName string
}

// Load reads environment variables and applies locked local defaults.
// Secrets are never hardcoded beyond the published local-dev password.
func Load() Config {
	return Config{
		Port:             envInt("PORT", DefaultPort),
		PostgresHost:     envOr("POSTGRES_HOST", "localhost"),
		PostgresPort:     envInt("POSTGRES_PORT", 5432),
		PostgresDB:       envFirst([]string{"POSTGRES_DB", "POSTGRES_DATABASE"}, "opn_db"),
		PostgresUser:     envOr("POSTGRES_USER", "opn_admin"),
		PostgresPassword: envOr("POSTGRES_PASSWORD", "opn_secret"),
		PostgresSSLMode:  envOr("POSTGRES_SSLMODE", "disable"),
		ServiceName:      envOr("OTEL_SERVICE_NAME", "api-go"),
	}
}

// ListenAddr is the TCP bind address (all interfaces so Docker/host clients work).
func (c Config) ListenAddr() string {
	return fmt.Sprintf("0.0.0.0:%d", c.Port)
}

// PostgresDSN builds a pgx-compatible URL. Password is URL-escaped.
func (c Config) PostgresDSN() string {
	user := url.UserPassword(c.PostgresUser, c.PostgresPassword)
	u := url.URL{
		Scheme: "postgres",
		User:   user,
		Host:   fmt.Sprintf("%s:%d", c.PostgresHost, c.PostgresPort),
		Path:   "/" + c.PostgresDB,
	}
	q := u.Query()
	q.Set("sslmode", c.PostgresSSLMode)
	u.RawQuery = q.Encode()
	return u.String()
}

// envOr returns the trimmed env value or fallback when unset/blank.
func envOr(key, fallback string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return fallback
}

// envFirst returns the first non-empty env var in keys, else fallback.
func envFirst(keys []string, fallback string) string {
	for _, key := range keys {
		if v := os.Getenv(key); v != "" {
			return v
		}
	}
	return fallback
}

// envInt parses a positive integer env var; invalid or missing → fallback.
func envInt(key string, fallback int) int {
	raw := os.Getenv(key)
	if raw == "" {
		return fallback
	}
	n, err := strconv.Atoi(raw)
	if err != nil || n <= 0 {
		return fallback
	}
	return n
}
