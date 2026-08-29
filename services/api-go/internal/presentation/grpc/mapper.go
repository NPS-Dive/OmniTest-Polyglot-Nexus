// ============================================================================
// File: services/api-go/internal/presentation/grpc/mapper.go
// Purpose: Bidirectional mapping between proto messages and domain.Person.
// SOLID: SRP — translation only. No SQL. Server methods stay orchestration.
// Dependencies: personpb stubs, domain. Seed labels are lowercase with spaces
//               or hyphens (male, "job seeker", "full-time", "single parent").
// ============================================================================

// Package grpc is the PersonService presentation layer (proto mapping + RPCs).
package grpc

import (
	"strings"
	"unicode"

	"github.com/omnitest/api-go/internal/domain"
	personpb "github.com/omnitest/api-go/internal/gen"
)

// PersonToProto maps a domain row to the shared Person message.
// gender ← sex, job_category ← occupation, embedding_vector ← embedding,
// birth_date is derived (never read from SQL).
func PersonToProto(p domain.Person) *personpb.Person {
	return &personpb.Person{
		Id:              p.ID,
		FirstName:       p.FirstName,
		LastName:        p.LastName,
		Age:             p.Age,
		BirthDate:       p.BirthDateISO(),
		Gender:          SexFromDB(p.Sex),
		MaritalStatus:   MaritalFromDB(p.MaritalStatus),
		ChildrenCount:   p.ChildrenCount,
		LivingPlace:     LivingFromDB(p.LivingPlace),
		JobCategory:     OccupationFromDB(p.Occupation),
		NationalCode:    p.NationalCode,
		HasPassport:     p.HasPassport,
		EmbeddingVector: p.Embedding,
	}
}

// PersonsToProto maps a slice (never returns a nil repeated field).
func PersonsToProto(persons []domain.Person) []*personpb.Person {
	out := make([]*personpb.Person, 0, len(persons))
	for _, p := range persons {
		out = append(out, PersonToProto(p))
	}
	return out
}

// PersonFromProto maps a create/update payload onto domain storage labels.
// Writes seed-style lowercase so new rows match the 1M CSV (male, job seeker).
func PersonFromProto(msg *personpb.Person) *domain.Person {
	if msg == nil {
		return nil
	}
	return &domain.Person{
		ID:            strings.TrimSpace(msg.GetId()),
		FirstName:     strings.TrimSpace(msg.GetFirstName()),
		LastName:      strings.TrimSpace(msg.GetLastName()),
		Age:           msg.GetAge(),
		Sex:           SexToDB(msg.GetGender()),
		MaritalStatus: MaritalToDB(msg.GetMaritalStatus()),
		ChildrenCount: msg.GetChildrenCount(),
		LivingPlace:   LivingToDB(msg.GetLivingPlace()),
		Occupation:    OccupationToDB(msg.GetJobCategory()),
		NationalCode:  strings.TrimSpace(msg.GetNationalCode()),
		HasPassport:   msg.GetHasPassport(),
		Embedding:     msg.GetEmbeddingVector(),
	}
}

// FilterFromProto copies optional proto fields into a domain filter.
// Unspecified gender is treated as "not provided" so we do not filter to unknown.
func FilterFromProto(req *personpb.FilterSearchRequest) domain.PersonFilter {
	f := domain.PersonFilter{
		Limit:  domain.DefaultLimit,
		Offset: 0,
	}
	if req == nil {
		return f
	}
	if req.FirstName != nil {
		v := strings.TrimSpace(req.GetFirstName())
		if v != "" {
			f.FirstName = &v
		}
	}
	if req.LastName != nil {
		v := strings.TrimSpace(req.GetLastName())
		if v != "" {
			f.LastName = &v
		}
	}
	if req.MinAge != nil {
		v := req.GetMinAge()
		f.MinAge = &v
	}
	if req.MaxAge != nil {
		v := req.GetMaxAge()
		f.MaxAge = &v
	}
	if req.Gender != nil && req.GetGender() != personpb.Sex_SEX_UNSPECIFIED {
		v := SexToDB(req.GetGender())
		f.Sex = &v
	}
	if req.NationalCode != nil {
		v := strings.TrimSpace(req.GetNationalCode())
		if v != "" {
			f.NationalCode = &v
		}
	}
	return f
}

// SexFromDB maps VARCHAR sex → proto Sex. Accepts seed, prefixless, and SEX_* forms.
func SexFromDB(raw string) personpb.Sex {
	switch normalizeLabel(raw) {
	case "male":
		return personpb.Sex_SEX_MALE
	case "female":
		return personpb.Sex_SEX_FEMALE
	case "bigender":
		return personpb.Sex_SEX_BIGENDER
	case "agender":
		return personpb.Sex_SEX_AGENDER
	default:
		return personpb.Sex_SEX_UNSPECIFIED
	}
}

// SexToDB maps proto Sex → seed-style storage ("male", not "SEX_MALE").
func SexToDB(v personpb.Sex) string {
	switch v {
	case personpb.Sex_SEX_MALE:
		return "male"
	case personpb.Sex_SEX_FEMALE:
		return "female"
	case personpb.Sex_SEX_BIGENDER:
		return "bigender"
	case personpb.Sex_SEX_AGENDER:
		return "agender"
	default:
		return "not specified"
	}
}

// MaritalFromDB maps VARCHAR marital_status → proto, including "single parent".
func MaritalFromDB(raw string) personpb.MaritalStatus {
	switch normalizeLabel(raw) {
	case "single":
		return personpb.MaritalStatus_MARITAL_STATUS_SINGLE
	case "married":
		return personpb.MaritalStatus_MARITAL_STATUS_MARRIED
	case "divorced":
		return personpb.MaritalStatus_MARITAL_STATUS_DIVORCED
	case "widowed":
		return personpb.MaritalStatus_MARITAL_STATUS_WIDOWED
	case "single parent":
		return personpb.MaritalStatus_MARITAL_STATUS_SINGLE_PARENT
	default:
		return personpb.MaritalStatus_MARITAL_STATUS_UNSPECIFIED
	}
}

// MaritalToDB maps proto MaritalStatus → seed label ("single parent").
func MaritalToDB(v personpb.MaritalStatus) string {
	switch v {
	case personpb.MaritalStatus_MARITAL_STATUS_SINGLE:
		return "single"
	case personpb.MaritalStatus_MARITAL_STATUS_MARRIED:
		return "married"
	case personpb.MaritalStatus_MARITAL_STATUS_DIVORCED:
		return "divorced"
	case personpb.MaritalStatus_MARITAL_STATUS_WIDOWED:
		return "widowed"
	case personpb.MaritalStatus_MARITAL_STATUS_SINGLE_PARENT:
		return "single parent"
	default:
		return "unspecified"
	}
}

// LivingFromDB maps VARCHAR living_place → proto LivingPlace.
func LivingFromDB(raw string) personpb.LivingPlace {
	switch normalizeLabel(raw) {
	case "studio":
		return personpb.LivingPlace_LIVING_PLACE_STUDIO
	case "apartment":
		return personpb.LivingPlace_LIVING_PLACE_APARTMENT
	case "house":
		return personpb.LivingPlace_LIVING_PLACE_HOUSE
	case "villa":
		return personpb.LivingPlace_LIVING_PLACE_VILLA
	case "hostel":
		return personpb.LivingPlace_LIVING_PLACE_HOSTEL
	case "dorm":
		return personpb.LivingPlace_LIVING_PLACE_DORM
	case "hotel":
		return personpb.LivingPlace_LIVING_PLACE_HOTEL
	default:
		return personpb.LivingPlace_LIVING_PLACE_UNSPECIFIED
	}
}

// LivingToDB maps proto LivingPlace → seed label ("apartment").
func LivingToDB(v personpb.LivingPlace) string {
	switch v {
	case personpb.LivingPlace_LIVING_PLACE_STUDIO:
		return "studio"
	case personpb.LivingPlace_LIVING_PLACE_APARTMENT:
		return "apartment"
	case personpb.LivingPlace_LIVING_PLACE_HOUSE:
		return "house"
	case personpb.LivingPlace_LIVING_PLACE_VILLA:
		return "villa"
	case personpb.LivingPlace_LIVING_PLACE_HOSTEL:
		return "hostel"
	case personpb.LivingPlace_LIVING_PLACE_DORM:
		return "dorm"
	case personpb.LivingPlace_LIVING_PLACE_HOTEL:
		return "hotel"
	default:
		return "unspecified"
	}
}

// OccupationFromDB maps VARCHAR occupation → proto job_category.
// Seed uses "job seeker" and "full-time"; proto uses OCCUPATION_JOB_SEEKER / FULL_TIME.
func OccupationFromDB(raw string) personpb.Occupation {
	switch normalizeLabel(raw) {
	case "job seeker":
		return personpb.Occupation_OCCUPATION_JOB_SEEKER
	case "jobless":
		return personpb.Occupation_OCCUPATION_JOBLESS
	case "full time":
		return personpb.Occupation_OCCUPATION_FULL_TIME
	case "part time":
		return personpb.Occupation_OCCUPATION_PART_TIME
	case "student":
		return personpb.Occupation_OCCUPATION_STUDENT
	case "housekeeper":
		return personpb.Occupation_OCCUPATION_HOUSEKEEPER
	default:
		return personpb.Occupation_OCCUPATION_UNSPECIFIED
	}
}

// OccupationToDB maps proto Occupation → seed label ("job seeker", "full-time").
func OccupationToDB(v personpb.Occupation) string {
	switch v {
	case personpb.Occupation_OCCUPATION_JOB_SEEKER:
		return "job seeker"
	case personpb.Occupation_OCCUPATION_JOBLESS:
		return "jobless"
	case personpb.Occupation_OCCUPATION_FULL_TIME:
		return "full-time"
	case personpb.Occupation_OCCUPATION_PART_TIME:
		return "part-time"
	case personpb.Occupation_OCCUPATION_STUDENT:
		return "student"
	case personpb.Occupation_OCCUPATION_HOUSEKEEPER:
		return "housekeeper"
	default:
		return "unspecified"
	}
}

// normalizeLabel is the Go twin of the SQL normalizer in postgres.go.
// Lowercase, unify _ and - to spaces, collapse whitespace, strip proto prefixes.
func normalizeLabel(raw string) string {
	s := strings.ToLower(strings.TrimSpace(raw))
	if s == "" {
		return ""
	}
	var b strings.Builder
	b.Grow(len(s))
	prevSpace := false
	for _, r := range s {
		if r == '_' || r == '-' {
			r = ' '
		}
		if unicode.IsSpace(r) {
			if prevSpace {
				continue
			}
			prevSpace = true
			b.WriteByte(' ')
			continue
		}
		prevSpace = false
		b.WriteRune(r)
	}
	s = strings.TrimSpace(b.String())
	for _, prefix := range []string{"sex ", "marital status ", "living place ", "occupation "} {
		s = strings.TrimPrefix(s, prefix)
	}
	return s
}
