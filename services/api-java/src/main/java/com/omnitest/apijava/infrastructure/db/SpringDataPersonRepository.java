package com.omnitest.apijava.infrastructure.db.repository;

import com.omnitest.apijava.infrastructure.db.entity.PersonEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

/**
 * Spring Data JPA Repository for Postgres interaction.
 *
 * SOLID Principle (Interface Segregation / Single Responsibility):
 * This interface is strictly responsible for database-level querying via Spring Data.
 * It strictly targets the 'persons_java' table, preserving the independent table constraint per language.
 */
@Repository
public interface SpringDataPersonRepository extends JpaRepository<PersonEntity, String> {

    /**
     * Derived query method provided by Spring Data JPA.
     * Uses Integer for enum values to perfectly match the PersonEntity and Postgres schema.
     * 
     * @param gender The integer mapping of the gender enum.
     * @param hasPassport Boolean indicating passport status.
     * @param jobCategory The integer mapping of the job category enum.
     * @return A list of matching entity records.
     */
    List<PersonEntity> findByGenderAndHasPassportAndJobCategory(Integer gender, Boolean hasPassport, Integer jobCategory);

    /**
     * Native query utilizing pgvector's Euclidean distance operator (<->).
     * We cast the String representation of the array directly to the postgres vector type.
     * 
     * @param queryVector The string format of the embedding array (e.g., "[0.1, 0.2, ...]").
     * @param topK The limit of nearest records to fetch.
     * @return A list of the closest matching entities based on vector similarity.
     */
    @Query(value = "SELECT * FROM persons_java ORDER BY embedding_vector <-> cast(:queryVector as vector) LIMIT :topK", nativeQuery = true)
    List<PersonEntity> findNearestNeighbors(@Param("queryVector") String queryVector, @Param("topK") int topK);
}
