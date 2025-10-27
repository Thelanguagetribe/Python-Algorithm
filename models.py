from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime, time
from enum import Enum


class LessonType(Enum):
    IN_PERSON = "in_person"
    ONLINE = "online"
    BOTH = "both"


class DayOfWeek(Enum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


@dataclass
class Location:
    """Represents a geographical location"""
    latitude: float
    longitude: float
    city: str
    country: str


@dataclass
class TimeSlot:
    """Represents an available time slot"""
    day: DayOfWeek
    start_time: time
    end_time: time


@dataclass
class LanguageLearner:
    """Model for language learners (customers)"""
    id: str
    name: str
    email: str
    age: int
    target_language: str  # Language they want to learn
    lesson_type_preference: LessonType
    location: Optional[Location]  # Required for in-person lessons
    availability: List[TimeSlot]
    max_distance_km: Optional[float]  # Max distance for in-person lessons
    created_at: datetime
    is_active: bool = True


@dataclass
class NativeSpeaker:
    """Model for native speakers (service providers)"""
    id: str
    name: str
    email: str
    age: int
    native_language: str
    teaching_languages: List[str]  # Languages they can teach
    lesson_types_offered: List[LessonType]
    location: Optional[Location]  # Required for in-person lessons
    availability: List[TimeSlot]
    hourly_rate: float
    years_experience: int
    bio: str
    is_verified: bool
    is_available: bool
    created_at: datetime


@dataclass
class Match:
    """Represents a potential match between learner and speaker"""
    learner: LanguageLearner
    speaker: NativeSpeaker
    compatibility_score: float
    language_match: bool
    lesson_type_match: bool
    age_compatibility: float
    location_distance_km: Optional[float]
    time_overlap_hours: float
    reasons: List[str]  # Explanation of match quality