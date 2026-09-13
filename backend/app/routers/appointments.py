from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from ..database import get_db
from ..models import Appointment, AIDecision, AppointmentStatus, AIDecisionEnum
from ai_agent.agent import AppointmentAgent
from ai_agent.schemas import AppointmentContext, Decision
import datetime

router = APIRouter()

@router.get("/", response_model=list[dict])
async def list_appointments(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Appointment))
    appointments = result.scalars().all()
    return [
        {
            "id": a.id,
            "patient_id": a.patient_id,
            "doctor_id": a.doctor_id,
            "date": a.appointment_date,
            "start_time": a.start_time,
            "status": a.status.value,
        }
        for a in appointments
    ]

@router.get("/{appointment_id}", response_model=dict)
async def get_appointment(appointment_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Appointment).where(Appointment.id == appointment_id))
    appointment = result.scalar_one_or_none()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return {
        "id": appointment.id,
        "patient_id": appointment.patient_id,
        "doctor_id": appointment.doctor_id,
        "date": appointment.appointment_date,
        "start_time": appointment.start_time,
        "status": appointment.status.value,
    }

@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_appointment(payload: dict, db: AsyncSession = Depends(get_db)):
    # Very simple creation, expects keys matching model fields
    new_appt = Appointment(**payload)
    db.add(new_appt)
    await db.commit()
    await db.refresh(new_appt)
    return {"id": new_appt.id}

@router.post("/{appointment_id}/confirm")
async def confirm_appointment(appointment_id: int, db: AsyncSession = Depends(get_db)):
    await db.execute(
        update(Appointment)
        .where(Appointment.id == appointment_id)
        .values(status=AppointmentStatus.CONFIRMED)
    )
    await db.commit()
    return {"status": "confirmed"}

@router.post("/{appointment_id}/cancel")
async def cancel_appointment(appointment_id: int, db: AsyncSession = Depends(get_db)):
    await db.execute(
        update(Appointment)
        .where(Appointment.id == appointment_id)
        .values(status=AppointmentStatus.CANCELLED)
    )
    await db.commit()
    return {"status": "cancelled"}

@router.post("/{appointment_id}/reschedule")
async def reschedule_appointment(appointment_id: int, payload: dict, db: AsyncSession = Depends(get_db)):
    # payload expects new date and times
    await db.execute(
        update(Appointment)
        .where(Appointment.id == appointment_id)
        .values(**payload, status=AppointmentStatus.RESCHEDULED)
    )
    await db.commit()
    return {"status": "rescheduled"}

@router.post("/{appointment_id}/evaluate", response_model=dict)
async def evaluate_appointment(appointment_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Appointment).where(Appointment.id == appointment_id))
    appointment = result.scalar_one_or_none()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    # Build minimal context using available fields and defaults
    ctx = AppointmentContext(
        appointment_id=str(appointment.id),
        patient_id=str(appointment.patient_id),
        patient_category="routine",  # default
        chronic_care=False,
        urgency=appointment.urgency.value.lower(),
        appointment_datetime=datetime.datetime.combine(appointment.appointment_date, appointment.start_time),
        previous_no_shows=0,
        previous_cancellations=0,
        total_previous_appointments=0,
        patient_confirmed=False,
        alternative_slots=[],
    )
    decision_obj = AppointmentAgent().evaluate(ctx)
    # Persist decision
    ai_decision = AIDecision(
        appointment_id=appointment.id,
        risk_score=int(decision_obj.risk_score),
        decision=AIDecisionEnum(decision_obj.decision.value),
        reasoning=decision_obj.reasoning,
        confidence=100,
    )
    db.add(ai_decision)
    await db.commit()
    await db.refresh(ai_decision)
    # Update appointment status based on decision (convert string to Enum if needed)
    try:
        new_status_enum = getattr(AppointmentStatus, decision_obj.updated_status)
    except AttributeError:
        # Fallback to original string (SQLAlchemy may coerce)
        new_status_enum = decision_obj.updated_status
    await db.execute(
        update(Appointment)
        .where(Appointment.id == appointment.id)
        .values(status=new_status_enum)
    )
    await db.commit()
    return {
        "decision": decision_obj.decision.value,
        "risk_score": decision_obj.risk_score,
        "risk_level": decision_obj.risk_level.value,
        "reasoning": decision_obj.reasoning,
        "requires_staff": decision_obj.requires_staff,
        "updated_status": decision_obj.updated_status,
    }
