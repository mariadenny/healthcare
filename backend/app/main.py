from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .database import engine, Base
from .routers import (
    auth,
    health,
    patients,
    doctors,
    appointments,
    availability,
    ai,
    notifications,
    staff_calls,
    analytics,
    admin,
)

app = FastAPI(title="Healthcare Appointment Flow Optimizer", version="0.1.0")

# CORS settings – allow frontend origin defined in env
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create DB tables on startup (for dev; production uses Alembic)
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"]) 
app.include_router(health.router, tags=["health"]) 
app.include_router(patients.router, prefix="/api/patients", tags=["patients"]) 
app.include_router(doctors.router, prefix="/api/doctors", tags=["doctors"]) 
app.include_router(appointments.router, prefix="/api/appointments", tags=["appointments"]) 
app.include_router(availability.router, prefix="/api/availability", tags=["availability"]) 
app.include_router(ai.router, prefix="/api/agent", tags=["ai"]) 
app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"]) 
app.include_router(staff_calls.router, prefix="/api/staff", tags=["staff_calls"]) 
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"]) 
app.include_router(admin.router, prefix="/api/admin", tags=["admin"]) 
