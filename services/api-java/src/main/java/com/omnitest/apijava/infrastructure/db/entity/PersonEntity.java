package com.omnitest.apijava.infrastructure.db.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.io.Serializable;

/**
 * ============================================================================
 * File: PersonEntity.java
 * Purpose: Represents the JPA entity for the Person domain model.
 *          Maps specifically to the "persons_java" table to ensure data 
 *          isolation for the Java microservice per architecture requirements.
 * Architecture: Infrastructure Layer -> Database / Persistence
 * ============================================================================
 */
@Entity
@Table(name = "persons_java")
public class PersonEntity implements Serializable {

    @Id
    @Column(name = "id", nullable = false, updatable = false)
    private String id;

    @Column(name = "first_name", nullable = false)
    private String firstName;

    @Column(name = "last_name", nullable = false)
    private String lastName;

    // Fixing the null value exception seen in previous logs
    @Column(name = "age", nullable = false)
    private Integer age;

    @Column(name = "birth_date")
    private String birthDate;

    // Stored as integer ordinals corresponding to Proto Enums
    @Column(name = "gender")
    private Integer gender;

    @Column(name = "marital_status")
    private Integer maritalStatus;

    @Column(name = "children_count")
    private Integer childrenCount;

    @Column(name = "living_place")
    private Integer livingPlace;

    @Column(name = "job_category")
    private Integer jobCategory;

    @Column(name = "national_code", unique = true)
    private String nationalCode;

    @Column(name = "has_passport")
    private Boolean hasPassport;

    // PgVector representation. Depending on your hibernate-vector setup, 
    // this can be mapped using @JdbcTypeCode or stored as a float array.
    @Column(name = "embedding_vector", columnDefinition = "vector")
    private float[] embeddingVector;

    /**
     * Default constructor required by JPA.
     */
    public PersonEntity() {
    }

    // ============================================================================
    // GETTERS AND SETTERS
    // ============================================================================

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }

    public String getFirstName() { return firstName; }
    public void setFirstName(String firstName) { this.firstName = firstName; }

    public String getLastName() { return lastName; }
    public void setLastName(String lastName) { this.lastName = lastName; }

    public Integer getAge() { return age; }
    public void setAge(Integer age) { this.age = age; }

    public String getBirthDate() { return birthDate; }
    public void setBirthDate(String birthDate) { this.birthDate = birthDate; }

    public Integer getGender() { return gender; }
    public void setGender(Integer gender) { this.gender = gender; }

    public Integer getMaritalStatus() { return maritalStatus; }
    public void setMaritalStatus(Integer maritalStatus) { this.maritalStatus = maritalStatus; }

    public Integer getChildrenCount() { return childrenCount; }
    public void setChildrenCount(Integer childrenCount) { this.childrenCount = childrenCount; }

    public Integer getLivingPlace() { return livingPlace; }
    public void setLivingPlace(Integer livingPlace) { this.livingPlace = livingPlace; }

    public Integer getJobCategory() { return jobCategory; }
    public void setJobCategory(Integer jobCategory) { this.jobCategory = jobCategory; }

    public String getNationalCode() { return nationalCode; }
    public void setNationalCode(String nationalCode) { this.nationalCode = nationalCode; }

    public Boolean getHasPassport() { return hasPassport; }
    public void setHasPassport(Boolean hasPassport) { this.hasPassport = hasPassport; }

    public float[] getEmbeddingVector() { return embeddingVector; }
    public void setEmbeddingVector(float[] embeddingVector) { this.embeddingVector = embeddingVector; }
}
