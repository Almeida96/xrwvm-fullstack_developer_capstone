# Dealership Reviews

Browse a sample dealership catalog, filter by state, create an account and publish vehicle reviews. This fork completes a local workflow for the [IBM full-stack capstone](https://github.com/ibm-developer-skills-network/xrwvm-fullstack_developer_capstone).

The default application uses Django and SQLite. Accounts, dealership records and reviews survive restarts. The original Node/MongoDB service remains available as an explicit alternative; neither MongoDB nor a cloud account is required for the local application.

## Run the local application

Requires Python 3.11 or later. Create and activate a virtual environment, then run from `server/`:

```sh
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver 127.0.0.1:8000
```

Open `http://127.0.0.1:8000/`. The seed command loads 50 example dealerships and 110 car models from the inherited course datasets. It creates no accounts, does not overwrite existing records, and can be repeated. Register through the navigation, sign in, open a dealership and post a review. Other visitors can read it immediately. Sample dealerships are not a verified business directory.

The native Django interface provides the complete workflow without a frontend build. Reviews have a 5,000-character limit. Car make, model and year must match the catalog; dates cannot be in the future. The author comes from the signed-in session, never from a client-supplied name. Passwords use Django hashing and password validators. Login, registration, logout and review writes use CSRF protection; logout requires POST.

## React frontend

The React implementation exposes the same browse, filter, registration, login, detail and review flows. It uses Vite and the same Django API:

```sh
cd server/frontend
npm ci
npm run dev
```

Keep Django running on port 8000. Add the exact Vite origin printed by the dev server to `DJANGO_CSRF_TRUSTED_ORIGINS` when starting Django (for example `http://127.0.0.1:5173`). Vite proxies `/djangoapp` to Django. The browser session is authoritative; changing session storage does not authenticate a user.

`npm run build` creates `dist/`. Production hosting of that bundle, same-origin API routing and TLS must be configured separately. The Django UI remains the simplest local launch path.

## Data and API

SQLite is stored at `server/db.sqlite3`. Back it up to preserve locally entered accounts and reviews.

| Route | Behavior |
|---|---|
| `GET /djangoapp/get_dealers` | Up to 1,000 catalog entries |
| `GET /djangoapp/get_dealers/STATE` | Case-insensitive state filtering in local mode |
| `GET /djangoapp/dealer/ID` | Dealer details, or 404 |
| `GET /djangoapp/get_dealer_reviews/ID` | Latest 200 reviews in local mode |
| `GET /djangoapp/get_cars` | Valid make/model/year options |
| `GET /djangoapp/session`, `/djangoapp/csrf` | Session state and CSRF token for the frontend |
| `POST /djangoapp/register`, `/djangoapp/login`, `/djangoapp/logout` | Account/session operations |
| `POST /djangoapp/add_review` | Validate and save the signed-in user's review; 201 on success |

Database migrations are checked in. `seed_demo` preserves existing dealership rows and user reviews. It does not create fabricated customer reviews or sentiment labels.

## Optional course services

Set `DEALERSHIP_STORAGE=remote` and `backend_url` to a running Node/MongoDB service to use the course API adapter. Authentication and the car catalog still live in Django. The data service under `server/database/` now reads data relative to its source file, seeds missing records without deleting existing reviews, and allocates review IDs through a MongoDB counter. It binds to loopback unless `HOST` is explicitly set.

The Node service is an internal development service, not a public authenticated API. Its MongoDB integration and Docker/cloud deployment need their own environment checks; the default Django tests do not prove them operational. The inherited sentiment service is not invoked by the completed local workflow. No prediction is fabricated when no model is configured.

## Validation

```sh
cd server
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
cd frontend
npm ci
npm run build
```

Tests cover registration/password checks, CSRF, login/logout, author ownership, dealer filters, persistent reviews, invalid inputs and repeatable seeding. CI runs Django checks and migrations, tests the local workflow, checks Node syntax and builds the React frontend from its lockfile.

For deployment, configure `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=0`, `DJANGO_ALLOWED_HOSTS`, HTTPS, rate limiting, backups and email/account recovery. The local application does not include these operational services. The original course materials and Apache 2.0 license are retained.

[License](LICENSE)
