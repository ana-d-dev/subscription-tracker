# SubTrack

SubTrack is a Flask web application for recording subscriptions, recurring billing details, and costs. Registered users store their data in PostgreSQL. Visitors can also try a demo whose data is held in the Flask session.

This is a portfolio project, not a production-ready subscription or payment service. It does not process payments or send billing reminders.

## Screenshots

### Home page

![SubTrack Home](static/images/home.png)

### Subscription dashboard

![SubTrack Subscriptions](static/images/my_subscriptions.png)

### Spending overview

![SubTrack Spending](static/images/total_spending.png)

## Features

- Register, log in, and manage an account.
- Create, view, edit, and delete subscriptions.
- Record service, plan, price, currency, category, billing interval, start date, duration, auto-renew setting, and notes.
- Calculate a date from the start date and billing interval, and display totals separately in EUR, USD, and GBP.
- Try subscription CRUD operations in demo mode without writing demo records to PostgreSQL. The demo is limited to three subscriptions and is intended to expire after 30 minutes of inactivity.
- Sort subscription table columns in the browser.

Supported currencies are EUR, USD, and GBP. Supported billing intervals are days, weeks, months, and years.

## Technology

- Python and Flask
- PostgreSQL and SQLAlchemy Core (the project does not use the SQLAlchemy ORM)
- Flask-WTF and WTForms
- Flask-Limiter
- Jinja2, HTML, CSS, and JavaScript
- pytest

## Project layout

```text
config/       Environment-based settings
db/           SQLAlchemy Core tables, engine, queries, and table creation
forms/        Authentication and subscription forms
security/     Password helpers, route decorators, limiter, and ID generation
services/     Billing calculations and demo-session setup
static/       CSS, JavaScript, images, and video
templates/    Jinja templates
tests/        Automated tests
main.py       Flask app and route handlers
requirements.txt
```

## Setup

Requirements: Python 3.10 or later and a PostgreSQL server.

1. Create and activate a virtual environment:

   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

   On macOS or Linux, activate it with `source .venv/bin/activate`.

2. Install the project dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

3. Create a PostgreSQL database, for example `subtrack`.

4. Create a `.env` file in the project root:

   ```env
   DB_URL=postgresql+psycopg2://username:password@localhost:5432/subtrack
   SECRET_KEY=replace-with-a-long-random-secret
   ```

   Replace the example credentials. Keep `.env` private and out of version control.

5. Create the tables and start the development server from the project root:

   ```bash
   python -m db.create_table
   python main.py
   ```

   The development server prints its local address, normally `http://127.0.0.1:5000`.

The application sets the session cookie's `Secure` flag, so browsers only send it over HTTPS. Local HTTP development may therefore not retain login or demo sessions. Use HTTPS locally or configure this flag appropriately for a local-only development environment. Do not disable secure cookies in an HTTPS deployment.

## Database tables

The app creates two tables through `db/create_table.py`:

### `subscription_users`

Stores a unique username, a Werkzeug password hash, and the account creation timestamp.

### `subscriptions`

Stores the owning user ID, service and plan details, price and currency, category, billing cycle, start and calculated payment dates, duration, auto-renew value, notes, and creation/update timestamps. Each subscription references its owner in `subscription_users`.

## Billing behavior

`services/billing.py` contains `calculate_next_payment(duration, started_on, billing_cycle)` and `total_price(subscriptions)`. The date calculation adds one specified duration to the provided start date; it does not advance old dates to the next occurrence after today. Totals are grouped by currency and are not converted between currencies.

## Validation and security notes

- Passwords are hashed with Werkzeug and authentication state is stored in Flask's signed session cookie.
- Flask-WTF forms provide CSRF tokens, and all form handlers validate on submit.
- Login and registration routes have Flask-Limiter rate limits. Rate limiting relies on the client IP; `ProxyFix` is configured to trust one forwarded address, which must match the actual trusted proxy setup when deployed.
- Subscription database queries scope records by both subscription ID and owner ID.
- The app expects `DB_URL` and `SECRET_KEY` to be set in the root `.env` file. Use a strong secret and HTTPS for any deployed instance.

This project has limited test coverage and has not received a production security review. Review deployment configuration before exposing it publicly.

## Tests

Run the current test suite from the project root:

```bash
pytest
```

At present, tests cover a basic monthly date calculation and currency-separated totals. Route, authentication, database, demo-session, and security behavior do not currently have automated test coverage.

## License

No open-source license is currently specified.
