// ==============================================================================
// File: Domain/Entities/PersonEntity.cs
// Purpose: EF Core row for persons_csharp. Property names match SQL columns.
// SOLID: SRP — persistence model. Domain Person is mapped in the repository.
// ==============================================================================

using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using Pgvector;

namespace OmniTest.Polyglot.Nexus.Api.CSharp.Domain.Entities;

/// <summary>EF entity mapped to persons_csharp (canonical schema).</summary>
[Table("persons_csharp")]
public sealed class PersonEntity
{
    [Key]
    [Column("id")]
    public Guid Id { get; set; }

    [Column("first_name")]
    public string FirstName { get; set; } = string.Empty;

    [Column("last_name")]
    public string LastName { get; set; } = string.Empty;

    [Column("age")]
    public int Age { get; set; }

    [Column("sex")]
    public string Sex { get; set; } = string.Empty;

    [Column("marital_status")]
    public string MaritalStatus { get; set; } = string.Empty;

    [Column("children_count")]
    public int ChildrenCount { get; set; }

    [Column("living_place")]
    public string LivingPlace { get; set; } = string.Empty;

    [Column("occupation")]
    public string Occupation { get; set; } = string.Empty;

    [Column("national_code")]
    public string NationalCode { get; set; } = string.Empty;

    [Column("embedding")]
    public Vector? Embedding { get; set; }

    [Column("has_passport")]
    public bool HasPassport { get; set; }
}
