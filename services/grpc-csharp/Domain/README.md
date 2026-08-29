# Domain (grpc-csharp)

`Person`, `PersonFilter`, `IPersonRepository`. EF `PersonEntity` is the persistence shape; the gRPC service must use the interface, not `AppDbContext`.
