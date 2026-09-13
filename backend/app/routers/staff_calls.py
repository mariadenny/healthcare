from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..database import get_db
from ..models import Appointment, AppointmentStatus, Urgency, CallPriority

router = APIRouter()

@router.get("/queue", response_model=list[dict])
async def staff_queue(db: AsyncSession = Depends(get_db)):
    # Appointments needing staff attention: high risk, critical urgency, high priority, pending reminders, reschedule offers
    stmt = select(Appointment).where(
        (Appointment.urgency.in_([Urgency.HIGH, Urgency.CRITICAL])) |
        (Appointment.status.in_([
            AppointmentStatus.STAFF_REVIEW,
            AppointmentStatus.RESCHEDULED,
            AppointmentStatus.SCHEDULED,
        ]))
    )
    result = await db.execute(stmt)
    appointments = result.scalars().all()
    return [
        {
            "id": a.id,
            "patient_id": a.patient_id,
            "doctor_id": a.doctor_id,
            "date": a.appointment_date,
            "status": a.status.value,
            "urgency": a.urgency.value,
        }
        for a in appointments
    ]
