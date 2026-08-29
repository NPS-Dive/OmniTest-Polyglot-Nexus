// ============================================================================
// File: src/infrastructure/telemetry/Otel.hpp
// Purpose: Composition-root hook for OpenTelemetry. Full C++ OTEL SDK is
//          optional; this stub records intent when a collector is configured.
// SOLID role: SRP — telemetry bootstrap only. Call from main, not from SQL.
// Dependencies: getenv. Endpoint: OTEL_EXPORTER_OTLP_ENDPOINT.
// ============================================================================

#pragma once

#include <cstdlib>
#include <iostream>
#include <string>

namespace infrastructure {
namespace telemetry {

/**
 * @class Otel
 * @brief Lightweight OTLP presence check used until the C++ SDK is wired.
 *
 * When OTEL_EXPORTER_OTLP_ENDPOINT is set, we log that traces would be
 * exported there. When unset, the service stays silent (local/dev default).
 */
class Otel {
public:
    /**
     * @brief Read OTEL_EXPORTER_OTLP_ENDPOINT once at process start.
     *
     * Does not throw: a missing collector must not block gRPC startup.
     */
    static void Initialize() {
        const char* endpoint = std::getenv("OTEL_EXPORTER_OTLP_ENDPOINT");
        if (endpoint != nullptr && endpoint[0] != '\0') {
            std::cout << "[otel] OTLP exporter configured at " << endpoint
                      << " (stub: C++ SDK not linked; endpoint is logged only)"
                      << std::endl;
        } else {
            std::cout << "[otel] OTEL_EXPORTER_OTLP_ENDPOINT unset; telemetry stub idle"
                      << std::endl;
        }
    }
};

}  // namespace telemetry
}  // namespace infrastructure
