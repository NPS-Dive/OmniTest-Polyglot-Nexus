"""
Exporters Module
Adheres to OCP (Open/Closed Principle) and DIP (Dependency Inversion Principle).
"""
import csv
import os
from abc import ABC, abstractmethod
from typing import Iterator
from dataclasses import asdict
from models import PersonModel

class BaseExporter(ABC):
    """
    Abstract base class. 
    OCP: We can add a JsonExporter or SqlExporter later without altering existing code.
    """
    @abstractmethod
    def export(self, data_stream: Iterator[PersonModel], file_path: str) -> None:
        pass

class CsvExporter(BaseExporter):
    """
    Concrete implementation for exporting to CSV.
    Chosen for maximum performance when seeding PostgreSQL.
    """
    def export(self, data_stream: Iterator[PersonModel], file_path: str) -> None:
        # Extract headers automatically from the Dataclass fields
        fieldnames = list(PersonModel.__annotations__.keys())
        
        # Ensure the directory exists before writing
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, mode='w', newline='', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            
            # Write row by row directly from the memory stream to the disk
            for person in data_stream:
                writer.writerow(asdict(person))
