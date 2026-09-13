from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Time, Enum, ForeignKey, UniqueConstraint, Text
from sqlalchemy.orm import relationship
from ..database import Base
import enum
from datetime import datetime

# Enums
class AuthProvider(str, enum.Enum):
    LOCAL = "LOCAL"
    GOOGLE = "GOOGLE"

class RoleName(str, enum.Enum):
    ADMIN = "ADMIN"
    DOCTOR = "DOCTOR"
    STAFF = "STAFF"
    PATIENT = "PATIENT"

class PermissionName(str, enum.Enum):
    VIEW_PATIENTS = "VIEW_PATIENTS"
    CREATE_PATIENT = "CREATE_PATIENT"
    UPDATE_PATIENT = "UPDATE_PATIENT"
    VIEW_APPOINTMENTS = "VIEW_APPOINTMENTS"
    CREATE_APPOINTMENT = "CREATE_APPOINTMENT"
    UPDATE_APPOINTMENT = "UPDATE_APPOINTMENT"
    CANCEL_APPOINTMENT = "CANCEL_APPOINTMENT"
    RESCHEDULE_APPOINTMENT = "RESCHEDULE_APPOINTMENT"
    MANAGE_STAFF = "MANAGE_STAFF"
    MANAGE_DOCTORS = "MANAGE_DOCTORS"
    MANAGE_PERMISSIONS = "MANAGE_PERMISSIONS"
    VIEW_ANALYTICS = "VIEW_ANALYTICS"
    VIEW_AGENT_ACTIVITY = "VIEW_AGENT_ACTIVITY"

class AppointmentType(str, enum.Enum):
    ROUTINE = "ROUTINE"
    FOLLOW_UP = "FOLLOW_UP"
    CONSULTATION = "CONSULTATION"

class Urgency(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class AppointmentStatus(str, enum.Enum):
    SCHEDULED = "SCHEDULED"
    CONFIRMED = "CONFIRMED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    RESCHEDULED = "RESCHEDULED"
    NO_SHOW = "NO_SHOW"
    STAFF_REVIEW = "STAFF_REVIEW"

class NotificationType(str, enum.Enum):
    REMINDER = "REMINDER"
    RESCHEDULE_OFFER = "RESCHEDULE_OFFER"

class NotificationChannel(str, enum.Enum):
    EMAIL = "EMAIL"

class ResponseStatus(str, enum.Enum):
    WAITING = "WAITING"
    REPLIED = "REPLIED"
    NO_REPLY = "NO_REPLY"

class CallPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class CallStatus(str, enum.Enum):
    PENDING = "PENDING"
    CALLING = "CALLING"
    CONTACTED = "CONTACTED"
    NO_ANSWER = "NO_ANSWER"
    CONFIRMED = "CONFIRMED"
    RESCHEDULED = "RESCHEDULED"
    CANCELLED = "CANCELLED"

class AIDecisionEnum(str, enum.Enum):
    SEND_REMINDER = "SEND_REMINDER"
    OFFER_RESCHEDULE = "OFFER_RESCHEDULE"
    ESCALATE_TO_STAFF = "ESCALATE_TO_STAFF"

# Models
class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(Enum(RoleName), unique=True, nullable=False)
    permissions = relationship("Permission", secondary="role_permissions", back_populates="roles")

class Permission(Base):
    __tablename__ = "permissions"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(Enum(PermissionName), unique=True, nullable=False)
    description = Column(String, nullable=True)
    roles = relationship("Role", secondary="role_permissions", back_populates="permissions")

class RolePermission(Base):
    __tablename__ = "role_permissions"
    role_id = Column(Integer, ForeignKey("roles.id"), primary_key=True)
    permission_id = Column(Integer, ForeignKey("permissions.id"), primary_key=True)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=True)
    google_id = Column(String, nullable=True, unique=True)
    auth_provider = Column(Enum(AuthProvider), default=AuthProvider.LOCAL, nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    role = relationship("Role")
    patient = relationship("Patient", uselist=False, back_populates="user")
    doctor = relationship("Doctor", uselist=False, back_populates="user")
    staff = relationship("Staff", uselist=False, back_populates="user")

class Patient(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    patient_id = Column(String, unique=True, nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    address = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="patient")
    emergency_contacts = relationship("EmergencyContact", back_populates="patient")
    appointments = relationship("Appointment", back_populates="patient")

class EmergencyContact(Base):
    __tablename__ = "emergency_contacts"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    name = Column(String, nullable=False)
    relationship_type = Column(String, nullable=True)
    phone = Column(String, nullable=False)
    is_primary = Column(Boolean, default=False)

    patient = relationship("Patient", back_populates="emergency_contacts")

class Specialization(Base):
    __tablename__ = "specializations"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=True)

    doctors = relationship("Doctor", back_populates="specialization")

class Doctor(Base):
    __tablename__ = "doctors"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    employee_id = Column(String, unique=True, nullable=False)
    specialization_id = Column(Integer, ForeignKey("specializations.id"), nullable=False)
    qualification = Column(String, nullable=True)
    status = Column(String, nullable=True)

    user = relationship("User", back_populates="doctor")
    specialization = relationship("Specialization", back_populates="doctors")
    availability = relationship("DoctorAvailability", back_populates="doctor")
    appointments = relationship("Appointment", back_populates="doctor")

class DoctorAvailability(Base):
    __tablename__ = "doctor_availability"
    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    day_of_week = Column(Integer, nullable=False)  # 0=Monday ... 6=Sunday
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    is_available = Column(Boolean, default=True)

    doctor = relationship("Doctor", back_populates="availability")

class Staff(Base):
    __tablename__ = "staff"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    employee_id = Column(String, unique=True, nullable=False)
    status = Column(String, nullable=True)

    user = relationship("User", back_populates="staff")
    call_queue = relationship("StaffCallQueue", back_populates="staff_member")

class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    appointment_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    appointment_type = Column(Enum(AppointmentType), nullable=False)
    reason = Column(Text, nullable=True)
    urgency = Column(Enum(Urgency), nullable=False)
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.SCHEDULED, nullable=False)
    cancellation_risk = Column(Integer, nullable=True)  # store as percentage integer 0-100
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")
    creator = relationship("User", foreign_keys=[created_by])
    reschedule_histories = relationship("RescheduleHistory", back_populates="appointment")
    notifications = relationship("Notification", back_populates="appointment")
    ai_decisions = relationship("AIDecision", back_populates="appointment")
    agent_activities = relationship("AgentActivity", back_populates="appointment")
    staff_calls = relationship("StaffCallQueue", back_populates="appointment")

class RescheduleHistory(Base):
    __tablename__ = "reschedule_history"
    id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=False)
    old_date = Column(Date, nullable=False)
    old_start_time = Column(Time, nullable=False)
    old_end_time = Column(Time, nullable=False)
    new_date = Column(Date, nullable=False)
    new_start_time = Column(Time, nullable=False)
    new_end_time = Column(Time, nullable=False)
    reason = Column(Text, nullable=True)
    changed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    appointment = relationship("Appointment", back_populates="reschedule_histories")

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    type = Column(Enum(NotificationType), nullable=False)
    channel = Column(Enum(NotificationChannel), nullable=False)
    message = Column(Text, nullable=False)
    sent_at = Column(DateTime, default=datetime.utcnow)
    response_status = Column(Enum(ResponseStatus), default=ResponseStatus.WAITING)
    response_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    appointment = relationship("Appointment", back_populates="notifications")
    patient = relationship("Patient")

class StaffCallQueue(Base):
    __tablename__ = "staff_call_queue"
    id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    reason = Column(Text, nullable=True)
    priority = Column(Enum(CallPriority), default=CallPriority.MEDIUM, nullable=False)
    status = Column(Enum(CallStatus), default=CallStatus.PENDING, nullable=False)
    assigned_to = Column(Integer, ForeignKey("staff.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    appointment = relationship("Appointment", back_populates="staff_calls")
    patient = relationship("Patient")
    staff_member = relationship("Staff", back_populates="call_queue")

class AIDecision(Base):
    __tablename__ = "ai_decisions"
    id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=False)
    risk_score = Column(Integer, nullable=False)  # 0-100
    decision = Column(Enum(AIDecisionEnum), nullable=False)
    reasoning = Column(Text, nullable=True)
    confidence = Column(Integer, nullable=False)  # 0-100
    created_at = Column(DateTime, default=datetime.utcnow)

    appointment = relationship("Appointment", back_populates="ai_decisions")

class AgentActivity(Base):
    __tablename__ = "agent_activity"
    id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=False)
    action = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    appointment = relationship("Appointment", back_populates="agent_activities")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String, nullable=False)
    entity_type = Column(String, nullable=False)
    entity_id = Column(Integer, nullable=False)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
