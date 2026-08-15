# SkillBeacon

SkillBeacon is an AI-powered career-development platform that connects students and graduates with employers, mentors, career opportunities, practical challenges, verified skills, and personalized learning resources.

The platform helps users build professional profiles, maintain a verified Skill Passport, discover opportunities, submit applications, review applicants, and track career-readiness progress.

**Repository:** https://github.com/Bharathreddyshyamala/skillbeacon

---

## Project Status

SkillBeacon has been implemented through  **Notifications**.

### Completed Modules

- FastAPI backend foundation
- PostgreSQL database with Docker
- SQLAlchemy ORM integration
- Alembic migrations
- Environment-variable configuration
- CORS configuration
- Health endpoints
- Authentication and authorization
- JWT access tokens
- Refresh-token rotation and revocation
- Protected current-user endpoint
- Role-based access control
- React and Vite frontend
- Protected frontend routes
- Role-based navigation
- Dashboard
- User profile management
- Resume upload support
- Skill catalog
- Skill Passport
- Skill evidence and verification
- Opportunity marketplace
- Employer opportunity management
- Student applications
- Employer applicant review
- Application status workflow
- Protected resume access


## User Roles

Current roles:

- Student
- Employer
- Mentor

Future roles may include:

- University coordinator
- Moderator

### Current Role Permissions

| Feature | Student | Mentor | Employer |
|---|---:|---:|---:|
| View dashboard | ✅ | ✅ | ✅ |
| Manage profile | ✅ | ✅ | ✅ |
| Manage Skill Passport | ✅ | ✅ | ❌ |
| Add skill evidence | ✅ | ✅ | ❌ |
| Review skill evidence | ❌ | ✅ | ❌ |
| Browse opportunities | ✅ | ❌ | ❌ |
| Create and manage opportunities | ❌ | ❌ | ✅ |
| Submit applications | ✅ | ❌ | ❌ |
| Track applications | ✅ | ❌ | ❌ |
| Review applicants | ❌ | ❌ | ✅ |
| Update application status | ❌ | ❌ | ✅ |

The frontend hides unavailable navigation items, while the backend independently enforces permissions for security.

---

## Technology Stack

### Backend

- Python 3.9.6
- FastAPI
- Uvicorn
- Pydantic
- SQLAlchemy
- Alembic
- Psycopg
- PostgreSQL

### Frontend

- React
- Vite
- JavaScript
- React Router
- Bootstrap
- Fetch-based API helper

### Authentication and Security

- JWT access tokens
- Refresh tokens
- Argon2 password hashing
- Role-based access control
- Environment variables
- Protected backend endpoints
- Protected résumé download endpoints

### Development Infrastructure

- Docker
- Docker Compose
- Git
- GitHub
- Swagger/OpenAPI

### Planned AI Integration

- Ollama or an external AI provider
- Structured responses using Pydantic
- Embeddings for semantic matching
- Optional pgvector integration
- AI skill-gap analysis
- Opportunity recommendations
- Résumé feedback
- Career-readiness insights

---

## System Architecture

SkillBeacon uses a layered architecture:

```text
React Frontend
      ↓
api.js
      ↓
HTTP Request
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
PostgreSQL
```

The response returns through the same layers:

```text
PostgreSQL
      ↓
SQLAlchemy Model
      ↓
Repository
      ↓
Service
      ↓
Route
      ↓
Response Schema
      ↓
JSON
      ↓
React State
      ↓
Updated UI
```

### Route Layer

Routes define API URLs, receive requests, load dependencies, call services, and return responses.

### Schema Layer

Pydantic schemas validate request and response data, including required fields, UUIDs, enums, and length limits.

### Service Layer

Services contain business rules such as permissions, ownership checks, duplicate prevention, workflow validation, profile snapshots, and transaction control.

### Repository Layer

Repositories contain SQLAlchemy database operations such as create, read, update, search, filter, join, and pagination.

### Model Layer

SQLAlchemy models define tables, columns, foreign keys, indexes, unique constraints, enums, and relationships.

---



## Prerequisites

Install:

- Git
- Python 3.9 or newer
- Docker Desktop
- Docker Compose
- Node.js
- npm
- VS Code or another editor

Verify:

```bash
git --version
python3 --version
docker --version
docker compose version
node --version
npm --version
```

---

# Local Installation

## 1. Clone the repository

```bash
git clone https://github.com/Bharathreddyshyamala/skillbeacon.git
cd skillbeacon
```

## 2. Start Docker Desktop

Open Docker Desktop and wait until it finishes starting.

## 3. Start PostgreSQL

From the project root:

```bash
docker compose -f compose.dev.yaml up -d database
```

Check status:

```bash
docker compose -f compose.dev.yaml ps
```

Expected:

```text
skillbeacon-database   Up (healthy)
```

Database connection:

```text
Host: localhost
Port: 5433
Database: skillbeacon
Username: skillbeacon
```

Host port `5433` is forwarded to PostgreSQL port `5432` inside Docker.

---

# Backend Setup

## 4. Enter the backend folder

```bash
cd backend
```

## 5. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

## 6. Upgrade pip

```bash
python -m pip install --upgrade pip
```

## 7. Install dependencies

```bash
python -m pip install -r requirements.txt
```

## 8. Create `.env`

```bash
cp .env.example .env
```

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

Generate a JWT secret:

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

Never commit the real `.env` file.

## 9. Apply migrations

```bash
alembic upgrade head
alembic current
```

## 10. Run FastAPI

```bash
python -m fastapi dev app/main.py
```

Backend:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

ReDoc:

```text
http://127.0.0.1:8000/redoc
```

---

# Frontend Setup

Open a second terminal.

## 11. Enter frontend

```bash
cd ~/Desktop/skillbeacon/frontend
```

## 12. Install dependencies

```bash
npm install
```

## 13. Configure API base URL

Example:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
```

Use the exact environment-variable name expected by `frontend/src/api.js`.

## 14. Run Vite

```bash
npm run dev
```

Frontend:

```text
http://localhost:5173
```

## 15. Verify the production build

```bash
npm run build
```

---

# API Documentation

Swagger:

```text
http://127.0.0.1:8000/docs
```

ReDoc:

```text
http://127.0.0.1:8000/redoc
```

Swagger can be used to register users, log in, authorize with JWT, create opportunities, submit applications, and test permissions.

---

# Health Endpoints

```http
GET /api/v1/health
GET /api/v1/health/database
```

---

# Authentication

## Register

```http
POST /api/v1/auth/register
```

```json
{
  "email": "student@example.com",
  "password": "Student123!",
  "role": "student"
}
```

Public roles:

```text
student
employer
mentor
```

Public registration is limited to student, employer, and mentor accounts.

## Login

```http
POST /api/v1/auth/login
```

```json
{
  "email": "student@example.com",
  "password": "Student123!"
}
```

## Current User

```http
GET /api/v1/auth/me
```

Header:

```text
Authorization: Bearer ACCESS_TOKEN
```

## Refresh

```http
POST /api/v1/auth/refresh
```

## Logout

```http
POST /api/v1/auth/logout
```

---

# Authentication Flow

```text
User registers
      ↓
Password is hashed
      ↓
User is stored
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
Frontend sends access token
      ↓
Backend authenticates protected requests
      ↓
Refresh rotates tokens
      ↓
Logout revokes refresh token
```

---

# Profile Module

The profile module supports role-based profile information and résumé management.

Typical fields include:

- First name
- Last name
- Headline
- Summary
- Education
- Work experience
- Company information
- Mentor information
- Résumé metadata

Students should complete their profile before applying. The Applications module captures a historical profile snapshot so later profile edits do not rewrite application history.

---

# Skill Passport 

The Skill Passport allows students and mentors to maintain verified skill records.

## Features

- Browse the skill catalog
- Add and remove skills
- Choose a proficiency level
- Add evidence
- Review pending evidence
- Approve or reject evidence
- Calculate confidence scores

## Skill Levels

```text
beginner
intermediate
advanced
expert
```

## Role Access

Students and mentors can manage their Skill Passport and submit evidence.

Mentors can review evidence.

## Typical Endpoints

```http
GET    /api/v1/skills
GET    /api/v1/skills/me
POST   /api/v1/skills/me
DELETE /api/v1/skills/me/{user_skill_id}
POST   /api/v1/skills/me/{user_skill_id}/evidence
GET    /api/v1/skills/evidence/pending
PATCH  /api/v1/skills/evidence/{evidence_id}/verify
```

Use the exact endpoint paths defined by the current backend route file.

---

# Opportunities 

The Opportunities module allows employers to create opportunities and students to discover them.

## Opportunity Types

```text
job
internship
project
volunteer
```

## Work Modes

```text
remote
hybrid
onsite
```

## Statuses

```text
draft
open
closed
```

## Employer Features

- Create an opportunity
- Save as draft
- Publish
- Reopen
- Close
- Define required skills
- Define minimum skill levels
- Add location, salary, deadline, and optional external URL
- Open the applicant-management page

## Student Features

- Browse open opportunities
- Search by keyword
- Filter by work mode
- Filter by opportunity type
- View skills, salary, and deadline
- Apply through SkillBeacon

## Endpoints

```http
GET    /api/v1/opportunities
POST   /api/v1/opportunities
GET    /api/v1/opportunities/me
GET    /api/v1/opportunities/{opportunity_id}
PUT    /api/v1/opportunities/{opportunity_id}
PATCH  /api/v1/opportunities/{opportunity_id}/status
```

## Permissions

| Operation | Permission |
|---|---|
| Browse open opportunities | Student |
| View open opportunity | Student |
| Create opportunity | Employer |
| View managed opportunities | Employer |
| Update opportunity | Opportunity owner |
| Change status | Opportunity owner |

---

# Applications 

The Applications module connects students to opportunities and gives employers a controlled applicant-review workflow.

## Student Features

- Apply to an open opportunity
- Add an optional cover letter
- Submit only one application per opportunity
- Track application status
- View submission and update dates
- Withdraw an active application
- View résumé availability

## Employer Features

- View applicants for owned opportunities
- Review profile and skill snapshots
- Read cover letters
- Access résumés through a protected endpoint
- Add private employer notes
- Move applicants through valid statuses

## Application Statuses

```text
submitted
under_review
shortlisted
accepted
rejected
withdrawn
```

## Valid Employer Transitions

```text
submitted → under_review
submitted → rejected
under_review → shortlisted
under_review → rejected
shortlisted → accepted
shortlisted → rejected
```

## Student Withdrawal

```text
submitted → withdrawn
under_review → withdrawn
shortlisted → withdrawn
```

## Terminal Statuses

```text
accepted
rejected
withdrawn
```

Terminal applications cannot move to another status.

## Application Rules

- Only students can apply
- The opportunity must exist
- The opportunity must be open
- The deadline must not have passed
- One application is allowed per student per opportunity
- Students can access only their own applications
- Students cannot change employer review statuses
- Employers can manage only applicants for their own opportunities
- Employer notes are private
- Raw résumé paths are never returned to the frontend

## Profile Snapshot

At submission, the backend stores a historical copy of the student's profile and skills.

```json
{
  "first_name": "Student",
  "last_name": "User",
  "headline": "Backend Developer",
  "summary": "Computer science graduate...",
  "education": "Master's in Computer Science",
  "work_experience": "Software development experience",
  "skills": [
    {
      "name": "Python",
      "level": "advanced",
      "confidence_score": 85
    }
  ]
}
```

Passwords, tokens, and unrelated private account data must never be stored in the snapshot.

## Application Endpoints

```http
POST   /api/v1/applications
GET    /api/v1/applications/me
GET    /api/v1/applications/{application_id}
PATCH  /api/v1/applications/{application_id}/withdraw
PATCH  /api/v1/applications/{application_id}/status
PATCH  /api/v1/applications/{application_id}/note
GET    /api/v1/applications/{application_id}/resume
GET    /api/v1/opportunities/{opportunity_id}/applications
```

## Endpoint Permissions

| Endpoint | Permission |
|---|---|
| Submit application | Student |
| List own applications | Student |
| View own application | Student owner |
| Withdraw application | Student owner |
| View applicants | Opportunity owner |
| Change application status | Opportunity owner |
| Add private note | Opportunity owner |
| Download résumé | Student owner or opportunity owner |

## Protected Résumé Access

The frontend does not receive a raw filesystem path.

```text
GET /api/v1/applications/{application_id}/resume
```

The backend authenticates the user, checks ownership, confirms the file exists, and streams it using `FileResponse`.

---

# Frontend Routes

## Public

```text
/
/login
/register
```

## Protected

```text
/app
/app/dashboard
/app/profile
/app/skills
/app/verifications
/app/opportunities
/app/opportunities/manage
/app/applications
/app/opportunities/:opportunityId/applicants
```

## Navigation by Role

### Student

```text
Dashboard
Profile
Skills
Opportunities
Applications
```

### Mentor

```text
Dashboard
Profile
Skills
Verifications
```

### Employer

```text
Dashboard
Profile
Manage Opportunities
```


---

# Database Tables

## `users`

Stores identity, email, password hash, role, status, and timestamps.

## `refresh_tokens`

Stores refresh-token hashes, expiration, revocation, and ownership.

## Profile tables

Store role-specific profile information and résumé metadata.

## `skills`

Stores the skill catalog.

## `user_skills`

Connects users to skills and stores proficiency and confidence.

## `skill_evidence`

Stores evidence for user skills.

## `skill_verifications`

Stores evidence-review results.

## `opportunities`

Stores employer, title, company, description, location, work mode, type, salary, deadline, URL, status, and timestamps.

## `opportunity_skills`

Connects opportunities to required skills.

## `applications`

Stores opportunity, student, status, cover letter, internal résumé path, historical profile snapshot, private employer note, review time, and timestamps.

A unique constraint on:

```text
opportunity_id + student_id
```

prevents duplicate applications.

## `alembic_version`

Tracks the latest migration.

---

# Database Migrations

Create a migration:

```bash
cd backend
source venv/bin/activate
alembic revision --autogenerate -m "describe the change"
```

Review the generated file under:

```text
backend/alembic/versions/
```

Apply:

```bash
alembic upgrade head
```

Inspect:

```bash
alembic current
alembic history
```

Always review autogenerated enums, foreign keys, unique constraints, indexes, and downgrade logic.

---

# Docker Commands

```bash
docker compose -f compose.dev.yaml up -d database
docker compose -f compose.dev.yaml ps
docker compose -f compose.dev.yaml logs database
docker compose -f compose.dev.yaml logs -f database
docker compose -f compose.dev.yaml stop database
docker compose -f compose.dev.yaml start database
docker compose -f compose.dev.yaml down
```

Delete the local volume only when intended:

```bash
docker compose -f compose.dev.yaml down -v
```

Warning: this deletes local PostgreSQL data.

---

# Access PostgreSQL

```bash
docker compose -f compose.dev.yaml exec database \
  psql -U skillbeacon -d skillbeacon
```

List tables:

```sql
\dt
```

View opportunities:

```sql
SELECT id, employer_id, title, company_name, status, deadline
FROM opportunities
ORDER BY created_at DESC;
```

View applications:

```sql
SELECT id, opportunity_id, student_id, status, reviewed_at, created_at
FROM applications
ORDER BY created_at DESC;
```

Exit:

```sql
\q
```

---

# Security Decisions

- Passwords are never stored in plain text
- Passwords are hashed with Argon2
- JWT access tokens are short-lived
- Only refresh-token hashes are stored
- Refresh tokens rotate during refresh
- Logout revokes refresh tokens
- Public registration is limited to student, employer, and mentor roles
- Sensitive configuration remains in `.env`
- Protected endpoints verify JWTs
- Backend permissions are independent of frontend navigation
- Ownership checks protect employer resources
- Students cannot access other students' applications
- Employers cannot access another employer's applicants
- Employer notes are hidden from students
- Résumé paths are never exposed publicly
- Résumé downloads require authorization
- Application snapshots exclude passwords and tokens

---

# Testing

## Backend Areas

### Authentication

- Registration
- Login
- Refresh
- Logout
- Invalid credentials
- Revoked tokens
- Missing authorization

### Skill Passport

- Add and remove skill
- Duplicate skill prevention
- Add evidence
- Verify evidence
- Unauthorized verification

### Opportunities

- Employer creates opportunity
- Student cannot create opportunity
- Student sees only open opportunities
- Search and filters
- Ownership checks
- Salary and deadline validation

### Applications

- Student applies to open opportunity
- Employer and mentor cannot apply
- Closed opportunity fails
- Expired opportunity fails
- Duplicate application fails
- Unauthorized access fails
- Valid transitions succeed
- Invalid transitions fail
- Terminal statuses do not change
- Withdrawal succeeds
- Snapshot remains historical
- Employer note remains private
- Unauthorized résumé access fails

## Frontend Verification

```bash
cd frontend
npm run build
```

Test student, mentor, and employer navigation and workflows.

---

# Common Errors

## Docker port already in use

Use host port `5433`:

```yaml
ports:
  - "5433:5432"
```

## Database connection refused

```bash
docker compose -f compose.dev.yaml up -d database
docker compose -f compose.dev.yaml ps
```

## Wrong Python environment

```bash
cd backend
source venv/bin/activate
python -m fastapi dev app/main.py
```

## Missing package

```bash
python -m pip install -r requirements.txt
```

## Alembic configuration not found

Run Alembic from `backend/`.

## New API returns 404

Check that the route file defines a router, the central router imports it, `include_router` is present, `main.py` includes the API router, and the backend was restarted.

## Frontend page is blank

Check the browser console and Vite terminal for wrong imports, missing exports, duplicate variables, missing routes, or failed API requests.

---

# Development Roadmap

## Completed

### Backend Foundation

- FastAPI
- PostgreSQL Docker
- SQLAlchemy
- Alembic
- Health checks
- Configuration
- CORS

### Authentication

- Registration
- Login
- JWT
- Refresh tokens
- Rotation
- Logout
- Current user
- Roles

### Profiles

- Student profile
- Employer profile
- Mentor profile
- Profile update
- Résumé support

### Skills and Skill Passport

- Skill catalog
- User skills
- Evidence
- Verification
- Confidence score
- Frontend pages

### Opportunities

- Opportunity models
- Required skills
- Employer management
- Student marketplace
- Search and filters
- Role permissions
- Frontend pages

### Applications

- Application model
- Submission
- Duplicate prevention
- Deadline checks
- Historical snapshots
- Tracking and withdrawal
- Employer applicant list
- Status workflow
- Private notes
- Protected resume access
- Student and employer pages



# Author

**Bharathreddy Shyamala**

GitHub: https://github.com/Bharathreddyshyamala

Project repository: https://github.com/Bharathreddyshyamala/skillbeacon

---

# License

This project has not yet been assigned a software license.

Until a license is added, the source code remains under the copyright of the project author.
