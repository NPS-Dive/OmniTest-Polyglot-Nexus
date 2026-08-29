// ==============================================================================
// File: Mappers/PersonMapper.cs
// Purpose: Maps between Database Entities (PersonEntity) and gRPC Messages (Person).
// ==============================================================================

using OmniTest.Polyglot.Nexus.Api.CSharp.Domain.Entities;
using OmniTest.Polyglot.Nexus.Shared.Proto;

namespace OmniTest.Polyglot.Nexus.Api.CSharp.Mappers
{
    public static class PersonMapper
    {
        public static Person ToProto(PersonEntity entity)
        {
            if (entity == null) return new Person();

            return new Person
            {
                Id = entity.Id.ToString(), // Fixed: Convert int DB Id to string Proto Id
                Name = entity.Name ?? string.Empty,
                Family = entity.Family ?? string.Empty,
                Age = entity.Age,
                Sex = MapEnum<Sex>(entity.Sex),
                MaritalStatus = MapEnum<MaritalStatus>(entity.MaritalStatus),
                ChildrenCount = entity.ChildrenCount,
                LivingPlace = MapEnum<LivingPlace>(entity.LivingPlace),
                Occupation = MapEnum<Occupation>(entity.Occupation),
                NationalCode = entity.NationalCode ?? string.Empty
            };
        }

        /// <summary>
        /// Generic helper to safely parse database string values into gRPC Enums.
        /// Ignores case and falls back to the default (Unspecified) if parsing fails.
        /// </summary>
        private static TEnum MapEnum<TEnum>(string? value) where TEnum : struct, Enum
        {
            if (!string.IsNullOrEmpty(value) && Enum.TryParse<TEnum>(value, true, out var result))
            {
                return result;
            }
            return default; // Returns the default 0-value (e.g., SEX_UNSPECIFIED)
        }
    }
}
