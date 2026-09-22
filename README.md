# Real-Time Order Tracking System

A backend service that simulates the core tracking pipeline of a delivery platform. It ingests high-frequency location updates from drivers and pushes them to connected clients in real time via WebSocket.

This project demonstrates reliable message delivery, geospatial data modeling, and scalable write handling using a modern Python stack.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Features](#features)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Environment Variables](#environment-variables)
  - [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Design Decisions](#design-decisions)
- [Future Improvements](#future-improvements)
- [License](#license)

---

## Overview

Delivery platforms must track thousands of drivers in real time while keeping data consistent and available. This project implements a simplified version of that pipeline:

1. Drivers send location updates to a REST endpoint at high frequency.
2. Each update is validated, stored, and published to a message queue.
3. A consumer processes the update and pushes it to subscribed clients over WebSocket.
4. The latest known position is cached in Redis for fast reads.
5. Historical positions are stored in PostgreSQL with PostGIS for spatial queries.

The goal is not to replicate a production system in full, but to demonstrate the architectural patterns that make such a system reliable.

---

## Architecture
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
                    │   Consumer       │────▶│   Redis Cache   │
                    │   (Worker)       │     │   (Latest Pos)  │
                    └────────┬─────────┘     └─────────────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │   WebSocket      │
                    │   (Connected     │
                    │    Clients)      │
                    └──────────────────┘

---

## Tech Stack

| Layer | Technology |
| :--- | :--- |
| Language | Python 3.11+ |
| Web Framework | FastAPI |
| Database | PostgreSQL with PostGIS |
| Cache | Redis |
| Message Queue | AWS SQS |
| Real-Time Transport | WebSocket |
| Containerization | Docker, Docker Compose |
| Testing | pytest, pytest-asyncio |

---

## Features

- High-frequency location ingestion via a dedicated REST endpoint
- Reliable message delivery using AWS SQS with a dead-letter queue
- Real-time push to clients over WebSocket
- Geospatial queries using PostGIS for proximity and radius searches
- Redis caching of the latest known driver position to reduce database load
- Time-partitioned storage for historical location data
- Structured logging and error handling
- Containerized development environment with Docker Compose

---

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Docker and Docker Compose
- An AWS account with SQS access (or LocalStack for local development)
- Git

### Installation

Clone the repository:

```bash
git clone https://github.com/YourUsername/real-time-order-tracking.git
cd real-time-order-tracking
