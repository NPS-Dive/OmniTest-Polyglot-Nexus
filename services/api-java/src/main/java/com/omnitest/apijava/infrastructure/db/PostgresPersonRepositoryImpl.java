// File: services/api-java/src/main/java/com/omnitest/apijava/infrastructure/db/PostgresPersonRepositoryImpl.java
package com.omnitest.apijava.infrastructure.db;

import com.omnitest.apijava.domain.model.Person;
import com.omnitest.apijava.domain.repository.PersonRepository;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;
import org.springframework.stereotype.Repository;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.List;
import java.util.UUID;

@Repository
public class PostgresPersonRepositoryImpl implements PersonRepository {

    private final JdbcTemplate jdbcTemplate;

    public PostgresPersonRepositoryImpl(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    private static final class PersonRowMapper implements RowMapper<Person> {
        @Override
        public Person mapRow(ResultSet rs, int rowNum) throws SQLException {
            Person person = new Person();

            person.setId(rs.getString("id"));
            person.setFirstName(rs.getString("first_name"));
            person.setLastName(rs.getString("last_name"));

            int age = rs.getInt("age");
            person.setAge(rs.wasNull() ? null : age);

            person.setBirthDate(rs.getString("birth_date"));

            int gender = rs.getInt("gender");
            person.setGender(rs.wasNull() ? null : gender);

            int maritalStatus = rs.getInt("marital_status");
            person.setMaritalStatus(rs.wasNull() ? null : maritalStatus);

            int childrenCount = rs.getInt("children_count");
            person.setChildrenCount(rs.wasNull() ? null : childrenCount);

            int livingPlace = rs.getInt("living_place");
            person.setLivingPlace(rs.wasNull() ? null : livingPlace);

            int jobCategory = rs.getInt("job_category");
            person.setJobCategory(rs.wasNull() ? null : jobCategory);

            person.setNationalCode(rs.getString("national_code"));

            Boolean hasPassport = null;
            try {
                boolean hp = rs.getBoolean("has_passport");
                if (!rs.wasNull()) {
                    hasPassport = hp;
                }
            } catch (SQLException ignored) {
            }
            person.setHasPassport(hasPassport);

            return person;
        }
    }

    private final RowMapper<Person> personRowMapper = new PersonRowMapper();

    @Override
    public Person save(Person person) {
        if (person.getId() == null || person.getId().isEmpty()) {
            person.setId(UUID.randomUUID().toString());
        }

        String sql = "INSERT INTO persons_java (" +
                "id, first_name, last_name, age, birth_date, gender, " +
                "marital_status, children_count, living_place, job_category, " +
                "national_code, has_passport" +
                ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)";

        jdbcTemplate.update(
                sql,
                person.getId(),
                person.getFirstName(),
                person.getLastName(),
                person.getAge(),
                person.getBirthDate(),
                person.getGender(),
                person.getMaritalStatus(),
                person.getChildrenCount(),
                person.getLivingPlace(),
                person.getJobCategory(),
                person.getNationalCode(),
                person.getHasPassport()
        );

        return person;
    }

    @Override
    public List<Person> findAll(int limit, int offset) {
        String sql = "SELECT id, first_name, last_name, age, birth_date, gender, " +
                "marital_status, children_count, living_place, job_category, " +
                "national_code, has_passport " +
                "FROM persons_java ORDER BY id LIMIT ? OFFSET ?";

        return jdbcTemplate.query(sql, personRowMapper, limit, offset);
    }

    @Override
    public List<Person> findByFilter(Integer gender, boolean hasPassport, Integer jobCategory) {
        StringBuilder sql = new StringBuilder(
                "SELECT id, first_name, last_name, age, birth_date, gender, " +
                "marital_status, children_count, living_place, job_category, " +
                "national_code, has_passport " +
                "FROM persons_java WHERE has_passport = ?"
        );

        java.util.List<Object> params = new java.util.ArrayList<>();
        params.add(hasPassport);

        if (gender != null) {
            sql.append(" AND gender = ?");
            params.add(gender);
        }

        if (jobCategory != null) {
            sql.append(" AND job_category = ?");
            params.add(jobCategory);
        }

        sql.append(" ORDER BY id");

        return jdbcTemplate.query(sql.toString(), personRowMapper, params.toArray());
    }

    @Override
    public List<Person> searchByVector(float[] queryVector, int topK) {
        String sql = "SELECT id, first_name, last_name, age, birth_date, gender, " +
                "marital_status, children_count, living_place, job_category, " +
                "national_code, has_passport " +
                "FROM persons_java " +
                "WHERE embedding_vector IS NOT NULL " +
                "ORDER BY embedding_vector <-> ? " +
                "LIMIT ?";

        String vectorLiteral = toPgVectorLiteral(queryVector);

        return jdbcTemplate.query(sql, personRowMapper, vectorLiteral, topK);
    }

    private String toPgVectorLiteral(float[] vector) {
        if (vector == null || vector.length == 0) {
            return "[]";
        }

        StringBuilder sb = new StringBuilder("[");
        for (int i = 0; i < vector.length; i++) {
            if (i > 0) {
                sb.append(",");
            }
            sb.append(vector[i]);
        }
        sb.append("]");
        return sb.toString();
    }
}
