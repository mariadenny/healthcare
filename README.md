# Healthcare Appointment Flow Optimizer

A collaborative hackathon project aimed at streamlining healthcare clinic workflows, minimizing patient wait times, predicting appointment cancellations/no-shows, and optimizing doctor-patient scheduling.

## Repository Overview

This repository is shared by a 4-person team and contains the following core components:
- **`backend/`**: Built with FastAPI. Responsible for core business logic, REST APIs, appointment lifecycle management, data validation, database orchestration, and serving AI model inferences.
- **`frontend/`**: The web application and user interface for clinic staff, healthcare providers, and patients.
- **`ai/`**: Machine learning models and optimization algorithms for wait-time predictions, no-show analysis, and intelligent slot scheduling.
- **`database/`**: Database schemas, relational models, migrations, and seed scripts.

## Backend Structure

The FastAPI backend is structured modularly under `backend/`:
```text
backend/
├── app/
│   ├── models/     # Database entities and ORM models
│   ├── schemas/    # Pydantic schemas for request/response validation
│   ├── routers/    # API endpoints grouped by resource
│   ├── services/   # Business logic and external service integrations
│   └── utils/      # Shared helpers, dependencies, and configuration
└── tests/          # Unit and integration test suites
```
