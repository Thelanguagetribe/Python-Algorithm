from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum
from datetime import datetime, timedelta
import uuid

class BookingStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"

class PaymentStatus(Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIAL_REFUND = "partial_refund"

class LessonType(Enum):
    TRIAL = "trial"
    SINGLE = "single"
    PACKAGE = "package"
    SUBSCRIPTION = "subscription"

class NotificationType(Enum):
    BOOKING_CONFIRMATION = "booking_confirmation"
    PAYMENT_CONFIRMATION = "payment_confirmation"
    LESSON_REMINDER = "lesson_reminder"
    LESSON_CANCELLED = "lesson_cancelled"
    RATING_REQUEST = "rating_request"

@dataclass
class TimeSlot:
    start_time: datetime
    end_time: datetime
    is_available: bool = True
    is_recurring: bool = False
    recurrence_pattern: Optional[str] = None  # weekly, daily, monthly

@dataclass
class Booking:
    id: str
    learner_id: int
    speaker_id: int
    lesson_date: datetime
    duration_minutes: int
    lesson_type: LessonType
    status: BookingStatus
    total_amount: float
    currency: str
    payment_status: PaymentStatus
    booking_notes: Optional[str]
    lesson_topic: Optional[str]
    meeting_link: Optional[str]  # For online lessons
    meeting_location: Optional[str]  # For in-person lessons
    created_at: datetime
    updated_at: datetime
    cancelled_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None
    rating_learner: Optional[float] = None
    rating_speaker: Optional[float] = None
    feedback_learner: Optional[str] = None
    feedback_speaker: Optional[str] = None

@dataclass
class Payment:
    id: str
    booking_id: str
    amount: float
    currency: str
    payment_method: str  # stripe, paypal, bank_transfer
    payment_intent_id: Optional[str]  # Stripe payment intent ID
    status: PaymentStatus
    transaction_fee: float
    net_amount: float  # Amount after fees
    processed_at: Optional[datetime]
    refund_amount: Optional[float] = None
    refund_reason: Optional[str] = None
    created_at: datetime

@dataclass
class Calendar:
    id: str
    speaker_id: int
    available_slots: List[TimeSlot]
    booked_slots: List[str]  # List of booking IDs
    blocked_slots: List[TimeSlot]  # Manually blocked time
    timezone: str
    auto_confirm: bool = True
    buffer_time_minutes: int = 15  # Time between lessons
    max_lessons_per_day: int = 8
    advance_booking_days: int = 30  # How far in advance bookings allowed

@dataclass
class LessonPackage:
    id: str
    speaker_id: int
    name: str
    description: str
    total_lessons: int
    lessons_used: int
    price_per_lesson: float
    total_price: float
    discount_percentage: float
    valid_until: datetime
    is_active: bool
    created_at: datetime

@dataclass
class Notification:
    id: str
    recipient_id: int  # learner or speaker ID
    recipient_type: str  # learner or speaker
    notification_type: NotificationType
    title: str
    message: str
    booking_id: Optional[str]
    is_read: bool = False
    is_sent: bool = False
    send_at: datetime  # When to send (for scheduled notifications)
    sent_at: Optional[datetime] = None
    created_at: datetime

@dataclass
class Review:
    id: str
    booking_id: str
    reviewer_id: int
    reviewer_type: str  # learner or speaker
    reviewee_id: int
    rating: float  # 1-5 stars
    comment: Optional[str]
    is_anonymous: bool = False
    is_verified: bool = True  # Only from completed bookings
    created_at: datetime

@dataclass
class Coupon:
    id: str
    code: str
    description: str
    discount_type: str  # percentage, fixed_amount
    discount_value: float
    minimum_amount: Optional[float]
    max_uses: Optional[int]
    current_uses: int = 0
    valid_from: datetime
    valid_until: datetime
    is_active: bool = True
    applicable_to: str = "all"  # all, first_booking, specific_speaker

@dataclass
class BookingSettings:
    speaker_id: int
    cancellation_policy_hours: int = 24
    late_cancellation_fee_percent: float = 50.0
    no_show_fee_percent: float = 100.0
    auto_confirm_bookings: bool = True
    require_payment_upfront: bool = True
    allow_reschedule: bool = True
    reschedule_limit_hours: int = 6
    buffer_time_minutes: int = 15
    max_advance_booking_days: int = 30