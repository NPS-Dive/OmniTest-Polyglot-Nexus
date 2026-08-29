// ============================================================================
// File: services/grpc-go/internal/domain/repository.go
// Purpose: Persistence port for Person (DIP). gRPC depends on this, not pgx.
// SOLID: ISP — four RPCs map to four methods; OCP — swap Postgres for a fake.
// Dependencies: context, domain.Person. Implemented by infrastructure/db.
// ============================================================================

package domain

import "context"

// PersonRepository is the data-access contract for persons_golang.
// Implementations must never query another persons_* table.
type PersonRepository interface {
	// Create inserts one person and returns the persisted UUID (inserted_id).
	Create(ctx context.Context, person *Person) (insertedID string, err error)

	// ReadAll returns a page of persons plus the unfiltered table count.
	ReadAll(ctx context.Context, limit, offset int32) (persons []Person, total int32, err error)

	// SearchByFilter applies optional lexical / range / gender predicates.
	// total is the count of matching rows (not just the page length).
	SearchByFilter(ctx context.Context, filter PersonFilter) (persons []Person, total int32, err error)

	// SearchByVector returns the nearest neighbors by L2 (<->). total is the
	// number of rows returned (kNN has no separate "match count").
	SearchByVector(ctx context.Context, vector []float32, topK int32) (persons []Person, total int32, err error)
}
