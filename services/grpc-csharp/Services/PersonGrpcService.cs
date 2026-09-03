// ==============================================================================
// File: Services/PersonGrpcService.cs
// Purpose: gRPC adapter. Depends on IPersonRepository (DIP). No SQL here.
// ==============================================================================

using Grpc.Core;
using OmniTest.Polyglot.Nexus.Api.CSharp.Domain;
using OmniTest.Polyglot.Nexus.Api.CSharp.Mappers;
using OmniTest.Polyglot.Nexus.Shared.Proto;

namespace OmniTest.Polyglot.Nexus.Api.CSharp.Services;

/// <summary>Implements PersonService. All four RPCs against persons_csharp via the repo.</summary>
public sealed class PersonGrpcService : PersonService.PersonServiceBase
{
    private readonly IPersonRepository _repository;
    private readonly ILogger<PersonGrpcService> _logger;

    public PersonGrpcService(IPersonRepository repository, ILogger<PersonGrpcService> logger)
    {
        _repository = repository;
        _logger = logger;
    }

    public override async Task<CreatePersonResponse> CreatePerson(CreatePersonRequest request, ServerCallContext context)
    {
        if (request.Person is null)
            throw new RpcException(new Status(StatusCode.InvalidArgument, "person is required"));

        var created = await _repository.CreateAsync(PersonMapper.FromProto(request.Person), context.CancellationToken);
        return new CreatePersonResponse
        {
            Success = true,
            Message = "created in persons_csharp",
            InsertedId = created.Id?.ToString() ?? string.Empty
        };
    }

    public override async Task<PersonListResponse> ReadAllPersons(ReadAllPersonsRequest request, ServerCallContext context)
    {
        var (items, count) = await _repository.ReadAllAsync(
            PersonMapper.ClampLimit(request.Limit),
            Math.Max(request.Offset, 0),
            context.CancellationToken);
        var response = new PersonListResponse { TotalCount = count };
        response.Persons.AddRange(items.Select(PersonMapper.ToProto));
        return response;
    }

    public override async Task<PersonListResponse> SearchByFilter(FilterSearchRequest request, ServerCallContext context)
    {
        string? sex = null;
        if (request.HasGender && request.Gender != Sex.Unspecified)
            sex = PersonMapper.ToSeedLabel(request.Gender.ToString(), "SEX_");

        var filter = new PersonFilter
        {
            FirstName = request.HasFirstName ? request.FirstName : null,
            LastName = request.HasLastName ? request.LastName : null,
            MinAge = request.HasMinAge ? request.MinAge : null,
            MaxAge = request.HasMaxAge ? request.MaxAge : null,
            Sex = sex,
            NationalCode = request.HasNationalCode ? request.NationalCode : null
        };

        var (items, total) = await _repository.SearchByFilterAsync(filter, 100, context.CancellationToken);
        var response = new PersonListResponse { TotalCount = total };
        response.Persons.AddRange(items.Select(PersonMapper.ToProto));
        return response;
    }

    public override async Task<PersonListResponse> SearchByVector(VectorSearchRequest request, ServerCallContext context)
    {
        if (request.Vector is null || request.Vector.Count == 0)
            throw new RpcException(new Status(StatusCode.InvalidArgument, "vector is required"));

        var items = await _repository.SearchByVectorAsync(
            request.Vector.ToArray(),
            PersonMapper.ClampTopK(request.TopK),
            context.CancellationToken);
        var response = new PersonListResponse { TotalCount = items.Count };
        response.Persons.AddRange(items.Select(PersonMapper.ToProto));
        return response;
    }
}
