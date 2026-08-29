"""
Models Module
Adheres to SRP (Single Responsibility Principle).
This file contains only plain data structures (DTOs). It has no logic for 
how data is generated or how it is saved.
"""
from dataclasses import dataclass

@dataclass
class PersonModel:
    """
    Data Transfer Object (DTO) representing a single Person record.
    Using dataclass ensures clean code and reduces boilerplate.
    """
    id: str
    first_name: str
    last_name: str
    age: int
    sex: str
    marital_status: str
    children_count: int
    living_place: str
    occupation: str
    national_code: str
