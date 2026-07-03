"""
Service Layer: gRPC Servicer Implementation.
Acts as the controller: maps gRPC requests to repository calls and formats gRPC responses.
"""
import grpc
import person_service_pb2
import person_service_pb2_grpc
from repository import PersonRepository
from database import SessionLocal
from models import PersonEntity

def _safe_enum_value(enum_name: str, db_value: str) -> int:
    """Safely maps database string values to Protobuf enum integers."""
    if not db_value:
        return 0
        
    val_upper = db_value.upper()
    
    try:
        if enum_name == "Sex":
            return getattr(person_service_pb2, f"SEX_{val_upper}")
        elif enum_name == "MaritalStatus":
            return getattr(person_service_pb2, f"MARITAL_STATUS_{val_upper}")
        elif enum_name == "LivingPlace":
            return getattr(person_service_pb2, f"LIVING_PLACE_{val_upper}")
        elif enum_name == "Occupation":
            return getattr(person_service_pb2, f"OCCUPATION_{val_upper}")
    except AttributeError:
        # If the exact enum isn't found, fallback to 0 (UNSPECIFIED)
        pass
        
    return 0

def _safe_enum_name(enum_descriptor, value_int):
    """Proto Int to DB String mapping."""
    if value_int is None:
        return "UNKNOWN"
    try:
        return enum_descriptor.Name(value_int)
    except (ValueError, TypeError):
        return "UNKNOWN"

class PersonGrpcService(person_service_pb2_grpc.PersonServiceServicer):
    
    def _map_entity_to_proto(self, entity: PersonEntity) -> person_service_pb2.Person:
        """Helper to centralize the mapping logic (SRP)."""
        return person_service_pb2.Person(
            id=str(entity.id),
            name=entity.name,
            family=entity.family,
            age=entity.age,
            # Pass strings here so the dictionary lookup in _safe_enum_value works
            sex=_safe_enum_value("Sex", entity.sex),
            marital_status=_safe_enum_value("MaritalStatus", entity.marital_status),
            children_count=entity.children_count,
            living_place=_safe_enum_value("LivingPlace", entity.living_place),
            occupation=_safe_enum_value("Occupation", entity.occupation),
            national_code=entity.national_code
        )

    def ReadAllPersons(self, request, context):
        db = SessionLocal()
        try:
            repo = PersonRepository(db)
            limit = getattr(request, 'limit', 100)
            offset = getattr(request, 'offset', 0)

            entities = repo.get_all(limit, offset)
            persons = [self._map_entity_to_proto(e) for e in entities]

            return person_service_pb2.PersonListResponse(persons=persons)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal server error: {str(e)}")
            return person_service_pb2.PersonListResponse()
        finally:
            db.close()

    def CreatePerson(self, request, context):
        db = SessionLocal()
        try:
            repo = PersonRepository(db)
            
            new_entity = PersonEntity(
                name=request.person.name,
                family=request.person.family,
                age=request.person.age,
                sex=_safe_enum_name(person_service_pb2.Sex, request.person.sex),
                marital_status=_safe_enum_name(person_service_pb2.MaritalStatus, request.person.marital_status),
                children_count=request.person.children_count,
                living_place=_safe_enum_name(person_service_pb2.LivingPlace, request.person.living_place),
                occupation=_safe_enum_name(person_service_pb2.Occupation, request.person.occupation),
                national_code=request.person.national_code,
                embedding=list(request.person.embedding) if request.person.embedding else None
            )
            
            created_entity = repo.create(new_entity)
            
            return person_service_pb2.CreatePersonResponse(
                success=True,
                message="Person created successfully",
                id=str(created_entity.id)
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Failed to create person: {str(e)}")
            return person_service_pb2.CreatePersonResponse(success=False, message=str(e))
        finally:
            db.close()

    def SearchByFilter(self, request, context):
        db = SessionLocal()
        try:
            repo = PersonRepository(db)
            
            filters = {
                "age": getattr(request, 'age', None),
                "occupation": _safe_enum_name(person_service_pb2.Occupation, getattr(request, 'occupation', 0)) if getattr(request, 'occupation', 0) != 0 else None,
                "living_place": _safe_enum_name(person_service_pb2.LivingPlace, getattr(request, 'living_place', 0)) if getattr(request, 'living_place', 0) != 0 else None
            }
            
            entities = repo.search_by_filter(filters)
            persons = [self._map_entity_to_proto(e) for e in entities]
            
            return person_service_pb2.PersonListResponse(persons=persons)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Filter search failed: {str(e)}")
            return person_service_pb2.PersonListResponse()
        finally:
            db.close()

    def SearchByVector(self, request, context):
        try:
            # Safely extract variables
            query_embedding = list(request.vector)
            # Use getattr to safely handle 'limit' if it was named differently in earlier proto versions
            limit = getattr(request, 'limit', 5)
            if limit <= 0:
                limit = 5
            
            with SessionLocal() as db:
                repo = PersonRepository(db)
                entities = repo.search_by_vector(query_embedding, limit)
                
                # Map entities to Protobuf messages
                proto_persons = [self._map_entity_to_proto(entity) for entity in entities]
                
                return person_service_pb2.PersonListResponse(
                    persons=proto_persons,
                    total_count=len(proto_persons)
                )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal server error: {str(e)}")
            return person_service_pb2.PersonListResponse()
