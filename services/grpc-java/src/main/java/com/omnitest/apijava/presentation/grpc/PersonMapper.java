// ============================================================================
// File: services/grpc-java/src/main/java/com/omnitest/apijava/presentation/grpc/PersonMapper.java
// Purpose: Bidirectional mapping between proto messages and domain.Person.
// SOLID: SRP — translation only. No SQL. PersonGrpcService stays orchestration.
// Dependencies: PersonServiceProto stubs, domain. Seed labels are lowercase with
//               spaces or hyphens (male, "job seeker", "full-time", "single parent").
// Mapping: proto.gender ↔ sex; proto.job_category ↔ occupation;
//          proto.embedding_vector ↔ embedding; birth_date derived from age.
// ============================================================================

package com.omnitest.apijava.presentation.grpc;

import com.omnitest.apijava.domain.PersonFilter;
import com.omnitest.apijava.domain.model.Person;
import com.omnitest.polyglot.nexus.shared.proto.PersonServiceProto;

import java.util.ArrayList;
import java.util.List;

/**
 * Proto ↔ domain translator. Writes seed-style lowercase so new rows match the 1M CSV.
 */
final class PersonMapper {

    private PersonMapper() {
    }

    /**
     * Domain row → shared Person message.
     * gender ← sex, job_category ← occupation, embedding_vector ← embedding,
     * birth_date is derived (never read from SQL).
     */
    static PersonServiceProto.Person toProto(Person person) {
        if (person == null) {
            return PersonServiceProto.Person.getDefaultInstance();
        }
        PersonServiceProto.Person.Builder builder = PersonServiceProto.Person.newBuilder()
                .setId(nullToEmpty(person.getId()))
                .setFirstName(nullToEmpty(person.getFirstName()))
                .setLastName(nullToEmpty(person.getLastName()))
                .setAge(person.getAge())
                .setBirthDate(person.birthDateIso())
                .setGender(sexFromDb(person.getSex()))
                .setMaritalStatus(maritalFromDb(person.getMaritalStatus()))
                .setChildrenCount(person.getChildrenCount())
                .setLivingPlace(livingFromDb(person.getLivingPlace()))
                .setJobCategory(occupationFromDb(person.getOccupation()))
                .setNationalCode(nullToEmpty(person.getNationalCode()))
                .setHasPassport(person.isHasPassport());
        List<Float> embedding = person.getEmbedding();
        if (embedding != null && !embedding.isEmpty()) {
            builder.addAllEmbeddingVector(embedding);
        }
        return builder.build();
    }

    /**
     * Maps a slice (never returns a null repeated field).
     */
    static List<PersonServiceProto.Person> toProtoList(List<Person> persons) {
        List<PersonServiceProto.Person> out = new ArrayList<>();
        if (persons == null) {
            return out;
        }
        for (Person person : persons) {
            out.add(toProto(person));
        }
        return out;
    }

    /**
     * Create payload → domain storage labels (seed-style lowercase).
     */
    static Person fromProto(PersonServiceProto.Person msg) {
        if (msg == null) {
            return null;
        }
        Person person = new Person();
        person.setId(trim(msg.getId()));
        person.setFirstName(trim(msg.getFirstName()));
        person.setLastName(trim(msg.getLastName()));
        person.setAge(msg.getAge());
        person.setSex(sexToDb(msg.getGender()));
        person.setMaritalStatus(maritalToDb(msg.getMaritalStatus()));
        person.setChildrenCount(msg.getChildrenCount());
        person.setLivingPlace(livingToDb(msg.getLivingPlace()));
        person.setOccupation(occupationToDb(msg.getJobCategory()));
        person.setNationalCode(trim(msg.getNationalCode()));
        person.setHasPassport(msg.getHasPassport());
        person.setEmbedding(new ArrayList<>(msg.getEmbeddingVectorList()));
        return person;
    }

    /**
     * Copies optional proto fields into a domain filter.
     * Unspecified gender is treated as "not provided" so we do not filter to unknown.
     * FilterSearchRequest has no limit/offset; defaults are 50 / 0.
     */
    static PersonFilter filterFromProto(PersonServiceProto.FilterSearchRequest req) {
        PersonFilter filter = new PersonFilter();
        filter.setLimit(Person.DEFAULT_LIMIT);
        filter.setOffset(0);
        if (req == null) {
            return filter;
        }
        if (req.hasFirstName()) {
            String value = trim(req.getFirstName());
            if (!value.isEmpty()) {
                filter.setFirstName(value);
            }
        }
        if (req.hasLastName()) {
            String value = trim(req.getLastName());
            if (!value.isEmpty()) {
                filter.setLastName(value);
            }
        }
        if (req.hasMinAge()) {
            filter.setMinAge(req.getMinAge());
        }
        if (req.hasMaxAge()) {
            filter.setMaxAge(req.getMaxAge());
        }
        if (req.hasGender() && req.getGender() != PersonServiceProto.Sex.SEX_UNSPECIFIED) {
            filter.setSex(sexToDb(req.getGender()));
        }
        if (req.hasNationalCode()) {
            String value = trim(req.getNationalCode());
            if (!value.isEmpty()) {
                filter.setNationalCode(value);
            }
        }
        return filter;
    }

    /**
     * VARCHAR sex → proto Sex. Accepts seed, prefixless, and SEX_* forms.
     * Flexible: uppercase, spaces/hyphens → underscore, then strip {@code sex_}.
     */
    static PersonServiceProto.Sex sexFromDb(String raw) {
        return switch (normalizeToken(raw, "sex_")) {
            case "male" -> PersonServiceProto.Sex.SEX_MALE;
            case "female" -> PersonServiceProto.Sex.SEX_FEMALE;
            case "bigender" -> PersonServiceProto.Sex.SEX_BIGENDER;
            case "agender" -> PersonServiceProto.Sex.SEX_AGENDER;
            default -> PersonServiceProto.Sex.SEX_UNSPECIFIED;
        };
    }

    /**
     * Proto Sex → seed-style storage ({@code male}, not {@code SEX_MALE}).
     */
    static String sexToDb(PersonServiceProto.Sex value) {
        if (value == null) {
            return "not specified";
        }
        return switch (value) {
            case SEX_MALE -> "male";
            case SEX_FEMALE -> "female";
            case SEX_BIGENDER -> "bigender";
            case SEX_AGENDER -> "agender";
            default -> "not specified";
        };
    }

    /**
     * VARCHAR marital_status → proto, including {@code single parent}.
     */
    static PersonServiceProto.MaritalStatus maritalFromDb(String raw) {
        return switch (normalizeToken(raw, "marital_status_")) {
            case "single" -> PersonServiceProto.MaritalStatus.MARITAL_STATUS_SINGLE;
            case "married" -> PersonServiceProto.MaritalStatus.MARITAL_STATUS_MARRIED;
            case "divorced" -> PersonServiceProto.MaritalStatus.MARITAL_STATUS_DIVORCED;
            case "widowed" -> PersonServiceProto.MaritalStatus.MARITAL_STATUS_WIDOWED;
            case "single_parent" -> PersonServiceProto.MaritalStatus.MARITAL_STATUS_SINGLE_PARENT;
            default -> PersonServiceProto.MaritalStatus.MARITAL_STATUS_UNSPECIFIED;
        };
    }

    /**
     * Proto MaritalStatus → seed label ({@code single parent}).
     */
    static String maritalToDb(PersonServiceProto.MaritalStatus value) {
        if (value == null) {
            return "unspecified";
        }
        return switch (value) {
            case MARITAL_STATUS_SINGLE -> "single";
            case MARITAL_STATUS_MARRIED -> "married";
            case MARITAL_STATUS_DIVORCED -> "divorced";
            case MARITAL_STATUS_WIDOWED -> "widowed";
            case MARITAL_STATUS_SINGLE_PARENT -> "single parent";
            default -> "unspecified";
        };
    }

    /**
     * VARCHAR living_place → proto LivingPlace.
     */
    static PersonServiceProto.LivingPlace livingFromDb(String raw) {
        return switch (normalizeToken(raw, "living_place_")) {
            case "studio" -> PersonServiceProto.LivingPlace.LIVING_PLACE_STUDIO;
            case "apartment" -> PersonServiceProto.LivingPlace.LIVING_PLACE_APARTMENT;
            case "house" -> PersonServiceProto.LivingPlace.LIVING_PLACE_HOUSE;
            case "villa" -> PersonServiceProto.LivingPlace.LIVING_PLACE_VILLA;
            case "hostel" -> PersonServiceProto.LivingPlace.LIVING_PLACE_HOSTEL;
            case "dorm" -> PersonServiceProto.LivingPlace.LIVING_PLACE_DORM;
            case "hotel" -> PersonServiceProto.LivingPlace.LIVING_PLACE_HOTEL;
            default -> PersonServiceProto.LivingPlace.LIVING_PLACE_UNSPECIFIED;
        };
    }

    /**
     * Proto LivingPlace → seed label ({@code apartment}).
     */
    static String livingToDb(PersonServiceProto.LivingPlace value) {
        if (value == null) {
            return "unspecified";
        }
        return switch (value) {
            case LIVING_PLACE_STUDIO -> "studio";
            case LIVING_PLACE_APARTMENT -> "apartment";
            case LIVING_PLACE_HOUSE -> "house";
            case LIVING_PLACE_VILLA -> "villa";
            case LIVING_PLACE_HOSTEL -> "hostel";
            case LIVING_PLACE_DORM -> "dorm";
            case LIVING_PLACE_HOTEL -> "hotel";
            default -> "unspecified";
        };
    }

    /**
     * VARCHAR occupation → proto job_category.
     * Seed uses {@code job seeker} and {@code full-time}.
     */
    static PersonServiceProto.Occupation occupationFromDb(String raw) {
        return switch (normalizeToken(raw, "occupation_")) {
            case "job_seeker" -> PersonServiceProto.Occupation.OCCUPATION_JOB_SEEKER;
            case "jobless" -> PersonServiceProto.Occupation.OCCUPATION_JOBLESS;
            case "full_time" -> PersonServiceProto.Occupation.OCCUPATION_FULL_TIME;
            case "part_time" -> PersonServiceProto.Occupation.OCCUPATION_PART_TIME;
            case "student" -> PersonServiceProto.Occupation.OCCUPATION_STUDENT;
            case "housekeeper" -> PersonServiceProto.Occupation.OCCUPATION_HOUSEKEEPER;
            default -> PersonServiceProto.Occupation.OCCUPATION_UNSPECIFIED;
        };
    }

    /**
     * Proto Occupation → seed label ({@code job seeker}, {@code full-time}).
     */
    static String occupationToDb(PersonServiceProto.Occupation value) {
        if (value == null) {
            return "unspecified";
        }
        return switch (value) {
            case OCCUPATION_JOB_SEEKER -> "job seeker";
            case OCCUPATION_JOBLESS -> "jobless";
            case OCCUPATION_FULL_TIME -> "full-time";
            case OCCUPATION_PART_TIME -> "part-time";
            case OCCUPATION_STUDENT -> "student";
            case OCCUPATION_HOUSEKEEPER -> "housekeeper";
            default -> "unspecified";
        };
    }

    /**
     * Lowercase, unify spaces/hyphens to underscore, collapse repeats, strip proto prefix.
     * {@code "full-time"} → {@code full_time}; {@code "single parent"} → {@code single_parent};
     * {@code SEX_MALE} → {@code male}.
     */
    static String normalizeToken(String raw, String prefix) {
        if (raw == null) {
            return "";
        }
        StringBuilder sb = new StringBuilder(raw.length());
        boolean prevUnderscore = false;
        for (int i = 0; i < raw.length(); i++) {
            char ch = raw.charAt(i);
            if (ch == '-' || ch == ' ' || ch == '_') {
                if (!prevUnderscore && sb.length() > 0) {
                    sb.append('_');
                    prevUnderscore = true;
                }
                continue;
            }
            if (Character.isWhitespace(ch)) {
                if (!prevUnderscore && sb.length() > 0) {
                    sb.append('_');
                    prevUnderscore = true;
                }
                continue;
            }
            sb.append(Character.toLowerCase(ch));
            prevUnderscore = false;
        }
        String token = sb.toString();
        while (token.endsWith("_")) {
            token = token.substring(0, token.length() - 1);
        }
        if (prefix != null && token.startsWith(prefix)) {
            token = token.substring(prefix.length());
        }
        return token;
    }

    private static String trim(String value) {
        return value == null ? "" : value.trim();
    }

    private static String nullToEmpty(String value) {
        return value == null ? "" : value;
    }
}
