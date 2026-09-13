from datetime import datetime, timedelta

from ai_agent.risk_engine import RiskEngine
from ai_agent.schemas import (
    AppointmentContext,
    PatientCategory,
    Urgency,
    RiskLevel,
)


def make_context(**overrides):
    data = {
        "appointment_id": "A001",
        "patient_id": "P001",
        "patient_category": PatientCategory.ROUTINE,
        "chronic_care": False,
        "urgency": Urgency.MEDIUM,
        "appointment_datetime": datetime.now() + timedelta(days=1),
        "previous_no_shows": 0,
        "previous_cancellations": 0,
        "total_previous_appointments": 5,
        "patient_confirmed": True,
    }

    data.update(overrides)

    return AppointmentContext(**data)


def test_low_risk_confirmed_patient():
    context = make_context()

    result = RiskEngine().evaluate(context)

    assert result.risk_score == 0
    assert result.risk_level == RiskLevel.LOW


def test_high_risk_multiple_no_shows():
    context = make_context(
        previous_no_shows=2,
        previous_cancellations=1,
        patient_confirmed=False,
    )

    result = RiskEngine().evaluate(context)

    assert result.risk_score == 70
    assert result.risk_level == RiskLevel.HIGH


def test_risk_score_cannot_exceed_100():
    context = make_context(
        previous_no_shows=10,
        previous_cancellations=10,
        patient_confirmed=False,
        chronic_care=True,
    )

    result = RiskEngine().evaluate(context)

    assert result.risk_score <= 100