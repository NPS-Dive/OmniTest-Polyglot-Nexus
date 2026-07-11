#pragma once
#include <string>

namespace domain {

/**
 * @class Person
 * @brief Domain Entity representing a Person.
 * 
 * Single Responsibility Principle (SRP): This struct only holds the data 
 * state of a Person in the core domain, independent of gRPC or the Database.
 */
struct Person {
    std::string id;
    std::string national_id;
    std::string first_name;
    std::string last_name;
    int age;
    std::string gender; // Using 'gender' to align with previous entity fixes
};

} // namespace domain
