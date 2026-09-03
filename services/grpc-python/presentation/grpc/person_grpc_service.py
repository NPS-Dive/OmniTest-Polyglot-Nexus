"""
File: presentation/grpc/person_grpc_service.py
Purpose: Map proto <-> domain. No SQL. Depends on IPersonRepository (DIP).
SOLID: presentation never constructs SessionLocal or the Postgres adapter;
       the composition root injects a unit-of-work factory.
"""

from __future__ import annotations

from typing import Callable, Tuple

import grpc

import person_service_pb2 as pb
import person_service_pb2_grpc as pb_grpc
from domain.i_person_repository import IPersonRepository
from domain.person import Person, PersonFilter
from presentation.grpc.enum_map import (
    clamp_limit,
    clamp_top_k,
    derived_birth_date,
    living_to_proto,
    marital_to_proto,
    occupation_to_proto,
    proto_enum_to_seed,
    sex_to_proto,
)

# Session + repository pair. Session must be closed by the caller (RPC finally).
RepoFactory = Callable[[], Tuple[object, IPersonRepository]]


def _to_proto(person: Person) -> pb.Person:
    """Domain Person → proto Person (gender/job_category/embedding_vector mapping)."""
    msg = pb.Person(
        id=str(person.id) if person.id else "",
        first_name=person.first_name,
        last_name=person.last_name,
        age=person.age,
        birth_date=derived_birth_date(person.age),
        gender=sex_to_proto(person.sex),
        marital_status=marital_to_proto(person.marital_status),
        children_count=person.children_count,
        living_place=living_to_proto(person.living_place),
        job_category=occupation_to_proto(person.occupation),
        national_code=person.national_code,
        has_passport=person.has_passport,
    )
    if person.embedding:
        msg.embedding_vector.extend(person.embedding)
    return msg


def _from_proto(msg: pb.Person) -> Person:
    """Proto Person → domain. birth_date is ignored (derived on read only)."""
    embedding = list(msg.embedding_vector) if msg.embedding_vector else None
    return Person(
        first_name=msg.first_name,
        last_name=msg.last_name,
        age=msg.age,
        sex=proto_enum_to_seed(pb.Sex.Name(msg.gender)),
        marital_status=proto_enum_to_seed(pb.MaritalStatus.Name(msg.marital_status)),
        children_count=msg.children_count,
        living_place=proto_enum_to_seed(pb.LivingPlace.Name(msg.living_place)),
        occupation=proto_enum_to_seed(pb.Occupation.Name(msg.job_category)),
        national_code=msg.national_code,
        has_passport=msg.has_passport,
        embedding=embedding,
    )


class PersonGrpcService(pb_grpc.PersonServiceServicer):
    """gRPC adapter. Opens a unit of work per RPC via the injected factory."""

    def __init__(self, open_repo: RepoFactory) -> None:
        self._open_repo = open_repo

    def _repo(self) -> Tuple[object, IPersonRepository]:
        """Why a factory: each RPC needs its own SQLAlchemy session (thread safety)."""
        return self._open_repo()

    def CreatePerson(self, request, context):
        session, repo = self._repo()
        try:
            if not request.HasField("person"):
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("person payload is required")
                return pb.CreatePersonResponse(success=False, message="missing person")
            created = repo.create(_from_proto(request.person))
            return pb.CreatePersonResponse(
                success=True,
                message="created in persons_python",
                inserted_id=str(created.id),
            )
        except Exception as exc:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(exc))
            return pb.CreatePersonResponse(success=False, message=str(exc))
        finally:
            session.close()

    def ReadAllPersons(self, request, context):
        session, repo = self._repo()
        try:
            people, count = repo.read_all(clamp_limit(request.limit), max(request.offset, 0))
            return pb.PersonListResponse(persons=[_to_proto(p) for p in people], total_count=count)
        except Exception as exc:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(exc))
            return pb.PersonListResponse()
        finally:
            session.close()

    def SearchByFilter(self, request, context):
        session, repo = self._repo()
        try:
            sex_label = None
            if request.HasField("gender") and request.gender != pb.SEX_UNSPECIFIED:
                sex_label = proto_enum_to_seed(pb.Sex.Name(request.gender))
            filters = PersonFilter(
                first_name=request.first_name if request.HasField("first_name") else None,
                last_name=request.last_name if request.HasField("last_name") else None,
                min_age=request.min_age if request.HasField("min_age") else None,
                max_age=request.max_age if request.HasField("max_age") else None,
                sex=sex_label,
                national_code=request.national_code if request.HasField("national_code") else None,
            )
            people, total = repo.search_by_filter(filters, 100)
            return pb.PersonListResponse(persons=[_to_proto(p) for p in people], total_count=total)
        except Exception as exc:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(exc))
            return pb.PersonListResponse()
        finally:
            session.close()

    def SearchByVector(self, request, context):
        session, repo = self._repo()
        try:
            vector = list(request.vector)
            if not vector:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("vector is required")
                return pb.PersonListResponse()
            people = repo.search_by_vector(vector, clamp_top_k(request.top_k))
            # Vector kNN: total_count is the returned neighbour count (documented).
            return pb.PersonListResponse(persons=[_to_proto(p) for p in people], total_count=len(people))
        except Exception as exc:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(exc))
            return pb.PersonListResponse()
        finally:
            session.close()
