// File: services/api-java/src/main/java/com/omnitest/apijava/domain/repository/PersonRepository.java
package com.omnitest.apijava.domain.repository;

import com.omnitest.apijava.domain.model.Person;

import java.util.List;

public interface PersonRepository {

    Person save(Person person);

    List<Person> findAll(int limit, int offset);

    List<Person> findByFilter(Integer gender, boolean hasPassport, Integer jobCategory);

    List<Person> searchByVector(float[] queryVector, int topK);
}
