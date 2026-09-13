from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class PatientCategory(str, Enum):
    ROUTINE = "routine"
    CHRONIC_CARE = "chronic_care"
    HIGH_PRIORITY = "high_priority"


class Urgency(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Decision(str, Enum):
    SEND_REMINDER = "SEND_REMINDER"
    OFFER_RESCHEDULE = "OFFER_RESCHEDULE"
    ESCALATE_TO_STAFF = "ESCALATE_TO_STAFF"
    NO_ACTION = "NO_ACTION"


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class AppointmentContext(BaseModel):
    appointment_id: str
    patient_id: str

    patient_category: PatientCategory
    chronic_care: bool

    urgency: Urgency

    appointment_datetime: datetime

    previous_no_shows: int = Field(ge=0)
    previous_cancellations: int = Field(ge=0)
    total_previous_appointments: int = Field(ge=0)

    patient_confirmed: bool

    alternative_slots: list[datetime] = Field(default_factory=list)


class RiskFactor(BaseModel):
    factor: str
    value: str | int | float | bool
    contribution: float


class RiskResult(BaseModel):
    risk_score: float = Field(ge=0, le=100)
    risk_level: RiskLevel
    risk_factors: list[RiskFactor]


class TriggeredRule(BaseModel):
    rule_id: str
    description: str
    priority: int


class AgentDecision(BaseModel):
    appointment_id: str

    decision: Decision

    risk_score: float = Field(ge=0, le=100)
    risk_level: RiskLevel

    reasoning: str

    risk_factors: list[RiskFactor]

    rules_triggered: list[TriggeredRule]

    recommended_slots: list[datetime]

    requires_staff: bool

    updated_status: str

    agent_version: str = "1.0.0"