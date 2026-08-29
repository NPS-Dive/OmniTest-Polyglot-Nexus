// ============================================================================
// File: services/api-go/internal/infrastructure/db/postgres.go
// Purpose: pgx implementation of domain.PersonRepository against persons_golang.
// SOLID: DIP — satisfies the domain port; SRP — SQL only, no proto mapping.
// Dependencies: pgx/v5 pool, domain, otel traces (no-op unless provider set).
// Contract: L2 operator <-> ; embedding stored as '[1,2,...]'::vector.
// ============================================================================

// Package db is the Postgres/pgx adapter for persons_golang.
package db

import (
	"context"
	"fmt"
	"strconv"
	"strings"
	"time"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/codes"
	"go.opentelemetry.io/otel/trace"

	"github.com/omnitest/api-go/internal/domain"
)

// personColumns is the SELECT list. embedding is cast to text so we can parse
// the pgvector literal without a CGO driver. birth_date is intentionally absent.
const personColumns = `
	id::text,
	first_name,
	last_name,
	age,
	sex,
	marital_status,
	children_count,
	living_place,
	occupation,
	national_code,
	COALESCE(has_passport, false) AS has_passport,
	embedding::text
`

// sqlNormalizeLabel turns seed labels and proto-style names into one key.
// "SEX_MALE" / "male" → "male"; "OCCUPATION_JOB_SEEKER" / "job seeker" → "job seeker";
// "full-time" / "FULL_TIME" → "full time"; "single parent" stays "single parent".
// %s is a trusted identifier or $N placeholder — never concatenate user SQL.
const sqlNormalizeLabel = `trim(both from regexp_replace(
	regexp_replace(replace(replace(lower(%s), '_', ' '), '-', ' '), '\s+', ' ', 'g'),
	'^(sex|marital status|living place|occupation) ',
	''
))`

// PostgresPersonRepository is the Postgres adapter for persons_golang.
type PostgresPersonRepository struct {
	pool   *pgxpool.Pool
	tracer trace.Tracer
}

// NewPostgresPersonRepository wraps an existing pool. The pool is owned by main.
func NewPostgresPersonRepository(pool *pgxpool.Pool) *PostgresPersonRepository {
	return &PostgresPersonRepository{
		pool:   pool,
		tracer: otel.Tracer("api-go/db"),
	}
}

// Connect opens a pgx pool, pings Postgres, and returns the pool for injection.
func Connect(ctx context.Context, dsn string) (*pgxpool.Pool, error) {
	cfg, err := pgxpool.ParseConfig(dsn)
	if err != nil {
		return nil, fmt.Errorf("parse postgres dsn: %w", err)
	}
	cfg.MaxConns = 16
	cfg.MinConns = 1
	cfg.MaxConnLifetime = time.Hour
	cfg.HealthCheckPeriod = 30 * time.Second

	pool, err := pgxpool.NewWithConfig(ctx, cfg)
	if err != nil {
		return nil, fmt.Errorf("open postgres pool: %w", err)
	}
	if err := pool.Ping(ctx); err != nil {
		pool.Close()
		return nil, fmt.Errorf("ping postgres: %w", err)
	}
	return pool, nil
}

// Create inserts one row. Empty ID → generated UUID. Empty embedding → NULL.
func (r *PostgresPersonRepository) Create(ctx context.Context, person *domain.Person) (string, error) {
	ctx, span := r.tracer.Start(ctx, "PersonRepository.Create")
	defer span.End()

	if person == nil {
		err := fmt.Errorf("person is required")
		span.RecordError(err)
		span.SetStatus(codes.Error, err.Error())
		return "", err
	}

	id := strings.TrimSpace(person.ID)
	if id == "" {
		id = uuid.NewString()
	} else if _, err := uuid.Parse(id); err != nil {
		span.RecordError(err)
		span.SetStatus(codes.Error, "invalid uuid")
		return "", fmt.Errorf("invalid person id: %w", err)
	}

	emb := vectorLiteral(person.Embedding)
	var embArg any
	if emb == "" {
		embArg = nil
	} else {
		embArg = emb
	}

	const q = `
		INSERT INTO persons_golang (
			id, first_name, last_name, age, sex, marital_status,
			children_count, living_place, occupation, national_code,
			embedding, has_passport
		) VALUES (
			$1::uuid, $2, $3, $4, $5, $6, $7, $8, $9, $10,
			$11::vector, $12
		)
		RETURNING id::text
	`

	start := time.Now()
	var inserted string
	err := r.pool.QueryRow(ctx, q,
		id,
		person.FirstName,
		person.LastName,
		person.Age,
		person.Sex,
		person.MaritalStatus,
		person.ChildrenCount,
		person.LivingPlace,
		person.Occupation,
		person.NationalCode,
		embArg,
		person.HasPassport,
	).Scan(&inserted)
	span.SetAttributes(attribute.Int64("db.duration_ms", time.Since(start).Milliseconds()))
	if err != nil {
		span.RecordError(err)
		span.SetStatus(codes.Error, err.Error())
		return "", fmt.Errorf("insert persons_golang: %w", err)
	}
	return inserted, nil
}

// ReadAll returns a deterministic page (ORDER BY id) plus the full table count.
func (r *PostgresPersonRepository) ReadAll(ctx context.Context, limit, offset int32) ([]domain.Person, int32, error) {
	ctx, span := r.tracer.Start(ctx, "PersonRepository.ReadAll")
	defer span.End()

	limit = domain.ClampLimit(limit)
	offset = domain.ClampOffset(offset)
	span.SetAttributes(
		attribute.Int("limit", int(limit)),
		attribute.Int("offset", int(offset)),
	)

	total, err := r.scalarCount(ctx, `SELECT COUNT(*) FROM persons_golang`, nil)
	if err != nil {
		span.RecordError(err)
		span.SetStatus(codes.Error, err.Error())
		return nil, 0, err
	}

	q := fmt.Sprintf(`
		SELECT %s
		FROM persons_golang
		ORDER BY id
		LIMIT $1 OFFSET $2
	`, personColumns)

	start := time.Now()
	rows, err := r.pool.Query(ctx, q, limit, offset)
	span.SetAttributes(attribute.Int64("db.duration_ms", time.Since(start).Milliseconds()))
	if err != nil {
		span.RecordError(err)
		span.SetStatus(codes.Error, err.Error())
		return nil, 0, fmt.Errorf("read persons_golang: %w", err)
	}
	persons, err := scanPersons(rows)
	if err != nil {
		span.RecordError(err)
		span.SetStatus(codes.Error, err.Error())
		return nil, 0, err
	}
	return persons, total, nil
}

// SearchByFilter builds a parameterized WHERE clause. Unset fields add no predicate.
func (r *PostgresPersonRepository) SearchByFilter(ctx context.Context, filter domain.PersonFilter) ([]domain.Person, int32, error) {
	ctx, span := r.tracer.Start(ctx, "PersonRepository.SearchByFilter")
	defer span.End()

	limit := domain.ClampLimit(filter.Limit)
	offset := domain.ClampOffset(filter.Offset)

	where, args := buildFilterWhere(filter)
	countSQL := `SELECT COUNT(*) FROM persons_golang` + where
	total, err := r.scalarCount(ctx, countSQL, args)
	if err != nil {
		span.RecordError(err)
		span.SetStatus(codes.Error, err.Error())
		return nil, 0, err
	}

	args = append(args, limit, offset)
	limitPH := len(args) - 1
	offsetPH := len(args)
	q := fmt.Sprintf(`
		SELECT %s
		FROM persons_golang
		%s
		ORDER BY id
		LIMIT $%d OFFSET $%d
	`, personColumns, where, limitPH, offsetPH)

	start := time.Now()
	rows, err := r.pool.Query(ctx, q, args...)
	span.SetAttributes(attribute.Int64("db.duration_ms", time.Since(start).Milliseconds()))
	if err != nil {
		span.RecordError(err)
		span.SetStatus(codes.Error, err.Error())
		return nil, 0, fmt.Errorf("filter persons_golang: %w", err)
	}
	persons, err := scanPersons(rows)
	if err != nil {
		span.RecordError(err)
		span.SetStatus(codes.Error, err.Error())
		return nil, 0, err
	}
	return persons, total, nil
}

// SearchByVector ranks by L2 distance (<->) to match HNSW vector_l2_ops.
func (r *PostgresPersonRepository) SearchByVector(ctx context.Context, vector []float32, topK int32) ([]domain.Person, int32, error) {
	ctx, span := r.tracer.Start(ctx, "PersonRepository.SearchByVector")
	defer span.End()

	topK = domain.ClampTopK(topK)
	lit := vectorLiteral(vector)
	if lit == "" {
		err := fmt.Errorf("vector is required")
		span.RecordError(err)
		span.SetStatus(codes.Error, err.Error())
		return nil, 0, err
	}

	q := fmt.Sprintf(`
		SELECT %s
		FROM persons_golang
		WHERE embedding IS NOT NULL
		ORDER BY embedding <-> $1::vector
		LIMIT $2
	`, personColumns)

	start := time.Now()
	rows, err := r.pool.Query(ctx, q, lit, topK)
	span.SetAttributes(
		attribute.Int64("db.duration_ms", time.Since(start).Milliseconds()),
		attribute.Int("top_k", int(topK)),
		attribute.Int("vector.dims", len(vector)),
	)
	if err != nil {
		span.RecordError(err)
		span.SetStatus(codes.Error, err.Error())
		return nil, 0, fmt.Errorf("vector search persons_golang: %w", err)
	}
	persons, err := scanPersons(rows)
	if err != nil {
		span.RecordError(err)
		span.SetStatus(codes.Error, err.Error())
		return nil, 0, err
	}
	return persons, int32(len(persons)), nil
}

// scalarCount runs a COUNT(*) (or equivalent) with the same args as the page query.
func (r *PostgresPersonRepository) scalarCount(ctx context.Context, sql string, args []any) (int32, error) {
	var n int64
	if err := r.pool.QueryRow(ctx, sql, args...).Scan(&n); err != nil {
		return 0, fmt.Errorf("count persons_golang: %w", err)
	}
	return int32(n), nil
}

// buildFilterWhere returns " WHERE …" (or "") and bind args. Column names are fixed.
func buildFilterWhere(filter domain.PersonFilter) (string, []any) {
	var clauses []string
	var args []any

	add := func(clause string, value any) {
		args = append(args, value)
		clauses = append(clauses, fmt.Sprintf(clause, len(args)))
	}

	if s := derefTrim(filter.FirstName); s != "" {
		add(`first_name ILIKE $%d ESCAPE '\'`, "%"+escapeLike(s)+"%")
	}
	if s := derefTrim(filter.LastName); s != "" {
		add(`last_name ILIKE $%d ESCAPE '\'`, "%"+escapeLike(s)+"%")
	}
	if filter.MinAge != nil {
		add("age >= $%d", *filter.MinAge)
	}
	if filter.MaxAge != nil {
		add("age <= $%d", *filter.MaxAge)
	}
	if s := derefTrim(filter.Sex); s != "" {
		args = append(args, s)
		n := len(args)
		clauses = append(clauses, fmt.Sprintf(
			"%s = %s",
			fmt.Sprintf(sqlNormalizeLabel, "sex"),
			fmt.Sprintf(sqlNormalizeLabel, fmt.Sprintf("$%d", n)),
		))
	}
	if s := derefTrim(filter.NationalCode); s != "" {
		add("national_code = $%d", s)
	}

	if len(clauses) == 0 {
		return "", args
	}
	return " WHERE " + strings.Join(clauses, " AND "), args
}

// scanPersons consumes rows shaped like personColumns and closes the row set.
func scanPersons(rows pgx.Rows) ([]domain.Person, error) {
	defer rows.Close()
	var out []domain.Person
	for rows.Next() {
		var (
			p           domain.Person
			embText     *string
			hasPassport bool
		)
		if err := rows.Scan(
			&p.ID,
			&p.FirstName,
			&p.LastName,
			&p.Age,
			&p.Sex,
			&p.MaritalStatus,
			&p.ChildrenCount,
			&p.LivingPlace,
			&p.Occupation,
			&p.NationalCode,
			&hasPassport,
			&embText,
		); err != nil {
			return nil, fmt.Errorf("scan person: %w", err)
		}
		p.HasPassport = hasPassport
		if embText != nil {
			p.Embedding = parseVectorLiteral(*embText)
		}
		out = append(out, p)
	}
	if err := rows.Err(); err != nil {
		return nil, fmt.Errorf("iterate persons: %w", err)
	}
	if out == nil {
		out = []domain.Person{}
	}
	return out, nil
}

// vectorLiteral formats a float slice as a pgvector text literal, or "" if empty.
func vectorLiteral(v []float32) string {
	if len(v) == 0 {
		return ""
	}
	var b strings.Builder
	b.WriteByte('[')
	for i, x := range v {
		if i > 0 {
			b.WriteByte(',')
		}
		b.WriteString(strconv.FormatFloat(float64(x), 'f', -1, 32))
	}
	b.WriteByte(']')
	return b.String()
}

// parseVectorLiteral parses "[1,2,3]" / "{1,2,3}" from embedding::text.
func parseVectorLiteral(raw string) []float32 {
	s := strings.TrimSpace(raw)
	s = strings.TrimPrefix(s, "[")
	s = strings.TrimSuffix(s, "]")
	s = strings.TrimPrefix(s, "{")
	s = strings.TrimSuffix(s, "}")
	s = strings.TrimSpace(s)
	if s == "" {
		return nil
	}
	parts := strings.Split(s, ",")
	out := make([]float32, 0, len(parts))
	for _, part := range parts {
		part = strings.TrimSpace(part)
		if part == "" {
			continue
		}
		f, err := strconv.ParseFloat(part, 32)
		if err != nil {
			continue
		}
		out = append(out, float32(f))
	}
	return out
}

// escapeLike prefixes \, %, and _ so user text is literal inside ILIKE.
func escapeLike(s string) string {
	s = strings.ReplaceAll(s, `\`, `\\`)
	s = strings.ReplaceAll(s, `%`, `\%`)
	s = strings.ReplaceAll(s, `_`, `\_`)
	return s
}

// derefTrim returns the trimmed pointer value, or "" when nil.
func derefTrim(p *string) string {
	if p == nil {
		return ""
	}
	return strings.TrimSpace(*p)
}
