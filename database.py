import sqlite3
import json
from typing import List, Optional, Dict, Any
from datetime import datetime, time
from models import (
    LanguageLearner, NativeSpeaker, Match, Location, 
    Availability, LessonType, DayOfWeek, TimeSlot
)

class LanguageTribeDatabase:
    def __init__(self, db_path: str = "language_tribe.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create language learners table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS language_learners (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                age INTEGER NOT NULL,
                target_language TEXT NOT NULL,
                native_language TEXT NOT NULL,
                lesson_type_preference TEXT NOT NULL,
                location_data TEXT,  -- JSON string
                availability_data TEXT NOT NULL,  -- JSON string
                experience_level TEXT NOT NULL,
                budget_per_hour REAL NOT NULL,
                created_at TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 1
            )
        """)
        
        # Create native speakers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS native_speakers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                age INTEGER NOT NULL,
                native_language TEXT NOT NULL,
                secondary_languages TEXT,  -- JSON string
                lesson_types_offered TEXT NOT NULL,  -- JSON string
                location_data TEXT,  -- JSON string
                availability_data TEXT NOT NULL,  -- JSON string
                teaching_experience_years INTEGER NOT NULL,
                hourly_rate REAL NOT NULL,
                max_students INTEGER NOT NULL,
                current_students INTEGER DEFAULT 0,
                rating REAL DEFAULT 0.0,
                bio TEXT,
                created_at TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                is_verified BOOLEAN DEFAULT 0
            )
        """)
        
        # Create matches table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                learner_id INTEGER NOT NULL,
                speaker_id INTEGER NOT NULL,
                compatibility_score REAL NOT NULL,
                language TEXT NOT NULL,
                lesson_type TEXT NOT NULL,
                distance_km REAL,
                age_difference INTEGER NOT NULL,
                availability_overlap TEXT NOT NULL,  -- JSON string
                created_at TEXT NOT NULL,
                is_confirmed BOOLEAN DEFAULT 0,
                FOREIGN KEY (learner_id) REFERENCES language_learners (id),
                FOREIGN KEY (speaker_id) REFERENCES native_speakers (id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save_language_learner(self, learner: LanguageLearner) -> int:
        """Save a language learner to the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Convert complex objects to JSON
        location_json = json.dumps({
            'latitude': learner.location.latitude,
            'longitude': learner.location.longitude,
            'city': learner.location.city,
            'country': learner.location.country
        }) if learner.location else None
        
        availability_json = json.dumps([{
            'day': avail.day.value,
            'time_slot': avail.time_slot.value,
            'specific_times': [t.strftime('%H:%M') for t in avail.specific_times]
        } for avail in learner.availability])
        
        if learner.id == 0:  # New learner
            cursor.execute("""
                INSERT INTO language_learners 
                (name, email, age, target_language, native_language, lesson_type_preference,
                 location_data, availability_data, experience_level, budget_per_hour, 
                 created_at, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                learner.name, learner.email, learner.age, learner.target_language,
                learner.native_language, learner.lesson_type_preference.value,
                location_json, availability_json, learner.experience_level,
                learner.budget_per_hour, learner.created_at.isoformat(), learner.is_active
            ))
            learner_id = cursor.lastrowid
        else:  # Update existing learner
            cursor.execute("""
                UPDATE language_learners SET
                name=?, email=?, age=?, target_language=?, native_language=?, 
                lesson_type_preference=?, location_data=?, availability_data=?, 
                experience_level=?, budget_per_hour=?, is_active=?
                WHERE id=?
            """, (
                learner.name, learner.email, learner.age, learner.target_language,
                learner.native_language, learner.lesson_type_preference.value,
                location_json, availability_json, learner.experience_level,
                learner.budget_per_hour, learner.is_active, learner.id
            ))
            learner_id = learner.id
        
        conn.commit()
        conn.close()
        return learner_id
    
    def save_native_speaker(self, speaker: NativeSpeaker) -> int:
        """Save a native speaker to the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Convert complex objects to JSON
        location_json = json.dumps({
            'latitude': speaker.location.latitude,
            'longitude': speaker.location.longitude,
            'city': speaker.location.city,
            'country': speaker.location.country
        }) if speaker.location else None
        
        secondary_languages_json = json.dumps(speaker.secondary_languages)
        lesson_types_json = json.dumps([lt.value for lt in speaker.lesson_types_offered])
        
        availability_json = json.dumps([{
            'day': avail.day.value,
            'time_slot': avail.time_slot.value,
            'specific_times': [t.strftime('%H:%M') for t in avail.specific_times]
        } for avail in speaker.availability])
        
        if speaker.id == 0:  # New speaker
            cursor.execute("""
                INSERT INTO native_speakers 
                (name, email, age, native_language, secondary_languages, lesson_types_offered,
                 location_data, availability_data, teaching_experience_years, hourly_rate,
                 max_students, current_students, rating, bio, created_at, is_active, is_verified)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                speaker.name, speaker.email, speaker.age, speaker.native_language,
                secondary_languages_json, lesson_types_json, location_json, availability_json,
                speaker.teaching_experience_years, speaker.hourly_rate, speaker.max_students,
                speaker.current_students, speaker.rating, speaker.bio, 
                speaker.created_at.isoformat(), speaker.is_active, speaker.is_verified
            ))
            speaker_id = cursor.lastrowid
        else:  # Update existing speaker
            cursor.execute("""
                UPDATE native_speakers SET
                name=?, email=?, age=?, native_language=?, secondary_languages=?, 
                lesson_types_offered=?, location_data=?, availability_data=?, 
                teaching_experience_years=?, hourly_rate=?, max_students=?, 
                current_students=?, rating=?, bio=?, is_active=?, is_verified=?
                WHERE id=?
            """, (
                speaker.name, speaker.email, speaker.age, speaker.native_language,
                secondary_languages_json, lesson_types_json, location_json, availability_json,
                speaker.teaching_experience_years, speaker.hourly_rate, speaker.max_students,
                speaker.current_students, speaker.rating, speaker.bio, 
                speaker.is_active, speaker.is_verified, speaker.id
            ))
            speaker_id = speaker.id
        
        conn.commit()
        conn.close()
        return speaker_id
    
    def get_language_learner(self, learner_id: int) -> Optional[LanguageLearner]:
        """Retrieve a language learner by ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM language_learners WHERE id = ?", (learner_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return self._row_to_language_learner(row)
    
    def get_native_speaker(self, speaker_id: int) -> Optional[NativeSpeaker]:
        """Retrieve a native speaker by ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM native_speakers WHERE id = ?", (speaker_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return self._row_to_native_speaker(row)
    
    def get_all_active_speakers(self) -> List[NativeSpeaker]:
        """Get all active native speakers."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM native_speakers WHERE is_active = 1")
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_native_speaker(row) for row in rows]
    
    def search_speakers_by_language(self, language: str) -> List[NativeSpeaker]:
        """Search for speakers who teach a specific language."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM native_speakers 
            WHERE is_active = 1 AND (
                LOWER(native_language) = LOWER(?) OR 
                LOWER(secondary_languages) LIKE LOWER(?)
            )
        """, (language, f'%"{language}"%'))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_native_speaker(row) for row in rows]
    
    def save_match(self, match: Match) -> int:
        """Save a match to the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        availability_json = json.dumps([{
            'day': avail.day.value,
            'time_slot': avail.time_slot.value,
            'specific_times': [t.strftime('%H:%M') for t in avail.specific_times]
        } for avail in match.availability_overlap])
        
        cursor.execute("""
            INSERT INTO matches 
            (learner_id, speaker_id, compatibility_score, language, lesson_type,
             distance_km, age_difference, availability_overlap, created_at, is_confirmed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            match.learner_id, match.speaker_id, match.compatibility_score,
            match.language, match.lesson_type.value, match.distance_km,
            match.age_difference, availability_json, match.created_at.isoformat(),
            match.is_confirmed
        ))
        
        match_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return match_id
    
    def get_matches_for_learner(self, learner_id: int) -> List[Match]:
        """Get all matches for a specific learner."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM matches 
            WHERE learner_id = ? 
            ORDER BY compatibility_score DESC
        """, (learner_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_match(row) for row in rows]
    
    def _row_to_language_learner(self, row) -> LanguageLearner:
        """Convert database row to LanguageLearner object."""
        (id, name, email, age, target_language, native_language, lesson_type_preference,
         location_data, availability_data, experience_level, budget_per_hour, 
         created_at, is_active) = row
        
        # Parse location
        location = None
        if location_data:
            loc_dict = json.loads(location_data)
            location = Location(**loc_dict)
        
        # Parse availability
        avail_list = json.loads(availability_data)
        availability = []
        for avail_dict in avail_list:
            specific_times = [datetime.strptime(t, '%H:%M').time() for t in avail_dict['specific_times']]
            availability.append(Availability(
                day=DayOfWeek(avail_dict['day']),
                time_slot=TimeSlot(avail_dict['time_slot']),
                specific_times=specific_times
            ))
        
        return LanguageLearner(
            id=id, name=name, email=email, age=age,
            target_language=target_language, native_language=native_language,
            lesson_type_preference=LessonType(lesson_type_preference),
            location=location, availability=availability,
            experience_level=experience_level, budget_per_hour=budget_per_hour,
            created_at=datetime.fromisoformat(created_at), is_active=bool(is_active)
        )
    
    def _row_to_native_speaker(self, row) -> NativeSpeaker:
        """Convert database row to NativeSpeaker object."""
        (id, name, email, age, native_language, secondary_languages, lesson_types_offered,
         location_data, availability_data, teaching_experience_years, hourly_rate,
         max_students, current_students, rating, bio, created_at, is_active, is_verified) = row
        
        # Parse location
        location = None
        if location_data:
            loc_dict = json.loads(location_data)
            location = Location(**loc_dict)
        
        # Parse secondary languages
        secondary_langs = json.loads(secondary_languages) if secondary_languages else []
        
        # Parse lesson types
        lesson_types = [LessonType(lt) for lt in json.loads(lesson_types_offered)]
        
        # Parse availability
        avail_list = json.loads(availability_data)
        availability = []
        for avail_dict in avail_list:
            specific_times = [datetime.strptime(t, '%H:%M').time() for t in avail_dict['specific_times']]
            availability.append(Availability(
                day=DayOfWeek(avail_dict['day']),
                time_slot=TimeSlot(avail_dict['time_slot']),
                specific_times=specific_times
            ))
        
        return NativeSpeaker(
            id=id, name=name, email=email, age=age,
            native_language=native_language, secondary_languages=secondary_langs,
            lesson_types_offered=lesson_types, location=location, availability=availability,
            teaching_experience_years=teaching_experience_years, hourly_rate=hourly_rate,
            max_students=max_students, current_students=current_students,
            rating=rating, bio=bio, created_at=datetime.fromisoformat(created_at),
            is_active=bool(is_active), is_verified=bool(is_verified)
        )
    
    def _row_to_match(self, row) -> Match:
        """Convert database row to Match object."""
        (id, learner_id, speaker_id, compatibility_score, language, lesson_type,
         distance_km, age_difference, availability_overlap, created_at, is_confirmed) = row
        
        # Parse availability overlap
        avail_list = json.loads(availability_overlap)
        availability = []
        for avail_dict in avail_list:
            specific_times = [datetime.strptime(t, '%H:%M').time() for t in avail_dict['specific_times']]
            availability.append(Availability(
                day=DayOfWeek(avail_dict['day']),
                time_slot=TimeSlot(avail_dict['time_slot']),
                specific_times=specific_times
            ))
        
        return Match(
            learner_id=learner_id, speaker_id=speaker_id,
            compatibility_score=compatibility_score, language=language,
            lesson_type=LessonType(lesson_type), distance_km=distance_km,
            age_difference=age_difference, availability_overlap=availability,
            created_at=datetime.fromisoformat(created_at), is_confirmed=bool(is_confirmed)
        )