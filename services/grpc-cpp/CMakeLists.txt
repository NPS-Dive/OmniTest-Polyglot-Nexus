# ============================================================================
# File: services/api-cpp/CMakeLists.txt
# Purpose: Build the C++ Person gRPC service (api_cpp) and generate C++ stubs
#          from shared/proto/person_service.proto (package omnitest.polyglot.nexus).
# SOLID role: build composition — every src/**/*.cpp is compiled, not just main.cpp.
# Dependencies: Protobuf, gRPC, libpqxx (pqxx). Optional vcpkg toolchain on Windows.
# ============================================================================

cmake_minimum_required(VERSION 3.15)
project(OmniTestApiCpp LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(Threads REQUIRED)
find_package(Protobuf REQUIRED)
find_package(gRPC CONFIG REQUIRED)

# vcpkg exports pqxx::pqxx; distro packages may only export the un-namespaced pqxx.
find_package(pqxx CONFIG QUIET)
if(NOT pqxx_FOUND)
    find_package(pqxx REQUIRED)
endif()

set(PROTO_SRC_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../../shared/proto")
set(PROTO_FILE "${PROTO_SRC_DIR}/person_service.proto")

# ---------------------------------------------------------------------------
# Locate protoc and grpc_cpp_plugin (vcpkg imported targets or PATH).
# ---------------------------------------------------------------------------
function(opn_imported_location out_var target_name)
    set(_loc "")
    if(TARGET ${target_name})
        foreach(_cfg LOCATION LOCATION_RELEASE LOCATION_RELWITHDEBINFO LOCATION_MINSIZEREL LOCATION_DEBUG)
            get_target_property(_loc ${target_name} IMPORTED_${_cfg})
            if(_loc)
                break()
            endif()
        endforeach()
    endif()
    set(${out_var} "${_loc}" PARENT_SCOPE)
endfunction()

opn_imported_location(PROTOC_EXECUTABLE protobuf::protoc)
if(NOT PROTOC_EXECUTABLE AND DEFINED Protobuf_PROTOC_EXECUTABLE)
    set(PROTOC_EXECUTABLE "${Protobuf_PROTOC_EXECUTABLE}")
endif()
if(NOT PROTOC_EXECUTABLE)
    find_program(PROTOC_EXECUTABLE protoc)
endif()
if(NOT PROTOC_EXECUTABLE)
    message(FATAL_ERROR "protoc not found. Install Protobuf or enable the vcpkg toolchain.")
endif()

opn_imported_location(GRPC_CPP_PLUGIN_EXECUTABLE gRPC::grpc_cpp_plugin)
if(NOT GRPC_CPP_PLUGIN_EXECUTABLE)
    find_program(GRPC_CPP_PLUGIN_EXECUTABLE grpc_cpp_plugin)
endif()
if(NOT GRPC_CPP_PLUGIN_EXECUTABLE)
    message(FATAL_ERROR "grpc_cpp_plugin not found. Install gRPC or enable the vcpkg toolchain.")
endif()

set(PROTO_SRCS "${CMAKE_CURRENT_BINARY_DIR}/person_service.pb.cc")
set(PROTO_HDRS "${CMAKE_CURRENT_BINARY_DIR}/person_service.pb.h")
set(GRPC_SRCS "${CMAKE_CURRENT_BINARY_DIR}/person_service.grpc.pb.cc")
set(GRPC_HDRS "${CMAKE_CURRENT_BINARY_DIR}/person_service.grpc.pb.h")

add_custom_command(
    OUTPUT ${PROTO_SRCS} ${PROTO_HDRS} ${GRPC_SRCS} ${GRPC_HDRS}
    COMMAND "${PROTOC_EXECUTABLE}"
            --grpc_out=${CMAKE_CURRENT_BINARY_DIR}
            --cpp_out=${CMAKE_CURRENT_BINARY_DIR}
            -I "${PROTO_SRC_DIR}"
            --plugin=protoc-gen-grpc=${GRPC_CPP_PLUGIN_EXECUTABLE}
            "${PROTO_FILE}"
    DEPENDS "${PROTO_FILE}"
    COMMENT "Generating C++ gRPC stubs from person_service.proto"
    VERBATIM
)

# Compile every application translation unit under src/ (repository, gRPC, main).
file(GLOB_RECURSE APP_SOURCES CONFIGURE_DEPENDS
    "${CMAKE_CURRENT_SOURCE_DIR}/src/*.cpp"
)

add_executable(api_cpp
    ${APP_SOURCES}
    ${PROTO_SRCS}
    ${GRPC_SRCS}
)

target_include_directories(api_cpp PRIVATE
    "${CMAKE_CURRENT_BINARY_DIR}"
    "${CMAKE_CURRENT_SOURCE_DIR}/src"
)

if(TARGET pqxx::pqxx)
    set(OPN_PQXX_LIB pqxx::pqxx)
else()
    set(OPN_PQXX_LIB pqxx)
endif()

target_link_libraries(api_cpp PRIVATE
    gRPC::grpc++
    protobuf::libprotobuf
    ${OPN_PQXX_LIB}
    Threads::Threads
)
