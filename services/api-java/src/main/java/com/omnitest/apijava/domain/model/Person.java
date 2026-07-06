// File: services/api-java/src/main/java/com/omnitest/apijava/domain/model/Person.java
package com.omnitest.apijava.domain.model;

public class Person {

    private String id;
    private String firstName;
    private String lastName;
    private Integer age;
    private Integer sex;

    private String birthDate;
    private Integer gender;
    private Integer maritalStatus;
    private Integer childrenCount;
    private Integer livingPlace;
    private Integer jobCategory;
    private String nationalCode;
    private Boolean hasPassport;

    public Person() {
    }

    public Person(String id, String firstName, String lastName, Integer age, Integer sex) {
        this.id = id;
        this.firstName = firstName;
        this.lastName = lastName;
        this.age = age;
        this.sex = sex;
    }

    public Person(String id, String firstName, String lastName, Integer age, Integer sex,
                  String birthDate, Integer gender, Integer maritalStatus, Integer childrenCount,
                  Integer livingPlace, Integer jobCategory, String nationalCode, Boolean hasPassport) {
        this.id = id;
        this.firstName = firstName;
        this.lastName = lastName;
        this.age = age;
        this.sex = sex;
        this.birthDate = birthDate;
        this.gender = gender;
        this.maritalStatus = maritalStatus;
        this.childrenCount = childrenCount;
        this.livingPlace = livingPlace;
        this.jobCategory = jobCategory;
        this.nationalCode = nationalCode;
        this.hasPassport = hasPassport;
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

    public Integer getAge() {
        return age;
    }

    public void setAge(Integer age) {
        this.age = age;
    }

    public Integer getSex() {
        return sex;
    }

    public void setSex(Integer sex) {
        this.sex = sex;
    }

    public String getBirthDate() {
        return birthDate;
    }

    public void setBirthDate(String birthDate) {
        this.birthDate = birthDate;
    }

    public Integer getGender() {
        return gender;
    }

    public void setGender(Integer gender) {
        this.gender = gender;
    }

    public Integer getMaritalStatus() {
        return maritalStatus;
    }

    public void setMaritalStatus(Integer maritalStatus) {
        this.maritalStatus = maritalStatus;
    }

    public Integer getChildrenCount() {
        return childrenCount;
    }

    public void setChildrenCount(Integer childrenCount) {
        this.childrenCount = childrenCount;
    }

    public Integer getLivingPlace() {
        return livingPlace;
    }

    public void setLivingPlace(Integer livingPlace) {
        this.livingPlace = livingPlace;
    }

    public Integer getJobCategory() {
        return jobCategory;
    }

    public void setJobCategory(Integer jobCategory) {
        this.jobCategory = jobCategory;
    }

    public String getNationalCode() {
        return nationalCode;
    }

    public void setNationalCode(String nationalCode) {
        this.nationalCode = nationalCode;
    }

    public Boolean getHasPassport() {
        return hasPassport;
    }

    public void setHasPassport(Boolean hasPassport) {
        this.hasPassport = hasPassport;
    }
}
