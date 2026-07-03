// ==============================================================================
// File: Services/PersonGrpcService.cs
// Purpose: Implements the gRPC contract defined in person_service.proto.
// ==============================================================================

using Grpc.Core;
using Microsoft.EntityFrameworkCore;
using OmniTest.Polyglot.Nexus.Api.CSharp.Domain.Entities;
using OmniTest.Polyglot.Nexus.Api.CSharp.Infrastructure.Data;
using OmniTest.Polyglot.Nexus.Api.CSharp.Mappers;
using OmniTest.Polyglot.Nexus.Shared.Proto;
using Pgvector;
using Pgvector.EntityFrameworkCore;

namespace OmniTest.Polyglot.Nexus.Api.CSharp.Services
{
    public class PersonGrpcService : PersonService.PersonServiceBase
    {
        private readonly AppDbContext _dbContext;
        private readonly ILogger<PersonGrpcService> _logger;

        public PersonGrpcService(AppDbContext dbContext, ILogger<PersonGrpcService> logger)
        {
            _dbContext = dbContext;
            _logger = logger;
        }

        public override async Task<PersonListResponse> ReadAllPersons(ReadAllPersonsRequest request, ServerCallContext context)
        {
            _logger.LogInformation("ReadAllPersons invoked. Offset: {Offset}, Limit: {Limit}", request.Offset, request.Limit);

            var limit = request.Limit > 0 ? request.Limit : 100;
            var offset = request.Offset > 0 ? request.Offset : 0;

            var entities = await _dbContext.Persons
                .AsNoTracking()
                .OrderBy(p => p.Id)
                .Skip(offset)
                .Take(limit)
                .ToListAsync(context.CancellationToken);

            var response = new PersonListResponse();
            response.TotalCount = entities.Count; // Added
            response.Persons.AddRange(entities.Select(PersonMapper.ToProto));

            return response;
        }

        public override async Task<PersonListResponse> SearchByFilter(FilterSearchRequest request, ServerCallContext context)
        {
            _logger.LogInformation("SearchByFilter invoked.");
            var query = _dbContext.Persons.AsNoTracking().AsQueryable();

            if (request.HasName) query = query.Where(p => p.Name == request.Name);
            if (request.HasFamily) query = query.Where(p => p.Family == request.Family);
            if (request.HasMinAge) query = query.Where(p => p.Age >= request.MinAge);
            if (request.HasMaxAge) query = query.Where(p => p.Age <= request.MaxAge);
            if (request.HasNationalCode) query = query.Where(p => p.NationalCode == request.NationalCode);
            
            if (request.HasSex && request.Sex != Sex.Unspecified)
            {
                var sexStr = request.Sex.ToString().ToUpperInvariant();
                query = query.Where(p => p.Sex.ToUpper() == sexStr);
            }

            var results = await query.Take(1000).ToListAsync(context.CancellationToken);

            var response = new PersonListResponse();
            response.TotalCount = results.Count; // Added
            response.Persons.AddRange(results.Select(PersonMapper.ToProto));
            
            return response;
        }

               public override async Task<PersonListResponse> SearchByVector(VectorSearchRequest request, ServerCallContext context)
        {
            _logger.LogInformation("SearchByVector invoked. TopK: {TopK}", request.TopK);

            if (request.Vector == null || request.Vector.Count == 0)
                throw new RpcException(new Status(StatusCode.InvalidArgument, "Vector data is required."));

            var searchVector = new Vector(request.Vector.ToArray());
            
            // Reverted back to TopK to match your .proto file
            var topK = request.TopK > 0 ? request.TopK : 10; 

            var results = await _dbContext.Persons
                .AsNoTracking()
                .Where(p => p.Embedding != null)
                .OrderBy(p => p.Embedding!.L2Distance(searchVector))
                .Take(topK)
                .ToListAsync(context.CancellationToken);

            var response = new PersonListResponse();
            response.TotalCount = results.Count; // Count added here
            response.Persons.AddRange(results.Select(PersonMapper.ToProto));
            
            return response;
        }


        public override async Task<CreatePersonResponse> CreatePerson(CreatePersonRequest request, ServerCallContext context)
        {
            var personDto = request.Person; 
            
            if (personDto == null)
                throw new RpcException(new Status(StatusCode.InvalidArgument, "Person payload is missing."));

            _logger.LogInformation("CreatePerson invoked for National Code: {NationalCode}", personDto.NationalCode);

            var entity = new PersonEntity
            {
                Name = personDto.Name,
                Family = personDto.Family,
                Age = personDto.Age,
                Sex = personDto.Sex.ToString().ToUpperInvariant(),
                MaritalStatus = personDto.MaritalStatus.ToString().ToUpperInvariant(),
                ChildrenCount = personDto.ChildrenCount,
                LivingPlace = personDto.LivingPlace.ToString().ToUpperInvariant(),
                Occupation = personDto.Occupation.ToString().ToUpperInvariant(),
                NationalCode = personDto.NationalCode,
                Embedding = null 
            };

            _dbContext.Persons.Add(entity);
            await _dbContext.SaveChangesAsync(context.CancellationToken);

            return new CreatePersonResponse(); 
        }
    }
}
