#include <iostream>
#include <memory>
#include <string>

#include <grpcpp/grpcpp.h>
#include "person_service.grpc.pb.h" // Generated header

using grpc::Server;
using grpc::ServerBuilder;
using grpc::ServerContext;
using grpc::Status;
using omnitest::polyglot::nexus::PersonService;

// Implementation of the PersonService gRPC interface
class PersonServiceImpl final : public PersonService::Service {
    // We will implement the RPC methods (CreatePerson, ReadAllPersons, etc.) here
};

void RunServer() {
    std::string server_address("0.0.0.0:50051");
    PersonServiceImpl service;

    ServerBuilder builder;
    builder.AddListeningPort(server_address, grpc::InsecureServerCredentials());
    builder.RegisterService(&service);
    
    std::unique_ptr<Server> server(builder.BuildAndStart());
    std::cout << "C++ Server listening on " << server_address << std::endl;
    server->Wait();
}

int main(int argc, char** argv) {
    RunServer();
    return 0;
}
