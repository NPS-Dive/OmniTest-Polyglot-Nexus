"""
Main Module (Orchestrator)
This is the entry point. It wires all the SOLID components together.
"""
import os
from factory import PersonFactory
from exporters import BaseExporter, CsvExporter

class DataGeneratorOrchestrator:
    """
    Coordinates the Factory and Exporter.
    DIP: Depends on BaseExporter abstraction, not the concrete CsvExporter.
    """
    def __init__(self, factory: PersonFactory, exporter: BaseExporter):
        self.factory = factory
        self.exporter = exporter

    def run(self, total_rows: int, output_path: str) -> None:
        print(f"Starting generation of {total_rows} rows...")
        
        # 1. Get the memory-efficient data stream
        data_stream = self.factory.generate_batch(total_rows)
        
        # 2. Pass stream to exporter to save to disk
        self.exporter.export(data_stream, output_path)
        
        print(f"Successfully generated and saved to: {output_path}")

if __name__ == "__main__":
    # Define parameters (Target is $10^6$ for AI/RAG benchmarking)
    TARGET_ROWS = 1000000 
    
    # Define output path (saving it one level up in the data/ folder)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    OUTPUT_FILE = os.path.join(base_dir, "..", "master_seed.csv")
    
    # Dependency Injection: Wire up the concrete implementations
    factory = PersonFactory()
    exporter = CsvExporter()
    orchestrator = DataGeneratorOrchestrator(factory, exporter)
    
    # Execute the process
    orchestrator.run(TARGET_ROWS, OUTPUT_FILE)
