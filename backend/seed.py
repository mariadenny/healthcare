import sys, os
sys.path.append(os.path.abspath("."))
from datetime import date, time

from backend.app.database import engine, AsyncSessionLocal
from backend.app.models import Base, User, Role, RoleName, Permission, PermissionName, Patient, Doctor, Appointment, AppointmentStatus, Urgency, AppointmentType
from backend.app.auth.jwt import get_password_hash

async def create_roles_permissions(session):
    # Create roles if not exist
    admin_role = Role(name=RoleName.ADMIN)
    doctor_role = Role(name=RoleName.DOCTOR)
    staff_role = Role(name=RoleName.STAFF)
    patient_role = Role(name=RoleName.PATIENT)
    session.add_all([admin_role, doctor_role, staff_role, patient_role])
    await session.flush()
    # Permissions can be added similarly if needed
    return admin_role, doctor_role, staff_role, patient_role

async def create_user(session, name, email, role, password="password"):
    user = User(
        name=name,
        email=email,
        password_hash=get_password_hash(password),
        role_id=role.id,
        auth_provider="LOCAL",
    )
    session.add(user)
    await session.flush()
    return user

async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as session:
        admin_role, doctor_role, staff_role, patient_role = await create_roles_permissions(session)
        # Create a doctor
        doctor_user = await create_user(session, "Dr. Smith", "dr.smith@example.com", doctor_role)
        doctor = Doctor(user_id=doctor_user.id, employee_id="D001", specialization_id=1, qualification="MD")
        session.add(doctor)
        # Create patients A-E with different scenarios
        # Patient A – LOW RISK (confirmed true, no shows)
        pat_a_user = await create_user(session, "Patient A", "patientA@example.com", patient_role)
        patient_a = Patient(user_id=pat_a_user.id, patient_id="PA001", date_of_birth=date(1990,1,1))
        session.add(patient_a)
        appt_a = Appointment(
            patient_id=patient_a.id,
            doctor_id=doctor.id,
            appointment_date=date.today(),
            start_time=time(9,0),
            end_time=time(9,30),
            appointment_type=AppointmentType.ROUTINE,
            urgency=Urgency.MEDIUM,
            status=AppointmentStatus.CONFIRMED,
            created_by=doctor_user.id,
        )
        session.add(appt_a)
        # Patient B – UNCONFIRMED
        pat_b_user = await create_user(session, "Patient B", "patientB@example.com", patient_role)
        patient_b = Patient(user_id=pat_b_user.id, patient_id="PB001", date_of_birth=date(1985,5,5))
        session.add(patient_b)
        appt_b = Appointment(
            patient_id=patient_b.id,
            doctor_id=doctor.id,
            appointment_date=date.today(),
            start_time=time(10,0),
            end_time=time(10,30),
            appointment_type=AppointmentType.ROUTINE,
            urgency=Urgency.MEDIUM,
            status=AppointmentStatus.SCHEDULED,
            created_by=doctor_user.id,
        )
        session.add(appt_b)
        # Patient C – HIGH RISK + alternative slot
        pat_c_user = await create_user(session, "Patient C", "patientC@example.com", patient_role)
        patient_c = Patient(user_id=pat_c_user.id, patient_id="PC001", date_of_birth=date(1970,3,15))
        session.add(patient_c)
        appt_c = Appointment(
            patient_id=patient_c.id,
            doctor_id=doctor.id,
            appointment_date=date.today(),
            start_time=time(11,0),
            end_time=time(11,30),
            appointment_type=AppointmentType.ROUTINE,
            urgency=Urgency.HIGH,
            status=AppointmentStatus.SCHEDULED,
            created_by=doctor_user.id,
        )
        session.add(appt_c)
        # Patient D – CRITICAL urgency
        pat_d_user = await create_user(session, "Patient D", "patientD@example.com", patient_role)
        patient_d = Patient(user_id=pat_d_user.id, patient_id="PD001", date_of_birth=date(1960,7,20))
        session.add(patient_d)
        appt_d = Appointment(
            patient_id=patient_d.id,
            doctor_id=doctor.id,
            appointment_date=date.today(),
            start_time=time(12,0),
            end_time=time(12,30),
            appointment_type=AppointmentType.ROUTINE,
            urgency=Urgency.CRITICAL,
            status=AppointmentStatus.SCHEDULED,
            created_by=doctor_user.id,
        )
        session.add(appt_d)
        # Patient E – HIGH_PRIORITY category (use patient_category via custom field – not in model, so we emulate via urgency HIGH)
        pat_e_user = await create_user(session, "Patient E", "patientE@example.com", patient_role)
        patient_e = Patient(user_id=pat_e_user.id, patient_id="PE001", date_of_birth=date(1995,12,12))
        session.add(patient_e)
        appt_e = Appointment(
            patient_id=patient_e.id,
            doctor_id=doctor.id,
            appointment_date=date.today(),
            start_time=time(13,0),
            end_time=time(13,30),
            appointment_type=AppointmentType.ROUTINE,
            urgency=Urgency.HIGH,
            status=AppointmentStatus.SCHEDULED,
            created_by=doctor_user.id,
        )
        session.add(appt_e)
        await session.commit()

if __name__ == "__main__":
    asyncio.run(seed())
