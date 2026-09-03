// ==============================================================================
// File: Mappers/PersonMapper.cs
// Purpose: Domain <-> proto. Uses first_name, last_name, gender, job_category,
//          embedding_vector, inserted_id. birth_date is derived from age.
// ==============================================================================

using OmniTest.Polyglot.Nexus.Api.CSharp.Domain;
using OmniTest.Polyglot.Nexus.Shared.Proto;
using DomainPerson = OmniTest.Polyglot.Nexus.Api.CSharp.Domain.Person;
using ProtoPerson = OmniTest.Polyglot.Nexus.Shared.Proto.Person;

namespace OmniTest.Polyglot.Nexus.Api.CSharp.Mappers;

/// <summary>Static mapper. No I/O (SRP).</summary>
public static class PersonMapper
{
    public static ProtoPerson ToProto(DomainPerson person)
    {
        var year = DateTime.UtcNow.Year - Math.Max(person.Age, 0);
        var msg = new ProtoPerson
        {
            Id = person.Id?.ToString() ?? string.Empty,
            FirstName = person.FirstName,
            LastName = person.LastName,
            Age = person.Age,
            BirthDate = $"{year:D4}-01-01",
            Gender = ParseEnum<Sex>(person.Sex, "SEX_"),
            MaritalStatus = ParseEnum<MaritalStatus>(person.MaritalStatus, "MARITAL_STATUS_"),
            ChildrenCount = person.ChildrenCount,
            LivingPlace = ParseEnum<LivingPlace>(person.LivingPlace, "LIVING_PLACE_"),
            JobCategory = ParseEnum<Occupation>(person.Occupation, "OCCUPATION_"),
            NationalCode = person.NationalCode,
            HasPassport = person.HasPassport
        };
        if (person.Embedding is { Length: > 0 })
            msg.EmbeddingVector.AddRange(person.Embedding);
        return msg;
    }

    public static DomainPerson FromProto(ProtoPerson msg) => new()
    {
        FirstName = msg.FirstName,
        LastName = msg.LastName,
        Age = msg.Age,
        Sex = ToSeedLabel(msg.Gender.ToString(), "SEX_"),
        MaritalStatus = ToSeedLabel(msg.MaritalStatus.ToString(), "MARITAL_STATUS_"),
        ChildrenCount = msg.ChildrenCount,
        LivingPlace = ToSeedLabel(msg.LivingPlace.ToString(), "LIVING_PLACE_"),
        Occupation = ToSeedLabel(msg.JobCategory.ToString(), "OCCUPATION_"),
        NationalCode = msg.NationalCode,
        HasPassport = msg.HasPassport,
        Embedding = msg.EmbeddingVector.Count > 0 ? msg.EmbeddingVector.ToArray() : null
    };

    public static string ToSeedLabel(string enumName, string prefix)
    {
        var token = enumName.ToUpperInvariant();
        if (token.StartsWith(prefix, StringComparison.Ordinal))
            token = token[prefix.Length..];
        return token switch
        {
            "FULL_TIME" => "full-time",
            "PART_TIME" => "part-time",
            "JOB_SEEKER" => "job seeker",
            "SINGLE_PARENT" => "single parent",
            "NOT_SPECIFIED" or "UNSPECIFIED" => "not specified",
            _ => token.ToLowerInvariant().Replace('_', ' ')
        };
    }

    private static TEnum ParseEnum<TEnum>(string? db, string prefix) where TEnum : struct, Enum
    {
        if (string.IsNullOrWhiteSpace(db))
            return default;
        var token = db.Trim().ToUpperInvariant().Replace(' ', '_').Replace('-', '_');
        if (!token.StartsWith(prefix, StringComparison.Ordinal))
            token = prefix + token;
        return Enum.TryParse<TEnum>(token, true, out var parsed) ? parsed : default;
    }

    public static int ClampLimit(int raw) => raw <= 0 ? 50 : Math.Min(raw, 500);
    public static int ClampTopK(int raw) => raw <= 0 ? 10 : Math.Min(raw, 100);
}
