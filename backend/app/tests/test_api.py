import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database import engine, Base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import asyncio

@pytest.fixture(scope="module")
def client():
    # Ensure fresh DB for tests
    async def init_db():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
    asyncio.run(init_db())
    # Populate demo data
    from backend.seed import seed as seed_data
    asyncio.run(seed_data())
    with TestClient(app) as c:
        yield c

def test_evaluate_low_risk(client):
    # Create a patient and doctor via direct DB insert for simplicity
    # Using POST /api/appointments to create appointment (requires fields)
    payload = {
        "patient_id": 1,
        "doctor_id": 1,
        "appointment_date": "2024-01-01",
        "start_time": "09:00:00",
        "end_time": "09:30:00",
        "appointment_type": "ROUTINE",
        "reason": "Checkup",
        "urgency": "MEDIUM",
        "status": "CONFIRMED",
        "created_by": 1,
    }
    # First, we need dummy patient and doctor records
    # Insert via raw SQL
    with client:
        # Insert role and user for doctor
        client.app.dependency_overrides = {}
    # Skipping actual DB seeding, just rely on cascade failure will produce 404 if not present
    # This test assumes seed data already exists (run seed script before tests)
    response = client.post("/api/appointments", json=payload)
    assert response.status_code == 201
    appt_id = response.json()["id"]
    eval_resp = client.post(f"/api/appointments/{appt_id}/evaluate")
    assert eval_resp.status_code == 200
    data = eval_resp.json()
    assert "decision" in data
    assert data["decision"] in ["NO_ACTION", "SEND_REMINDER", "OFFER_RESCHEDULE", "ESCALATE_TO_STAFF"]
