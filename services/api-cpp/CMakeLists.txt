# ==============================================================================
# CMake configuration for OmniTest-Polyglot-Nexus: C++ gRPC API
# Adheres to Clean Architecture and SOLID principles by separating concerns
# and clearly defining build targets.
# ==============================================================================

cmake_minimum_required(VERSION 3.15)
project(OmniTestApiCpp VERSION 1.0.0 LANGUAGES CXX)

# Require C++17 standard for modern features like std::optional used in the Domain layer
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# ------------------------------------------------------------------------------
# 1. Find External Dependencies (Infrastructure Drivers)
# ------------------------------------------------------------------------------

# Find threading library (required for gRPC and general server operations)
find_package(Threads REQUIRED)

# Find Protocol Buffers
find_package(Protobuf REQUIRED)

# Find gRPC
find_package(gRPC REQUIRED)

# Find PostgreSQL C++ library (libpqxx) for independent DB access
# Note: If CMake cannot find this natively, you may need to use vcpkg or set pqxx_DIR
find_package(pqxx REQUIRED)

# ------------------------------------------------------------------------------
# 2. Protocol Buffers & gRPC Code Generation
# ------------------------------------------------------------------------------
# In a production environment, proto files are often compiled dynamically.
# Assuming you have generated the .pb.cc and .grpc.pb.cc files and placed them
# in a directory (e.g., src/presentation/grpc/proto_gen/)

set(PROTO_GEN_SRC_DIR "${CMAKE_CURRENT_SOURCE_DIR}/src/presentation/grpc/proto_gen")
set(PROTO_SRCS 
    "${PROTO_GEN_SRC_DIR}/person.pb.cc"
    "${PROTO_GEN_SRC_DIR}/person.grpc.pb.cc"
)

# ------------------------------------------------------------------------------
# 3. Define Project Source Files
# ------------------------------------------------------------------------------
set(DOMAIN_SRCS 
    # Domain entities are header-only structs in our SRP design, so no .cpp files here
)

set(INFRASTRUCTURE_SRCS
    # Concrete database implementations (DIP)
    "${CMAKE_CURRENT_SOURCE_DIR}/src/infrastructure/db/PostgresPersonRepository.cpp"
)

set(PRESENTATION_SRCS
    # gRPC controllers (Interface Adapters)
    "${CMAKE_CURRENT_SOURCE_DIR}/src/presentation/grpc/PersonGrpcService.cpp"
)

set(MAIN_SRC
    # Orchestrator
    "${CMAKE_CURRENT_SOURCE_DIR}/src/main.cpp"
)

# ------------------------------------------------------------------------------
# 4. Create the Executable Target
# ------------------------------------------------------------------------------
add_executable(${PROJECT_NAME} 
    ${PROTO_SRCS} 
    ${INFRASTRUCTURE_SRCS} 
    ${PRESENTATION_SRCS} 
    ${MAIN_SRC}
)

# ------------------------------------------------------------------------------
# 5. Link Libraries and Include Directories
# ------------------------------------------------------------------------------
# Include directories so #include statements find headers easily
target_include_directories(${PROJECT_NAME} PRIVATE 
    "${CMAKE_CURRENT_SOURCE_DIR}/src"
    "${PROTO_GEN_SRC_DIR}"
)

# Link all required frameworks and drivers to our executable
target_link_libraries(${PROJECT_NAME} PRIVATE
    gRPC::grpc++
    gRPC::grpc++_reflection # Optional: Good for Postman/UI testing
    protobuf::libprotobuf
    pqxx::pqxx
    Threads::Threads
)

# Print a status message during configuration
message(STATUS "Configured C++ gRPC API for OmniTest-Polyglot-Nexus.")
message(STATUS "Ensure 'persons_cpp' database is accessible on port 5432.")
