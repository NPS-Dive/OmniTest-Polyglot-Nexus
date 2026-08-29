// ==============================================================================
// File: Domain/Person.cs
// Purpose: Persistence-free Person used by IPersonRepository.
// SOLID: SRP — shape only. EF mapping lives on PersonEntity.
// ==============================================================================

namespace OmniTest.Polyglot.Nexus.Api.CSharp.Domain;

/// <summary>Domain person. Categoricals match seed VARCHAR labels.</summary>
public sealed class Person
{
    public Guid? Id { get; set; }
    public string FirstName { get; set; } = string.Empty;
    public string LastName { get; set; } = string.Empty;
    public int Age { get; set; }
    public string Sex { get; set; } = string.Empty;
    public string MaritalStatus { get; set; } = string.Empty;
    public int ChildrenCount { get; set; }
    public string LivingPlace { get; set; } = string.Empty;
    public string Occupation { get; set; } = string.Empty;
    public string NationalCode { get; set; } = string.Empty;
    public bool HasPassport { get; set; }
    public float[]? Embedding { get; set; }
}

/// <summary>SearchByFilter criteria. Null means unconstrained.</summary>
public sealed class PersonFilter
{
    public string? FirstName { get; set; }
    public string? LastName { get; set; }
    public int? MinAge { get; set; }
    public int? MaxAge { get; set; }
    public string? Sex { get; set; }
    public string? NationalCode { get; set; }
}
