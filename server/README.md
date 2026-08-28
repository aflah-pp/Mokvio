# Mokvio Server

Backend application for Mokvio.

This Django project provides the REST API, authentication, project/resource/field management, data generators, dashboard data, and dynamically generated mock API responses. Product‑level details are in the root [README](../README.md); this file focuses on running and extending the backend.

---

## Tech Stack

- Python
- Django
- Django REST Framework
- PostgreSQL
- JWT authentication
- Ruff
- Django test framework

---

## Requirements

- Python 3.12+
- PostgreSQL
- pip
- Git

Check Python version:

```bash
python --version
```

---

## Project Structure

```text
server/
├── config/
├── dashboard/
├── generators/
├── projects/
├── resources/
├── users/
├── shared/
├── manage.py
├── requirements.txt
└── ...
```

The backend is split into Django apps by responsibility.

### Core Applications

- **users**  
  Registration, login, JWT auth, token refresh, logout (including “logout from all sessions”), profile, password changes, email verification, account deactivation.

- **projects**  
  Project management (top‑level containers for mock APIs).

- **resources**  
  Resources inside projects (e.g. `Product`, `User`, `Order`).

- **generators**  
  Generator registry and API. Generators produce realistic values like `person.full_name`, `internet.email`, `commerce.price`, `random.integer`, `random.boolean`, `uuid.v4`.

- **dashboard**  
  Aggregated stats for the frontend dashboard (project counts, resource info, recent activity, etc.), computed from real data instead of hardcoded values.

---

## Installation

From the repository root:

```bash
cd server
python -m venv .venv
```

Activate the virtual environment:

- macOS / Linux:

  ```bash
  source .venv/bin/activate
  ```

- Windows:

  ```bash
  .venv\Scripts\activate
  ```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Environment Configuration

Mokvio uses environment variables for configuration. At minimum, configure:

- `SECRET_KEY`
- `DATABASE_URL`
- `CORS_ALLOWED_ORIGINS`
- JWT‑related settings as required by the project

Example PostgreSQL URL:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/moackvio
```

Do not commit environment files or secrets.

full env config will look like this

```env
DATABASE_URL=YOUR_RENDER_DATABASE_URL
CELERY_BROKER_URL=rediss://default:YOUR_UPSTASH_PASSWORD@YOUR_UPSTASH_HOST:637
CELERY_RESULT_BACKEND=rediss://default:YOUR_UPSTASH_PASSWORD@YOUR_UPSTASH_HOST:6379
TELEGRAM_BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
TELEGRAM_ADMIN_CHAT_IDS=YOUR_TELEGRAM_CHAT_ID
TELEGRAM_WEBHOOK_SECRET=YOUR_RANDOM_WEBHOOK_SECRET
ALLOWED_HOSTS=YOUR_RENDER_DOMAIN.onrender.com
CORS_ALLOWED_ORIGINS=https://YOUR_FRONTEND_DOMAIN
CSRF_TRUSTED_ORIGINS=https://YOUR_FRONTEND_DOMAIN
JWT_REFRESH_COOKIE_SECURE=True
JWT_REFRESH_COOKIE_SAMESITE=None
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```
---

## Database

Mokvio uses PostgreSQL as its primary database. It stores:

- Users
- Projects
- Resources
- Fields
- Generator configuration
- Audit‑related information

Mock response values are generated dynamically; the DB does not need thousands of fake rows just to return mock data.

---

## Migrations

Apply migrations:

```bash
python manage.py migrate
```

When you change models:

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## Run the Development Server

```bash
python manage.py runserver
```

By default, the backend is available at:

```text
http://127.0.0.1:8000
```

The main API namespace is:

```text
/api/v1/
```

Key areas include:

- `/api/v1/users/`
- `/api/v1/projects/`
- `/api/v1/generators/`

Resource and mock API routes are provided by their respective apps.

---

## Generator API

Available generators:

```bash
GET /api/v1/generators/
```

Response includes:

- Generator key
- Supported field types
- Available configuration options

Example:

- `person.full_name` supports `string`
- `random.integer` supports `integer`

This allows the frontend to show only compatible generators for each field type.

---

## Mock API Generation

Core workflow:

1. Project  
2. Resource  
3. Fields  
4. Generator configuration  
5. Publish  
6. Mock API request  
7. Generated JSON  

Mock responses are generated from the resource definition and field generator configuration; they are not stored as permanent rows.

---

## Authentication

Mokvio uses JWT authentication. Refresh tokens are handled via secure HttpOnly cookies according to the backend configuration.

Endpoints cover:

- Login
- Registration
- Token refresh
- Logout
- Password changes
- User deactivation

Whenever you touch these areas, test:

- Login / registration flows
- Token refresh behavior
- Logout (single and “all sessions”)
- Password change & deactivation paths

---

## Testing

Run the Django test suite:

```bash
python manage.py test
```

CI also runs the backend tests. Before merging backend changes, verify:

- Tests pass
- Linting passes
- Application checks pass
- Manual review of changed files and migrations

---

## Linting

Mokvio uses Ruff for linting and formatting.

Check:

```bash
ruff check .
```

Format (if configured for the project):

```bash
ruff format .
```

Do not ignore lint errors without understanding them.

---

## Django Checks

Run Django’s system checks:

```bash
python manage.py check
```

This should pass before committing changes.

---

## Development Workflow

Typical local setup:

1. PostgreSQL running  
2. Django backend running  
3. React frontend running  

For a mock API feature:

- Create project  
- Create resource  
- Create fields  
- Configure generators  
- Publish resource  
- Hit the mock endpoint  
- Verify generated JSON  

---

## Production Considerations

The Django development server is for local use only. For production, deploy with a proper WSGI/ASGI setup and configure:

- Production `SECRET_KEY`
- PostgreSQL
- Allowed hosts
- CORS
- Secure cookies
- JWT configuration
- HTTPS
- Static/media handling
- Environment‑specific settings

Never expose development secrets in production.

---

## Docker

Docker is not currently part of the self‑hosted setup. The project runs directly with Python, Django, PostgreSQL, Node.js, and React. Docker support may be added later as deployment needs evolve.

---

## Backend Quality Rules

Before committing backend changes:

- Run Django checks.
- Run the test suite.
- Run Ruff.
- Verify database migrations.
- Test affected API endpoints.
- Check authentication behavior where relevant.
- Review migrations and changed files.
- Confirm that no secrets or environment files are committed.

When contributing:

- Keep business logic in services.
- Keep views focused on HTTP concerns.
- Keep serializers responsible for validation and representation.
- Keep generator behavior inside the generator system.
- Avoid duplicating business rules.
- Add tests for new business behavior.
- Keep API behavior backwards‑compatible where possible.

The goal is to keep the backend modular as Mokvio grows into a larger API mocking platform.