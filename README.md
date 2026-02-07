# Library Management API

Professional, production-ready RESTful backend for managing a library system.

> Built with Django 6, Django REST Framework (DRF), JWT auth (SimpleJWT), PostgreSQL, Docker.  
> Designed with real-world integrity rules: no double-borrowing, ownership enforcement on returns, derived availability flags, and overdue blocking.

---
## 🌐 Live API

Deployed on Render (free tier):

[Library Management API](https://library-management-api-ym28.onrender.com)

**Notes:**
- First request may take 10–30 seconds due to free-tier cold start.
- Public endpoints: `/api/books/`, `/api/register/`
- Authenticated endpoints require Bearer token (from `/api/token/`)
- Test with Postman using included collection: `postman/Library Management API – Final Tests.postman_collection.json`

---
## 🌟 Features

### Public Features
- Browse library catalog with search and filter by availability
- JWT authentication with public registration and auto-login

### Borrowing System
- Borrow and return books with strict rules:
  - No double-borrowing
  - Borrower ownership enforcement
  - Overdue blocking
  - Maximum 5 active loans per user

### Staff Features
- Staff-only book CRUD operations (create, update, delete)
- Derived fields: `is_available` and `is_overdue` always up-to-date

### Technical Highlights
- Domain rules enforced at multiple layers: DB constraints + app validation + atomic transactions
- Automated tests covering models, permissions, and borrowing workflows
- Fully Dockerized (Django + PostgreSQL) for reproducible setup

---
## 🛠️ Technology Stack

- Python 3.11+
- Django 6
- Django REST Framework (DRF)
- JWT Authentication via `djangorestframework-simplejwt`
- PostgreSQL (production) / SQLite (local fallback)
- Docker & Docker Compose
- Black, Ruff, isort (code formatting & linting)
 

---
## 🚀 Setup (Local Development)

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd library-management-api


Create virtual environment & install dependencies

python -m venv venv
source venv/bin/activate   # Linux/Mac
# venv\Scripts\activate    # Windows
pip install -r requirements.txt


Start PostgreSQL via Docker (optional but recommended)

docker run --name library-postgres \
  -e POSTGRES_USER=library_user \
  -e POSTGRES_PASSWORD=library_pass \
  -e POSTGRES_DB=library_db \
  -p 5432:5432 -d postgres:16-alpine

export DATABASE_URL=postgres://library_user:library_pass@localhost:5432/library_db


Apply migrations

python src/library/manage.py migrate


Create a superuser

python src/library/manage.py createsuperuser


Run the development server

python src/library/manage.py runserver


---

### **6️⃣ Authentication Flow**

```markdown
## 🔑 Authentication Flow

| Action         | Endpoint            | Description                                  |
|----------------|------------------|----------------------------------------------|
| Register       | POST /api/register/ | Creates user + returns access & refresh tokens |
| Login          | POST /api/token/    | Obtain JWT access + refresh tokens           |
| Refresh Token  | POST /api/token/refresh/ | Refresh access token                     |
| Current User   | GET /api/me/       | Requires Bearer token; returns user info    |

**Example: Register User**
```json
POST /api/register/
{
  "username": "test_user",
  "email": "test_user@example.com",
  "password": "testpass123",
  "password2": "testpass123"
}

---
## 📌 Key Endpoints

| Endpoint                  | Method | Description                          | Auth                     |
|----------------------------|--------|--------------------------------------|--------------------------|
| /api/books/               | GET    | List all books (filter `?available=true`) | None                     |
| /api/books/<id>/          | GET    | Get book detail                       | None                     |
| /api/books/               | POST   | Create new book                        | Staff only               |
| /api/books/<id>/          | PATCH  | Update book                            | Staff only               |
| /api/books/<id>/          | DELETE | Delete book                            | Staff only               |
| /api/loans/               | POST   | Borrow a book                          | Authenticated user       |
| /api/loans/<id>/return/   | PATCH  | Return a borrowed book                 | Borrower or Staff        |
| /api/loans/my-active/     | GET    | List user's active loans               | Authenticated user       |


---
## 🐳 Docker (PostgreSQL + Django)

Run everything with one command:

```bash
docker-compose up --build

---
## Testing

Run the full suite locally:

```bash
pytest -v


---
Postman Collection

Import this collection to Postman to test all endpoints:

Library Management API – Final Tests

    Includes all endpoints grouped by Auth, Books, Loans, Users/Profile

    Example requests for registration, login, book CRUD, borrow/return flows

    Automatically sets access_token for authenticated requests


---

### **10️⃣ Notes & Architecture**

```
## 📝 Notes & Architectural Highlights

- Zero hard-coded DB credentials — uses `DATABASE_URL`
- Local fallback to SQLite if environment variable not set
- Fully Dockerized — exact same setup as production
- All endpoints tested end-to-end
- Portfolio-ready, production-grade backend

### Lessons Learned
- Derived state fields (`is_available`, `is_overdue`) prevent data drift under concurrency
- Partial unique constraints + app-level validation = defense in depth
- Atomic transactions + double-checks in `perform_create` prevent race conditions
- JWT authentication allows horizontal scaling and mobile-friendly API
- Public registration improves UX, but would require rate limiting & email verification in production
- SQLite fallback allows fast dev iteration; Postgres ready via `DATABASE_URL`
- Docker + docker-compose ensures reproducible setup for interviewers, staging, production


## 🚀 Future Improvements

- Fine calculation on late returns
- Reservation queue system
- Celery + email/SMS notifications
- Full-text search (Postgres trigram or Elasticsearch)
- Rate limiting for public registration
