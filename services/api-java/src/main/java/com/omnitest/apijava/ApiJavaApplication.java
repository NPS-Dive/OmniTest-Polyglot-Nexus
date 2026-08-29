package com.omnitest.apijava;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class ApiJavaApplication {
    public static void main(String[] args) {
        SpringApplication.run(ApiJavaApplication.class, args);
        System.out.println("Java gRPC Service is up and running!");
    }
}
