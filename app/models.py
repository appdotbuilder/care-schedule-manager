from sqlmodel import SQLModel, Field, Relationship, JSON, Column
from datetime import datetime, date, time
from typing import Optional, List, Dict, Any
from enum import Enum
from decimal import Decimal


# Enums for status tracking
class EmployeeRole(str, Enum):
    CARETAKER = "caretaker"
    ADMINISTRATOR = "administrator"
    SUPERVISOR = "supervisor"


class AppointmentStatus(str, Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class AvailabilityType(str, Enum):
    AVAILABLE = "available"
    VACATION = "vacation"
    SICK_LEAVE = "sick_leave"
    UNAVAILABLE = "unavailable"


class PresenceStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    DECLINED = "declined"
    NO_RESPONSE = "no_response"


class NotificationStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"


class NotificationType(str, Enum):
    ASSIGNMENT = "assignment"
    REMINDER = "reminder"
    SCHEDULE_CHANGE = "schedule_change"
    CONFIRMATION_REQUEST = "confirmation_request"


# Persistent models (stored in database)
class Employee(SQLModel, table=True):
    __tablename__ = "employees"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    email: str = Field(unique=True, max_length=255)
    phone: Optional[str] = Field(default=None, max_length=20)
    role: EmployeeRole = Field(default=EmployeeRole.CARETAKER)
    is_active: bool = Field(default=True)
    hourly_rate: Optional[Decimal] = Field(default=None, decimal_places=2)
    qualifications: List[str] = Field(default=[], sa_column=Column(JSON))
    notes: str = Field(default="", max_length=1000)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    appointments: List["Appointment"] = Relationship(back_populates="employee")
    availability_periods: List["AvailabilityPeriod"] = Relationship(back_populates="employee")
    notifications: List["Notification"] = Relationship(back_populates="employee")


class CareRecipient(SQLModel, table=True):
    __tablename__ = "care_recipients"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    address: str = Field(max_length=500)
    phone: Optional[str] = Field(default=None, max_length=20)
    emergency_contact: str = Field(max_length=200)
    emergency_phone: str = Field(max_length=20)
    medical_conditions: List[str] = Field(default=[], sa_column=Column(JSON))
    care_requirements: List[str] = Field(default=[], sa_column=Column(JSON))
    special_instructions: str = Field(default="", max_length=1000)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    appointments: List["Appointment"] = Relationship(back_populates="care_recipient")


class Appointment(SQLModel, table=True):
    __tablename__ = "appointments"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    care_recipient_id: int = Field(foreign_key="care_recipients.id")
    employee_id: Optional[int] = Field(default=None, foreign_key="employees.id")
    scheduled_date: date
    start_time: time
    end_time: time
    duration_minutes: int = Field(ge=15)  # Minimum 15 minutes
    status: AppointmentStatus = Field(default=AppointmentStatus.SCHEDULED)
    presence_status: PresenceStatus = Field(default=PresenceStatus.PENDING)
    care_tasks: List[str] = Field(default=[], sa_column=Column(JSON))
    notes: str = Field(default="", max_length=1000)
    completion_notes: str = Field(default="", max_length=1000)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    confirmed_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)

    # Relationships
    care_recipient: CareRecipient = Relationship(back_populates="appointments")
    employee: Optional[Employee] = Relationship(back_populates="appointments")


class AvailabilityPeriod(SQLModel, table=True):
    __tablename__ = "availability_periods"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    employee_id: int = Field(foreign_key="employees.id")
    start_date: date
    end_date: date
    start_time: Optional[time] = Field(default=None)  # None means all day
    end_time: Optional[time] = Field(default=None)  # None means all day
    availability_type: AvailabilityType = Field(default=AvailabilityType.AVAILABLE)
    recurring_days: List[str] = Field(default=[], sa_column=Column(JSON))  # ["monday", "tuesday", ...]
    notes: str = Field(default="", max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    employee: Employee = Relationship(back_populates="availability_periods")


class Notification(SQLModel, table=True):
    __tablename__ = "notifications"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    employee_id: int = Field(foreign_key="employees.id")
    notification_type: NotificationType
    subject: str = Field(max_length=200)
    message: str = Field(max_length=2000)
    status: NotificationStatus = Field(default=NotificationStatus.PENDING)
    delivery_method: str = Field(default="email", max_length=50)
    scheduled_for: datetime = Field(default_factory=datetime.utcnow)
    sent_at: Optional[datetime] = Field(default=None)
    delivered_at: Optional[datetime] = Field(default=None)
    related_appointment_id: Optional[int] = Field(default=None, foreign_key="appointments.id")
    notification_metadata: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    employee: Employee = Relationship(back_populates="notifications")


class ScheduleTemplate(SQLModel, table=True):
    __tablename__ = "schedule_templates"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, unique=True)
    description: str = Field(default="", max_length=500)
    is_active: bool = Field(default=True)
    template_data: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Non-persistent schemas (for validation, forms, API requests/responses)
class EmployeeCreate(SQLModel, table=False):
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    email: str = Field(max_length=255)
    phone: Optional[str] = Field(default=None, max_length=20)
    role: EmployeeRole = Field(default=EmployeeRole.CARETAKER)
    hourly_rate: Optional[Decimal] = Field(default=None, decimal_places=2)
    qualifications: List[str] = Field(default=[])
    notes: str = Field(default="", max_length=1000)


class EmployeeUpdate(SQLModel, table=False):
    first_name: Optional[str] = Field(default=None, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)
    email: Optional[str] = Field(default=None, max_length=255)
    phone: Optional[str] = Field(default=None, max_length=20)
    role: Optional[EmployeeRole] = Field(default=None)
    is_active: Optional[bool] = Field(default=None)
    hourly_rate: Optional[Decimal] = Field(default=None, decimal_places=2)
    qualifications: Optional[List[str]] = Field(default=None)
    notes: Optional[str] = Field(default=None, max_length=1000)


class CareRecipientCreate(SQLModel, table=False):
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    address: str = Field(max_length=500)
    phone: Optional[str] = Field(default=None, max_length=20)
    emergency_contact: str = Field(max_length=200)
    emergency_phone: str = Field(max_length=20)
    medical_conditions: List[str] = Field(default=[])
    care_requirements: List[str] = Field(default=[])
    special_instructions: str = Field(default="", max_length=1000)


class CareRecipientUpdate(SQLModel, table=False):
    first_name: Optional[str] = Field(default=None, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)
    address: Optional[str] = Field(default=None, max_length=500)
    phone: Optional[str] = Field(default=None, max_length=20)
    emergency_contact: Optional[str] = Field(default=None, max_length=200)
    emergency_phone: Optional[str] = Field(default=None, max_length=20)
    medical_conditions: Optional[List[str]] = Field(default=None)
    care_requirements: Optional[List[str]] = Field(default=None)
    special_instructions: Optional[str] = Field(default=None, max_length=1000)
    is_active: Optional[bool] = Field(default=None)


class AppointmentCreate(SQLModel, table=False):
    care_recipient_id: int
    employee_id: Optional[int] = Field(default=None)
    scheduled_date: date
    start_time: time
    end_time: time
    duration_minutes: int = Field(ge=15)
    care_tasks: List[str] = Field(default=[])
    notes: str = Field(default="", max_length=1000)


class AppointmentUpdate(SQLModel, table=False):
    employee_id: Optional[int] = Field(default=None)
    scheduled_date: Optional[date] = Field(default=None)
    start_time: Optional[time] = Field(default=None)
    end_time: Optional[time] = Field(default=None)
    duration_minutes: Optional[int] = Field(default=None, ge=15)
    status: Optional[AppointmentStatus] = Field(default=None)
    presence_status: Optional[PresenceStatus] = Field(default=None)
    care_tasks: Optional[List[str]] = Field(default=None)
    notes: Optional[str] = Field(default=None, max_length=1000)
    completion_notes: Optional[str] = Field(default=None, max_length=1000)


class AvailabilityPeriodCreate(SQLModel, table=False):
    employee_id: int
    start_date: date
    end_date: date
    start_time: Optional[time] = Field(default=None)
    end_time: Optional[time] = Field(default=None)
    availability_type: AvailabilityType = Field(default=AvailabilityType.AVAILABLE)
    recurring_days: List[str] = Field(default=[])
    notes: str = Field(default="", max_length=500)


class AvailabilityPeriodUpdate(SQLModel, table=False):
    start_date: Optional[date] = Field(default=None)
    end_date: Optional[date] = Field(default=None)
    start_time: Optional[time] = Field(default=None)
    end_time: Optional[time] = Field(default=None)
    availability_type: Optional[AvailabilityType] = Field(default=None)
    recurring_days: Optional[List[str]] = Field(default=None)
    notes: Optional[str] = Field(default=None, max_length=500)


class NotificationCreate(SQLModel, table=False):
    employee_id: int
    notification_type: NotificationType
    subject: str = Field(max_length=200)
    message: str = Field(max_length=2000)
    delivery_method: str = Field(default="email", max_length=50)
    scheduled_for: datetime = Field(default_factory=datetime.utcnow)
    related_appointment_id: Optional[int] = Field(default=None)
    notification_metadata: Dict[str, Any] = Field(default={})


class ScheduleTemplateCreate(SQLModel, table=False):
    name: str = Field(max_length=100)
    description: str = Field(default="", max_length=500)
    template_data: Dict[str, Any] = Field(default={})


class ScheduleTemplateUpdate(SQLModel, table=False):
    name: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    is_active: Optional[bool] = Field(default=None)
    template_data: Optional[Dict[str, Any]] = Field(default=None)


# Response schemas for API
class EmployeeResponse(SQLModel, table=False):
    id: int
    first_name: str
    last_name: str
    email: str
    phone: Optional[str]
    role: EmployeeRole
    is_active: bool
    hourly_rate: Optional[Decimal]
    qualifications: List[str]
    notes: str
    created_at: str  # ISO format string
    updated_at: str  # ISO format string


class AppointmentResponse(SQLModel, table=False):
    id: int
    care_recipient_id: int
    employee_id: Optional[int]
    scheduled_date: str  # ISO format string
    start_time: str
    end_time: str
    duration_minutes: int
    status: AppointmentStatus
    presence_status: PresenceStatus
    care_tasks: List[str]
    notes: str
    completion_notes: str
    created_at: str  # ISO format string
    updated_at: str  # ISO format string
    confirmed_at: Optional[str]  # ISO format string
    completed_at: Optional[str]  # ISO format string


class AvailabilityPeriodResponse(SQLModel, table=False):
    id: int
    employee_id: int
    start_date: str  # ISO format string
    end_date: str  # ISO format string
    start_time: Optional[str]
    end_time: Optional[str]
    availability_type: AvailabilityType
    recurring_days: List[str]
    notes: str
    created_at: str  # ISO format string
    updated_at: str  # ISO format string
