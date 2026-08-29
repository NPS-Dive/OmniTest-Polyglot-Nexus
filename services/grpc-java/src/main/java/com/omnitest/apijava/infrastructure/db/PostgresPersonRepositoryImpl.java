// ============================================================================
// File: services/grpc-java/src/main/java/com/omnitest/apijava/infrastructure/db/PostgresPersonRepositoryImpl.java
// Purpose: JdbcTemplate adapter for domain.PersonRepository against persons_java.
// SOLID: DIP — satisfies the domain port; SRP — SQL only, no proto mapping.
// Dependencies: Spring JDBC, OpenTelemetry tracer (no-op unless OTEL env set).
// Contract: L2 operator <-> ; embedding stored as '[1,2,...]'::vector.
//           Columns: id, first_name, last_name, age, sex, marital_status,
//           children_count, living_place, occupation, national_code,
//           embedding vector(384), has_passport. Never birth_date / gender / job_category.
// ============================================================================

package com.omnitest.apijava.infrastructure.db;

import com.omnitest.apijava.domain.PersonFilter;
import com.omnitest.apijava.domain.model.Person;
import com.omnitest.apijava.domain.repository.PersonRepository;
import io.opentelemetry.api.OpenTelemetry;
import io.opentelemetry.api.trace.Span;
import io.opentelemetry.api.trace.StatusCode;
import io.opentelemetry.api.trace.Tracer;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;
import org.springframework.stereotype.Repository;
import org.springframework.transaction.annotation.Transactional;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

/**
 * Postgres adapter for {@code persons_java}. Presentation never imports this class (DIP).
 */
@Repository
public class PostgresPersonRepositoryImpl implements PersonRepository {

    /**
     * SELECT list. {@code embedding} is cast to text so we can parse the pgvector literal.
     * {@code birth_date} is intentionally absent.
     */
    private static final String PERSON_COLUMNS = """
            id::text,
            first_name,
            last_name,
            age,
            sex,
            marital_status,
            children_count,
            living_place,
            occupation,
            national_code,
            COALESCE(has_passport, false) AS has_passport,
            embedding::text
            """;

    /**
     * Turns seed labels and proto-style names into one key.
     * {@code SEX_MALE}/{@code male} → male; {@code full-time}/{@code FULL_TIME} → full time.
     * {@code %s} is a trusted identifier or {@code ?} — never concatenate user SQL.
     */
    private static final String SQL_NORMALIZE_LABEL = """
            trim(both from regexp_replace(
                regexp_replace(replace(replace(lower(%s), '_', ' '), '-', ' '), '\\s+', ' ', 'g'),
                '^(sex|marital status|living place|occupation) ',
                ''
            ))
            """;

    private final JdbcTemplate jdbcTemplate;
    private final Tracer tracer;
    private final RowMapper<Person> personRowMapper = new PersonRowMapper();

    public PostgresPersonRepositoryImpl(JdbcTemplate jdbcTemplate, OpenTelemetry openTelemetry) {
        this.jdbcTemplate = jdbcTemplate;
        this.tracer = openTelemetry.getTracer("grpc-java/db");
    }

    /**
     * Inserts one row. Empty ID → generated UUID. Empty embedding → NULL.
     */
    @Override
    @Transactional
    public Person save(Person person) {
        Span span = tracer.spanBuilder("PersonRepository.save").startSpan();
        try (var scope = span.makeCurrent()) {
            if (person == null) {
                throw new IllegalArgumentException("person is required");
            }

            String id = person.getId() == null ? "" : person.getId().trim();
            if (id.isEmpty()) {
                id = UUID.randomUUID().toString();
            } else {
                try {
                    UUID.fromString(id);
                } catch (IllegalArgumentException ex) {
                    throw new IllegalArgumentException("invalid person id: " + id, ex);
                }
            }
            person.setId(id);

            String emb = vectorLiteral(person.getEmbedding());
            String sql = """
                    INSERT INTO persons_java (
                        id, first_name, last_name, age, sex, marital_status,
                        children_count, living_place, occupation, national_code,
                        embedding, has_passport
                    ) VALUES (
                        ?::uuid, ?, ?, ?, ?, ?, ?, ?, ?, ?, CAST(? AS vector), ?
                    )
                    """;

            jdbcTemplate.update(
                    sql,
                    id,
                    person.getFirstName(),
                    person.getLastName(),
                    person.getAge(),
                    person.getSex(),
                    person.getMaritalStatus(),
                    person.getChildrenCount(),
                    person.getLivingPlace(),
                    person.getOccupation(),
                    person.getNationalCode(),
                    emb.isEmpty() ? null : emb,
                    person.isHasPassport()
            );
            return person;
        } catch (RuntimeException ex) {
            span.recordException(ex);
            span.setStatus(StatusCode.ERROR, ex.getMessage() == null ? "save failed" : ex.getMessage());
            throw ex;
        } finally {
            span.end();
        }
    }

    /**
     * Deterministic page ({@code ORDER BY id}) plus the full table count.
     */
    @Override
    @Transactional(readOnly = true)
    public Page findAll(int limit, int offset) {
        Span span = tracer.spanBuilder("PersonRepository.findAll").startSpan();
        try (var scope = span.makeCurrent()) {
            int safeLimit = Person.clampLimit(limit);
            int safeOffset = Person.clampOffset(offset);
            span.setAttribute("limit", safeLimit);
            span.setAttribute("offset", safeOffset);

            Integer total = jdbcTemplate.queryForObject("SELECT COUNT(*) FROM persons_java", Integer.class);
            int totalCount = total == null ? 0 : total;

            String sql = "SELECT " + PERSON_COLUMNS
                    + " FROM persons_java ORDER BY id LIMIT ? OFFSET ?";
            List<Person> persons = jdbcTemplate.query(sql, personRowMapper, safeLimit, safeOffset);
            return new Page(persons, totalCount);
        } catch (RuntimeException ex) {
            span.recordException(ex);
            span.setStatus(StatusCode.ERROR, ex.getMessage() == null ? "findAll failed" : ex.getMessage());
            throw ex;
        } finally {
            span.end();
        }
    }

    /**
     * Parameterized WHERE. Unset fields add no predicate. Filter RPC has no limit → default 50.
     */
    @Override
    @Transactional(readOnly = true)
    public Page findByFilter(PersonFilter filter) {
        Span span = tracer.spanBuilder("PersonRepository.findByFilter").startSpan();
        try (var scope = span.makeCurrent()) {
            PersonFilter safe = filter == null ? new PersonFilter() : filter;
            int safeLimit = Person.clampLimit(safe.getLimit());
            int safeOffset = Person.clampOffset(safe.getOffset());

            FilterSql built = buildFilterWhere(safe);
            Integer total = built.args.isEmpty()
                    ? jdbcTemplate.queryForObject("SELECT COUNT(*) FROM persons_java" + built.where, Integer.class)
                    : jdbcTemplate.queryForObject(
                    "SELECT COUNT(*) FROM persons_java" + built.where, Integer.class, built.args.toArray());
            int totalCount = total == null ? 0 : total;

            List<Object> pageArgs = new ArrayList<>(built.args);
            pageArgs.add(safeLimit);
            pageArgs.add(safeOffset);
            String sql = "SELECT " + PERSON_COLUMNS
                    + " FROM persons_java"
                    + built.where
                    + " ORDER BY id LIMIT ? OFFSET ?";
            List<Person> persons = jdbcTemplate.query(sql, personRowMapper, pageArgs.toArray());
            return new Page(persons, totalCount);
        } catch (RuntimeException ex) {
            span.recordException(ex);
            span.setStatus(StatusCode.ERROR, ex.getMessage() == null ? "findByFilter failed" : ex.getMessage());
            throw ex;
        } finally {
            span.end();
        }
    }

    /**
     * Ranks by L2 distance ({@code <->}) to match HNSW {@code vector_l2_ops}.
     */
    @Override
    @Transactional(readOnly = true)
    public List<Person> searchByVector(List<Float> queryVector, int topK) {
        Span span = tracer.spanBuilder("PersonRepository.searchByVector").startSpan();
        try (var scope = span.makeCurrent()) {
            int safeTopK = Person.clampTopK(topK);
            String lit = vectorLiteral(queryVector);
            if (lit.isEmpty()) {
                throw new IllegalArgumentException("vector is required");
            }
            span.setAttribute("top_k", safeTopK);
            span.setAttribute("vector.dims", queryVector == null ? 0 : queryVector.size());

            String sql = "SELECT " + PERSON_COLUMNS
                    + " FROM persons_java"
                    + " WHERE embedding IS NOT NULL"
                    + " ORDER BY embedding <-> CAST(? AS vector)"
                    + " LIMIT ?";
            return jdbcTemplate.query(sql, personRowMapper, lit, safeTopK);
        } catch (RuntimeException ex) {
            span.recordException(ex);
            span.setStatus(StatusCode.ERROR, ex.getMessage() == null ? "searchByVector failed" : ex.getMessage());
            throw ex;
        } finally {
            span.end();
        }
    }

    /**
     * Builds {@code WHERE …} (or empty) and bind args. Column names are fixed.
     */
    private static FilterSql buildFilterWhere(PersonFilter filter) {
        List<String> clauses = new ArrayList<>();
        List<Object> args = new ArrayList<>();

        String firstName = trimToNull(filter.getFirstName());
        if (firstName != null) {
            clauses.add("first_name ILIKE ? ESCAPE '\\'");
            args.add("%" + escapeLike(firstName) + "%");
        }
        String lastName = trimToNull(filter.getLastName());
        if (lastName != null) {
            clauses.add("last_name ILIKE ? ESCAPE '\\'");
            args.add("%" + escapeLike(lastName) + "%");
        }
        if (filter.getMinAge() != null) {
            clauses.add("age >= ?");
            args.add(filter.getMinAge());
        }
        if (filter.getMaxAge() != null) {
            clauses.add("age <= ?");
            args.add(filter.getMaxAge());
        }
        String sex = trimToNull(filter.getSex());
        if (sex != null) {
            clauses.add(SQL_NORMALIZE_LABEL.formatted("sex") + " = " + SQL_NORMALIZE_LABEL.formatted("?"));
            args.add(sex);
        }
        String nationalCode = trimToNull(filter.getNationalCode());
        if (nationalCode != null) {
            clauses.add("national_code = ?");
            args.add(nationalCode);
        }

        String where = clauses.isEmpty() ? "" : " WHERE " + String.join(" AND ", clauses);
        return new FilterSql(where, args);
    }

    private static String trimToNull(String value) {
        if (value == null) {
            return null;
        }
        String trimmed = value.trim();
        return trimmed.isEmpty() ? null : trimmed;
    }

    /**
     * Formats a float list as a pgvector text literal, or {@code ""} if empty.
     */
    static String vectorLiteral(List<Float> vector) {
        if (vector == null || vector.isEmpty()) {
            return "";
        }
        StringBuilder sb = new StringBuilder(vector.size() * 8);
        sb.append('[');
        for (int i = 0; i < vector.size(); i++) {
            if (i > 0) {
                sb.append(',');
            }
            Float value = vector.get(i);
            sb.append(value == null ? "0" : value);
        }
        sb.append(']');
        return sb.toString();
    }

    /**
     * Parses {@code [1,2,3]} / {@code {1,2,3}} from {@code embedding::text}.
     */
    static List<Float> parseVectorLiteral(String raw) {
        if (raw == null) {
            return List.of();
        }
        String s = raw.trim();
        if (s.startsWith("[") || s.startsWith("{")) {
            s = s.substring(1);
        }
        if (s.endsWith("]") || s.endsWith("}")) {
            s = s.substring(0, s.length() - 1);
        }
        s = s.trim();
        if (s.isEmpty()) {
            return List.of();
        }
        List<Float> out = new ArrayList<>();
        for (String part : s.split(",")) {
            String token = part.trim();
            if (token.isEmpty()) {
                continue;
            }
            try {
                out.add(Float.parseFloat(token));
            } catch (NumberFormatException ignored) {
                // skip malformed dimensions rather than failing the whole page
            }
        }
        return out;
    }

    /**
     * Prefixes {@code \}, {@code %}, and {@code _} so user text is literal inside ILIKE.
     */
    static String escapeLike(String value) {
        return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_");
    }

    private record FilterSql(String where, List<Object> args) {
    }

    /**
     * Maps one {@code persons_java} row onto a domain {@link Person} (column names, not proto).
     */
    private static final class PersonRowMapper implements RowMapper<Person> {
        @Override
        public Person mapRow(ResultSet rs, int rowNum) throws SQLException {
            Person person = new Person();
            person.setId(rs.getString("id"));
            person.setFirstName(rs.getString("first_name"));
            person.setLastName(rs.getString("last_name"));
            person.setAge(rs.getInt("age"));
            person.setSex(nullToEmpty(rs.getString("sex")));
            person.setMaritalStatus(nullToEmpty(rs.getString("marital_status")));
            person.setChildrenCount(rs.getInt("children_count"));
            person.setLivingPlace(nullToEmpty(rs.getString("living_place")));
            person.setOccupation(nullToEmpty(rs.getString("occupation")));
            person.setNationalCode(nullToEmpty(rs.getString("national_code")));
            person.setHasPassport(rs.getBoolean("has_passport"));
            person.setEmbedding(parseVectorLiteral(rs.getString("embedding")));
            return person;
        }

        private static String nullToEmpty(String value) {
            return value == null ? "" : value;
        }
    }
}
