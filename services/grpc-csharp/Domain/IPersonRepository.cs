// ==============================================================================
// File: Domain/IPersonRepository.cs
// Purpose: DIP contract. PersonGrpcService must not use AppDbContext.
// ==============================================================================

namespace OmniTest.Polyglot.Nexus.Api.CSharp.Domain;

/// <summary>Data access for persons_csharp only.</summary>
public interface IPersonRepository
{
    Task<Person> CreateAsync(Person person, CancellationToken cancellationToken);

    /// <summary>Paginated rows plus full-table COUNT(*) (not page length).</summary>
    Task<(IReadOnlyList<Person> Items, int TotalCount)> ReadAllAsync(int limit, int offset, CancellationToken cancellationToken);

    /// <summary>Filtered page plus matching COUNT(*) so languages compare fairly.</summary>
    Task<(IReadOnlyList<Person> Items, int TotalCount)> SearchByFilterAsync(PersonFilter filter, int limit, CancellationToken cancellationToken);

    Task<IReadOnlyList<Person>> SearchByVectorAsync(float[] vector, int topK, CancellationToken cancellationToken);
}
