cmake_minimum_required(VERSION 3.15)
project(OmniTestApiCpp)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find Protobuf, gRPC, and libpqxx
find_package(Protobuf REQUIRED)
find_package(gRPC CONFIG REQUIRED)
find_package(pqxx REQUIRED)

# Set Proto paths
set(PROTO_SRC_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../../shared/proto")
set(PROTO_FILE "${PROTO_SRC_DIR}/person_service.proto")

# Determine paths for the protoc compiler and grpc_cpp_plugin
find_program(PROTOC_EXECUTABLE protoc)
if(NOT PROTOC_EXECUTABLE)
    message(FATAL_ERROR "protoc not found.")
endif()

# Find gRPC CPP plugin
find_program(GRPC_CPP_PLUGIN_EXECUTABLE grpc_cpp_plugin)
if(NOT GRPC_CPP_PLUGIN_EXECUTABLE)
    message(FATAL_ERROR "grpc_cpp_plugin not found.")
endif()

# Define generated output files
set(PROTO_SRCS "${CMAKE_CURRENT_BINARY_DIR}/person_service.pb.cc")
set(PROTO_HDRS "${CMAKE_CURRENT_BINARY_DIR}/person_service.pb.h")
set(GRPC_SRCS "${CMAKE_CURRENT_BINARY_DIR}/person_service.grpc.pb.cc")
set(GRPC_HDRS "${CMAKE_CURRENT_BINARY_DIR}/person_service.grpc.pb.h")

# Custom command to generate C++ code from proto
add_custom_command(
    OUTPUT ${PROTO_SRCS} ${PROTO_HDRS} ${GRPC_SRCS} ${GRPC_HDRS}
    COMMAND ${PROTOC_EXECUTABLE}
    ARGS --grpc_out="${CMAKE_CURRENT_BINARY_DIR}"
         --cpp_out="${CMAKE_CURRENT_BINARY_DIR}"
         -I "${PROTO_SRC_DIR}"
         --plugin=protoc-gen-grpc="${GRPC_CPP_PLUGIN_EXECUTABLE}"
         "${PROTO_FILE}"
    DEPENDS "${PROTO_FILE}"
)

# Include directories
include_directories(${CMAKE_CURRENT_BINARY_DIR})
include_directories(include)

# Define executable
add_executable(api_cpp 
    src/main.cpp 
    ${PROTO_SRCS} 
    ${GRPC_SRCS}
)

# Link libraries
target_link_libraries(api_cpp
    gRPC::grpc++
    protobuf::libprotobuf
    pqxx
)
