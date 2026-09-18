# SubTrack

SubTrack is a subscription tracking web application built with Python and Flask.

The application allows users to create an account, manage their subscriptions,
track recurring payments, and view their subscription costs. It also includes
a demo mode that allows visitors to try the application without creating an
account.

The project was created as a portfolio project to practice backend web
development, database design, authentication, form validation, database
operations, testing, and application structure.

---

## Screenshots

### Home page

![SubTrack Home](static/images/home.png)

### Subscription dashboard

![SubTrack Subscriptions](static/images/my_subscriptions.png)

### Spending overview

![SubTrack Spending](static/images/total_spending.png)

---

## Features

### User authentication

- User registration
- User login and logout
- Password hashing
- Session-based authentication
- Protected routes for authenticated users
- Login and registration rate limiting
- CSRF protection through Flask-WTF

### Subscription management

Authenticated users can:

- Add subscriptions
- View all their subscriptions
- View subscription details
- Edit subscriptions
- Edit subscription notes
- Delete subscriptions
- Organize subscriptions by category
- Select subscription currencies
- Set billing cycles
- Set subscription duration
- Calculate the next payment date
- Enable or disable automatic payment
- Add notes to subscriptions

Supported currencies:

- EUR
- USD
- GBP

Supported billing cycles:

- Days
- Weekly
- Monthly
- Yearly

### Demo mode

SubTrack provides a demo mode so visitors can try the application without
creating an account.

Demo data is stored in the Flask session rather than the PostgreSQL database.

The demo session:

- Allows users to add subscriptions
- Supports editing subscriptions
- Supports editing notes
- Supports deleting subscriptions
- Calculates subscription totals
- Automatically expires after 30 minutes of inactivity

Demo data is temporary and does not modify the permanent PostgreSQL
database.

### Subscription calculations

The application calculates the next payment date based on:

- Billing cycle
- Duration
- Starting date

Supported calculations include:

- Days
- Weeks
- Months
- Years

The application also calculates subscription totals separately for EUR,
USD, and GBP.

---

## Technology Stack

### Backend

- Python
- Flask
- SQLAlchemy Core
- PostgreSQL
- Flask-WTF
- WTForms
- Flask-Limiter
- Werkzeug

### Frontend

- HTML
- CSS
- Jinja2
- JavaScript

### Database

PostgreSQL is used as the application's relational database.

SQLAlchemy Core is used for:

- Database connections
- Table definitions
- SELECT queries
- INSERT queries
- UPDATE queries
- DELETE queries

The project does not use SQLAlchemy ORM.

### Testing

- pytest

### Security

The application includes several security-related mechanisms:

- Password hashing using Werkzeug
- Session-based authentication
- CSRF protection through Flask-WTF
- Login and registration rate limiting
- User-specific database queries
- Environment variables for sensitive configuration

---

## Project Structure

```text
subscription_track/
│
├── config/
│   ├── __init__.py
│   └── settings.py
│
├── db/
│   ├── __init__.py
│   ├── create_table.py
│   ├── engine.py
│   ├── queries.py
│   └── tables.py
│
├── forms/
│   ├── __init__.py
│   ├── auth_forms.py
│   └── subscription_forms.py
│
├── security/
│   ├── __init__.py
│   ├── decorators.py
│   ├── hashing.py
│   ├── limiter.py
│   └── tokens.py
│
├── services/
│   ├── __init__.py
│   ├── billing.py
│   └── demo.py
│
├── static/
│   ├── css/
│   │   └── styles.css
│   ├── images/
│   ├── js/
│   └── videos/
│
├── templates/
│
├── tests/
│   ├── __init__.py
│   └── test_billing.py
│
├── .gitignore
├── .env
├── main.py
└── requirements.txt
```

The `.env` file contains local configuration and should not be committed to
the repository.

---

## Database Structure

SubTrack uses two main PostgreSQL tables.

### `subscription_users`

Stores user account information.

| Column | Description |
|---|---|
| `id` | Unique user identifier |
| `username` | Unique username |
| `hashed_password` | Hashed user password |
| `created_at` | Account creation timestamp |

### `subscriptions`

Stores subscription information belonging to users.

| Column | Description |
|---|---|
| `id` | Unique subscription identifier |
| `user_id` | User who owns the subscription |
| `service` | Subscription service name |
| `price` | Subscription price |
| `currency` | EUR, USD, or GBP |
| `category` | Subscription category |
| `plan` | Subscription plan |
| `billing_cycle` | Billing frequency |
| `started_on` | Subscription start date |
| `next_payment` | Next calculated payment date |
| `duration` | Billing duration |
| `auto_renew` | Automatic payment status |
| `notes` | Optional subscription notes |
| `created_at` | Creation timestamp |
| `updated_at` | Last update timestamp |

The `subscriptions.user_id` column is a foreign key referencing
`subscription_users.id`.

---

## Authentication

User authentication is handled using Flask sessions.

When a user successfully logs in, their user ID is stored in the session.

Protected routes use a custom `login_required` decorator to ensure that
only authenticated users can access them.

Passwords are never stored directly in the database.

Instead, passwords are hashed using Werkzeug:

```python
generate_password_hash(password)
```

During login, the submitted password is checked against the stored hash using:

```python
check_password_hash(hashed_password, password)
```

---

## Form Validation

SubTrack uses Flask-WTF and WTForms for server-side form validation.

### Registration validation

Usernames must:

- Contain between 4 and 10 characters
- Contain only letters and numbers

Passwords must:

- Contain between 8 and 21 characters
- Contain at least two letters
- Contain at least two digits
- Contain at least two special characters

### Subscription validation

Subscription forms validate fields such as:

- Service name
- Price
- Currency
- Billing cycle
- Duration
- Start date
- Plan
- Category
- Notes
- Automatic payment

This ensures that invalid input is rejected by the server before it is
stored in the database.

---

## Demo Mode

The demo mode allows visitors to explore the application without creating
an account.

Demo subscriptions are stored in the Flask session.

The demo session contains:

```text
demo_all_subscriptions
demo_total
demo_last_activity
```

The demo session has a 30-minute inactivity timeout.

When the timeout is exceeded, the temporary subscription data is removed and
a new demo session can be started.

This means that changes made inside demo mode do not modify the PostgreSQL
database.

---

## Billing Logic

The subscription calculation logic is separated from the Flask routes in:

```text
services/billing.py
```

The `calculate_next_payment()` function uses the subscription's:

- Start date
- Duration
- Billing cycle

to calculate the next payment date.

For example:

```python
calculate_next_payment(
    3,
    date(2027, 1, 1),
    "monthly"
)
```

returns:

```text
2027-04-01
```

The `total_price()` function calculates subscription totals separately for
each supported currency.

---

## Database Access

The project uses SQLAlchemy Core rather than SQLAlchemy ORM.

Database operations are separated into:

```text
db/
├── engine.py
├── queries.py
├── tables.py
└── create_table.py
```

### `tables.py`

Defines the PostgreSQL database tables and their columns.

### `engine.py`

Creates the SQLAlchemy database engine and metadata object.

### `queries.py`

Contains database operations such as:

- Finding users
- Creating users
- Finding subscriptions
- Creating subscriptions
- Updating subscriptions
- Deleting subscriptions

### `create_table.py`

Creates the database tables using SQLAlchemy metadata.

---

## Application Architecture

The project separates different responsibilities into dedicated modules.

```text
main.py
    │
    ├── Routes
    │
    ├── Forms
    │
    ├── Security
    │
    ├── Services
    │
    └── Database
```

### `main.py`

Contains the Flask application and application routes.

### `forms/`

Contains WTForms classes used for:

- Registration
- Login
- Adding subscriptions
- Editing subscriptions
- Deleting subscriptions

### `db/`

Contains database table definitions, the SQLAlchemy engine, and database
queries.

### `security/`

Contains:

- Authentication decorators
- Password hashing
- Rate limiting
- Token generation utilities

### `services/`

Contains application business logic such as:

- Billing calculations
- Demo session management

### `templates/`

Contains the Jinja2 HTML templates used by Flask.

### `static/`

Contains:

- CSS
- JavaScript
- Images
- Videos

### `tests/`

Contains automated tests written with pytest.

---

## Testing

The project uses pytest for automated testing.

Tests are located in:

```text
tests/
```

Run the test suite with:

```bash
pytest
```

The current tests cover billing functionality, including:

- Next payment date calculation
- Subscription total calculation

Example:

```python
def test_calculate_next_payment():
    started_on = date(2027, 1, 1)

    assert calculate_next_payment(
        3,
        started_on,
        "monthly"
    ) == date(2027, 4, 1)
```

---

## Environment Variables

Sensitive configuration is stored in a `.env` file.

Example:

```env
DB_URL=postgresql+psycopg2://username:password@localhost:5432/subtrack
SECRET_KEY=your-secret-key
```

Replace the database username, password, host, port, and database name with
your PostgreSQL configuration.

The `.env` file should not be committed to Git.

Recommended `.gitignore` entries include:

```text
.env
.venv/
venv/
__pycache__/
.pytest_cache/
```

---

## Installation

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd subscription_track
```

Replace `YOUR_GITHUB_REPOSITORY_URL` with the URL of your GitHub repository.

### 2. Create a virtual environment

On Windows:

```bash
python -m venv .venv
```

Activate the virtual environment:

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create the PostgreSQL database

Create a PostgreSQL database for the application.

For example:

```text
subtrack
```

Then configure the connection string in `.env`:

```env
DB_URL=postgresql+psycopg2://username:password@localhost:5432/subtrack
SECRET_KEY=your-secret-key
```

### 5. Create the database tables

Run:

```bash
python db/create_table.py
```

This creates the tables defined in `db/tables.py`.

### 6. Run the application

Start the Flask application:

```bash
python main.py
```

The application will normally be available at:

```text
http://127.0.0.1:5000
```

---

## Requirements

The project uses the following main Python packages:

```text
Flask
Flask-Limiter
Flask-WTF
SQLAlchemy
psycopg2-binary
python-dateutil
python-dotenv
pytest
WTForms
```

The current `requirements.txt` was generated using `pip freeze`.

If the environment contains packages unrelated to SubTrack, they should be
removed from `requirements.txt` before the final repository is published.

For example, Django-related packages are not used by the application shown
in this project.

---

## Security Considerations

The application uses several security mechanisms appropriate for a Flask
application:

- Passwords are hashed before storage.
- CSRF protection is provided by Flask-WTF.
- Authentication is handled using Flask sessions.
- Protected routes verify the authenticated user.
- Subscription queries filter by both subscription ID and user ID.
- Login and registration endpoints use rate limiting.
- Sensitive configuration is stored using environment variables.
- Demo data is kept separate from permanent database data.

The application is a portfolio project and should not be considered a
production-ready security implementation without additional security review,
testing, and configuration.

---

## Future Improvements

Possible future improvements include:

- More comprehensive automated test coverage
- Additional spending analytics
- Improved charts and reporting
- Email notifications for upcoming payments
- Password reset functionality
- Improved profile management
- API endpoints
- More advanced subscription filtering
- Additional currency functionality
- Production deployment improvements

---

## Project Purpose

SubTrack was created as a portfolio project to practice building a complete
backend web application.

The project demonstrates practical experience with:

- Python
- Flask
- PostgreSQL
- SQLAlchemy Core
- Authentication
- Password hashing
- Flask sessions
- WTForms
- Server-side validation
- Database design
- CRUD operations
- Business logic separation
- pytest
- HTML and CSS
- Jinja2 templates
- Basic web application security

The main goal of the project is to demonstrate how these technologies can be
combined into a structured web application rather than to provide a
production SaaS platform.

---

## License

This project was created as a portfolio project.

If you decide to publish the project under an open-source license, add the
appropriate license information here.