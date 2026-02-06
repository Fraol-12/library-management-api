Markdown# Library Management API

Production-style RESTful API for a library system — public catalog browsing, authenticated borrowing/returning, staff inventory management.

Built with Django + Django REST Framework + JWT authentication.  
Designed with real-world integrity rules (no double-borrowing, ownership on returns, derived availability).

## Tech Stack

- Python 3.11+
- Django 5.x / 6.x
- Django REST Framework
- djangorestframework-simplejwt (JWT auth)
- SQLite (local) / PostgreSQL-ready (production)
- Black, Ruff, isort (formatting & linting)

## Features

- Public catalog (GET books list/detail + search/filter by availability)
- User registration + auto-login (POST /api/register/)
- JWT authentication (token obtain + refresh)
- Role-based access:
  - Regular users: borrow/return own books, see own loans
  - Staff (is_staff=True): full book CRUD, view all loans, force returns
- Enforced rules:
  - Only one active loan per book (DB constraint + app validation)
  - No borrow if unavailable or overdue
  - Only borrower or staff can return
- Derived state (is_available, is_overdue) — never stale flags

## Setup

1. Clone repo
   ```bash
   git clone <your-repo-url>
   cd library-management-api

Create & activate venv

python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate     # Windows

Install dependencies

pip install -r requirements.txt
Apply migrations & create superuserBashpython src/library/manage.py migrate
python src/library/manage.py createsuperuser
Run serverBashcd src/library
python manage.py runserver

API will be at http://127.0.0.1:8000/
Authentication Flow

Register
POST /api/register/JSON{
  "username": "testuser",
  "email": "test@example.com",
  "password": "StrongPass123!",
  "password2": "StrongPass123!"
}→ Returns access + refresh tokens + user info
Login (alternative)
POST /api/token/JSON{"username": "testuser", "password": "StrongPass123!"}
Use token
Header: Authorization: Bearer <access-token>
Refresh
POST /api/token/refresh/JSON{"refresh": "<refresh-token>"}

Key Endpoints

Public
GET /api/books/ → list books (filter ?available=true, ?search=keyword, ?ordering=title)
GET /api/books/<id>/ → book detail

Authenticated
POST /api/loans/ → borrow book {"book": id, "due_date": "YYYY-MM-DD"}
PATCH /api/loans/<id>/return/ → return book (empty body)
GET /api/loans/my-active/ → current active loans
GET /api/me/ → current user profile

Staff only
POST /api/books/ → create book
PATCH /api/books/<id>/ → update book
DELETE /api/books/<id>/ → delete book
GET /api/loans/ → all loans


Roles & Permissions

Anonymous → browse catalog only
Regular user → borrow/return own books, see own loans
Staff (is_staff=True) → full book CRUD, view/force-return any loan

Testing
Bashpytest
(Tests coming in next commit — model integrity, permissions, borrow/return cycle)
Deployment Notes (Production)

Use PostgreSQL (change DATABASES in settings)
Run with gunicorn + nginx
Docker support coming soon
Rate limit login/register endpoints (django-ratelimit)
HTTPS mandatory

Postman Collection
See Library Management API – Final Tests.postman_collection.json in repo root for full API flow.

Made with ❤️ in Addis Ababa – Fraol M.