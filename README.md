# FastAPI Microservices Project

A production-ready FastAPI microservices template with authentication, user management, database integration, and comprehensive logging.

## Features

- ✅ **FastAPI Framework** - Modern, fast web framework for building APIs
- ✅ **JWT Authentication** - Secure token-based authentication
- ✅ **SQLAlchemy ORM** - Database modeling and querying
- ✅ **PostgreSQL Integration** - Reliable relational database
- ✅ **Request Logging** - Comprehensive API request/response logging
- ✅ **Request Context Middleware** - Request ID tracking across services
- ✅ **Configuration Management** - Environment-based settings with `.env` support
- ✅ **Health Check Endpoint** - Service health monitoring
- ✅ **Error Handling** - Global exception handling with structured responses
- ✅ **Pydantic Schemas** - Data validation and serialization
- ✅ **Repository Pattern** - Clean data access layer

## Project Structure

```
Python-FastAPI-Microservices/
├── main.py                 # Application entry point
├── pyproject.toml          # Project dependencies and configuration
├── README.md               # This file
├── app/
│   ├── __init__.py
│   ├── main.py             # FastAPI app creation and setup
│   ├── api/
│   │   ├── router.py       # Main API router (routes aggregation)
│   │   ├── dependencies/
│   │   │   └── auth.py     # Authentication dependencies (JWT validation)
│   │   └── routes/
│   │       ├── auth.py     # Authentication routes (login, register)
│   │       ├── health.py   # Health check endpoint
│   │       └── users.py    # User management routes
│   ├── core/
│   │   ├── config.py       # Configuration and settings
│   │   ├── logging.py      # Logging configuration
│   │   ├── middleware.py   # Request context middleware
│   │   ├── request_logging.py # API request/response logging
│   │   └── security.py     # Security utilities (JWT, hashing)
│   ├── db/
│   │   ├── base.py         # Database base and metadata
│   │   └── session.py      # Database session management
│   ├── entities/
│   │   └── user.py         # User database model (SQLAlchemy)
│   ├── repositories/
│   │   └── user_repository.py # User data access layer
│   ├── schemas/
│   │   ├── auth.py         # Authentication request/response schemas
│   │   └── user.py         # User request/response schemas
│   └── services/
│       ├── auth_service.py # Authentication business logic
│       └── user_service.py # User management business logic
├── scripts/
│   └── sql/                # Database migration scripts
└── tests/
    └── test_api.py         # API integration tests
```

## Prerequisites

- **Python 3.13+**
- **PostgreSQL** (or modify connection for another database)
- **pip** or **poetry** (package manager)

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Python-FastAPI-Microservices
```

### 2. Create Virtual Environment

```bash
# Using venv
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -e .
```

Or with poetry:
```bash
poetry install
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
APP_ENVIRONMENT=development
APP_DEBUG=true
APP_APP_NAME=FastAPI Microservice
APP_LOG_LEVEL=INFO
APP_DATABASE_URL=postgresql://user:password@localhost:5432/microservice_db
APP_DATABASE_SCHEMA=migros_store
APP_JWT_SECRET_KEY=your-secret-key-here-change-in-production
APP_JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
APP_API_REQUEST_LOGGING_ENABLED=true
```

**Important Security Notes:**
- Change `APP_JWT_SECRET_KEY` to a strong random key in production
- Use environment-specific `.env` files (dev, staging, production)
- Never commit `.env` files to version control

### 5. Set Up Database

Create the PostgreSQL database:

```sql
CREATE DATABASE microservice_db;
```

Run migration scripts (if available in `scripts/sql/`):

```bash
psql -U user -d microservice_db -f scripts/sql/init.sql
```

### Migration Helpers (PowerShell)

Use the helper script for code-first Alembic migrations:

```powershell
# Apply latest migrations
.\scripts\migrate.ps1 up

# Create migration file
.\scripts\migrate.ps1 new "create orders table"

# Create migration with model diff
.\scripts\migrate.ps1 new "add orders status" --autogenerate

# Roll back one revision
.\scripts\migrate.ps1 down

# Show migration status/history
.\scripts\migrate.ps1 current
.\scripts\migrate.ps1 history
```

### Seed Catalog Data

```powershell
.\.venv\Scripts\python.exe scripts\seed_catalog.py
```

The script is idempotent, so running it multiple times updates seed rows instead of creating duplicates.

### Seed Cart Data

```powershell
.\.venv\Scripts\python.exe scripts\seed_cart.py
```

Run this after catalog seed data, because Cart seed references an existing `product_variant`.

### Seed Payment Method Data

```powershell
.\.venv\Scripts\python.exe scripts\seed_payment_method.py
```

Run this after user data is available. The script creates a fallback user `id=1` when needed.

### Seed Payment Intent Data

```powershell
.\.venv\Scripts\python.exe scripts\seed_payment_intent.py
```

Run this after payment method/order migrations are applied. The script upserts user, payment method, catalog, order, and linked payment intent data.

## Running the Application

### Development Mode

```bash
# Run with uvicorn auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
# Run without auto-reload
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at: `http://localhost:8000`

### Interactive API Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## API Endpoints

### Health Check
```
GET /health
```
Check service health status (authentication required).

### Authentication
```
POST /auth/login
- body: { "email": "user@example.com", "password": "password" }
- response: { "access_token": "...", "token_type": "bearer" }

POST /auth/register
- body: { "email": "user@example.com", "password": "password", "full_name": "..." }
- response: { "id": 1, "email": "...", "full_name": "..." }
```

### User Management
```
GET /users
- Get all users (requires authentication)
- response: [{ "id": 1, "email": "...", "full_name": "..." }]

GET /users/{user_id}
- Get specific user (requires authentication)
- response: { "id": 1, "email": "...", "full_name": "..." }

PUT /users/{user_id}
- Update user (requires authentication)
- body: { "full_name": "..." }
- response: { "id": 1, "email": "...", "full_name": "..." }
```

## Architecture

### Layered Architecture

1. **API Layer** (`app/api/`) - HTTP endpoints and request handling
2. **Service Layer** (`app/services/`) - Business logic
3. **Repository Layer** (`app/repositories/`) - Data access
4. **Database Layer** (`app/db/`) - ORM configuration and sessions
5. **Core Layer** (`app/core/`) - Cross-cutting concerns (logging, middleware, security)

### Key Design Patterns

- **Dependency Injection** - FastAPI's dependency system for loose coupling
- **Repository Pattern** - Abstract data access logic
- **Service Layer** - Encapsulate business logic
- **Middleware** - Global request/response handling (logging, context)
- **Configuration Management** - Environment-based settings

## Security

- **JWT Authentication** - Token-based API authentication
- **Password Hashing** - Secure password storage (see `app/core/security.py`)
- **Request Context** - Unique request IDs for tracing
- **Error Handling** - Generic error messages (no sensitive info leakage)
- **Environment Secrets** - Sensitive configuration via environment variables

## Configuration

Configuration is managed through `app/core/config.py` using Pydantic Settings:

| Setting | Default | Description |
|---------|---------|-------------|
| `app_name` | fastapi-microservice | Application name |
| `environment` | development | Environment (development, staging, production) |
| `debug` | true | Enable debug mode |
| `database_url` | - | PostgreSQL connection string |
| `jwt_secret_key` | change-me | Secret key for JWT (change in production!) |
| `jwt_access_token_expire_minutes` | 60 | Token expiration time |
| `log_level` | INFO | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `api_request_logging_enabled` | true | Enable API request/response logging |

## Testing

Run tests with:

```bash
pytest tests/
```

Or with coverage:

```bash
pytest tests/ --cov=app --cov-report=html
```

## Development Workflow

### Adding a New Endpoint

1. Create a route in `app/api/routes/` (e.g., `products.py`)
2. Define Pydantic schemas in `app/schemas/` (e.g., `product.py`)
3. Create a repository in `app/repositories/` (if needed)
4. Create a service in `app/services/` (if needed)
5. Include the router in `app/api/router.py`

### Adding a New Database Model

1. Create the model in `app/entities/` (e.g., `product.py`)
2. Create a repository in `app/repositories/` (e.g., `product_repository.py`)
3. Run database migrations

## Logging

The application includes:
- **Application Logging** - General logs in `app/core/logging.py`
- **Request Logging** - API request/response details in `app/core/request_logging.py`
- **Request Context** - Unique request IDs via middleware

Logs are configured based on `APP_LOG_LEVEL` setting.

## Troubleshooting

### Database Connection Error
```
sqlalchemy.exc.OperationalError: could not connect to server
```
- Verify PostgreSQL is running
- Check `APP_DATABASE_URL` in `.env`
- Ensure database exists

### JWT Token Errors
- Verify `APP_JWT_SECRET_KEY` matches between requests
- Check token expiration time
- Ensure `Authorization: Bearer <token>` header is present

### Import Errors
- Verify virtual environment is activated
- Run `pip install -e .` to install package
- Check PYTHONPATH includes project root

## Contributing

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Commit changes: `git commit -am 'Add feature'`
3. Push branch: `git push origin feature/my-feature`
4. Submit a pull request

## License

[Specify your license here, e.g., MIT, Apache 2.0]

## Support

For issues, questions, or suggestions, please open an issue in the repository.

---

**Happy coding!** 🚀
