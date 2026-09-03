// ============================================================================
// File: src/infrastructure/telemetry/Otel.hpp
// Purpose: OTLP presence log plus a host Prometheus /metrics fallback.
//          Full C++ OTEL SDK is optional on Windows; Grafana still needs a
//          series, so we expose opn_rpc_server_duration_milliseconds_* on
//          METRICS_PORT (default 15051) for Prometheus host scrape.
// SOLID role: SRP — telemetry bootstrap + in-process histogram only.
// ============================================================================

#pragma once

#include <atomic>
#include <chrono>
#include <cstdlib>
#include <iostream>
#include <mutex>
#include <sstream>
#include <string>
#include <thread>
#include <vector>

#ifdef _WIN32
#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
#include <winsock2.h>
#include <ws2tcpip.h>
#pragma comment(lib, "ws2_32.lib")
#else
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <unistd.h>
#endif

namespace infrastructure {
namespace telemetry {

/**
 * @class Otel
 * @brief In-process histogram + optional /metrics HTTP listener (C++ SDK fallback).
 */
class Otel {
public:
    /**
     * @brief Log OTLP endpoint intent and start the Prometheus scrape listener.
     */
    static void Initialize() {
        const char* endpoint = std::getenv("OTEL_EXPORTER_OTLP_ENDPOINT");
        if (endpoint != nullptr && endpoint[0] != '\0') {
            std::cout << "[otel] OTLP exporter configured at " << endpoint
                      << " (C++ SDK not linked; host /metrics fallback is active)"
                      << std::endl;
        } else {
            std::cout << "[otel] OTEL_EXPORTER_OTLP_ENDPOINT unset; host /metrics still available"
                      << std::endl;
        }
        StartMetricsServer();
    }

    /**
     * @brief Record one RPC duration in milliseconds for the Grafana RED series.
     */
    static void Record(double duration_ms, const char* status_code) {
        (void)status_code;
        Histogram().Observe(duration_ms);
    }

private:
    static constexpr double kBuckets[] = {5, 10, 25, 50, 100, 250, 500, 1000, 2500, 5000};

    class Hist {
    public:
        Hist() : counts_(11, 0), sum_(0), count_(0) {}

        void Observe(double value) {
            std::lock_guard<std::mutex> lock(mu_);
            for (size_t i = 0; i < 10; ++i) {
                if (value <= kBuckets[i]) {
                    counts_[i] += 1;
                }
            }
            counts_[10] += 1;  // +Inf
            sum_ += value;
            count_ += 1;
        }

        std::string Render() const {
            std::lock_guard<std::mutex> lock(mu_);
            std::ostringstream os;
            os << "# HELP opn_rpc_server_duration_milliseconds gRPC unary duration\n";
            os << "# TYPE opn_rpc_server_duration_milliseconds histogram\n";
            for (size_t i = 0; i < 10; ++i) {
                os << "opn_rpc_server_duration_milliseconds_bucket{service_name=\"grpc-cpp\",le=\""
                   << kBuckets[i] << "\"} " << counts_[i] << "\n";
            }
            os << "opn_rpc_server_duration_milliseconds_bucket{service_name=\"grpc-cpp\",le=\"+Inf\"} "
               << counts_[10] << "\n";
            os << "opn_rpc_server_duration_milliseconds_sum{service_name=\"grpc-cpp\"} " << sum_ << "\n";
            os << "opn_rpc_server_duration_milliseconds_count{service_name=\"grpc-cpp\"} " << count_ << "\n";
            return os.str();
        }

    private:
        mutable std::mutex mu_;
        std::vector<long long> counts_;
        double sum_;
        long long count_;
    };

    static Hist& Histogram() {
        static Hist hist;
        return hist;
    }

    static void StartMetricsServer() {
        static std::once_flag once;
        std::call_once(once, []() {
            std::thread([]() { Listen(); }).detach();
        });
    }

    static int MetricsPort() {
        const char* raw = std::getenv("METRICS_PORT");
        if (raw == nullptr || raw[0] == '\0') {
            return 15051;
        }
        return std::atoi(raw);
    }

    static void Listen() {
#ifdef _WIN32
        WSADATA wsa;
        if (WSAStartup(MAKEWORD(2, 2), &wsa) != 0) {
            std::cerr << "[otel] WSAStartup failed; /metrics disabled\n";
            return;
        }
#endif
        const int port = MetricsPort();
#ifdef _WIN32
        SOCKET sock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
        if (sock == INVALID_SOCKET) {
            return;
        }
        BOOL reuse = TRUE;
        setsockopt(sock, SOL_SOCKET, SO_REUSEADDR, reinterpret_cast<const char*>(&reuse), sizeof(reuse));
#else
        int sock = socket(AF_INET, SOCK_STREAM, 0);
        if (sock < 0) {
            return;
        }
        int reuse = 1;
        setsockopt(sock, SOL_SOCKET, SO_REUSEADDR, &reuse, sizeof(reuse));
#endif
        sockaddr_in addr{};
        addr.sin_family = AF_INET;
        addr.sin_addr.s_addr = htonl(INADDR_ANY);
        addr.sin_port = htons(static_cast<unsigned short>(port));
        if (bind(sock, reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) != 0) {
            std::cerr << "[otel] bind :" << port << " failed\n";
            return;
        }
        listen(sock, 8);
        std::cout << "[otel] Prometheus /metrics on 0.0.0.0:" << port << std::endl;
        for (;;) {
#ifdef _WIN32
            SOCKET client = accept(sock, nullptr, nullptr);
            if (client == INVALID_SOCKET) {
                continue;
            }
#else
            int client = accept(sock, nullptr, nullptr);
            if (client < 0) {
                continue;
            }
#endif
            const std::string body = Histogram().Render();
            std::ostringstream resp;
            resp << "HTTP/1.1 200 OK\r\nContent-Type: text/plain; version=0.0.4\r\nContent-Length: "
                 << body.size() << "\r\nConnection: close\r\n\r\n"
                 << body;
            const std::string out = resp.str();
#ifdef _WIN32
            send(client, out.data(), static_cast<int>(out.size()), 0);
            closesocket(client);
#else
            send(client, out.data(), out.size(), 0);
            close(client);
#endif
        }
    }
};

/**
 * @class RpcTimer
 * @brief RAII timer — record duration when an RPC method returns.
 */
class RpcTimer {
public:
    RpcTimer() : start_(std::chrono::steady_clock::now()) {}
    ~RpcTimer() {
        const auto ms = std::chrono::duration<double, std::milli>(
                            std::chrono::steady_clock::now() - start_)
                            .count();
        Otel::Record(ms, "0");
    }

private:
    std::chrono::steady_clock::time_point start_;
};

}  // namespace telemetry
}  // namespace infrastructure
