# Primetrade Backend — Scalable REST API with Auth & RBAC

A REST API built with **FastAPI + PostgreSQL** featuring JWT authentication, role-based access control (user/admin), and a full CRUD Task Manager, plus a **Vanilla JS** frontend for testing it end-to-end.

Built for the Primetrade.ai Backend Developer (Intern) assignment.

---

## Tech Stack

| Layer | Choice |
|---|---|
| Backend framework | FastAPI |
| Database | PostgreSQL |
| ORM / Migrations | SQLAlchemy 2.0 (async) + Alembic |
| Validation | Pydantic v2 |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| Frontend | Vanilla JS / HTML / CSS |
| Testing | Pytest + httpx (in-memory SQLite) |

---

## Project Structure

```
backend/
  app/
    main.py          # app entrypoint, middleware, exception handlers, /health
    core/            # config, security (hash/JWT), logging
    db/              # engine/session, declarative base
    models/          # SQLAlchemy models (User, Task)
    schemas/         # Pydantic request/response models
    crud/            # DB access functions
    api/v1/          # versioned routers (auth, users, tasks)
  alembic/           # DB migrations
  tests/             # pytest suite
frontend/
  index.html         # register / login
  dashboard.html      # protected task dashboard
  js/, css/
postman_collection.json
```

---

## Setup & Run

### 1. Prerequisites
- Python 3.11+
- PostgreSQL running locally (or update `DATABASE_URL`)

### 2. Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# edit .env: set DATABASE_URL, JWT_SECRET, ADMIN_EMAIL, etc.

createdb primetrade          # or create the DB via psql
alembic upgrade head         # run migrations

uvicorn app.main:app --reload --port 8001
```

- API base: `http://127.0.0.1:8001/api/v1`
- Swagger UI: `http://127.0.0.1:8001/docs`
- ReDoc: `http://127.0.0.1:8001/redoc`
- Health check: `http://127.0.0.1:8001/health`

### 3. Frontend

```bash
cd frontend
python3 -m http.server 5500
```

Open `http://127.0.0.1:5500/index.html`. Make sure `CORS_ORIGINS` in `backend/.env` includes this origin (it does by default).

#### Frontend Guide

**Step 1: Registration**
- Navigate to the **Register** tab.
- Enter your test email.
- Enter your test password.
- Click on the **Register** button to create a new account.

**Step 2: Login**
- Navigate to the **Login** tab.
- Enter your test email.
- Enter your test password.
- Click on the **Log In** button to access the task dashboard.

**Step 3: Task Management**
Once logged in, you can manage your tasks:
- **Add a Task:**
  - Add a title for your task.
  - Give a description to your task.
  - Click on the status button to change the status of your task.
  - Click on the **Add Task** button to successfully add the task.
- **Update a Task:** Click on the **Edit** button to update the task.
- **Remove a Task:** Click on the **Delete** button to remove the task.

### 4. Run tests

```bash
cd backend
source .venv/bin/activate
pytest -v
```

29 tests covering registration, login, RBAC, task CRUD, validation errors, and edge cases (all against an isolated in-memory SQLite DB — no impact on your dev Postgres data).

---

## Authentication & Admin Setup

- Register via `POST /api/v1/auth/register` with `{ "email", "password" }`.
- Any user whose email matches `ADMIN_EMAIL` in `.env` is **automatically assigned the `admin` role** on registration — no seed script needed. Default: `admin@example.com`.
- Login via `POST /api/v1/auth/login` (OAuth2 form fields: `username`, `password`) → returns a JWT `access_token`.
- Pass the token as `Authorization: Bearer <token>` on subsequent requests.
- In Swagger (`/docs`), click **Authorize** and log in directly — the docs page handles the OAuth2 password flow for you.

## Ownership Rules (RBAC)

- A **user** can create, view, update, and delete only their **own** tasks.
- An **admin** can view, update, and delete **any** user's tasks, and can list all registered users (`GET /api/v1/users`).
- Any cross-user access attempt by a non-admin returns **403 Forbidden**.
- Accessing a protected route without a valid token returns **401 Unauthorized**.

## API Summary

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/health` | — | Service health check |
| POST | `/api/v1/auth/register` | — | Register a new user |
| POST | `/api/v1/auth/login` | — | Login, returns JWT |
| GET | `/api/v1/auth/me` | user | Current user profile |
| GET | `/api/v1/users` | admin | List all users |
| POST | `/api/v1/tasks` | user | Create a task |
| GET | `/api/v1/tasks` | user | List tasks (pagination, filter, search, sort) |
| GET | `/api/v1/tasks/{id}` | user | Get a task |
| PUT | `/api/v1/tasks/{id}` | user | Update a task |
| DELETE | `/api/v1/tasks/{id}` | user | Delete a task |

**Task list query params:** `skip`, `limit` (pagination) · `status` (filter: `todo`/`in_progress`/`done`) · `search` (matches title/description) · `sort` (`created_at`, `updated_at`, `title`, `status`).

**Status code contract:** `201` create · `200` read/update · `204` delete · `401` unauthenticated · `403` forbidden · `404` not found · `409` duplicate · `422` validation error.

A **Postman collection** (`postman_collection.json`) is included as a backup to the Swagger docs.

---

## Database Schema

**users** — `id` (PK), `email` (unique, indexed), `hashed_password`, `role` (`user`/`admin`), `created_at`, `updated_at`.

**tasks** — `id` (PK), `title`, `description`, `status` (indexed), `owner_id` (FK → users, indexed, `ON DELETE CASCADE`), `created_at` (indexed), `updated_at`.

Indexes on `email`, `owner_id`, `status`, and `created_at` keep lookups, ownership filtering, status filtering, and recency sorting fast as data grows.

---

## Architecture

```
Frontend (Vanilla JS)
        │  fetch + JWT
        ▼
   FastAPI (app/main.py)
        │
        ▼
   PostgreSQL (SQLAlchemy + Alembic)
```

### Auth Sequence

```
Register:  User → FastAPI → hash password (bcrypt) → store in PostgreSQL
Login:     User → FastAPI → verify password → issue JWT → client stores token
Request:   Client → FastAPI (Authorization: Bearer <JWT>) → decode & validate → handler
```

---

## Scalability Note

- **Stateless JWT auth** means any request can be handled by any backend instance — enables horizontal scaling behind a load balancer with no shared session store.
- **Connection pooling** via SQLAlchemy's async engine avoids per-request connection overhead.
- **Indexed columns** (`email`, `owner_id`, `status`, `created_at`) keep the most common queries (lookup by email, list-by-owner, filter-by-status, sort-by-recency) performant as row counts grow.
- **API versioning** (`/api/v1`) allows introducing breaking changes in a `/api/v2` without disrupting existing clients.
- **Modular structure** (`api/`, `crud/`, `models/`, `schemas/`) makes it straightforward to add new resource modules without touching existing ones.

### Future Improvements

- Refresh tokens for longer-lived sessions without re-entering credentials.
- Rate limiting on auth endpoints to mitigate brute-force attempts.
- Redis caching layer for hot read paths (e.g., per-user task lists) with write-through invalidation.
- Background job processing (e.g., Celery/RQ) for any async workloads.
- Object storage (S3-compatible) if file attachments are added to tasks.
- Containerized deployment (Docker/Kubernetes) for reproducible environments and easy scaling.
- CI/CD pipeline to run the test suite and deploy on merge.
- Centralized structured logging + monitoring (Prometheus/Grafana) for observability in production.

---

## Deployment (Railway)

Deployed as two Railway services from this monorepo — `backend` (FastAPI, root directory `backend/`) and `frontend` (static site, root directory `frontend/`) — plus a managed PostgreSQL plugin. See the deployment procedure for full steps.

- `backend/Procfile` runs migrations then starts the API: `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
- `frontend/nixpacks.toml` serves the static files: `python3 -m http.server $PORT`.
- `app/core/config.py` auto-converts Railway's `postgres://`/`postgresql://` `DATABASE_URL` to `postgresql+asyncpg://`.
- Set `CORS_ORIGINS` on the backend service to the frontend's Railway domain, and update `API_BASE` in `frontend/js/api.js` to the backend's Railway domain.
