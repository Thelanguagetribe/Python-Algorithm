from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from enum import Enum
from datetime import datetime, time
import sqlite3
import json

class LessonType(Enum):
    IN_PERSON = "in_person"
    ONLINE = "online"
    BOTH = "both"

class DayOfWeek(Enum):
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"

class TimeSlot(Enum):
    MORNING = "morning"  # 6AM - 12PM
    AFTERNOON = "afternoon"  # 12PM - 6PM
    EVENING = "evening"  # 6PM - 10PM

@dataclass
class Location:
    latitude: float
    longitude: float
    city: str
    country: str

@dataclass
class Availability:
    day: DayOfWeek
    time_slot: TimeSlot
    specific_times: List[time]  # More specific time preferences

@dataclass
class LanguageLearner:
    id: int
    name: str
    email: str
    age: int
    target_language: str  # Language they want to learn
    native_language: str  # Their native language
    lesson_type_preference: LessonType
    location: Optional[Location]  # Required for in-person lessons
    availability: List[Availability]
    experience_level: str  # beginner, intermediate, advanced
    budget_per_hour: float  # Maximum budget per hour
    created_at: datetime
    is_active: bool = True

@dataclass
class NativeSpeaker:
    id: int
    name: str
    email: str
    age: int
    native_language: str  # Language they teach
    secondary_languages: List[str]  # Other languages they speak
    lesson_types_offered: List[LessonType]
    location: Optional[Location]  # Required for in-person lessons
    availability: List[Availability]
    teaching_experience_years: int
    hourly_rate: float
    max_students: int  # Maximum concurrent students
    current_students: int  # Current number of students
    rating: float  # Average rating from students
    bio: str
    created_at: datetime
    is_active: bool = True
    is_verified: bool = False

@dataclass
class Match:
    learner_id: int
    speaker_id: int
    compatibility_score: float
    language: str
    lesson_type: LessonType
    distance_km: Optional[float]  # For in-person lessons
    age_difference: int
    availability_overlap: List[Availability]
    created_at: datetime
    is_confirmed: bool = False