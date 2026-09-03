// ============================================================================
// File: services/grpc-go/cmd/server/main.go
// Purpose: Composition root — env → telemetry → pool → repository → gRPC server.
// SOLID: DIP — main is the only place that constructs concrete adapters.
//         Domain and presentation never import pgx or listen sockets.
// Dependencies: config, telemetry, db, presentation/grpc, grpc reflection.
// ============================================================================

// Package main is the composition root for the Go Person gRPC server.
package main

import (
	"context"
	"log"
	"net"
	"os"
	"os/signal"
	"syscall"
	"time"

	"go.opentelemetry.io/contrib/instrumentation/google.golang.org/grpc/otelgrpc"
	"google.golang.org/grpc"
	"google.golang.org/grpc/reflection"

	"github.com/omnitest/grpc-go/internal/config"
	personpb "github.com/omnitest/grpc-go/internal/gen"
	"github.com/omnitest/grpc-go/internal/infrastructure/db"
	"github.com/omnitest/grpc-go/internal/infrastructure/telemetry"
	grpcsvc "github.com/omnitest/grpc-go/internal/presentation/grpc"
)

// main wires the process and blocks until SIGINT/SIGTERM.
func main() {
	cfg := config.Load()
	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()

	shutdownTel, err := telemetry.Init(ctx, cfg.ServiceName)
	if err != nil {
		log.Fatalf("telemetry init: %v", err)
	}
	defer func() {
		c, cancel := context.WithTimeout(context.Background(), 5*time.Second)
		defer cancel()
		if err := shutdownTel(c); err != nil {
			log.Printf("telemetry shutdown: %v", err)
		}
	}()

	pool, err := db.Connect(ctx, cfg.PostgresDSN())
	if err != nil {
		log.Fatalf("postgres: %v", err)
	}
	defer pool.Close()

	repo := db.NewPostgresPersonRepository(pool)
	svc := grpcsvc.NewServer(repo)

	var opts []grpc.ServerOption
	opts = append(opts, grpc.ChainUnaryInterceptor(telemetry.UnaryMetricsInterceptor()))
	if telemetry.Enabled() {
		// Stats handler (not unary interceptor) is the current otelgrpc API.
		opts = append(opts, grpc.StatsHandler(otelgrpc.NewServerHandler()))
	}
	server := grpc.NewServer(opts...)
	personpb.RegisterPersonServiceServer(server, svc)
	reflection.Register(server)

	lis, err := net.Listen("tcp", cfg.ListenAddr())
	if err != nil {
		log.Fatalf("listen %s: %v", cfg.ListenAddr(), err)
	}

	go func() {
		<-ctx.Done()
		log.Printf("shutting down gRPC on %s", cfg.ListenAddr())
		stopped := make(chan struct{})
		go func() {
			server.GracefulStop()
			close(stopped)
		}()
		select {
		case <-stopped:
		case <-time.After(10 * time.Second):
			server.Stop()
		}
	}()

	log.Printf("grpc-go PersonService listening on %s (table=persons_golang, otel=%v)", cfg.ListenAddr(), telemetry.Enabled())
	if err := server.Serve(lis); err != nil {
		log.Fatalf("serve: %v", err)
	}
}
