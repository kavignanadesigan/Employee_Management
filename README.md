# Employee Management REST API

Django + Django REST Framework API with JWT auth, employee CRUD, pagination,
search/filtering, validation, MySQL, interactive API docs, and a branded
admin panel.

## Stack
- Django 5.x (pinned — see MySQL version note below), Django REST Framework
- SimpleJWT (access/refresh tokens, blacklist on rotation)
- django-filter (search & filtering)
- drf-spectacular (OpenAPI schema, Swagger UI, ReDoc)
- MySQL 8.0+

## Project layout
```
employee_management_api/
├── employee_management/     # project settings, root urls
├── employees/                # app: models, serializers, views, filters, admin
├── static/admin/css/         # admin branding overrides
├── templates/admin/          # admin template override (loads branding.css)
├── requirements.txt
├── .env.example
└── manage.py
```

## 1. Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

`mysqlclient` needs MySQL's dev headers to build. If `pip install` fails on it:
- **Ubuntu/Debian**: `sudo apt-get install default-libmysqlclient-dev build-essential pkg-config`
- **macOS**: `brew install mysql-client pkg-config` then
  `export PKG_CONFIG_PATH="$(brew --prefix mysql-client)/lib/pkgconfig"` before `pip install`
- **Windows**: if `mysqlclient` won't build even with build tools, comment it out
  in `requirements.txt` and uncomment `pymysql` instead. `employee_management/__init__.py`
  already has the two-line shim (`pymysql.install_as_MySQLdb()`) wired up for this.

## 2. Configure the database

Edit the `DATABASES` block in `employee_management/settings.py` (or switch it
back to reading from `.env` via `python-decouple`, which is safer if this repo
is ever pushed anywhere — see the note below).

Create the database first (the app won't create it for you):
```sql
CREATE DATABASE employee_management CHARACTER SET utf8mb4;
```

**Security note:** the current `settings.py` has the DB password hardcoded
directly (`"PASSWORD": "tiger"`). That's fine for local dev, but if this ever
goes into version control, switch it to `config("DB_PASSWORD")` (using
`python-decouple`, already a dependency) and put the real password in a
gitignored `.env` file instead.

## 3. Migrate & create an admin user

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

## 4. Collect static files (needed for the branded admin CSS)

```bash
python manage.py collectstatic
```

## 5. Run

```bash
python manage.py runserver
```

- API: `http://127.0.0.1:8000/api/`
- Admin: `http://127.0.0.1:8000/admin/`
- Interactive docs: `http://127.0.0.1:8000/api/docs/`

## ⚠️ Important: Django/MySQL version compatibility

**Django 6.x requires MySQL 8.4 or later.** Most existing MySQL installs
(including MySQL 8.0.x, still very common) are below that. If you see:

```
django.db.utils.NotSupportedError: MySQL 8.4 or later is required (found 8.0.x)
```

Keep Django pinned to `<6.0` as in `requirements.txt` — Django 5.x fully
supports MySQL 8.0+. If you already have Django 6.x installed:
`pip install "Django>=5.0,<6.0" --force-reinstall`.

## Interactive API documentation

Three new endpoints, auto-generated from the actual DRF serializers/views —
always in sync with the code, nothing to hand-maintain:

| Endpoint | What it is |
|---|---|
| `/api/docs/` | Swagger UI — browse every endpoint, expand each one, click "Try it out" and send real requests (including JWT auth) right from the browser |
| `/api/redoc/` | ReDoc — a cleaner, read-only reference view. Good for sharing with a client who just wants to *read* the API surface |
| `/api/schema/` | Raw OpenAPI 3.0 schema (YAML/JSON) — import into Postman, Insomnia, or codegen tools |

To try authenticated requests in Swagger UI: call `/api/auth/token/` first to
get an access token, then click the **Authorize** button (top right) and
paste `Bearer <your_access_token>`. It stays authorized as you click through
other endpoints.

## Branded admin panel

`/admin/` now shows "Employee Management" as the header/title instead of the
default "Django administration", with a custom color scheme (deep blue +
amber accent) instead of Django's default teal. This comes from:
- `employees/admin.py` — sets `site_header`, `site_title`, `index_title`
- `templates/admin/base_site.html` — overrides the default template to load a custom stylesheet
- `static/admin/css/branding.css` — overrides Django 5.2's built-in CSS custom properties (`--primary`, `--header-bg`, etc.) — no need to fight Django's CSS specificity

To change the colors, edit the `:root` variables at the top of
`static/admin/css/branding.css`, then re-run `collectstatic`.

The employee list view also now shows salary and join date columns, plus a
date-based drill-down (`date_hierarchy`) on join date.

## Authentication (JWT)

| Endpoint | Method | Description |
|---|---|---|
| `/api/auth/token/` | POST | Get access + refresh token (body: `username`, `password`) |
| `/api/auth/token/refresh/` | POST | Get a new access token (body: `refresh`) |
| `/api/auth/token/blacklist/` | POST | Invalidate a refresh token (logout) |

```bash
curl -X POST http://127.0.0.1:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "yourpassword"}'
```

Use the returned `access` token on every employee/department request:
```
Authorization: Bearer <access_token>
```

## Employee endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/employees/` | GET | List employees (paginated) |
| `/api/employees/` | POST | Create employee |
| `/api/employees/{id}/` | GET | Retrieve one employee |
| `/api/employees/{id}/` | PUT/PATCH | Update employee |
| `/api/employees/{id}/` | DELETE | Delete employee |
| `/api/departments/` | GET/POST/... | Manage departments |
| `/api/leave-requests/` | GET/POST/... | Manage leave requests |
| `/api/leave-requests/{id}/approve/` | POST | Approve a pending leave request (body: `{"comment": "..."}`, optional) |
| `/api/leave-requests/{id}/reject/` | POST | Reject a pending leave request (body: `{"comment": "..."}`, optional) |
| `/api/attendance/` | GET/POST/... | Manage daily attendance records |

### Search
`GET /api/employees/?search=jane` — matches first name, last name, email,
employee code, designation, or department name.

### Filter
```
GET /api/employees/?status=ACTIVE
GET /api/employees/?department=Engineering
GET /api/employees/?min_salary=30000&max_salary=80000
GET /api/employees/?joined_after=2023-01-01&joined_before=2024-01-01
```

### Ordering
`GET /api/employees/?ordering=-salary` (prefix `-` for descending). Allowed
fields: `first_name`, `last_name`, `salary`, `date_of_joining`, `created_at`.

### Pagination
`GET /api/employees/?page=2&page_size=20` (default page size 10, max 100).

Full request/response shapes for every field are documented at `/api/docs/`.

## Leave management

Employees submit leave requests; a reviewer (any authenticated user, in this
simple version) approves or rejects them.

- `POST /api/leave-requests/` — apply for leave (`employee`, `leave_type`
  one of `SICK`/`CASUAL`/`EARNED`/`UNPAID`, `start_date`, `end_date`, `reason`)
- Validation: `end_date` can't be before `start_date`; can't apply for leave
  starting in the past; `days_requested` is computed automatically
- `POST /api/leave-requests/{id}/approve/` and `/reject/` — only works on
  `PENDING` requests (returns 400 if already reviewed); records `reviewed_at`
  and an optional `review_comment`
- Filter: `?status=PENDING`, `?leave_type=SICK`, `?employee=<uuid>`,
  `?starts_after=2024-01-01&ends_before=2024-12-31`
- The Django admin also has bulk **Approve/Reject selected** actions on the
  leave request list page

## Attendance

Daily check-in/check-out records, one per employee per day.

- `POST /api/attendance/` — (`employee`, `date`, `check_in`, `check_out`,
  `status` one of `PRESENT`/`ABSENT`/`HALF_DAY`/`ON_LEAVE`)
- Validation: `check_out` must be after `check_in`; one record per
  employee/date combination (database-enforced); date can't be in the future
- Filter: `?employee=<uuid>`, `?status=PRESENT`,
  `?date_after=2024-01-01&date_before=2024-01-31`

## Validation rules
- `email` must be unique (case-insensitive).
- `salary` must be greater than 0.
- `date_of_joining` cannot be in the future.
- `phone_number` must match `+<countrycode><number>` (9–15 digits).
- `first_name`/`last_name` cannot be blank (auto-trimmed and title-cased).
- `employee_code` is auto-generated and read-only.

## Troubleshooting

| Error | Fix |
|---|---|
| `MySQL 8.4 or later is required (found 8.0.x)` | See version compatibility section above — pin Django `<6.0` |
| `Can't connect to MySQL server...` | MySQL isn't running, or host/port in `settings.py` is wrong |
| `Access denied for user...` | Wrong DB username/password, or that user lacks privileges |
| `Unknown database...` | You haven't created the database yet — run the `CREATE DATABASE` statement above |
| `ModuleNotFoundError: No module named 'MySQLdb'` and not using pymysql | `mysqlclient` isn't installed / failed to build — see Setup, or switch to the pymysql fallback |
| Admin branding CSS not showing | Run `python manage.py collectstatic`, and make sure `DEBUG=True` in dev (runserver only auto-serves static files when DEBUG is on) |
| `/api/docs/` 404s | Make sure `drf_spectacular` is in `INSTALLED_APPS` and the three schema/docs paths are in the root `urls.py` |

If none of these match what you're seeing, share the exact error/traceback
and I can pinpoint it.

## Notes
- All employee/department endpoints require authentication (`IsAuthenticated`).
- `Employee.id` is a UUID (safer for public-facing APIs than sequential IDs).
- Deleting a department sets its employees' `department` to null (kept, not cascaded).
- For production: set `DEBUG=False`, a strong `SECRET_KEY`, proper `ALLOWED_HOSTS`,
  move the DB password back to `.env`, and serve behind gunicorn/uwsgi + nginx
  rather than `runserver`.
