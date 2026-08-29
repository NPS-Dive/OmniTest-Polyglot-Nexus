// ============================================================================
// File: services/grpc-go/internal/presentation/grpc/server.go
// Purpose: PersonService RPC adapter — proto ↔ domain, then repository calls.
// SOLID: SRP — transport mapping only (no SQL). DIP — depends on PersonRepository.
// Dependencies: personpb, domain, google.golang.org/grpc status codes.
// ============================================================================

package grpc

import (
	"context"
	"errors"
	"strings"

	"github.com/google/uuid"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"

	"github.com/omnitest/grpc-go/internal/domain"
	personpb "github.com/omnitest/grpc-go/internal/gen"
)

// ExpectedEmbeddingDims is MiniLM-L6-v2 / persons_*.embedding vector(384).
const ExpectedEmbeddingDims = 384

// Server implements omnitest.polyglot.nexus.PersonService.
type Server struct {
	personpb.UnimplementedPersonServiceServer
	repo domain.PersonRepository
}

// NewServer wires the repository. main is the only composition root.
func NewServer(repo domain.PersonRepository) *Server {
	return &Server{repo: repo}
}

// CreatePerson validates the payload, maps proto → domain, and inserts one row.
func (s *Server) CreatePerson(ctx context.Context, req *personpb.CreatePersonRequest) (*personpb.CreatePersonResponse, error) {
	if req == nil || req.GetPerson() == nil {
		return nil, status.Error(codes.InvalidArgument, "person is required")
	}

	src := req.GetPerson()
	if strings.TrimSpace(src.GetFirstName()) == "" {
		return nil, status.Error(codes.InvalidArgument, "first_name is required")
	}
	if strings.TrimSpace(src.GetLastName()) == "" {
		return nil, status.Error(codes.InvalidArgument, "last_name is required")
	}
	if src.GetAge() < 0 {
		return nil, status.Error(codes.InvalidArgument, "age must be >= 0")
	}
	if src.GetChildrenCount() < 0 {
		return nil, status.Error(codes.InvalidArgument, "children_count must be >= 0")
	}
	if nc := strings.TrimSpace(src.GetNationalCode()); nc != "" && len(nc) > 10 {
		return nil, status.Error(codes.InvalidArgument, "national_code must be at most 10 characters")
	}
	if id := strings.TrimSpace(src.GetId()); id != "" {
		if _, err := uuid.Parse(id); err != nil {
			return nil, status.Error(codes.InvalidArgument, "id must be a valid UUID")
		}
	}
	if emb := src.GetEmbeddingVector(); len(emb) > 0 && len(emb) != ExpectedEmbeddingDims {
		return nil, status.Errorf(codes.InvalidArgument, "embedding_vector must be empty or %d dimensions", ExpectedEmbeddingDims)
	}

	person := PersonFromProto(src)
	insertedID, err := s.repo.Create(ctx, person)
	if err != nil {
		return &personpb.CreatePersonResponse{
			Success: false,
			Message: err.Error(),
		}, mapRepoError(err)
	}

	return &personpb.CreatePersonResponse{
		Success:    true,
		Message:    "person created in persons_golang",
		InsertedId: insertedID,
	}, nil
}

// ReadAllPersons returns a page of persons. limit default 50, max 500.
func (s *Server) ReadAllPersons(ctx context.Context, req *personpb.ReadAllPersonsRequest) (*personpb.PersonListResponse, error) {
	var limit, offset int32
	if req != nil {
		limit = req.GetLimit()
		offset = req.GetOffset()
	}
	limit = domain.ClampLimit(limit)
	offset = domain.ClampOffset(offset)

	persons, total, err := s.repo.ReadAll(ctx, limit, offset)
	if err != nil {
		return nil, mapRepoError(err)
	}
	return &personpb.PersonListResponse{
		Persons:    PersonsToProto(persons),
		TotalCount: total,
	}, nil
}

// SearchByFilter applies optional first_name, last_name, age range, gender, national_code.
func (s *Server) SearchByFilter(ctx context.Context, req *personpb.FilterSearchRequest) (*personpb.PersonListResponse, error) {
	filter := FilterFromProto(req)
	persons, total, err := s.repo.SearchByFilter(ctx, filter)
	if err != nil {
		return nil, mapRepoError(err)
	}
	return &personpb.PersonListResponse{
		Persons:    PersonsToProto(persons),
		TotalCount: total,
	}, nil
}

// SearchByVector finds nearest neighbors with L2 (<->). top_k default 10, max 100.
func (s *Server) SearchByVector(ctx context.Context, req *personpb.VectorSearchRequest) (*personpb.PersonListResponse, error) {
	if req == nil || len(req.GetVector()) == 0 {
		return nil, status.Error(codes.InvalidArgument, "vector is required")
	}
	if n := len(req.GetVector()); n != ExpectedEmbeddingDims {
		return nil, status.Errorf(codes.InvalidArgument, "vector must have %d dimensions, got %d", ExpectedEmbeddingDims, n)
	}

	topK := domain.ClampTopK(req.GetTopK())
	persons, total, err := s.repo.SearchByVector(ctx, req.GetVector(), topK)
	if err != nil {
		return nil, mapRepoError(err)
	}
	return &personpb.PersonListResponse{
		Persons:    PersonsToProto(persons),
		TotalCount: total,
	}, nil
}

// mapRepoError turns repository failures into gRPC statuses without leaking SQL.
func mapRepoError(err error) error {
	if err == nil {
		return nil
	}
	msg := err.Error()
	switch {
	case strings.Contains(msg, "invalid person id"):
		return status.Error(codes.InvalidArgument, "id must be a valid UUID")
	case strings.Contains(msg, "person is required"), strings.Contains(msg, "vector is required"):
		return status.Error(codes.InvalidArgument, msg)
	case errors.Is(err, context.Canceled):
		return status.Error(codes.Canceled, "request canceled")
	case errors.Is(err, context.DeadlineExceeded):
		return status.Error(codes.DeadlineExceeded, "deadline exceeded")
	default:
		return status.Errorf(codes.Internal, "database error: %s", msg)
	}
}
