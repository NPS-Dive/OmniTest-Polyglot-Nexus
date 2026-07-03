"""
Factory Module
Adheres to SRP.
Responsible solely for instantiating PersonModel objects with mock data.
"""
import uuid
import random
from typing import Iterator
from faker import Faker
from models import PersonModel
from rules import NationalCodeGenerator

class PersonFactory:
    """
    Uses the Faker library and predefined constraints to assemble valid Person records.
    """
    def __init__(self):
        self.faker = Faker()
        # Pre-defined constraints based on QAQC project requirements
        self.sexes = ['male', 'female', 'bigender', 'agender', 'not specified']
        self.marital_statuses = ['single', 'married', 'divorced', 'widowed', 'single parent']
        self.living_places = ['studio', 'apartment', 'house', 'villa', 'hostel', 'dorm', 'hotel']
        self.occupations = ['job seeker', 'jobless', 'full-time', 'part-time', 'student', 'housekeeper']

    def create_person(self) -> PersonModel:
        """Generates a single, valid PersonModel."""
        return PersonModel(
            id=str(uuid.uuid4()),
            first_name=self.faker.first_name(),
            last_name=self.faker.last_name(),
            age=random.randint(16, 78),
            sex=random.choice(self.sexes),
            marital_status=random.choice(self.marital_statuses),
            children_count=random.randint(0, 5),
            living_place=random.choice(self.living_places),
            occupation=random.choice(self.occupations),
            national_code=NationalCodeGenerator.generate()
        )

    def generate_batch(self, count: int) -> Iterator[PersonModel]:
        """
        Yields a batch of PersonModels using a Python Generator (yield).
        Clean Code: Prevents RAM exhaustion when generating $1000000$ rows.
        """
        for _ in range(count):
            yield self.create_person()
