// ============================================================================
// File: services/grpc-java/src/main/java/com/omnitest/apijava/domain/model/Person.java
// Purpose: Persistence-shaped Person entity for persons_java (SQL columns, not proto).
// SOLID: SRP — data + pagination clamps only. No SQL, no proto, no I/O.
// Dependencies: none (stdlib). Presentation maps proto; infrastructure maps rows.
// Contract: sex / occupation / embedding (not gender / job_category / embedding_vector).
//           birth_date is derived as (currentYear - age)-01-01; it is never stored.
// ============================================================================

package com.omnitest.apijava.domain.model;

import java.time.Year;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/**
 * Domain record for one row in {@code persons_java}.
 * Field names follow SQL columns so the repository can map 1:1 without proto types (DIP).
 */
public class Person {

    /** Applied when ReadAll / filter {@code limit} is 0 or omitted. */
    public static final int DEFAULT_LIMIT = 50;

    /** Caps page size so a client cannot dump the 1M-row table. */
    public static final int MAX_LIMIT = 500;

    /** Applied when {@code VectorSearchRequest.top_k} is 0 or omitted. */
    public static final int DEFAULT_TOP_K = 10;

    /** Caps ANN result size (HNSW + LIMIT). */
    public static final int MAX_TOP_K = 100;

    /** MiniLM-L6-v2 / {@code persons_*.embedding vector(384)}. */
    public static final int EMBEDDING_DIMS = 384;

    /** The only table this service may touch (table-per-language isolation). */
    public static final String TABLE_NAME = "persons_java";

    private String id;
    private String firstName;
    private String lastName;
    private int age;
    /** VARCHAR {@code sex} (seed: {@code male}; proto: {@code SEX_MALE}). */
    private String sex;
    /** VARCHAR {@code marital_status} (seed: {@code single parent}). */
    private String maritalStatus;
    private int childrenCount;
    /** VARCHAR {@code living_place} (seed: {@code apartment}). */
    private String livingPlace;
    /** VARCHAR {@code occupation} (seed: {@code job seeker}, {@code full-time}). */
    private String occupation;
    private String nationalCode;
    private boolean hasPassport;
    /** 384-dim pgvector payload. Null/empty means SQL NULL. */
    private List<Float> embedding;

    public Person() {
        this.embedding = new ArrayList<>();
    }

    public Person(String id, String firstName, String lastName, int age, String sex,
                  String maritalStatus, int childrenCount, String livingPlace,
                  String occupation, String nationalCode, boolean hasPassport,
                  List<Float> embedding) {
        this.id = id;
        this.firstName = firstName;
        this.lastName = lastName;
        this.age = age;
        this.sex = sex;
        this.maritalStatus = maritalStatus;
        this.childrenCount = childrenCount;
        this.livingPlace = livingPlace;
        this.occupation = occupation;
        this.nationalCode = nationalCode;
        this.hasPassport = hasPassport;
        this.embedding = embedding == null ? new ArrayList<>() : new ArrayList<>(embedding);
    }

    /**
     * Approximate ISO date from stored age. Contract: {@code (currentYear - age)-01-01}.
     */
    public String birthDateIso() {
        return birthDateFromAge(age);
    }

    /**
     * Shared birth_date derivation used on every read. Age is stored; birth_date is not.
     */
    public static String birthDateFromAge(int age) {
        int safeAge = Math.max(0, age);
        int year = Year.now().getValue() - safeAge;
        if (year < 1) {
            year = 1;
        }
        return String.format("%04d-01-01", year);
    }

    /** Pagination: default 50, max 500. */
    public static int clampLimit(int limit) {
        if (limit <= 0) {
            return DEFAULT_LIMIT;
        }
        return Math.min(limit, MAX_LIMIT);
    }

    /** Vector page size: default 10, max 100. */
    public static int clampTopK(int topK) {
        if (topK <= 0) {
            return DEFAULT_TOP_K;
        }
        return Math.min(topK, MAX_TOP_K);
    }

    /** Negative offsets are treated as the start of the result set. */
    public static int clampOffset(int offset) {
        return Math.max(0, offset);
    }

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
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

    public int getAge() {
        return age;
    }

    public void setAge(int age) {
        this.age = age;
    }

    public String getSex() {
        return sex;
    }

    public void setSex(String sex) {
        this.sex = sex;
    }

    public String getMaritalStatus() {
        return maritalStatus;
    }

    public void setMaritalStatus(String maritalStatus) {
        this.maritalStatus = maritalStatus;
    }

    public int getChildrenCount() {
        return childrenCount;
    }

    public void setChildrenCount(int childrenCount) {
        this.childrenCount = childrenCount;
    }

    public String getLivingPlace() {
        return livingPlace;
    }

    public void setLivingPlace(String livingPlace) {
        this.livingPlace = livingPlace;
    }

    public String getOccupation() {
        return occupation;
    }

    public void setOccupation(String occupation) {
        this.occupation = occupation;
    }

    public String getNationalCode() {
        return nationalCode;
    }

    public void setNationalCode(String nationalCode) {
        this.nationalCode = nationalCode;
    }

    public boolean isHasPassport() {
        return hasPassport;
    }

    public void setHasPassport(boolean hasPassport) {
        this.hasPassport = hasPassport;
    }

    public List<Float> getEmbedding() {
        return embedding == null ? List.of() : Collections.unmodifiableList(embedding);
    }

    public void setEmbedding(List<Float> embedding) {
        this.embedding = embedding == null ? new ArrayList<>() : new ArrayList<>(embedding);
    }
}
