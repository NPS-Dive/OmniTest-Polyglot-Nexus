"""
File: presentation/grpc/enum_map.py
Purpose: Map seed VARCHAR labels <-> proto enums without renaming proto fields.
Seed examples: male, job seeker, full-time, single parent, not specified.
SOLID: SRP — mapping only, no I/O.
"""

from __future__ import annotations

from datetime import date

import person_service_pb2 as pb


def _norm(value: str) -> str:
    """Uppercase and turn spaces/hyphens into underscores."""
    return (value or "").strip().upper().replace(" ", "_").replace("-", "_")


def _strip_prefix(token: str, prefixes: tuple[str, ...]) -> str:
    for prefix in prefixes:
        if token.startswith(prefix):
            return token[len(prefix) :]
    return token


def sex_to_proto(db_value: str) -> int:
    token = _strip_prefix(_norm(db_value), ("SEX_",))
    if token in ("NOT_SPECIFIED", "UNSPECIFIED", ""):
        return pb.SEX_UNSPECIFIED
    return getattr(pb, f"SEX_{token}", pb.SEX_UNSPECIFIED)


def marital_to_proto(db_value: str) -> int:
    token = _strip_prefix(_norm(db_value), ("MARITAL_STATUS_",))
    return getattr(pb, f"MARITAL_STATUS_{token}", pb.MARITAL_STATUS_UNSPECIFIED)


def living_to_proto(db_value: str) -> int:
    token = _strip_prefix(_norm(db_value), ("LIVING_PLACE_",))
    return getattr(pb, f"LIVING_PLACE_{token}", pb.LIVING_PLACE_UNSPECIFIED)


def occupation_to_proto(db_value: str) -> int:
    token = _strip_prefix(_norm(db_value), ("OCCUPATION_",))
    return getattr(pb, f"OCCUPATION_{token}", pb.OCCUPATION_UNSPECIFIED)


def proto_enum_to_seed(enum_name: str) -> str:
    """
    Proto name SEX_MALE -> seed label male.
    OCCUPATION_FULL_TIME -> full-time; JOB_SEEKER -> job seeker.
    """
    token = _norm(enum_name)
    for prefix in ("SEX_", "MARITAL_STATUS_", "LIVING_PLACE_", "OCCUPATION_"):
        if token.startswith(prefix):
            token = token[len(prefix) :]
            break
    special = {
        "FULL_TIME": "full-time",
        "PART_TIME": "part-time",
        "JOB_SEEKER": "job seeker",
        "SINGLE_PARENT": "single parent",
        "NOT_SPECIFIED": "not specified",
    }
    if token in special:
        return special[token]
    return token.lower().replace("_", " ")


def derived_birth_date(age: int) -> str:
    """Approximate ISO date: not stored in CSV/SQL."""
    year = date.today().year - max(age, 0)
    return f"{year}-01-01"


def clamp_limit(raw: int) -> int:
    if raw <= 0:
        return 50
    return min(raw, 500)


def clamp_top_k(raw: int) -> int:
    if raw <= 0:
        return 10
    return min(raw, 100)
