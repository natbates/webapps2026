# Project Dependencies (explanation)

This document explains each dependency listed in `requirements.txt`, whether it's required for the project as described in the brief, and recommended additions.

- Django
  - Purpose: Main web framework. REQUIRED.
  - Use: project core, models, templates, admin, auth.

- djangorestframework
  - Purpose: Build REST APIs. RECOMMENDED if you plan to expose endpoints (brief requests a conversion endpoint).
  - Use: `api` app -> JSON endpoints for conversion and other services.

- django-crispy-forms
  - Purpose: Easier form rendering and integration with Bootstrap. RECOMMENDED for clean forms in templates.

- crispy-bootstrap5
  - Purpose: Bootstrap 5 template pack for crispy forms. RECOMMENDED if using Bootstrap 5.

- requests
  - Purpose: HTTP client for external APIs. OPTIONAL — the brief says rates are hardcoded, but `requests` is useful if you later fetch live exchange rates.

- pytest
  - Purpose: Test runner. RECOMMENDED for faster, more readable tests than `unittest`.

- pytest-django
  - Purpose: Django test integration for `pytest`. RECOMMENDED if you use `pytest`.

- pytest-cov
  - Purpose: Coverage reporting integration for `pytest`.

- coverage
  - Purpose: Coverage measurement (compatible with pytest-cov). Useful but optional if using `pytest-cov`.

Suggested additional packages (optional but useful):

- gunicorn
  - Purpose: WSGI server for deployment. Add when deploying to Linux servers.

- whitenoise
  - Purpose: Serve static files in production without configuring nginx. Useful for simple deployments on Heroku/EC2.

- python-dotenv or django-environ
  - Purpose: Manage secret keys and environment variables. Recommended for production configuration.

- django-debug-toolbar
  - Purpose: Debugging panels in development. Optional.

- psycopg2-binary
  - Purpose: PostgreSQL adapter. Only needed if you switch from SQLite to Postgres.

Notes:
- The current `requirements.txt` is reasonable for the brief. Add `gunicorn` and `whitenoise` before deploying, and consider `django-environ` to manage secrets.
- Test and CI dependencies (pytest, pytest-django, pytest-cov) are useful for Phase 4.
