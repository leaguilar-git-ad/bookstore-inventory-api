# Bookstore Inventory API

REST API built with Python, Django 4.x, Django REST Framework, PostgreSQL/Supabase, Docker and Gunicorn.

## Features

- CRUD for books.
- PostgreSQL only; no SQLite fallback.
- Global limit/offset pagination.
- ISBN normalization and uniqueness validation.
- Database constraints for positive cost, non-negative stock and canonical ISBN format.
- External USD exchange-rate integration with a configurable fallback rate.
- Suggested selling price using a strict 40% margin.
- Category search and low-stock endpoints.
- Consistent JSON handling for validation, not-found, database and unexpected errors.

## Requirements

- Python 3.10+
- PostgreSQL 14+ or Supabase PostgreSQL
- Docker / Docker Compose (optional)

## Environment

Copy the example file:

```bash
cp .env.example .env
```

Configure the Supabase connection values in `.env`.

Important variables:

```env
DJANGO_SECRET_KEY=...
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=...
DB_HOST=db.<project-ref>.supabase.co
DB_PORT=5432
DB_SSLMODE=require
LOCAL_CURRENCY=EUR
DEFAULT_EXCHANGE_RATE=1.0
```

If the deployment environment cannot reach the Supabase direct database hostname, use the Supabase connection-pooler host/port values instead.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

API base URL:

```text
http://localhost:8000/books
```

## Run with Docker Compose

```bash
cp .env.example .env
# Fill in the real Supabase credentials
docker compose up --build
```

The service starts on `http://localhost:8000` and applies Django migrations before Gunicorn starts.

## Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/books` | Paginated book list |
| POST | `/books` | Create a book |
| GET | `/books/{id}` | Retrieve a book |
| PUT | `/books/{id}` | Full update |
| PATCH | `/books/{id}` | Partial update provided by DRF |
| DELETE | `/books/{id}` | Delete a book |
| GET | `/books/search?category=Literatura%20Clásica` | Search by category |
| GET | `/books/low-stock?threshold=10` | Find books at or below threshold |
| POST | `/books/{id}/calculate-price` | Calculate and persist suggested local price |

Pagination uses DRF `LimitOffsetPagination`:

```text
GET /books?limit=10&offset=0
```

## Create book example

```bash
curl -X POST http://localhost:8000/books \
  -H "Content-Type: application/json" \
  -d '{
    "title": "El Quijote",
    "author": "Miguel de Cervantes",
    "isbn": "978-84-376-0494-7",
    "cost_usd": "15.99",
    "stock_quantity": 25,
    "category": "Literatura Clásica",
    "supplier_country": "ES"
  }'
```

The ISBN is normalized before persistence, so the stored value is `9788437604947`. This prevents formatted and unformatted variants of the same ISBN from bypassing the unique constraint.

## Calculate price example

```bash
curl -X POST http://localhost:8000/books/1/calculate-price
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

Formula:

```text
selling_price_local = cost_usd * exchange_rate * 1.40
```

If the exchange-rate API is unavailable, returns an invalid payload, times out or the requested currency is absent, the service logs the failure and uses `DEFAULT_EXCHANGE_RATE` instead of collapsing the request.

## Production notes

- Set `DJANGO_DEBUG=False`.
- Use a strong `DJANGO_SECRET_KEY`.
- Set `DJANGO_ALLOWED_HOSTS` to the public API hostname.
- Keep Supabase credentials only in the cloud provider's secret/environment settings.
- Keep `DB_SSLMODE=require` for Supabase.
- Run migrations as a release/pre-deploy step when the hosting platform supports it. The Compose command runs migrations automatically for this technical exercise.
- The included Postman collection uses a `base_url` variable. Replace it with the public deployment URL before exporting the final submission.
