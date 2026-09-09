```markdown
# Bookstore Inventory API

REST API for bookstore inventory management built with **Django**, **Django REST Framework**, PostgreSQL/Supabase and containerized deployment.

The application provides inventory management for books, ISBN validation, price calculation using external exchange rates, API documentation through OpenAPI/Swagger, and cloud deployment using Google Cloud Run.

---

# Technology Stack

| Technology | Version / Service |
|---|---|
| Python | 3.10+ |
| Django | 4.2 |
| Django REST Framework | Latest compatible |
| Database | PostgreSQL |
| Cloud Database | Supabase PostgreSQL |
| Database Connectivity | Supabase Connection Pooler |
| WSGI Server | Gunicorn |
| Containerization | Docker & Docker Compose |
| Cloud Deployment | Google Cloud Run |
| API Documentation | drf-spectacular (Swagger/OpenAPI) |

---

# Production Deployment

The API is deployed publicly using **Google Cloud Run**.

## Production API

```

[https://bookstore-inventory-api-546900969932.europe-west2.run.app](https://bookstore-inventory-api-546900969932.europe-west2.run.app)

```

## Swagger UI

Interactive API documentation:

```

[https://bookstore-inventory-api-546900969932.europe-west2.run.app/api/docs/](https://bookstore-inventory-api-546900969932.europe-west2.run.app/api/docs/)

````

---

# Features

- Complete CRUD operations for books.
- PostgreSQL-only architecture.
- Supabase PostgreSQL cloud database integration.
- Containerized execution using Docker.
- Automatic migrations during local Docker startup.
- Global pagination using Django REST Framework.
- ISBN normalization and uniqueness validation.
- Database constraints for:
  - Positive book cost.
  - Non-negative stock quantity.
  - Unique ISBN values.
- Category search endpoint.
- Low-stock filtering endpoint.
- External USD exchange-rate integration.
- Suggested selling price calculation with a strict 40% margin.
- Swagger/OpenAPI documentation.
- Structured JSON error handling.

---

# Requirements

Before running the project locally, install:

- Python 3.10+
- Docker
- Docker Compose
- Git

The application requires a PostgreSQL-compatible database.

The recommended database service is:

**Supabase PostgreSQL**

---

# Environment Configuration

Create your local environment file from the provided example:

```bash
cp .env.example .env
````

Configure the required variables.

Example:

```env
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# ============================================================
# SUPABASE POSTGRESQL
# Shared / Session Pooler
# ============================================================

DB_NAME=postgres
DB_USER=postgres.<project-ref>
DB_PASSWORD=...
DB_HOST=aws-0-eu-west-2.pooler.supabase.com
DB_PORT=5432
DB_SSLMODE=require

DB_CONN_MAX_AGE=30
DB_CONN_HEALTH_CHECKS=True
DB_CONNECT_TIMEOUT=10

# ============================================================
# BUSINESS CONFIGURATION
# ============================================================

LOCAL_CURRENCY=VES
DEFAULT_EXCHANGE_RATE=1.0

# ============================================================
# EXCHANGE RATE API
# ============================================================

EXCHANGE_RATE_API_URL=https://api.exchangerate-api.com/v4/latest/USD
EXCHANGE_RATE_TIMEOUT=5
```

---

# Database Configuration

The project uses **Supabase PostgreSQL through the official Supabase connection pooler**.

The production database connection is configured using the Shared/Session Pooler:

```
Host:
aws-0-eu-west-2.pooler.supabase.com

Port:
5432

Database:
postgres
```

The pooler is part of the application database architecture and is configured through environment variables.

---

# Installation and Local Execution

## 1. Clone repository

```bash
git clone <repository-url>

cd bookstore-inventory-api
```

---

## 2. Configure environment variables

Create the environment file:

```bash
cp .env.example .env
```

Update the Supabase PostgreSQL credentials.

---

## 3. Run application with Docker Compose

Build and start the application:

```bash
docker compose up --build
```

The Docker startup process performs:

1. Database migrations.
2. Gunicorn startup.
3. API exposure on port `8000`.

For local Docker execution, migrations are executed automatically before starting Gunicorn.

The local API will be available at:

```
http://localhost:8000
```

---

# API Documentation (Swagger / OpenAPI)

The project uses **drf-spectacular** for automatic OpenAPI documentation.

## Local Swagger UI

```
http://localhost:8000/api/docs/
```

## Local OpenAPI Schema

```
http://localhost:8000/api/schema/
```

## Local Redoc

```
http://localhost:8000/api/redoc/
```

Production Swagger:

```
https://bookstore-inventory-api-546900969932.europe-west2.run.app/api/docs/
```

---

# Postman Collection

The repository includes the Postman collection and production environment configuration under:

```
postman/
```

Files included:

```
postman/
├── bookstore-inventory-api.postman_collection.json
└── bookstore-inventory-api-production.postman_environment.json
```

The environment file is already configured with the production variable:

```text
base_url
```

with the Cloud Run deployment URL:

```
https://bookstore-inventory-api-546900969932.europe-west2.run.app
```

The collection can be imported directly into Postman together with the production environment to execute API validations without requiring a local application execution.

---

# API Endpoints

## Books CRUD

| Method | Endpoint      | Description                |
| ------ | ------------- | -------------------------- |
| GET    | `/books`      | List books with pagination |
| POST   | `/books`      | Create book                |
| GET    | `/books/{id}` | Retrieve book              |
| PUT    | `/books/{id}` | Full update                |
| PATCH  | `/books/{id}` | Partial update             |
| DELETE | `/books/{id}` | Delete book                |

---

# Pagination

The list endpoint uses Django REST Framework pagination.

Example:

```
GET /books?limit=10&offset=0
```

Parameters:

| Parameter | Description                |
| --------- | -------------------------- |
| limit     | Number of records returned |
| offset    | Initial record position    |

---

# Search and Filters

## Search by category

Endpoint:

```
GET /books/search?category={category}
```

Example:

```
GET /books/search?category=Literatura Clasica
```

---

## Low stock filter

Endpoint:

```
GET /books/low-stock?threshold=10
```

Returns books with stock quantity equal or below the configured threshold.

---

# Price Calculation Endpoint

## Calculate suggested selling price

Endpoint:

```
POST /books/{id}/calculate-price
```

The calculation process:

1. Reads the book `cost_usd`.
2. Retrieves the current USD exchange rate.
3. Converts the cost to local currency.
4. Applies a 40% profit margin.
5. Updates `selling_price_local`.
6. Returns the calculation details.

Formula:

```
selling_price_local = cost_usd * exchange_rate * 1.40
```

Example response:

```json
{
  "book_id": 1,
  "cost_usd": 15.99,
  "exchange_rate": 0.85,
  "cost_local": 13.59,
  "margin_percentage": 40,
  "selling_price_local": 19.03,
  "currency": "EUR",
  "calculation_timestamp": "2026-09-08T20:00:00Z"
}
```

If the external exchange-rate service is unavailable, the application uses:

```
DEFAULT_EXCHANGE_RATE
```

to keep the service available.

---

# Business Rules

## ISBN Validation

The API applies ISBN normalization before persistence.

Rules:

* ISBN must contain 10 or 13 digits.
* Formatted and unformatted ISBN values are normalized.
* Duplicate ISBN values are rejected.

Example:

Input:

```
978-84-376-0494-7
```

Stored value:

```
9788437604947
```

---

## Book Cost Validation

Rule:

```
cost_usd > 0
```

Values equal to or below zero are rejected.

---

## Stock Validation

Rule:

```
stock_quantity >= 0
```

Negative inventory values are not allowed.

---

# Production Configuration Notes

For cloud deployment:

* Set `DJANGO_DEBUG=False`.
* Use a secure `DJANGO_SECRET_KEY`.
* Store credentials using cloud secret management.
* Do not commit `.env` files with real credentials.
* Keep Supabase SSL enabled.
* Configure production environment variables through the cloud provider.

---

# Project Structure

```
bookstore-inventory-api/

├── core/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── inventory/
│   ├── models.py
│   ├── serializers.py
│   ├── services.py
│   ├── views.py
│   └── urls.py
│
├── postman/
│   ├── bookstore-inventory-api.postman_collection.json
│   └── bookstore-inventory-api-production.postman_environment.json
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```
