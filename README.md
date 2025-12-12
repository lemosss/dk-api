DK Invoices Calendar
=====================

Requirements
- Python 3.9+
- PostgreSQL

Setup
1. Create a virtualenv and install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\pip install fastapi uvicorn[standard] sqlalchemy psycopg2-binary jinja2 passlib[bcrypt] python-jose pydantic
```

2. Configure `.env` in project root with `DATABASE_URL`, `SECRET_KEY`, `SUPERADMIN_EMAIL`, `SUPERADMIN_PASSWORD` optionally.

3. Run seed to create initial data:

```powershell
python -m app.seed
```

4. Run the app:

```powershell
uvicorn app.main:app --reload
```

Notes
- Login at `/login`. Use seeded credentials from `.env` or defaults.
- The calendar UI is at `/calendar`.
