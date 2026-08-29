// ============================================================================
// File: services/api-java/src/main/java/com/omnitest/apijava/domain/repository/PersonRepository.java
// Purpose: Persistence port for Person (DIP). gRPC depends on this, not JdbcTemplate.
// SOLID: ISP — four RPCs map to four methods; OCP — swap Postgres for a fake.
// Dependencies: domain.Person / PersonFilter. Implemented by infrastructure/db.
// ============================================================================

package com.omnitest.apijava.domain.repository;

import com.omnitest.apijava.domain.PersonFilter;
import com.omnitest.apijava.domain.model.Person;

import java.util.List;

/**
 * Data-access contract for {@code persons_java}.
 * Implementations must never query another {@code persons_*} table.
 */
public interface PersonRepository {

    /**
     * One page of persons plus the unfiltered (or filter-matched) row count.
     */
    record Page(List<Person> persons, int totalCount) {
        public Page {
            persons = persons == null ? List.of() : List.copyOf(persons);
        }
    }

    /**
     * Inserts one person and returns the persisted entity (id is always set).
     */
    Person save(Person person);

    /**
     * Page of persons plus {@code COUNT(*)} over the full table.
     */
    Page findAll(int limit, int offset);

    /**
     * Optional lexical / range / gender predicates. {@code totalCount} is the match count.
     */
    Page findByFilter(PersonFilter filter);

    /**
     * Nearest neighbors by L2 ({@code <->}). Return size is the result count (no extra COUNT).
     */
    List<Person> searchByVector(List<Float> queryVector, int topK);
}
