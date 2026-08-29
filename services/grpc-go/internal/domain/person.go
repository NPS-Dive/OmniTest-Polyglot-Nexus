// ============================================================================
// File: services/grpc-go/internal/domain/person.go
// Purpose: Persistence-shaped Person entity and SearchByFilter criteria.
// SOLID: SRP — data only. No SQL, no proto, no I/O.
// Dependencies: none (stdlib). Presentation maps proto; infrastructure maps rows.
// Contract: column names match persons_golang. birth_date is derived, not stored.
// ============================================================================

// Package domain holds the Person entity, filter, pagination clamps, and the
// repository port. Nothing here imports proto or pgx (DIP).
package domain

import (
	"fmt"
	"time"
)

// DefaultLimit is applied when ReadAll / filter limit is 0 or omitted.
const DefaultLimit int32 = 50

// MaxLimit caps page size so a client cannot dump the 1M-row table.
const MaxLimit int32 = 500

// DefaultTopK is applied when VectorSearchRequest.top_k is 0 or omitted.
const DefaultTopK int32 = 10

// MaxTopK caps ANN result size (HNSW + LIMIT).
const MaxTopK int32 = 100

// TableName is the only table this service may touch (table-per-language isolation).
const TableName = "persons_golang"

// Person is the domain record for one row in persons_golang.
// Field names follow SQL columns (sex, occupation, embedding), not proto names
// (gender, job_category, embedding_vector). Mapping lives in presentation.
type Person struct {
	// ID is the UUID primary key (string form). Empty on create → generated.
	ID string
	// FirstName maps to first_name.
	FirstName string
	// LastName maps to last_name.
	LastName string
	// Age is stored; birth_date is derived from this on read.
	Age int32
	// Sex is the VARCHAR sex column (seed: "male"; proto: SEX_MALE).
	Sex string
	// MaritalStatus is the VARCHAR marital_status column (seed: "single parent").
	MaritalStatus string
	// ChildrenCount maps to children_count (>= 0).
	ChildrenCount int32
	// LivingPlace is the VARCHAR living_place column (seed: "apartment").
	LivingPlace string
	// Occupation is the VARCHAR occupation column (seed: "job seeker", "full-time").
	Occupation string
	// NationalCode is a 10-character national identifier.
	NationalCode string
	// HasPassport maps to has_passport (default false on seed rows).
	HasPassport bool
	// Embedding is the 384-dim pgvector payload. Nil/empty means SQL NULL.
	Embedding []float32
}

// PersonFilter is the SearchByFilter criteria. Nil / empty fields are ignored.
// Sex is the proto-or-seed label; the repository matches aliases flexibly.
type PersonFilter struct {
	// FirstName, when set and non-empty, is a case-insensitive partial match.
	FirstName *string
	// LastName, when set and non-empty, is a case-insensitive partial match.
	LastName *string
	// MinAge, when set, requires age >= MinAge.
	MinAge *int32
	// MaxAge, when set, requires age <= MaxAge.
	MaxAge *int32
	// Sex, when set, is matched against column sex after label normalization.
	Sex *string
	// NationalCode, when set and non-empty, is an exact match.
	NationalCode *string
	// Limit is the page size after ClampLimit (default 50, max 500).
	Limit int32
	// Offset is the number of matching rows to skip (never negative).
	Offset int32
}

// BirthDateISO derives an approximate ISO date from age.
// Contract: (current calendar year − age)-01-01. Age is stored; birth_date is not.
func (p Person) BirthDateISO() string {
	return BirthDateFromAge(p.Age)
}

// BirthDateFromAge implements the shared birth_date derivation used on every read.
func BirthDateFromAge(age int32) string {
	if age < 0 {
		age = 0
	}
	year := time.Now().Year() - int(age)
	if year < 1 {
		year = 1
	}
	return fmt.Sprintf("%04d-01-01", year)
}

// ClampLimit enforces pagination: default 50, max 500.
func ClampLimit(limit int32) int32 {
	if limit <= 0 {
		return DefaultLimit
	}
	if limit > MaxLimit {
		return MaxLimit
	}
	return limit
}

// ClampTopK enforces vector page size: default 10, max 100.
func ClampTopK(topK int32) int32 {
	if topK <= 0 {
		return DefaultTopK
	}
	if topK > MaxTopK {
		return MaxTopK
	}
	return topK
}

// ClampOffset rejects negative offsets (treat as start of the result set).
func ClampOffset(offset int32) int32 {
	if offset < 0 {
		return 0
	}
	return offset
}
