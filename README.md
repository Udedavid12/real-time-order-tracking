# Real-Time Order Tracking System

A backend service that simulates the core tracking pipeline of a delivery platform. It ingests high-frequency location updates from drivers and pushes them to connected clients in real time via WebSocket.

This project demonstrates layered architecture, geospatial data modeling, event-driven processing, and real-time communication using a modern Python stack.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Features](#features)
- [Getting Started](#getting-started)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Design Decisions](#design-decisions)
- [Future Improvements](#future-improvements)

---

## Overview

Delivery platforms must track thousands of drivers in real time while keeping data consistent and available. This project implements a simplified version of that pipeline:

1. Drivers send location updates to a REST endpoint.
2. Each update is validated and stored in PostgreSQL with PostGIS.
3. The API enqueues the update to SQS and returns immediately.
4. A separate worker consumes the message, updates the Redis cache, and broadcasts to WebSocket subscribers.
5. Historical positions remain queryable for geospatial searches.

The goal is not to replicate a production system in full, but to demonstrate the architectural patterns that make such a system reliable.

---

## Architecture

```
                    ┌──────────────────┐
                    │   Driver         │
                    │   (Client)       │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐     ┌─────────────────┐
                    │   REST API       │────▶│   PostgreSQL    │
                    │   (FastAPI)      │     │   + PostGIS     │
                    └────────┬─────────┘     └─────────────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │   Message Queue  │
                    │   (AWS SQS)      │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐     ┌─────────────────┐
                    │   Worker         │────▶│   Redis Cache   │
                    │   (Consumer)     │     │   (Latest Pos)  │
                    └────────┬─────────┘     └─────────────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │   WebSocket      │
                    │   (Connected     │
                    │    Clients)      │
                    └──────────────────┘
```

---

## Tech Stack

| Layer | Technology |
| :--- | :--- |
| Language | Python 3.12 |
| Web Framework | FastAPI |
| Database | PostgreSQL with PostGIS |
| Cache | Redis |
| Message Queue | AWS SQS (via LocalStack locally) |
| Real-Time Transport | WebSocket |
| Containerization | Docker, Docker Compose |
| Testing | pytest |

---

## Features

- High-frequency location ingestion via a dedicated REST endpoint
- Event-driven processing with SQS and a dedicated worker
- Real-time push to clients over WebSocket
- Geospatial queries using PostGIS for proximity and radius searches
- Redis read-through cache for the latest known driver position
- Layered architecture (routers → services → repositories)
- Versioned schema migrations with Alembic
- Containerized 5-service stack with Docker Compose
- Automated tests with per-test database isolation

---

## Getting Started

### Prerequisites

- Docker Desktop
- Git

### Installation

Clone the repository:

```bash
git clone https://github.com/Udedavid12/real-time-order-tracking.git
cd real-time-order-tracking
```

Copy the environment template:

```bash
cp .env.example .env
```

Build and start the full stack:

```bash
docker compose up -d --build
```

Run the database migrations:

```bash
docker exec -it order_tracking_api alembic upgrade head
```

The API is now available at:

- **API:** http://localhost:8000
- **Interactive docs:** http://localhost:8000/docs

### Environment Variables

See `.env.example` for all required variables. The `.env` file is git-ignored and should never be committed.

### Stopping

```bash
docker compose down
```

To wipe all data and start fresh:

```bash
docker compose down -v
```

---

## API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Health check |
| `POST` | `/api/v1/drivers` | Create a driver |
| `GET` | `/api/v1/drivers` | List all drivers |
| `GET` | `/api/v1/drivers/{driver_id}` | Get a driver by ID |
| `POST` | `/api/v1/locations` | Record a driver location update |
| `GET` | `/api/v1/locations/{driver_id}/latest` | Get latest location for a driver |
| `GET` | `/api/v1/locations/{driver_id}/history` | Get location history |
| `GET` | `/api/v1/locations/nearby` | Find drivers within a radius |
| `WS` | `/ws/tracking/{driver_id}` | Subscribe to real-time updates |

---

## Testing

Run the test suite:

```bash
pytest tests/ -v
```

The tests use a dedicated test database (`order_tracking_test`) with per-test transaction rollback, so running tests never affects development data.

---

## Design Decisions

**Layered architecture.** Controllers handle HTTP, services contain business logic, and repositories own data access. This separation keeps logic testable and interchangeable.

**PostGIS for geospatial queries.** Radius searches use `ST_DWithin` with a GIST index, allowing sub-second queries across thousands of locations.

**Read-through Redis cache.** The latest-location endpoint is read-heavy and changes slowly. Caching reduces database load on the hot path.

**SQS for async processing.** The API returns immediately after writing to Postgres and enqueuing. A separate worker handles cache updates and WebSocket broadcasts, so a slow subscriber can't slow down the API.

**Alembic for migrations.** Schema changes are versioned and committed to the repository, matching how production teams manage databases.

---

## Future Improvements

- Authentication and authorization for drivers and clients
- Dead-letter queue for messages that fail repeatedly
- Batching of location updates to reduce HTTP overhead
- Prometheus metrics and Grafana dashboards
- Deployment to real AWS with Terraform
- Horizontal scaling for WebSocket connections using Redis Pub/Sub

---
