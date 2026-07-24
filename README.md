# SkillBeacon

SkillBeacon is an AI-powered career-development platform designed to connect students and graduates with employers, mentors, career opportunities, practical challenges, and personalized learning resources.

The long-term goal of SkillBeacon is to help users identify skill gaps, build verified portfolios, receive mentorship, complete employer challenges, discover suitable opportunities, and track their overall career readiness.

Repository: https://github.com/Bharathreddyshyamala/skillbeacon

---

## Project Status

The project is currently in the backend-foundation stage.

The following features have been completed:

* FastAPI backend setup
* API routing structure
* PostgreSQL database running with Docker
* SQLAlchemy database integration
* Alembic database migrations
* User database model
* Refresh-token database model
* User registration
* User login
* Secure password hashing
* JWT access-token generation
* Refresh-token generation and rotation
* Logout and refresh-token revocation
* Current authenticated-user endpoint
* Basic role support
* Role-based dependency foundation
* FastAPI health endpoint
* PostgreSQL health endpoint
* Swagger API documentation
* Environment-variable configuration
* CORS configuration

---

## Planned Platform Features

SkillBeacon will eventually support the following user roles:

* Student or graduate
* Employer
* Mentor
* University coordinator
* Moderator
* Administrator

Planned features include:

* Student, employer, and mentor profiles
* Resume uploads
* Opportunity marketplace
* Internship and job applications
* Verified skill passport
* Skill evidence and mentor verification
* Employer challenges
* Mentorship requests and programs
* Career-readiness score
* Personalized learning roadmaps
* AI skill-gap analysis
* AI resume feedback
* AI cover-letter generation
* Opportunity recommendations
* Application feedback
* Moderation and trust system
* Notifications
* Analytics dashboards
* Docker-based deployment
* CI/CD with GitHub Actions

---

## Technology Stack

### Backend

* Python
* FastAPI
* Uvicorn
* Pydantic
* SQLAlchemy
* Alembic
* Psycopg
* PostgreSQL

### Authentication and Security

* JWT access tokens
* Refresh tokens
* Argon2 password hashing
* Role-based access control
* Environment variables

### Development Infrastructure

* Docker
* Docker Compose
* Git
* GitHub

### Planned Frontend

* React
* Vite
* JavaScript
* Bootstrap
* React Router
* Axios

### Planned AI Integration

* Ollama or an external AI provider
* Structured AI responses using Pydantic
* Embeddings for semantic matching
* Optional pgvector integration

---

## Current Architecture

The backend follows a layered architecture:

```text
Client or Frontend
        ↓
FastAPI Route
        ↓
Pydantic Schema
        ↓
Service Layer
        ↓
Repository Layer
        ↓
SQLAlchemy Model
        ↓
PostgreSQL Database
```

### Route Layer

Routes receive HTTP requests and return HTTP responses.

Example:

```text
POST /api/v1/auth/register
```

### Schema Layer

Pydantic schemas validate request and response data.

### Service Layer

Services contain business logic such as:

* Checking duplicate users
* Hashing passwords
* Authenticating users
* Generating tokens
* Revoking refresh tokens

### Repository Layer

Repositories contain direct database operations.

### Model Layer

SQLAlchemy models define PostgreSQL tables and relationships.

---

## Project Structure

```text
skillbeacon/
│
├── compose.dev.yaml
├── .gitignore
├── README.md
│
└── backend/
    ├── .env.example
    ├── requirements.txt
    ├── alembic.ini
    │
    ├── alembic/
    │   ├── env.py
    │   └── versions/
    │
    ├── app/
    │   ├── main.py
    │   │
    │   ├── api/
    │   │   ├── router.py
    │   │   ├── dependencies.py
    │   │   │
    │   │   └── routes/
    │   │       ├── health_routes.py
    │   │       └── auth_routes.py
    │   │
    │   ├── core/
    │   │   ├── config.py
    │   │   ├── database.py
    │   │   └── security.py
    │   │
    │   ├── models/
    │   │   ├── base.py
    │   │   ├── user.py
    │   │   ├── refresh_token.py
    │   │   └── __init__.py
    │   │
    │   ├── schemas/
    │   │   └── auth_schema.py
    │   │
    │   ├── repositories/
    │   │   ├── user_repository.py
    │   │   └── refresh_token_repository.py
    │   │
    │   └── services/
    │       └── auth_service.py
    │
    └── venv/
```

The local virtual environment and `.env` file are not committed to GitHub.

---

## Prerequisites

Install the following software before running the project:

* Git
* Python 3.9 or newer
* Python 3.11 recommended
* Docker Desktop
* Docker Compose
* VS Code or another code editor

Verify the installations:

```bash
git --version
python3 --version
docker --version
docker compose version
```

---

## Local Installation

### 1. Clone the repository

```bash
git clone https://github.com/Bharathreddyshyamala/skillbeacon.git
cd skillbeacon
```

---

### 2. Start Docker Desktop

Open Docker Desktop and wait until Docker finishes starting.

Verify:

```bash
docker --version
docker compose version
```

---

### 3. Start PostgreSQL

From the root `skillbeacon` folder, run:

```bash
docker compose -f compose.dev.yaml up -d database
```

Check the container status:

```bash
docker compose -f compose.dev.yaml ps
```

Expected result:

```text
skillbeacon-database   Up (healthy)
```

The local PostgreSQL port is configured as:

```text
localhost:5433
```

Port `5433` on the Mac is forwarded to PostgreSQL port `5432` inside the Docker container.

---

### 4. Enter the backend folder

```bash
cd backend
```

---

### 5. Create a Python virtual environment

Using Python 3.11:

```bash
python3.11 -m venv venv
```

If Python 3.11 is unavailable:

```bash
python3 -m venv venv
```

Activate the environment on macOS or Linux:

```bash
source venv/bin/activate
```

The terminal prompt should begin with:

```text
(venv)
```

---

### 6. Upgrade pip

```bash
python -m pip install --upgrade pip
```

---

### 7. Install dependencies

```bash
python -m pip install -r requirements.txt
```

---

### 8. Create the environment file

Copy the example file:

```bash
cp .env.example .env
```

Open `.env` and configure the values.

Example:

```env
APP_NAME=SkillBeacon
APP_ENV=development
DEBUG=true

DATABASE_URL=postgresql+psycopg://skillbeacon:development_password@localhost:5433/skillbeacon

JWT_SECRET_KEY=replace_with_a_secure_random_secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

FRONTEND_URL=http://localhost:5173
```

Generate a secure JWT secret:

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

Copy the generated value into:

```env
JWT_SECRET_KEY=generated_value
```

Never commit the real `.env` file.

---

### 9. Apply database migrations

Run:

```bash
alembic upgrade head
```

Check the current migration:

```bash
alembic current
```

---

### 10. Run the FastAPI backend

```bash
python -m fastapi dev app/main.py
```

The backend should run at:

```text
http://127.0.0.1:8000
```

---

## API Documentation

Open Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

Alternative API documentation:

```text
http://127.0.0.1:8000/redoc
```

---

## Health Endpoints

### Backend health

```http
GET /api/v1/health
```

Example response:

```json
{
  "status": "ok",
  "service": "skillbeacon-backend"
}
```

### Database health

```http
GET /api/v1/health/database
```

Example response:

```json
{
  "status": "ok",
  "database": "connected"
}
```

---

## Authentication Endpoints

### Register a user

```http
POST /api/v1/auth/register
```

Example request:

```json
{
  "email": "student@example.com",
  "password": "Student123!",
  "role": "student"
}
```

Supported public registration roles:

```text
student
employer
mentor
```

Moderator and administrator accounts cannot be created through public registration.

---

### Log in

```http
POST /api/v1/auth/login
```

Example request:

```json
{
  "email": "student@example.com",
  "password": "Student123!"
}
```

Example response:

```json
{
  "access_token": "jwt-access-token",
  "refresh_token": "random-refresh-token",
  "token_type": "bearer",
  "user": {
    "id": "user-uuid",
    "email": "student@example.com",
    "role": "student",
    "is_active": true,
    "is_verified": false,
    "created_at": "timestamp",
    "updated_at": "timestamp"
  }
}
```

---

### Get the current authenticated user

```http
GET /api/v1/auth/me
```

Required header:

```text
Authorization: Bearer ACCESS_TOKEN
```

---

### Refresh authentication tokens

```http
POST /api/v1/auth/refresh
```

Example request:

```json
{
  "refresh_token": "current-refresh-token"
}
```

The backend revokes the old refresh token and returns a new access token and refresh token.

---

### Log out

```http
POST /api/v1/auth/logout
```

Example request:

```json
{
  "refresh_token": "current-refresh-token"
}
```

Logout revokes the submitted refresh token.

---

## Authentication Flow

```text
User registers
      ↓
Password is hashed
      ↓
User is stored in PostgreSQL
      ↓
User logs in
      ↓
Password is verified
      ↓
Access token is generated
      ↓
Refresh token is generated
      ↓
Refresh-token hash is stored
      ↓
Client uses access token for protected endpoints
```

---

## Database Tables

### `users`

Stores:

* User ID
* Email
* Password hash
* Role
* Active status
* Verification status
* Creation timestamp
* Update timestamp

### `refresh_tokens`

Stores:

* Token ID
* User ID
* Refresh-token hash
* Expiration date
* Revocation date
* Creation timestamp
* Update timestamp

### `alembic_version`

Tracks the latest database migration applied to PostgreSQL.

---

## Database Migrations

Create a migration after changing a SQLAlchemy model:

```bash
alembic revision --autogenerate -m "describe the database change"
```

Review the generated migration inside:

```text
backend/alembic/versions/
```

Apply the migration:

```bash
alembic upgrade head
```

Check the migration state:

```bash
alembic current
```

View migration history:

```bash
alembic history
```

Do not manually modify production tables when an Alembic migration can be used.

---

## Docker Commands

Start PostgreSQL:

```bash
docker compose -f compose.dev.yaml up -d database
```

Check status:

```bash
docker compose -f compose.dev.yaml ps
```

View logs:

```bash
docker compose -f compose.dev.yaml logs database
```

Follow logs continuously:

```bash
docker compose -f compose.dev.yaml logs -f database
```

Stop PostgreSQL:

```bash
docker compose -f compose.dev.yaml stop database
```

Start an existing stopped container:

```bash
docker compose -f compose.dev.yaml start database
```

Remove the container and network while keeping database data:

```bash
docker compose -f compose.dev.yaml down
```

Remove the container, network, and database volume:

```bash
docker compose -f compose.dev.yaml down -v
```

Warning: `down -v` deletes the local PostgreSQL data.

---

## Access PostgreSQL Manually

From the project root:

```bash
docker compose -f compose.dev.yaml exec database \
  psql -U skillbeacon -d skillbeacon
```

List tables:

```sql
\dt
```

Exit PostgreSQL:

```sql
\q
```

---

## Security Decisions

The project currently follows these security practices:

* Passwords are never stored in plain text
* Passwords are hashed using Argon2
* JWT access tokens are short-lived
* Refresh tokens are randomly generated
* Only refresh-token hashes are stored in PostgreSQL
* Refresh tokens are rotated during refresh
* Refresh tokens are revoked during logout
* Public users cannot register as moderators or administrators
* Sensitive values are stored in `.env`
* `.env` is excluded from Git
* Protected endpoints verify the user through JWT
* User activity can later be restricted by role

---

## Common Errors

### Docker port already in use

The project uses host port `5433` because port `5432` may already be occupied.

Confirm `compose.dev.yaml` contains:

```yaml
ports:
  - "5433:5432"
```

Confirm `.env` contains:

```env
DATABASE_URL=postgresql+psycopg://skillbeacon:development_password@localhost:5433/skillbeacon
```

---

### Docker daemon unavailable

Open Docker Desktop and wait until it finishes starting.

Then run:

```bash
docker compose -f compose.dev.yaml ps
```

---

### Database connection refused

Confirm the PostgreSQL container is running:

```bash
docker compose -f compose.dev.yaml up -d database
docker compose -f compose.dev.yaml ps
```

---

### FastAPI command uses the wrong Python installation

Run FastAPI through the active virtual environment:

```bash
python -m fastapi dev app/main.py
```

---

### Missing Python package

Activate the virtual environment and reinstall dependencies:

```bash
source venv/bin/activate
python -m pip install -r requirements.txt
```

---

### Alembic cannot find configuration

Run Alembic from the backend folder:

```bash
cd backend
alembic current
```

---

### `.env` is not loading

Make sure the file exists here:

```text
backend/.env
```

Test the loaded database URL:

```bash
python -c "from app.core.config import settings; print(settings.database_url)"
```

---

## Development Roadmap

### Completed

* Project setup
* Backend structure
* FastAPI application
* PostgreSQL Docker container
* SQLAlchemy connection
* Alembic configuration
* User model
* Refresh-token model
* Registration
* Login
* JWT authentication
* Refresh-token rotation
* Logout
* Current-user endpoint
* Health endpoints

### Next

* Student profile
* Employer profile
* Mentor profile
* Profile update endpoints
* Resume upload
* Skill catalog
* User skills
* Skill evidence
* Public profile pages

### Future Modules

* Opportunity marketplace
* Applications
* Mentorship
* Employer challenges
* Notifications
* Moderation
* AI skill-gap analyzer
* AI cover-letter generator
* Rule-based recommendations
* Career-readiness score
* Analytics dashboards
* Frontend application
* Production deployment

---

## Suggested Git Workflow

Update the local main branch:

```bash
git checkout main
git pull origin main
```

Create a feature branch:

```bash
git checkout -b feature/profile-module
```

Commit changes:

```bash
git add .
git commit -m "Implement profile module"
```

Push the branch:

```bash
git push -u origin feature/profile-module
```

Create a pull request on GitHub and merge the branch after reviewing it.

---

## Contributing

This project is currently under active development.

For each new backend module, follow this pattern:

```text
Model
  ↓
Alembic migration
  ↓
Pydantic schema
  ↓
Repository
  ↓
Service
  ↓
Route
  ↓
API test
```

Keep routes small and place business logic in services.

---

## Author

**Bharathreddy Shyamala**

GitHub: https://github.com/Bharathreddyshyamala

Project repository: https://github.com/Bharathreddyshyamala/skillbeacon

---

## License

This project has not yet been assigned a software license.

Until a license is added, the source code remains under the copyright of the project author.
