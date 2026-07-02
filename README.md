# Primetrade Backend — Scalable REST API with JWT Auth, RBAC & Task Management

A full-stack task management application built for the **Primetrade.ai Backend Developer (Intern) assignment**.

It includes a **FastAPI + PostgreSQL** backend with **JWT authentication**, **role-based access control (RBAC)**, and **Task CRUD APIs**, along with a **Vanilla JavaScript frontend** to demonstrate the complete register → login → task management flow.

---

## Live Deployment

### Frontend
**https://primeai-frontend.onrender.com/**

### Backend API
**https://primeai-backendtest.onrender.com**

### Swagger Docs
**https://primeai-backendtest.onrender.com/docs**

### ReDoc
**https://primeai-backendtest.onrender.com/redoc**

### Health Check
**https://primeai-backendtest.onrender.com/health**

---

# Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Live Deployment](#live-deployment)
- [Project Structure](#project-structure)
- [Local Setup & Run](#local-setup--run)
- [Authentication & RBAC](#authentication--rbac)
- [API Summary](#api-summary)
- [Database Schema](#database-schema)
- [Architecture](#architecture)
- [Web App Usage](#web-app-usage)
- [Testing](#testing)
- [Deployment](#deployment-render--neon)
- [Scalability Note](#scalability-note)
- [Important Notes](#important-notes)

---

# Overview

This project is a **secure, scalable REST API** with a simple web frontend. It was built as a greenfield implementation for the Primetrade.ai assignment.

The application supports:

- User registration and login
- JWT-based authentication
- Role-based access control with **user** and **admin** roles
- Full CRUD operations for a secondary entity (**Tasks**)
- Versioned REST API (`/api/v1`)
- Validation, error handling, and Swagger documentation
- A lightweight frontend to test the system end-to-end

---

# Features

## Authentication
- Register a new account
- Login with email + password
- JWT access token generation
- Protected routes using bearer authentication
- Current-user profile endpoint

## Role-Based Access Control (RBAC)
- **User** role → can manage only their own tasks
- **Admin** role → can view all users and access all tasks

## Task Management
- Create a task
- View tasks
- Update a task
- Delete a task
- Filter, paginate, search, and sort task lists

## Developer Experience
- Auto-generated API docs via Swagger and ReDoc
- Alembic migrations for schema management
- Automated test suite with Pytest
- Production deployment on Render + Neon

---

# Tech Stack

| Layer | Choice |
|---|---|
| Backend framework | FastAPI |
| Database | PostgreSQL |
| Production DB hosting | Neon PostgreSQL |
| ORM / Migrations | SQLAlchemy 2.0 (async) + Alembic |
| Validation | Pydantic v2 |
| Authentication | JWT (`python-jose`) + bcrypt (`passlib`) |
| Frontend | Vanilla JavaScript + HTML + CSS |
| Testing | Pytest + HTTPX + in-memory SQLite |
| Deployment | Render (Web Service + Static Site) |

---

# Project Structure

```text
backend/
  app/
    main.py                  # FastAPI entrypoint, middleware, exception handlers, /health
    core/
      config.py              # environment settings
      security.py            # password hashing + JWT helpers
      logging.py             # request logging
    db/
      base.py                # declarative base
      session.py             # async engine/session + DB connection check
    models/
      user.py                # User model
      task.py                # Task model
    schemas/
      user.py                # request/response schemas
      task.py
      token.py
    crud/
      user.py                # user DB operations
      task.py                # task DB operations
    api/
      deps.py                # auth/session dependencies
      v1/
        auth.py              # register, login, me
        users.py             # admin-only routes
        tasks.py             # task CRUD
        router.py            # API v1 router aggregation
  alembic/                   # migrations
  tests/                     # test suite
  requirements.txt
  Procfile

frontend/
  index.html                 # login / register page
  dashboard.html             # protected task dashboard
  css/
    styles.css
  js/
    api.js                   # API base + fetch wrapper
    auth.js                  # auth flow
    tasks.js                 # task CRUD logic

postman_collection.json
README.md
USER_MANUAL.md