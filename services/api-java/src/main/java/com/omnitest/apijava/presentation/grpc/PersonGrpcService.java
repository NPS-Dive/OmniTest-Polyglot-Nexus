// ============================================================================
// File: services/api-java/src/main/java/com/omnitest/apijava/presentation/grpc/PersonGrpcService.java
// Purpose: PersonService RPC adapter — proto ↔ domain, then repository calls.
// SOLID: SRP — transport mapping only (no SQL). DIP — depends on PersonRepository.
// Dependencies: PersonServiceProto, domain, gRPC Status. All four RPCs live here.
// ============================================================================

package com.omnitest.apijava.presentation.grpc;

import com.omnitest.apijava.domain.PersonFilter;
import com.omnitest.apijava.domain.model.Person;
import com.omnitest.apijava.domain.repository.PersonRepository;
import com.omnitest.polyglot.nexus.shared.proto.PersonServiceGrpc;
import com.omnitest.polyglot.nexus.shared.proto.PersonServiceProto;
import io.grpc.Status;
import io.grpc.stub.StreamObserver;
import net.devh.boot.grpc.server.service.GrpcService;

import java.util.List;
import java.util.UUID;

/**
 * Implements {@code omnitest.polyglot.nexus.PersonService} for {@code persons_java}.
 */
@GrpcService
public class PersonGrpcService extends PersonServiceGrpc.PersonServiceImplBase {

    private final PersonRepository personRepository;

    public PersonGrpcService(PersonRepository personRepository) {
        this.personRepository = personRepository;
    }

    /**
     * Validates the payload, maps proto → domain, and inserts one row.
     */
    @Override
    public void createPerson(PersonServiceProto.CreatePersonRequest request,
                             StreamObserver<PersonServiceProto.CreatePersonResponse> responseObserver) {
        try {
            if (request == null || !request.hasPerson()) {
                responseObserver.onError(Status.INVALID_ARGUMENT
                        .withDescription("person is required")
                        .asRuntimeException());
                return;
            }

            PersonServiceProto.Person src = request.getPerson();
            if (src.getFirstName().trim().isEmpty()) {
                responseObserver.onError(Status.INVALID_ARGUMENT
                        .withDescription("first_name is required")
                        .asRuntimeException());
                return;
            }
            if (src.getLastName().trim().isEmpty()) {
                responseObserver.onError(Status.INVALID_ARGUMENT
                        .withDescription("last_name is required")
                        .asRuntimeException());
                return;
            }
            if (src.getAge() < 0) {
                responseObserver.onError(Status.INVALID_ARGUMENT
                        .withDescription("age must be >= 0")
                        .asRuntimeException());
                return;
            }
            if (src.getChildrenCount() < 0) {
                responseObserver.onError(Status.INVALID_ARGUMENT
                        .withDescription("children_count must be >= 0")
                        .asRuntimeException());
                return;
            }
            String nationalCode = src.getNationalCode().trim();
            if (!nationalCode.isEmpty() && nationalCode.length() > 10) {
                responseObserver.onError(Status.INVALID_ARGUMENT
                        .withDescription("national_code must be at most 10 characters")
                        .asRuntimeException());
                return;
            }
            String id = src.getId().trim();
            if (!id.isEmpty()) {
                try {
                    UUID.fromString(id);
                } catch (IllegalArgumentException ex) {
                    responseObserver.onError(Status.INVALID_ARGUMENT
                            .withDescription("id must be a valid UUID")
                            .asRuntimeException());
                    return;
                }
            }
            if (src.getEmbeddingVectorCount() > 0
                    && src.getEmbeddingVectorCount() != Person.EMBEDDING_DIMS) {
                responseObserver.onError(Status.INVALID_ARGUMENT
                        .withDescription("embedding_vector must be empty or " + Person.EMBEDDING_DIMS + " dimensions")
                        .asRuntimeException());
                return;
            }

            Person saved = personRepository.save(PersonMapper.fromProto(src));
            PersonServiceProto.CreatePersonResponse response = PersonServiceProto.CreatePersonResponse.newBuilder()
                    .setSuccess(true)
                    .setMessage("person created in persons_java")
                    .setInsertedId(saved.getId() == null ? "" : saved.getId())
                    .build();
            responseObserver.onNext(response);
            responseObserver.onCompleted();
        } catch (IllegalArgumentException ex) {
            responseObserver.onError(mapInvalid(ex));
        } catch (Exception ex) {
            responseObserver.onError(mapInternal(ex));
        }
    }

    /**
     * Returns a page of persons. {@code limit} default 50, max 500.
     */
    @Override
    public void readAllPersons(PersonServiceProto.ReadAllPersonsRequest request,
                               StreamObserver<PersonServiceProto.PersonListResponse> responseObserver) {
        try {
            int limit = request == null ? 0 : request.getLimit();
            int offset = request == null ? 0 : request.getOffset();
            PersonRepository.Page page = personRepository.findAll(limit, offset);
            completeList(responseObserver, page.persons(), page.totalCount());
        } catch (Exception ex) {
            responseObserver.onError(mapInternal(ex));
        }
    }

    /**
     * Optional first_name, last_name, age range, gender, national_code.
     */
    @Override
    public void searchByFilter(PersonServiceProto.FilterSearchRequest request,
                               StreamObserver<PersonServiceProto.PersonListResponse> responseObserver) {
        try {
            PersonFilter filter = PersonMapper.filterFromProto(request);
            PersonRepository.Page page = personRepository.findByFilter(filter);
            completeList(responseObserver, page.persons(), page.totalCount());
        } catch (Exception ex) {
            responseObserver.onError(mapInternal(ex));
        }
    }

    /**
     * Nearest neighbors with L2 ({@code <->}). {@code top_k} default 10, max 100.
     */
    @Override
    public void searchByVector(PersonServiceProto.VectorSearchRequest request,
                               StreamObserver<PersonServiceProto.PersonListResponse> responseObserver) {
        try {
            if (request == null || request.getVectorCount() == 0) {
                responseObserver.onError(Status.INVALID_ARGUMENT
                        .withDescription("vector is required")
                        .asRuntimeException());
                return;
            }
            if (request.getVectorCount() != Person.EMBEDDING_DIMS) {
                responseObserver.onError(Status.INVALID_ARGUMENT
                        .withDescription("vector must have " + Person.EMBEDDING_DIMS
                                + " dimensions, got " + request.getVectorCount())
                        .asRuntimeException());
                return;
            }

            List<Person> persons = personRepository.searchByVector(
                    request.getVectorList(), request.getTopK());
            completeList(responseObserver, persons, persons.size());
        } catch (IllegalArgumentException ex) {
            responseObserver.onError(mapInvalid(ex));
        } catch (Exception ex) {
            responseObserver.onError(mapInternal(ex));
        }
    }

    private static void completeList(StreamObserver<PersonServiceProto.PersonListResponse> observer,
                                     List<Person> persons, int totalCount) {
        PersonServiceProto.PersonListResponse response = PersonServiceProto.PersonListResponse.newBuilder()
                .addAllPersons(PersonMapper.toProtoList(persons))
                .setTotalCount(totalCount)
                .build();
        observer.onNext(response);
        observer.onCompleted();
    }

    private static io.grpc.StatusException mapInvalid(IllegalArgumentException ex) {
        String msg = ex.getMessage() == null ? "invalid argument" : ex.getMessage();
        if (msg.contains("invalid person id")) {
            return Status.INVALID_ARGUMENT.withDescription("id must be a valid UUID").asRuntimeException();
        }
        return Status.INVALID_ARGUMENT.withDescription(msg).asRuntimeException();
    }

    private static io.grpc.StatusException mapInternal(Exception ex) {
        String msg = ex.getMessage() == null ? "database error" : ex.getMessage();
        return Status.INTERNAL.withDescription("database error: " + msg).asRuntimeException();
    }
}
