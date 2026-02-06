# Library Management API

Professional, production-ready RESTful backend for managing a library system.

> Built with Django 6, Django REST Framework (DRF), JWT auth (SimpleJWT), PostgreSQL, Docker.  
> Designed with real-world integrity rules: no double-borrowing, ownership enforcement on returns, derived availability flags, and overdue blocking.

---

## Features

- Public catalog browsing (search/filter by availability)  
- JWT authentication with public registration + auto-login  
- Borrow/return books with strict rules:  
  - No double-borrowing  
  - Borrower ownership enforcement  
  - Overdue blocking  
  - Maximum 5 active loans per user  
- Staff-only book CRUD operations (create, update, delete)  
- DB-level constraints + transactions ensure data integrity  
- Derived state fields: `is_available`, `is_overdue` (always up-to-date)  

---

## Tech Stack

- Python 3.11+  
- Django 6  
- Django REST Framework  
- djangorestframework-simplejwt (JWT auth)  
- PostgreSQL (production-ready) / SQLite (local fallback)  
- Docker & Docker Compose  
- Black, Ruff, isort (formatting & linting)  

---

## Setup (Local Development)

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd library-management-api

    Create virtual environment & install dependencies

python -m venv venv
source venv/bin/activate   # Linux/Mac
# venv\Scripts\activate     # Windows
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

API base URL: http://127.0.0.1:8000
Authentication Flow
Action	Endpoint	Description
Register	POST /api/register/	Creates user + returns access & refresh tokens
Login	POST /api/token/	Obtain JWT access + refresh tokens
Refresh	POST /api/token/refresh/	Refresh access token
Current User	GET /api/me/	Requires Bearer token; returns current user info

Example: Register User

POST /api/register/
{
  "username": "test_user",
  "email": "test_user@example.com",
  "password": "testpass123",
  "password2": "testpass123"
}

Key Endpoints
Endpoint	Method	Description	Auth
/api/books/	GET	List all books (filter ?available=true)	None
/api/books/<id>/	GET	Get book detail	None
/api/books/	POST	Create new book	Staff only
/api/books/<id>/	PATCH	Update book	Staff only
/api/books/<id>/	DELETE	Delete book	Staff only
/api/loans/	POST	Borrow a book	Authenticated user
/api/loans/<id>/return/	PATCH	Return a borrowed book	Borrower or staff
/api/loans/my-active/	GET	List user's active loans	Authenticated user
Docker (Postgres + Django)

Run everything with one command:

docker-compose up --build

    API exposed at http://localhost:8000

    PostgreSQL container auto-created

    Migrations run automatically

    Use superuser token to create books

Optional production tweaks:

    Replace Django dev server with Gunicorn in Dockerfile

    Use environment variables (.env) for secrets

    Enable SSL and connection pooling in production

Testing

Run all tests:

pytest -v

Coverage:

    Models & constraints

    Permissions

    Borrow/return cycle

    Overdue loan blocking

Example overdue test snippet

def test_borrow_blocked_if_overdue(self, setup):
    user, _, book = setup
    overdue_loan = Loan.objects.create(
        user=user,
        book=Book.objects.create(title="Old Book", author="Author X", isbn="9999999999999"),
        due_date=timezone.now() - timedelta(days=1)
    )
    response = self.client.post("/api/loans/", {"book": book.id, "due_date": "2026-03-20"})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "overdue" in str(response.data).lower()

Postman Collection

Import this collection to Postman to test all endpoints:

Library Management API – Final Tests

    Includes all endpoints grouped by Auth, Books, Loans, Users/Profile

    Example requests for registration, login, book CRUD, borrow/return flows

    Automatically sets access_token for authenticated requests

Notes

    Zero hard-coded DB credentials — uses DATABASE_URL

    Local fallback to SQLite if env var not set

    Fully Dockerized — exact same setup as production

    All endpoints tested end-to-end

    Portfolio-ready, production-grade backend

    Made with ❤️ in Addis Ababa — Fraol M.