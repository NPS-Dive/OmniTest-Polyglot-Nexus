// ============================================================================
// File: services/api-java/src/main/java/com/omnitest/apijava/ApiJavaApplication.java
// Purpose: Spring Boot composition root. Wires JDBC, gRPC, and optional OTEL.
// SOLID: SRP — bootstrap only. No SQL and no proto mapping live here.
// Dependencies: Spring Boot autoconfig. JPA is intentionally not on the classpath.
// ============================================================================

package com.omnitest.apijava;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * Entry point for the Java Person gRPC service ({@code persons_java}, port 50053).
 */
@SpringBootApplication
public class ApiJavaApplication {

    public static void main(String[] args) {
        SpringApplication.run(ApiJavaApplication.class, args);
    }
}
