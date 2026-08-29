// ==============================================================================
// File: Infrastructure/Data/PostgresPersonRepository.cs
// Purpose: IPersonRepository via EF Core. SQL only against persons_csharp.
// Vector metric: L2Distance <-> matching HNSW vector_l2_ops.
// ==============================================================================

using Microsoft.EntityFrameworkCore;
using OmniTest.Polyglot.Nexus.Api.CSharp.Domain;
using OmniTest.Polyglot.Nexus.Api.CSharp.Domain.Entities;
using Pgvector;
using Pgvector.EntityFrameworkCore;

namespace OmniTest.Polyglot.Nexus.Api.CSharp.Infrastructure.Data;

/// <summary>EF adapter. Presentation never sees AppDbContext.</summary>
public sealed class PostgresPersonRepository : IPersonRepository
{
    private readonly AppDbContext _db;

    public PostgresPersonRepository(AppDbContext db) => _db = db;

    public async Task<Person> CreateAsync(Person person, CancellationToken cancellationToken)
    {
        var entity = ToEntity(person);
        entity.Id = Guid.NewGuid();
        _db.Persons.Add(entity);
        await _db.SaveChangesAsync(cancellationToken);
        return ToDomain(entity);
    }

    public async Task<(IReadOnlyList<Person> Items, int PageCount)> ReadAllAsync(
        int limit, int offset, CancellationToken cancellationToken)
    {
        var rows = await _db.Persons.AsNoTracking()
            .OrderBy(p => p.Id)
            .Skip(offset)
            .Take(limit)
            .ToListAsync(cancellationToken);
        var items = rows.Select(ToDomain).ToList();
        return (items, items.Count);
    }

    public async Task<IReadOnlyList<Person>> SearchByFilterAsync(
        PersonFilter filter, int limit, CancellationToken cancellationToken)
    {
        var query = _db.Persons.AsNoTracking().AsQueryable();
        if (!string.IsNullOrWhiteSpace(filter.FirstName))
            query = query.Where(p => p.FirstName.ToLower().Contains(filter.FirstName.ToLower()));
        if (!string.IsNullOrWhiteSpace(filter.LastName))
            query = query.Where(p => p.LastName.ToLower().Contains(filter.LastName.ToLower()));
        if (filter.MinAge.HasValue)
            query = query.Where(p => p.Age >= filter.MinAge.Value);
        if (filter.MaxAge.HasValue)
            query = query.Where(p => p.Age <= filter.MaxAge.Value);
        if (!string.IsNullOrWhiteSpace(filter.Sex))
            query = query.Where(p => p.Sex.ToLower() == filter.Sex.ToLower());
        if (!string.IsNullOrWhiteSpace(filter.NationalCode))
            query = query.Where(p => p.NationalCode == filter.NationalCode);

        var rows = await query.Take(limit).ToListAsync(cancellationToken);
        return rows.Select(ToDomain).ToList();
    }

    public async Task<IReadOnlyList<Person>> SearchByVectorAsync(
        float[] vector, int topK, CancellationToken cancellationToken)
    {
        var search = new Vector(vector);
        var rows = await _db.Persons.AsNoTracking()
            .Where(p => p.Embedding != null)
            .OrderBy(p => p.Embedding!.L2Distance(search))
            .Take(topK)
            .ToListAsync(cancellationToken);
        return rows.Select(ToDomain).ToList();
    }

    private static Person ToDomain(PersonEntity e) => new()
    {
        Id = e.Id,
        FirstName = e.FirstName,
        LastName = e.LastName,
        Age = e.Age,
        Sex = e.Sex,
        MaritalStatus = e.MaritalStatus,
        ChildrenCount = e.ChildrenCount,
        LivingPlace = e.LivingPlace,
        Occupation = e.Occupation,
        NationalCode = e.NationalCode,
        HasPassport = e.HasPassport,
        Embedding = e.Embedding?.ToArray()
    };

    private static PersonEntity ToEntity(Person p) => new()
    {
        FirstName = p.FirstName,
        LastName = p.LastName,
        Age = p.Age,
        Sex = p.Sex,
        MaritalStatus = p.MaritalStatus,
        ChildrenCount = p.ChildrenCount,
        LivingPlace = p.LivingPlace,
        Occupation = p.Occupation,
        NationalCode = p.NationalCode,
        HasPassport = p.HasPassport,
        Embedding = p.Embedding is { Length: > 0 } ? new Vector(p.Embedding) : null
    };
}
