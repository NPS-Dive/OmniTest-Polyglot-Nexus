// ==============================================================================
// File: Infrastructure/Data/AppDbContext.cs
// Purpose: Entity Framework Core database context configuration.
// ==============================================================================

using Microsoft.EntityFrameworkCore;
using OmniTest.Polyglot.Nexus.Api.CSharp.Domain.Entities;

namespace OmniTest.Polyglot.Nexus.Api.CSharp.Infrastructure.Data
{
    /// <summary>
    /// The main database context handling operations for the PostgreSQL database.
    /// </summary>
    public class AppDbContext : DbContext
    {
        // Constructor accepting DbContextOptions, required for DI in Program.cs
        public AppDbContext(DbContextOptions<AppDbContext> options) : base(options)
        {
        }

        // DbSet representing our 'persons_csharp' table
        public DbSet<PersonEntity> Persons { get; set; }

        /// <summary>
        /// Configures the database schema and extensions.
        /// </summary>
        /// <param name="modelBuilder">Provides API to configure entities.</param>
        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            base.OnModelCreating(modelBuilder);

            // Register the pgvector extension within PostgreSQL
            modelBuilder.HasPostgresExtension("vector");

            // Explicitly define the vector column configuration (384 dimensions for all-MiniLM-L6-v2)
            modelBuilder.Entity<PersonEntity>()
                .Property(p => p.Embedding)
                .HasColumnType("vector(384)");
        }
    }
}
