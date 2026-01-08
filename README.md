# Hotel Booking System API

A layered FastAPI-based API for a hotel booking system, using SQLAlchemy with an SQLite database.

## Overview

This project began as the layered API example from ArjanCodes’ Domain Modeling & FastAPI module in The Software Designer Mindset. It has since been expanded to include production‑grade components:
- **Refactored & Updated**: Fixed deprecated method/attribute calls and refactored core sections for better maintainability.
- **Comprehensive Testing**: Added a robust testing suite covering business logic and API endpoints.
- **Environment-Based Configuration**: Credentials stay in `.env` files; supports different configurations per environment; Pydantic validates all settings on startup.
- **Health Checks**: Implemented liveness and readiness probe endpoints for monitoring and orchestration.
- **Custom Exceptions**: Developed a custom exception hierarchy for consistent, informative error handling.
- **Rate Limiting**: Integrated rate limiting and IP whitelisting to protect the API from abuse.
- **Query Validation & Pagination**: Robust validation of query parameters using FastAPI `Query`; implements standardized pagination and sorting for list endpoints.

Ultimately, the goal was to transform the initial prototype into a more mature, operationally sound application that reflects modern engineering standards.

### Key Features
- **Layered Architecture**: Clear separation of concerns between database models, business logic (operations), and API endpoints (routers).
- **FastAPI**: Modern, fast (high-performance) web framework for building APIs with Python.
- **SQLAlchemy**: Powerful SQL Toolkit and Object-Relational Mapper (ORM).
- **Pydantic**: Data validation and settings management using Python type annotations.
- **SQLite**: Lightweight, file-based database.

## Tech Stack

- **Language**: Python 3.10+
- **Framework**: FastAPI
- **Database**: SQLite (via SQLAlchemy ORM)
- **Validation**: Pydantic
- **Server**: Uvicorn
- **Testing**: Pytest / Unittest

## Project Structure

```text
.
├── hotel/
│   ├── db/                             # Database models and session management
│   │   ├── create_db.py                # Database initialization script
│   │   ├── db_interface.py             # Generic database interface
│   │   ├── engine.py                   # SQLAlchemy engine and session setup
│   │   ├── models.py                   # SQLAlchemy database models
│   │   └── sample_data.py              # Seed data for the database
│   ├── operations/                     # Business logic layer
│   │   ├── bookings.py                 # Booking-related operations
│   │   ├── customers.py                # Customer-related operations
│   │   ├── interface.py                # Interfaces for operations
│   │   ├── models.py                   # Pydantic models for data validation
│   │   └── rooms.py                    # Room-related operations
│   ├── routers/                        # FastAPI router definitions
│   │   ├── bookings.py                 # Booking API endpoints
│   │   ├── customers.py                # Customer API endpoints
│   │   ├── rooms.py                    # Room API endpoints
│   │   └── health.py                   # Health check endpoints
│   ├── middleware/                     # Middleware components
│   │   ├── exception_handlers.py       # Global exception handlers
│   │   ├── rate_limiter.py             # Rate limiting configuration
│   │   └── rate_limit_handlers.py      # Rate limit error handlers
│   ├── config.py                       # Configuration management with Pydantic settings
│   └── exceptions.py                   # Custom exception hierarchy
├── tests/                              # Test suite organized by type
│   ├── unit/                           # Unit tests (business logic, individual components)
│   │   └── test_bookings.py
│   ├── integration/                    # Integration tests (API endpoints, database)
│   │   └── test_complete_suite.py
│   ├── functional/                     # Functional/End-to-end tests
│   ├── test_exceptions.py              # Cross-cutting exception handling tests
│   ├── test_rate_limiting.py           # Infrastructure-level rate limiting tests
│   └── conftest.py                     # Shared pytest fixtures
├── main.py                             # Application entry point
├── requirements.txt                    # Project dependencies
├── Dockerfile                          # Docker configuration for containerization
├── .env.example                        # Template for environment variables
├── LICENSE                             # Project license
└── hotel.db                            # SQLite database file (generated)
```

## Requirements

Ensure you have Python 3.10 or higher installed.

The following packages are required:
- `fastapi`
- `sqlalchemy`
- `uvicorn`
- `pydantic`
- `pydantic-settings`
- `python-dotenv`
- `slowapi`
- `pytest`

## Setup and Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd layered-api
   ```

2. **Create a virtual environment**:
   - Windows:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```
   - Linux/macOS:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   - Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   - Edit `.env` to customize settings (optional - defaults work for development)

5. **Initialize the Database**:
   The database can be initialized with sample data. You can call `create_db` from `hotel.db.create_db`:
   ```bash
   python -c "from hotel.db.create_db import create_db; create_db('sqlite:///hotel.db')"
   ```

## Running the Application

### Option 1: Using uvicorn CLI (recommended for development)
   ```bash
   uvicorn main:app --reload
   ```

### Option 2: Direct Python execution
   ```bash
   python main.py
   ```

### Option 3: Using Docker
   ```bash
   # Build the image
   docker build -t hotel-api .

   # Run the container
   docker run -p 8000:8000 hotel-api
   ```

### Access the API
   - API Root: `http://127.0.0.1:8000/`
   - Interactive Docs (Swagger UI): `http://127.0.0.1:8000/docs`
   - Alternative Docs (Redoc): `http://127.0.0.1:8000/redoc`
   - Health Check: `http://127.0.0.1:8000/health/`
   - Readiness Check: `http://127.0.0.1:8000/health/ready`

## Running Tests

The project uses a structured testing approach with `pytest`:

- **Unit Tests**: Focus on individual components and business logic in `hotel/operations/`.
- **Integration Tests**: Verify the interaction between different layers, including API endpoints and database.
- **Cross-cutting Tests**: Cover infrastructure concerns like rate limiting and exception handling.

### Test Organization
- `tests/unit/`: Isolated tests for business logic.
- `tests/integration/`: API and database integration tests.
- `tests/functional/`: End-to-end scenarios (planned).
- `tests/*.py`: Cross-cutting and infrastructure tests.

### Execution Commands

- **Run all tests**:
   ```bash
   pytest
   ```

- **Run tests by category**:
   ```bash
   pytest tests/unit
   pytest tests/integration
   ```

- **Run specific test file**:
   ```bash
   pytest tests/unit/test_bookings.py
   ```

### Running Tests with Docker

You can run tests inside the Docker container. This ensures a consistent environment regardless of your local setup.

**Prerequisites:**
- [Docker](https://www.docker.com/products/docker-desktop/) must be installed and running.

```bash
# Build the image (if not already built)
docker build -t hotel-api .

# Run all tests
docker run --rm hotel-api pytest

# Run a specific category
docker run --rm hotel-api pytest tests/unit
```

#### Troubleshooting Docker Issues

If you encounter errors like `failed to connect to the docker API` or `the system cannot find the file specified`:

1.  **Check if Docker Desktop is running**: Ensure the Docker icon is visible in your system tray and indicates "Docker Desktop is running".
2.  **Verify Daemon Connectivity**: Run `docker info` or `docker version` in your terminal to check if the client can communicate with the daemon.
3.  **Check Context/Engine**: On Windows, if you are using WSL 2, ensure "Use the WSL 2 based engine" is checked in Docker Desktop settings.
4.  **Restart Docker**: Sometimes restarting Docker Desktop resolves intermittent pipe connection issues.

## Configuration

Configuration is managed through environment variables using Pydantic settings (see `hotel/config.py`). Settings can be configured via a `.env` file or environment variables.

### Available Configuration Options

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `sqlite:///hotel.db` |
| `HOST` | Server host address | `0.0.0.0` |
| `PORT` | Server port | `8000` |
| `RELOAD` | Enable auto-reload (development) | `False` |
| `APP_NAME` | Application name | `Hotel Management API` |
| `DEBUG` | Enable debug mode | `False` |

### Database Configuration Examples

**SQLite (default)**:
```bash
DATABASE_URL=sqlite:///hotel.db
```

**PostgreSQL**:
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/hotel_db
```

**MySQL**:
```bash
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/hotel_db
```

See `.env.example` for a complete configuration template.

## Rate Limiting

The API implements rate limiting to protect against abuse, DDoS attacks, and resource exhaustion.

### Configuration

Rate limits are configured via environment variables with different tiers for different operation types:

| Variable | Default | Description |
|----------|---------|-------------|
| `RATE_LIMIT_ENABLED` | `True` | Enable/disable rate limiting |
| `RATE_LIMIT_STORAGE` | `memory://` | Storage backend (memory for development) |
| `RATE_LIMIT_READ` | `100/minute` | Limit for GET operations (single resource) |
| `RATE_LIMIT_WRITE` | `20/minute` | Limit for POST/PATCH operations |
| `RATE_LIMIT_DELETE` | `10/minute` | Limit for DELETE operations |
| `RATE_LIMIT_SEARCH` | `50/minute` | Limit for search/filter operations |
| `RATE_LIMIT_WHITELIST` | `127.0.0.1,::1` | Comma-separated IPs exempt from limits |

### Rate Limit Tiers

Different endpoint types have different rate limits based on their resource intensity:

| Endpoint Type | Rate Limit | Examples |
|--------------|------------|----------|
| **Read Operations** | 100/minute | `GET /customer/{id}`, `GET /room/{id}` |
| **Search Operations** | 50/minute | `GET /customers`, `GET /rooms`, `GET /bookings` |
| **Write Operations** | 20/minute | `POST /customer`, `PATCH /customer/{id}` |
| **Delete Operations** | 10/minute | `DELETE /booking/{id}` |
| **Health Checks** | Unlimited | `GET /health/`, `GET /health/ready` |

### Rate Limit Response

When a rate limit is exceeded, the API returns HTTP 429 with details:

**Response (429 Too Many Requests):**
```json
{
  "error": "Rate Limit Exceeded",
  "message": "Too many requests. Please try again later.",
  "details": {
    "limit": "50 per 1 minute",
    "retry_after": 60,
    "endpoint": "/customers"
  }
}
```

**Response Headers:**
```
HTTP/1.1 429 Too Many Requests
Retry-After: 60
X-RateLimit-Limit: 50/minute
X-RateLimit-Remaining: 0
```

### Whitelist

Localhost (127.0.0.1) and IPv6 localhost (::1) are whitelisted by default. Additional IPs can be added via the `RATE_LIMIT_WHITELIST` environment variable.

### Benefits

- **DDoS Protection**: Prevents overwhelming the service with requests
- **Fair Resource Allocation**: Ensures all clients get fair access
- **Abuse Prevention**: Stops malicious scraping and brute force attacks
- **Graceful Degradation**: Service remains available under load
- **Client-Friendly**: Clear error messages with retry guidance

## Error Handling

The API implements a comprehensive custom exception system for consistent error responses across all endpoints.

### Exception Hierarchy

```
HotelAPIException (base)
├── ResourceNotFoundException
│   ├── BookingNotFoundException
│   ├── CustomerNotFoundException
│   └── RoomNotFoundException
├── ValidationException
│   ├── InvalidDateRangeException
│   └── InvalidDataException
├── DatabaseException
│   └── ForeignKeyViolationException
```

### HTTP Status Codes

| Exception Type | HTTP Status | Description |
|---------------|-------------|-------------|
| `ResourceNotFoundException` | 404 | Requested resource does not exist |
| `ValidationException` | 422 | Business logic validation failed |
| `DatabaseException` | 500 | Internal database error occurred |
| `ForeignKeyViolationException` | 422 | Referenced resource does not exist |

### Error Response Format

All errors return a consistent JSON structure:

**404 Not Found:**
```json
{
  "error": "Resource Not Found",
  "message": "Customer with ID 123 not found",
  "resource_type": "Customer",
  "resource_id": 123,
  "details": {}
}
```

**422 Validation Error:**
```json
{
  "error": "Validation Error",
  "message": "Check-out date must be after check-in date",
  "details": {
    "check_in": "2024-01-05",
    "check_out": "2024-01-05",
    "days": 0
  }
}
```

**500 Database Error:**
```json
{
  "error": "Database Error",
  "message": "An internal database error occurred",
  "details": {}
}
```

### Exception Layers

1. **Database Layer** (`hotel/db/`): Raises `ResourceNotFoundException` when entities are not found
2. **Operations Layer** (`hotel/operations/`): Raises business logic exceptions like `InvalidDateRangeException`
3. **Router Layer** (`hotel/routers/`): FastAPI automatically converts exceptions to HTTP responses
4. **Middleware Layer** (`hotel/middleware/exception_handlers.py`): Global handlers ensure consistent formatting

### Benefits

- **Consistent API Responses**: All errors follow the same structure
- **Better Debugging**: Clear exception types and detailed error messages
- **Type Safety**: Specific exception classes for different error scenarios
- **Monitoring**: Exception types enable better alerting and metrics
- **Client-Friendly**: Proper HTTP status codes and descriptive messages

## Health Check Endpoints

The API provides health check endpoints for monitoring and orchestration systems like Kubernetes, Docker, and load balancers.

### Liveness Probe
**Endpoint**: `GET /health/`

Basic health check that returns 200 OK if the service is running.

**Response**:
```json
{
  "status": "healthy",
  "service": "hotel-api"
}
```

**Kubernetes Configuration**:
```yaml
livenessProbe:
  httpGet:
    path: /health/
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 30
  timeoutSeconds: 5
  failureThreshold: 3
```

### Readiness Probe
**Endpoint**: `GET /health/ready`

Verifies the service can connect to the database. Returns 200 OK if ready, 503 Service Unavailable if not.

**Success Response** (200):
```json
{
  "status": "ready",
  "service": "hotel-api",
  "database": "connected"
}
```

**Failure Response** (503):
```json
{
  "detail": "Database not ready: <error message>"
}
```

**Kubernetes Configuration**:
```yaml
readinessProbe:
  httpGet:
    path: /health/ready
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3
```

### Docker Compose Healthcheck
```yaml
services:
  hotel-api:
    image: hotel-api:latest
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health/ready"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 10s
```

## Future Enhancements / TODO

### Logging & Monitoring (Planned)

Implement a production-grade logging and monitoring system to enhance observability and debugging.

**High-Level Goals:**
- **Structured Logging**: Implement JSON logging for better integration with aggregation tools.
- **Request Tracing**: Add unique request IDs to track requests across the application.
- **Performance Metrics**: Monitor response times and other key performance indicators.
- **Security & Auditing**: Log security-related events and mask sensitive data.
- **Error Observability**: Enhance exception logging with detailed context and stack traces.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
