# The Contacts Service API (FastAPI)

A clean, educational REST API built with **FastAPI**, **SQLAlchemy**, and **PostgreSQL** for managing contacts.  
Includes CRUD, search, and upcoming birthdays, plus Alembic migrations and consistent error responses.

---

## Features

- FastAPI with automatic OpenAPI (Swagger at `/docs`, ReDoc at `/redoc`)
- SQLAlchemy ORM models + Alembic migrations
- PostgreSQL as the database
- CRUD for contacts
- Search by first name / last name / email (`/api/contacts/search/?q=...`)
- Upcoming birthdays for the next N days (`/api/contacts/upcoming-birthdays/?days=7`)
- Pydantic v2 schemas with validation (email, phone regex, lengths)
- Unified JSON error format (422/404/409/500)
- Healthcheck endpoint

---

## Project Structure

```
goit-web-hw-12/
├─ .env                     # environment variables (DB url, JWT secret, admin credentials)
├─ main.py                  # FastAPI app entrypoint
├─ poetry.lock              # poetry lockfile
├─ pyproject.toml           # poetry project config
├─ seed.py                  # script to create initial admin user
├─ README.md                # project readme
│
├─ migrations/              # Alembic migrations
│   ├─ env.py
│   └─ versions/...
│
└─ src/
    ├─ conf/
    │   └─ config.py        # global settings (DATABASE_URL, SECRET_KEY, etc.)
    │
    ├─ core/                
    │ └─ error_handlers.py  # unified error responses (422, 404, 409, 500)
    │
    ├─ database/
    │   ├─ db.py            # async engine/session and dependency get_db
    │   └─ models.py        # SQLAlchemy ORM models (User, Contact)
    │
    ├─ repository/
    │   ├─ contacts.py      # DB operations with contacts (CRUD, search, birthdays)
    │   └─ users.py         # DB operations with users (create, roles, tokens, list)
    │
    ├─ routes/
    │   ├─ auth.py          # /api/auth (signup, login, refresh)
    │   ├─ contacts.py      # /api/contacts (CRUD, search, birthdays)
    │   ├─ health.py        # /api/health (healthcheck)
    │   └─ users.py         # /api/users (admin only: list, set role)
    │
    └─ services/
        ├─ auth.py          # password hashing, JWT utils, current_user dependency
        ├─ permissions.py   # RoleAccess dependency for role-based access
        └─ schemas.py       # Pydantic models for request/response

```

---

## Requirements

- Python 3.11+ (3.13 OK)
- PostgreSQL 13+
- (Optional) Poetry for dependency management

**Python packages (pip):**
```
fastapi
uvicorn[standard]
sqlalchemy
psycopg2-binary
alembic
pydantic>=2
python-dotenv  # optional
```
If you plan to log in JSON: `python-json-logger` (optional).

---

## Environment

Set the database URL (adjust user/password/host/db name as needed):

```bash
# Linux/macOS
export DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5432/rest_app"

# Windows PowerShell
$env:DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/rest_app"
```

`src/database/db.py` reads `DATABASE_URL` and falls back to a sensible default.

---

## Database & Alembic

### 1) Initialize Alembic (first time only)
```bash
alembic init migrations
```
> If `migrations/` already exists, skip this step.

### 2) Configure Alembic
- In `alembic.ini` set `sqlalchemy.url` to your `DATABASE_URL` (or set it in `migrations/env.py` via `config.set_main_option`).
- In `migrations/env.py` make sure:
  ```python
  from src.database.db import Base
  from src.database import models  # ensure models are imported
  target_metadata = Base.metadata
  ```

### 3) Create and apply migrations
```bash
# Autogenerate a new revision from models
alembic revision --autogenerate -m "Init contacts"

# Apply to database
alembic upgrade head
```

> When you change models later, repeat the `revision --autogenerate` + `upgrade head` flow.

---

## Run the API

Using `uvicorn`:
```bash
uvicorn main:app --reload
# App will be available at http://127.0.0.1:8000
```

Docs:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

---

## Endpoints (high level)

### System
- `GET /system/health/healthchecker` — basic healthcheck

### Contacts (under `/api` prefix)
- `GET /api/contacts/` — list contacts (query: `skip`, `limit`)
- `GET /api/contacts/{id}` — get one contact
- `POST /api/contacts/` — create contact
- `PUT /api/contacts/{id}` — update contact
- `DELETE /api/contacts/{id}` — delete contact
- `GET /api/contacts/search/?q=...` — search by first/last name or email
- `GET /api/contacts/upcoming-birthdays/?days=7` — nearest birthdays

---

## cURL examples

Create:
```bash
curl -X POST "http://127.0.0.1:8000/api/contacts/"   -H "Content-Type: application/json"   -d '{
    "first_name": "Ivan",
    "last_name": "Petrov",
    "email": "ivan.petrov@example.com",
    "phone": "+380671234567",
    "birthday": "1990-01-01",
    "extra": "Friend"
  }'
```

List:
```bash
curl "http://127.0.0.1:8000/api/contacts/?skip=0&limit=100"
```

Search:
```bash
curl "http://127.0.0.1:8000/api/contacts/search/?q=ivan"
```

Upcoming birthdays:
```bash
curl "http://127.0.0.1:8000/api/contacts/upcoming-birthdays/?days=7"
```

Health:
```bash
curl "http://127.0.0.1:8000/system/health/healthchecker"
```

---

## Validation & Error Handling

- **Pydantic v2** schemas validate request/response:
  - `EmailStr` for emails
  - `Field(..., min_length, max_length)` for strings
  - Phone regex example: `r"^\+?[0-9\-()\s]+$"`
  - `birthday: date` is **required**
- **Unified error responses** via `src/core/error_handlers.py`:
  - `422` — validation failed (`RequestValidationError`)
  - `404` — resource not found (`HTTPException`)
  - `409` — duplicate email (unique constraint)
  - `500` — unhandled / DB errors

Example error shape:
```json
{
  "error": {
    "code": 422,
    "message": "Validation failed",
    "path": "/api/contacts/",
    "method": "POST",
    "timestamp": "2025-08-19T10:20:30.123456+00:00",
    "details": []
  }
}
```

---

## License

MIT (or your choice). Educational use encouraged.
