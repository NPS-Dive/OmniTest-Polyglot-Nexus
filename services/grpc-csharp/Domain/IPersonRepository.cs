// ==============================================================================
// File: Domain/IPersonRepository.cs
// Purpose: DIP contract. PersonGrpcService must not use AppDbContext.
// ==============================================================================

namespace OmniTest.Polyglot.Nexus.Api.CSharp.Domain;

/// <summary>Data access for persons_csharp only.</summary>
public interface IPersonRepository
{
    Task<Person> CreateAsync(Person person, CancellationToken cancellationToken);
    Task<(IReadOnlyList<Person> Items, int PageCount)> ReadAllAsync(int limit, int offset, CancellationToken cancellationToken);
    Task<IReadOnlyList<Person>> SearchByFilterAsync(PersonFilter filter, int limit, CancellationToken cancellationToken);
    Task<IReadOnlyList<Person>> SearchByVectorAsync(float[] vector, int topK, CancellationToken cancellationToken);
}
