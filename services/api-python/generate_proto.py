"""
File: generate_proto.py
Purpose: Regenerate person_service_pb2*.py from the shared proto (source of truth).
Run from services/api-python: python generate_proto.py
"""

from pathlib import Path
from grpc_tools import protoc

ROOT = Path(__file__).resolve().parents[2]
PROTO_DIR = ROOT / "shared" / "proto"
OUT = Path(__file__).resolve().parent

code = protoc.main(
    [
        "grpc_tools.protoc",
        f"-I{PROTO_DIR}",
        f"--python_out={OUT}",
        f"--grpc_python_out={OUT}",
        str(PROTO_DIR / "person_service.proto"),
    ]
)
raise SystemExit(code)
