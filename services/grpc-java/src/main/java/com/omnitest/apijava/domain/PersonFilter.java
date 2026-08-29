// ============================================================================
// File: services/grpc-java/src/main/java/com/omnitest/apijava/domain/PersonFilter.java
// Purpose: SearchByFilter criteria. Null / blank fields are ignored by SQL.
// SOLID: SRP — filter DTO only. No SQL, no proto types (DIP).
// Dependencies: none. Presentation copies proto optionals here; repository binds them.
// Contract: proto.gender is stored as {@code sex}. Pagination defaults live on Person.
// ============================================================================

package com.omnitest.apijava.domain;

import com.omnitest.apijava.domain.model.Person;

/**
 * Optional predicates for {@code SearchByFilter}.
 * {@code sex} is a proto-or-seed label; the repository matches aliases after normalization.
 */
public class PersonFilter {

    /** Case-insensitive partial match on {@code first_name}. */
    private String firstName;
    /** Case-insensitive partial match on {@code last_name}. */
    private String lastName;
    /** Inclusive lower bound: {@code age >= minAge}. */
    private Integer minAge;
    /** Inclusive upper bound: {@code age <= maxAge}. */
    private Integer maxAge;
    /** Matched against column {@code sex} after label normalization. */
    private String sex;
    /** Exact match on {@code national_code}. */
    private String nationalCode;
    /** Page size after {@link Person#clampLimit(int)} (default 50, max 500). */
    private int limit = Person.DEFAULT_LIMIT;
    /** Rows to skip (never negative after clamp). */
    private int offset;

    public PersonFilter() {
    }

    public String getFirstName() {
        return firstName;
    }

    public void setFirstName(String firstName) {
        this.firstName = firstName;
    }

    public String getLastName() {
        return lastName;
    }

    public void setLastName(String lastName) {
        this.lastName = lastName;
    }

    public Integer getMinAge() {
        return minAge;
    }

    public void setMinAge(Integer minAge) {
        this.minAge = minAge;
    }

    public Integer getMaxAge() {
        return maxAge;
    }

    public void setMaxAge(Integer maxAge) {
        this.maxAge = maxAge;
    }

    public String getSex() {
        return sex;
    }

    public void setSex(String sex) {
        this.sex = sex;
    }

    public String getNationalCode() {
        return nationalCode;
    }

    public void setNationalCode(String nationalCode) {
        this.nationalCode = nationalCode;
    }

    public int getLimit() {
        return limit;
    }

    public void setLimit(int limit) {
        this.limit = limit;
    }

    public int getOffset() {
        return offset;
    }

    public void setOffset(int offset) {
        this.offset = offset;
    }
}
