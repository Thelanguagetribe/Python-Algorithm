#!/usr/bin/env python3
"""
Language Tribe - Main Application
Demonstrates the language matching algorithm with sample data.
"""

from datetime import datetime, time
from models import (
    LanguageLearner, NativeSpeaker, Location, Availability, 
    LessonType, DayOfWeek, TimeSlot
)
from database import LanguageTribeDatabase
from matching_algorithm import LanguageMatchingAlgorithm

def create_sample_data():
    """Create sample language learners and native speakers for testing."""
    
    # Sample Language Learners
    learners = [
        LanguageLearner(
            id=0,  # Will be auto-assigned
            name="Emma Johnson",
            email="emma.johnson@email.com",
            age=28,
            target_language="Spanish",
            native_language="English",
            lesson_type_preference=LessonType.BOTH,
            location=Location(
                latitude=51.5074,
                longitude=-0.1278,
                city="London",
                country="UK"
            ),
            availability=[
                Availability(DayOfWeek.TUESDAY, TimeSlot.EVENING, [time(19, 0)]),
                Availability(DayOfWeek.THURSDAY, TimeSlot.EVENING, [time(19, 30)]),
                Availability(DayOfWeek.SATURDAY, TimeSlot.MORNING, [time(10, 0)])
            ],
            experience_level="beginner",
            budget_per_hour=25.0,
            created_at=datetime.now()
        ),
        
        LanguageLearner(
            id=0,
            name="David Chen",
            email="david.chen@email.com",
            age=34,
            target_language="French",
            native_language="English",
            lesson_type_preference=LessonType.ONLINE,
            location=Location(
                latitude=51.5074,
                longitude=-0.1278,
                city="London",
                country="UK"
            ),
            availability=[
                Availability(DayOfWeek.MONDAY, TimeSlot.EVENING, [time(18, 0)]),
                Availability(DayOfWeek.WEDNESDAY, TimeSlot.EVENING, [time(18, 0)]),
                Availability(DayOfWeek.FRIDAY, TimeSlot.EVENING, [time(18, 30)])
            ],
            experience_level="intermediate",
            budget_per_hour=35.0,
            created_at=datetime.now()
        ),
        
        LanguageLearner(
            id=0,
            name="Sarah Williams",
            email="sarah.williams@email.com",
            age=22,
            target_language="German",
            native_language="English",
            lesson_type_preference=LessonType.IN_PERSON,
            location=Location(
                latitude=51.5154,
                longitude=-0.1415,
                city="London",
                country="UK"
            ),
            availability=[
                Availability(DayOfWeek.SATURDAY, TimeSlot.MORNING, [time(9, 0)]),
                Availability(DayOfWeek.SUNDAY, TimeSlot.AFTERNOON, [time(14, 0)])
            ],
            experience_level="beginner",
            budget_per_hour=20.0,
            created_at=datetime.now()
        ),
        
        LanguageLearner(
            id=0,
            name="Michael Rodriguez",
            email="michael.rodriguez@email.com",
            age=45,
            target_language="Italian",
            native_language="Spanish",
            lesson_type_preference=LessonType.BOTH,
            location=Location(
                latitude=51.4994,
                longitude=-0.1245,
                city="London",
                country="UK"
            ),
            availability=[
                Availability(DayOfWeek.TUESDAY, TimeSlot.EVENING, [time(19, 0)]),
                Availability(DayOfWeek.THURSDAY, TimeSlot.EVENING, [time(19, 0)]),
                Availability(DayOfWeek.SATURDAY, TimeSlot.AFTERNOON, [time(15, 0)])
            ],
            experience_level="advanced",
            budget_per_hour=40.0,
            created_at=datetime.now()
        )
    ]
    
    # Sample Native Speakers
    speakers = [
        NativeSpeaker(
            id=0,
            name="Carlos Mendoza",
            email="carlos.mendoza@email.com",
            age=31,
            native_language="Spanish",
            secondary_languages=["English"],
            lesson_types_offered=[LessonType.BOTH],
            location=Location(
                latitude=51.5064,
                longitude=-0.1201,
                city="London",
                country="UK"
            ),
            availability=[
                Availability(DayOfWeek.TUESDAY, TimeSlot.EVENING, [time(19, 0), time(20, 0)]),
                Availability(DayOfWeek.THURSDAY, TimeSlot.EVENING, [time(19, 0), time(20, 0)]),
                Availability(DayOfWeek.SATURDAY, TimeSlot.MORNING, [time(10, 0), time(11, 0)])
            ],
            teaching_experience_years=5,
            hourly_rate=22.0,
            max_students=15,
            current_students=8,
            rating=4.8,
            bio="Native Spanish speaker from Mexico with 5 years of teaching experience. I love helping students discover the beauty of Spanish culture through language.",
            created_at=datetime.now(),
            is_verified=True
        ),
        
        NativeSpeaker(
            id=0,
            name="Marie Dubois",
            email="marie.dubois@email.com",
            age=29,
            native_language="French",
            secondary_languages=["English", "Spanish"],
            lesson_types_offered=[LessonType.ONLINE, LessonType.IN_PERSON],
            location=Location(
                latitude=51.5074,
                longitude=-0.1278,
                city="London",
                country="UK"
            ),
            availability=[
                Availability(DayOfWeek.MONDAY, TimeSlot.EVENING, [time(18, 0), time(19, 0)]),
                Availability(DayOfWeek.WEDNESDAY, TimeSlot.EVENING, [time(18, 0), time(19, 0)]),
                Availability(DayOfWeek.FRIDAY, TimeSlot.EVENING, [time(18, 30), time(19, 30)])
            ],
            teaching_experience_years=3,
            hourly_rate=30.0,
            max_students=12,
            current_students=5,
            rating=4.9,
            bio="Parisian native now living in London. I specialize in conversational French and French culture. Let's make learning French fun and engaging!",
            created_at=datetime.now(),
            is_verified=True
        ),
        
        NativeSpeaker(
            id=0,
            name="Hans Mueller",
            email="hans.mueller@email.com",
            age=26,
            native_language="German",
            secondary_languages=["English"],
            lesson_types_offered=[LessonType.IN_PERSON],
            location=Location(
                latitude=51.5154,
                longitude=-0.1415,
                city="London",
                country="UK"
            ),
            availability=[
                Availability(DayOfWeek.SATURDAY, TimeSlot.MORNING, [time(9, 0), time(10, 0)]),
                Availability(DayOfWeek.SUNDAY, TimeSlot.AFTERNOON, [time(14, 0), time(15, 0)])
            ],
            teaching_experience_years=2,
            hourly_rate=18.0,
            max_students=8,
            current_students=3,
            rating=4.6,
            bio="German native from Berlin. I'm passionate about sharing my language and culture. Perfect for beginners wanting to start their German journey!",
            created_at=datetime.now(),
            is_verified=True
        ),
        
        NativeSpeaker(
            id=0,
            name="Giulia Romano",
            email="giulia.romano@email.com",
            age=38,
            native_language="Italian",
            secondary_languages=["English", "French"],
            lesson_types_offered=[LessonType.BOTH],
            location=Location(
                latitude=51.4994,
                longitude=-0.1245,
                city="London",
                country="UK"
            ),
            availability=[
                Availability(DayOfWeek.TUESDAY, TimeSlot.EVENING, [time(19, 0), time(20, 0)]),
                Availability(DayOfWeek.THURSDAY, TimeSlot.EVENING, [time(19, 0), time(20, 0)]),
                Availability(DayOfWeek.SATURDAY, TimeSlot.AFTERNOON, [time(15, 0), time(16, 0)])
            ],
            teaching_experience_years=8,
            hourly_rate=35.0,
            max_students=20,
            current_students=12,
            rating=4.9,
            bio="Experienced Italian teacher from Rome. I've been teaching for 8 years and love helping advanced students perfect their Italian skills.",
            created_at=datetime.now(),
            is_verified=True
        ),
        
        NativeSpeaker(
            id=0,
            name="Yuki Tanaka",
            email="yuki.tanaka@email.com",
            age=24,
            native_language="Japanese",
            secondary_languages=["English"],
            lesson_types_offered=[LessonType.ONLINE],
            location=Location(
                latitude=35.6762,
                longitude=139.6503,
                city="Tokyo",
                country="Japan"
            ),
            availability=[
                Availability(DayOfWeek.MONDAY, TimeSlot.MORNING, [time(9, 0), time(10, 0)]),
                Availability(DayOfWeek.WEDNESDAY, TimeSlot.MORNING, [time(9, 0), time(10, 0)]),
                Availability(DayOfWeek.FRIDAY, TimeSlot.MORNING, [time(9, 0), time(10, 0)])
            ],
            teaching_experience_years=1,
            hourly_rate=25.0,
            max_students=10,
            current_students=4,
            rating=4.7,
            bio="Native Japanese speaker offering online lessons. Great for beginners wanting to learn Japanese culture and language from a Tokyo native!",
            created_at=datetime.now(),
            is_verified=True
        )
    ]
    
    return learners, speakers

def demo_matching_system():
    """Demonstrate the complete matching system."""
    print("🌍 Welcome to The Language Tribe Matching System!")
    print("=" * 60)
    
    # Initialize database and algorithm
    db = LanguageTribeDatabase("language_tribe_demo.db")
    algorithm = LanguageMatchingAlgorithm()
    
    # Create sample data
    print("\n📊 Creating sample data...")
    learners, speakers = create_sample_data()
    
    # Save learners to database
    print(f"💾 Saving {len(learners)} language learners...")
    for learner in learners:
        learner_id = db.save_language_learner(learner)
        learner.id = learner_id
        print(f"   ✅ Saved: {learner.name} (ID: {learner_id})")
    
    # Save speakers to database
    print(f"\n👥 Saving {len(speakers)} native speakers...")
    for speaker in speakers:
        speaker_id = db.save_native_speaker(speaker)
        speaker.id = speaker_id
        print(f"   ✅ Saved: {speaker.name} (ID: {speaker_id})")
    
    print("\n" + "=" * 60)
    print("🔍 FINDING MATCHES FOR EACH LEARNER")
    print("=" * 60)
    
    # Find matches for each learner
    for learner in learners:
        print(f"\n🎓 Finding matches for {learner.name}")
        print(f"   📚 Learning: {learner.target_language}")
        print(f"   📍 Location: {learner.location.city}")
        print(f"   💰 Budget: £{learner.budget_per_hour}/hour")
        print(f"   🏠 Preference: {learner.lesson_type_preference.value}")
        
        # Get potential speakers (you could filter by language here)
        all_speakers = db.get_all_active_speakers()
        
        # Find matches
        matches = algorithm.find_matches(learner, all_speakers, max_matches=3)
        
        if matches:
            print(f"   🎯 Found {len(matches)} matches:")
            for i, match in enumerate(matches, 1):
                speaker = db.get_native_speaker(match.speaker_id)
                print(f"      {i}. {speaker.name} ({match.compatibility_score:.1%} match)")
                print(f"         💰 £{speaker.hourly_rate}/hour | ⭐ {speaker.rating}/5.0")
                print(f"         📍 {match.distance_km:.1f}km away | 👥 Age diff: {match.age_difference} years")
                print(f"         📅 {len(match.availability_overlap)} overlapping time slots")
                
            # Save best match to database
            best_match = matches[0]
            db.save_match(best_match)
            print(f"   💾 Saved best match to database")
        else:
            print("   ❌ No suitable matches found")
    
    print("\n" + "=" * 60)
    print("📈 DATABASE STATISTICS")
    print("=" * 60)
    
    # Show database statistics
    all_speakers = db.get_all_active_speakers()
    all_learners = [db.get_language_learner(i+1) for i in range(len(learners))]
    
    print(f"👥 Total Active Speakers: {len(all_speakers)}")
    print(f"🎓 Total Language Learners: {len([l for l in all_learners if l])}")
    
    # Language breakdown
    languages = {}
    for speaker in all_speakers:
        lang = speaker.native_language
        languages[lang] = languages.get(lang, 0) + 1
    
    print(f"\n📚 Languages Available:")
    for lang, count in languages.items():
        print(f"   • {lang}: {count} speaker(s)")
    
    print(f"\n🎯 Total Matches Generated: {len(learners)}")
    
    print("\n✨ Demo completed! Database saved as 'language_tribe_demo.db'")
    print("🌐 You can now run the web interface to see the visual representation!")

if __name__ == "__main__":
    demo_matching_system()