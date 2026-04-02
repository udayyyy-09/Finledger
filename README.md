# FinLedger — Personal Finance Tracking API

A production-ready REST API built with Django and Django REST Framework for managing personal financial records, generating analytics, and enforcing role-based access control across different user types.

---

## Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [API Reference](#api-reference)
- [Role & Permission Matrix](#role--permission-matrix)
- [Filtering & Search](#filtering--search)
- [Analytics Endpoints](#analytics-endpoints)
- [Project Structure](#project-structure)
- [Assumptions](#assumptions)
- [Author](#author)

---

## Overview

FinLedger is a backend finance tracking system designed to help users record, categorize, and analyze their income and expenses. The system supports multi-user access with distinct roles, JWT-based authentication, and a clean analytics layer that powers financial summaries, category breakdowns, and monthly trends.

Built as a backend-first project, FinLedger is structured to scale cleanly — with business logic separated from views, permission logic isolated in dedicated classes, and filtering handled independently from the data layer. Designed to demonstrate scalable backend architecture, clean code practices, and production-ready API design.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10+ |
| Framework | Django 4.x + Django REST Framework |
| Database | PostgreSQL |
| Authentication | JWT via `djangorestframework-simplejwt` |
| Filtering | `django-filter` |
| ORM | Django ORM with aggregations |

---

## Architecture

The project is split into two Django apps with clear responsibilities:

**`users`** — Handles user registration, login, role assignment, and user management. Contains custom permission classes used across the system.

**`transactions`** — Handles all financial record operations (CRUD), filtering, and analytics. Business logic is isolated in `services.py` and never mixed into views.
```
Request → URL Router → View → Permission Check
                                    ↓
                            Queryset (scoped by role)
                                    ↓
                         Serializer (validation)
                                    ↓
                         Service Layer (analytics)
                                    ↓
                              Response
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL 18+
- pip

### Installation
```bash
# 1. Clone the repository
git clone https://github.com/udayyyy-09/Finledger.git
cd finledger

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies

pip install -r requirements.txt

# 4. Set up PostgreSQL
# Create a database and user in psql:
#   CREATE DATABASE finance_tracker;
#   CREATE USER finance_user WITH PASSWORD 'yourpassword';
#   GRANT ALL PRIVILEGES ON DATABASE finance_tracker TO finance_user;

# 5. Configure environment variables
cp .env.example .env
# Edit .env with your database credentials

# 6. Run migrations
python manage.py migrate

# 7. Seed test data
python seed.py

# 8. Start the server
python manage.py runserver
```

---

## Environment Variables

Create a `.env` file at the project root. A `.env.example` is provided as a template.

| Variable | Description | Default |
|---|---|---|
| `DB_NAME` | PostgreSQL database name | `finance_tracker` |
| `DB_USER` | PostgreSQL username | `finance_user` |
| `DB_PASSWORD` | PostgreSQL password | — |
| `DB_HOST` | Database host | `localhost` |
| `DB_PORT` | Database port | `5432` |
| `SECRET_KEY` | Django secret key | set in settings |

---

## API Reference

### Authentication

All endpoints except `/register/` and `/login/` require a valid JWT token in the `Authorization` header.
```
Authorization: Bearer <access_token>
```

### Auth Endpoints

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| POST | `/api/users/register/` | Register a new user | No |
| POST | `/api/users/login/` | Obtain JWT token pair | No |
| POST | `/api/users/token/refresh/` | Refresh access token | No |
| GET | `/api/users/me/` | Get current user profile | Yes |
| GET | `/api/users/` | List all users | Admin only |
| GET | `/api/users/<id>/` | Get user by ID | Admin only |
| PUT | `/api/users/<id>/` | Update user role | Admin only |
| DELETE | `/api/users/<id>/` | Delete user | Admin only |

### Transaction Endpoints

| Method | Endpoint | Description | Min Role |
|---|---|---|---|
| GET | `/api/transactions/` | List transactions | Viewer |
| POST | `/api/transactions/` | Create transaction | Admin |
| GET | `/api/transactions/<id>/` | Get transaction detail | Viewer |
| PUT | `/api/transactions/<id>/` | Update transaction | Admin |
| PATCH | `/api/transactions/<id>/` | Partial update | Admin |
| DELETE | `/api/transactions/<id>/` | Delete transaction | Admin |
| GET | `/api/transactions/summary/` | Financial summary | Analyst |
| GET | `/api/transactions/category-breakdown/` | Category totals | Analyst |
| GET | `/api/transactions/monthly-totals/` | Monthly trends | Analyst |
| GET | `/api/transactions/recent/` | Recent activity | Viewer |

---

## Role & Permission Matrix

| Action | Viewer | Analyst | Admin |
|---|---|---|---|
| View own transactions | ✅ | ✅ | ✅ |
| View all transactions | ❌ | ❌ | ✅ |
| Create / Edit / Delete transactions | ❌ | ❌ | ✅ |
| Access summary & analytics | ❌ | ✅ | ✅ |
| Manage users | ❌ | ❌ | ✅ |

---

## Filtering & Search

The `/api/transactions/` endpoint supports the following query parameters:

| Parameter | Type | Example | Description |
|---|---|---|---|
| `type` | string | `?type=expense` | Filter by income or expense |
| `category` | string | `?category=rent` | Filter by category |
| `date_from` | date | `?date_from=2025-01-01` | Start of date range |
| `date_to` | date | `?date_to=2025-03-31` | End of date range |
| `month` | integer | `?month=3` | Filter by month number |
| `year` | integer | `?year=2025` | Filter by year |
| `amount_min` | decimal | `?amount_min=500` | Minimum amount |
| `amount_max` | decimal | `?amount_max=5000` | Maximum amount |
| `search` | string | `?search=freelance` | Search notes and category |
| `ordering` | string | `?ordering=-amount` | Sort by field (prefix `-` for descending) |

**Combined example:**
```
GET /api/transactions/?type=expense&year=2025&month=3&ordering=-amount
```

---

## Analytics Endpoints

All analytics endpoints respect active filters, so you can scope summaries to specific time periods or categories.

### Financial Summary
```
GET /api/transactions/summary/
```
```json
{
    "total_income": "18500.00",
    "total_expenses": "7240.00",
    "balance": "11260.00",
    "transaction_count": 34
}
```

### Category Breakdown
```
GET /api/transactions/category-breakdown/
```
```json
[
    {"category": "salary", "type": "income", "total": "15000.00", "count": 3},
    {"category": "rent", "type": "expense", "total": "3000.00", "count": 3}
]
```

### Monthly Totals
```
GET /api/transactions/monthly-totals/
```
```json
{
    "2025-01": {"income": "6000.00", "expense": "2100.00"},
    "2025-02": {"income": "6500.00", "expense": "2400.00"},
    "2025-03": {"income": "6000.00", "expense": "2740.00"}
}
```

### Recent Activity
```
GET /api/transactions/recent/?limit=5
```

---

## Project Structure
```
finledger/
├── core/
│   ├── settings.py         # Project configuration and DRF setup
│   ├── urls.py             # Root URL routing
│   └── wsgi.py
│
├── users/
│   ├── models.py           # Custom user model with role field
│   ├── serializers.py      # Registration and user serializers
│   ├── permissions.py      # IsAdmin, IsAnalystOrAbove classes
│   ├── views.py            # Register, login, user management
│   ├── urls.py
│   └── admin.py
│
├── transactions/
│   ├── models.py           # Transaction model with category/type choices
│   ├── serializers.py      # Input validation and field-level checks
│   ├── filters.py          # Date, amount, category filter definitions
│   ├── services.py         # Analytics and business logic layer
│   ├── views.py            # ViewSet delegating to services
│   ├── urls.py
│   └── admin.py
│
├── seed.py                 # Creates test users and sample transactions
├── .env.example            # Environment variable template
├── .gitignore
└── README.md
```

---

## Test Credentials (after running seed.py)

| Username | Password | Role |
|---|---|---|
| `admin_user` | `Admin@1234` | Admin |
| `analyst_user` | `Analyst@1234` | Analyst |
| `viewer_user` | `Viewer@1234` | Viewer |

---

## Assumptions

- Admins see all transactions across all users. Viewers and Analysts only see their own records.
- The `role` field defaults to `viewer` on registration unless explicitly set. In a real system, role assignment would be a separate admin operation.
- Amount validation enforces values greater than zero. Income-type categories (salary, freelance, investment) cannot be assigned to expense records.
- JWT access tokens expire after 12 hours. Refresh tokens last 7 days.
- PostgreSQL is the recommended database. SQLite can be used for local testing by swapping the `DATABASES` config in `settings.py`.

---

## Author

Built by *Uday Chaudhary* as part of a backend engineering assessment 
