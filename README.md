# Compliance Task Tracker API

A production-style REST API built with Django, DRF, PostgreSQL, Redis, and Celery.

## Features

- **RESTful API** - Full CRUD operations for compliance tasks
- **JWT Authentication** - Secure token-based authentication
- **Redis Caching** - High-performance caching for API responses
- **Celery Background Tasks** - Asynchronous job processing
- **PostgreSQL Database** - Reliable data persistence
- **Swagger UI Documentation** - Interactive API documentation at `/api/docs/`
- **Docker Compose** - Easy containerized deployment

---

## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Git (for cloning from GitHub)

### Option 1: Clone from GitHub

1. **Clone the repository:**
```bash
git clone https://github.com/Escannnor/compliance_tracker.git
cd compliance_tracker
```

2. **Start all services:**
```bash
docker-compose up --build
```

3. **Run database migrations:**
```bash
docker-compose exec web python manage.py migrate
```

4. **Create admin superuser:**
```bash
docker-compose exec web python manage.py createsuperuser
```

5. **Access the API:**
- API Documentation: http://localhost:8000/api/docs/
- Django Admin: http://localhost:8000/admin/
- API Base URL: http://localhost:8000/api/

### Option 2: Running Locally

If you already have the project locally:

1. **Start all services:**
```bash
docker-compose up --build
```

2. **Run database migrations:**
```bash
docker-compose exec web python manage.py migrate
```

3. **Create admin superuser:**
```bash
docker-compose exec web python manage.py createsuperuser
```

4. **Access the API:**
- API Documentation: http://localhost:8000/api/docs/
- Django Admin: http://localhost:8000/admin/
- API Base URL: http://localhost:8000/api/

---

## How Django Works (read this first)

Django follows a pattern called **MVT — Model, View, Template**.
Since we're building an API (no frontend), we only care about **Model and View**.

```
Request → URLs → View → Model (database) → Response
```

- **Model** = your database table, written as a Python class
- **View** = your logic — what happens when a request hits an endpoint
- **URL** = maps a path like /api/tasks/ to a view
- **Serializer** (DRF) = converts your Model data to JSON and validates incoming data

---

## Project Structure

```
compliance_tracker/
├── config/
│   ├── settings.py        # All Django configuration lives here
│   ├── urls.py            # Root URL file — registers all app URLs
│   ├── celery.py          # Celery configuration
├── apps/
│   ├── users/             # User model, JWT auth
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   └── urls.py
│   ├── tasks/             # Compliance tasks
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── tasks.py      # Celery background jobs
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── API_ENDPOINTS.txt      # Detailed API documentation
├── TECH_STACK.txt        # Technology stack information
└── manage.py              # Django's command-line tool
```

---

## How Redis is Used Here

Redis is used in **two ways**:

1. **Caching** — when someone hits GET /api/tasks/, instead of querying
   PostgreSQL every time, we store the result in Redis for 60 seconds.
   Next request? Redis returns it instantly.

2. **Celery Broker** — Celery needs somewhere to store background jobs
   before processing them. Redis acts as that queue.

```
User request → Django checks Redis first
                ├── Cache hit?  → return instantly (no DB query)
                └── Cache miss? → query PostgreSQL → store in Redis → return
```

---

## API Documentation

### Interactive Swagger UI
Visit http://localhost:8000/api/docs/ for interactive API documentation with:
- Auto-generated endpoint documentation
- Built-in testing interface
- Request/response examples
- Authentication support

### Alternative Documentation
- ReDoc: http://localhost:8000/api/redoc/
- OpenAPI Schema: http://localhost:8000/api/schema/

---

## Default Credentials

**Django Admin:**
- Username: `admin`
- Password: `admin123`

**Database:**
- Name: `compliance_db`
- User: `postgres`
- Password: `postgres`

---

## Testing the API

See `API_ENDPOINTS.txt` for detailed instructions on testing all endpoints using Postman or curl.

---

## Background Tasks

### Running Celery Tasks Manually

```bash
docker-compose exec web python manage.py shell
```

Then in the shell:
```python
from apps.tasks.tasks import check_overdue_tasks
check_overdue_tasks.delay()  # sends job to Redis, Celery worker picks it up
```

### Available Background Tasks
- `check_overdue_tasks` - Marks overdue tasks as overdue status
- `send_deadline_reminder` - Sends reminder for a specific task

---

## Development

### Adding New Endpoints
1. Create views in `apps/[app_name]/views.py`
2. Add URLs in `apps/[app_name]/urls.py`
3. Create serializers in `apps/[app_name]/serializers.py`
4. Run migrations if models change

### Running Migrations
```bash
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```

---

## Technology Stack

See `TECH_STACK.txt` for detailed information about all technologies used in this project.

---

## License

This project is for educational purposes.
