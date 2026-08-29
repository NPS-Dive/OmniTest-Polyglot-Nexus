// File: services/api-java/src/main/java/com/omnitest/apijava/presentation/grpc/PersonGrpcService.java
package com.omnitest.apijava.presentation.grpc;

import com.omnitest.apijava.domain.model.Person;
import com.omnitest.apijava.domain.repository.PersonRepository;
import com.omnitest.polyglot.nexus.shared.proto.PersonServiceGrpc;
import com.omnitest.polyglot.nexus.shared.proto.PersonServiceProto;
import com.omnitest.polyglot.nexus.shared.proto.PersonServiceProto.CreatePersonRequest;
import com.omnitest.polyglot.nexus.shared.proto.PersonServiceProto.CreatePersonResponse;
import com.omnitest.polyglot.nexus.shared.proto.PersonServiceProto.ReadAllPersonsRequest;
import com.omnitest.polyglot.nexus.shared.proto.PersonServiceProto.PersonListResponse;

import io.grpc.Status;
import io.grpc.stub.StreamObserver;
import net.devh.boot.grpc.server.service.GrpcService;

import java.util.List;
import java.util.stream.Collectors;

@GrpcService
public class PersonGrpcService extends PersonServiceGrpc.PersonServiceImplBase {

    private final PersonRepository personRepository;

    public PersonGrpcService(PersonRepository personRepository) {
        this.personRepository = personRepository;
    }

    @Override
    public void createPerson(CreatePersonRequest request,
                             StreamObserver<CreatePersonResponse> responseObserver) {
        try {
            if (!request.hasPerson()) {
                responseObserver.onError(
                        Status.INVALID_ARGUMENT
                                .withDescription("CreatePersonRequest.person is required")
                                .asRuntimeException()
                );
                return;
            }

            PersonServiceProto.Person protoPerson = request.getPerson();

            String firstName = protoPerson.getFirstName();
            String lastName = protoPerson.getLastName();
            int rawAge = protoPerson.getAge();
            int age = rawAge <= 0 ? 18 : rawAge;

            Person newPerson = new Person(
                    null,
                    firstName,
                    lastName,
                    age,
                    null
            );

            Person savedPerson = personRepository.save(newPerson);

            String insertedId = savedPerson.getId() != null ? savedPerson.getId() : "";

            CreatePersonResponse response = CreatePersonResponse.newBuilder()
                    .setInsertedId(insertedId)
                    .setSuccess(true)
                    .build();

            responseObserver.onNext(response);
            responseObserver.onCompleted();

        } catch (Exception e) {
            System.err.println("Error in createPerson: " + e.getMessage());
            e.printStackTrace();

            responseObserver.onError(
                    Status.INTERNAL
                            .withDescription("Error creating person: " + e.getMessage())
                            .withCause(e)
                            .asRuntimeException()
            );
        }
    }

    @Override
    public void readAllPersons(ReadAllPersonsRequest request,
                               StreamObserver<PersonListResponse> responseObserver) {
        try {
            int limit = request.getLimit() > 0 ? request.getLimit() : 100;
            int offset = Math.max(0, request.getOffset());

            List<Person> persons = personRepository.findAll(limit, offset);

            List<PersonServiceProto.Person> protoPersons = persons.stream()
                    .map(p -> PersonServiceProto.Person.newBuilder()
                            .setId(p.getId() != null ? p.getId() : "")
                            .setFirstName(p.getFirstName() != null ? p.getFirstName() : "")
                            .setLastName(p.getLastName() != null ? p.getLastName() : "")
                            .setAge(p.getAge() != null ? p.getAge() : 0)
                            .build())
                    .collect(Collectors.toList());

            PersonListResponse response = PersonListResponse.newBuilder()
                    .addAllPersons(protoPersons)
                    .setTotalCount(protoPersons.size())
                    .build();

            responseObserver.onNext(response);
            responseObserver.onCompleted();

        } catch (Exception e) {
            System.err.println("Error in readAllPersons: " + e.getMessage());
            e.printStackTrace();

            responseObserver.onError(
                    Status.INTERNAL
                            .withDescription("Error fetching persons: " + e.getMessage())
                            .withCause(e)
                            .asRuntimeException()
            );
        }
    }
}
