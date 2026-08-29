// ==============================================================================
// File: Domain/Entities/PersonEntity.cs
// Purpose: Represents the domain model mapped to the 'persons_csharp' table.
// ==============================================================================

using Pgvector;
using System; // Added for Guid
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace OmniTest.Polyglot.Nexus.Api.CSharp.Domain.Entities
{
    /// <summary>
    /// Entity representing a Person record in the database.
    /// Maps directly to the 'persons_csharp' table.
    /// </summary>
    [Table("persons_csharp")]
    public class PersonEntity
    {
        // Primary Key for the table. Must be Guid to match PostgreSQL UUID.
        [Key]
        [Column("id")]
        public Guid Id { get; set; }

        // Mapped to first_name in the database
        [Column("first_name")]
        public string Name { get; set; } = string.Empty;

        // Mapped to last_name in the database
        [Column("last_name")]
        public string Family { get; set; } = string.Empty;

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

        // Pgvector specific type for storing the 384-dimensional vector embedding
        [Column("embedding")]
        public Vector? Embedding { get; set; }
    }
}
