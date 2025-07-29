#!/usr/bin/env python3
"""
The Language Tribe - Matching Algorithm Demo
Author: Assistant for Afreen
Date: January 2025

This demo shows how the language matching algorithm works with sample data.
"""

from datetime import datetime, time
from models import (
    LanguageLearner, NativeSpeaker, Location, TimeSlot, 
    LessonType, DayOfWeek
)
from language_matcher import (
    LanguageMatcher, DatabaseConnector, LanguageTribeMatchingService,
    MatchingWeights
)
from utils import format_time_slot


def create_sample_data():
    """Create sample language learners and native speakers for demonstration"""
    
    # Create locations
    london = Location(51.5074, -0.1278, "London", "UK")
    manchester = Location(53.4808, -2.2426, "Manchester", "UK")
    birmingham = Location(52.4862, -1.8904, "Birmingham", "UK")
    paris = Location(48.8566, 2.3522, "Paris", "France")
    madrid = Location(40.4168, -3.7038, "Madrid", "Spain")
    
    # Create time slots
    weekday_evening = TimeSlot(DayOfWeek.TUESDAY, time(19, 0), time(21, 0))
    saturday_morning = TimeSlot(DayOfWeek.SATURDAY, time(9, 0), time(12, 0))
    sunday_afternoon = TimeSlot(DayOfWeek.SUNDAY, time(14, 0), time(17, 0))
    weekday_morning = TimeSlot(DayOfWeek.WEDNESDAY, time(9, 0), time(11, 0))
    friday_evening = TimeSlot(DayOfWeek.FRIDAY, time(18, 0), time(20, 0))
    
    # Sample Language Learners
    learners = [
        LanguageLearner(
            id="learner_001",
            name="Emma Thompson",
            email="emma@email.com",
            age=28,
            target_language="Spanish",
            lesson_type_preference=LessonType.IN_PERSON,
            location=london,
            availability=[weekday_evening, saturday_morning],
            max_distance_km=25.0,
            created_at=datetime.now(),
            is_active=True
        ),
        LanguageLearner(
            id="learner_002", 
            name="James Wilson",
            email="james@email.com",
            age=35,
            target_language="French",
            lesson_type_preference=LessonType.ONLINE,
            location=manchester,
            availability=[sunday_afternoon, weekday_morning],
            max_distance_km=None,  # Online only
            created_at=datetime.now(),
            is_active=True
        ),
        LanguageLearner(
            id="learner_003",
            name="Sarah Johnson", 
            email="sarah@email.com",
            age=22,
            target_language="Spanish",
            lesson_type_preference=LessonType.BOTH,
            location=birmingham,
            availability=[friday_evening, saturday_morning],
            max_distance_km=50.0,
            created_at=datetime.now(),
            is_active=True
        )
    ]
    
    # Sample Native Speakers
    speakers = [
        NativeSpeaker(
            id="speaker_001",
            name="Carlos Rodriguez",
            email="carlos@email.com", 
            age=30,
            native_language="Spanish",
            teaching_languages=["Spanish", "English"],
            lesson_types_offered=[LessonType.IN_PERSON, LessonType.ONLINE],
            location=london,
            availability=[weekday_evening, saturday_morning, sunday_afternoon],
            hourly_rate=35.0,
            years_experience=5,
            bio="Native Spanish speaker from Madrid with 5 years teaching experience.",
            is_verified=True,
            is_available=True,
            created_at=datetime.now()
        ),
        NativeSpeaker(
            id="speaker_002",
            name="Marie Dubois", 
            email="marie@email.com",
            age=26,
            native_language="French",
            teaching_languages=["French"],
            lesson_types_offered=[LessonType.ONLINE],
            location=paris,
            availability=[sunday_afternoon, weekday_morning, friday_evening],
            hourly_rate=40.0,
            years_experience=3,
            bio="French native from Paris, specializes in conversational French.",
            is_verified=True,
            is_available=True,
            created_at=datetime.now()
        ),
        NativeSpeaker(
            id="speaker_003",
            name="Isabella Garcia",
            email="isabella@email.com",
            age=24,
            native_language="Spanish", 
            teaching_languages=["Spanish"],
            lesson_types_offered=[LessonType.IN_PERSON],
            location=birmingham,
            availability=[friday_evening, saturday_morning],
            hourly_rate=30.0,
            years_experience=2,
            bio="Young and enthusiastic Spanish teacher, focuses on conversation practice.",
            is_verified=True,
            is_available=True,
            created_at=datetime.now()
        ),
        NativeSpeaker(
            id="speaker_004",
            name="Pedro Martinez",
            email="pedro@email.com",
            age=45,
            native_language="Spanish",
            teaching_languages=["Spanish", "Portuguese"],
            lesson_types_offered=[LessonType.BOTH],
            location=madrid,
            availability=[weekday_evening, saturday_morning],
            hourly_rate=50.0,
            years_experience=15,
            bio="Experienced language teacher with 15 years of teaching Spanish and Portuguese.",
            is_verified=True,
            is_available=True,
            created_at=datetime.now()
        )
    ]
    
    return learners, speakers


def demonstrate_matching():
    """Demonstrate the matching algorithm with sample data"""
    
    print("=" * 60)
    print("THE LANGUAGE TRIBE - MATCHING ALGORITHM DEMO")
    print("=" * 60)
    print()
    
    # Create sample data
    learners, speakers = create_sample_data()
    
    # Set up the matching service
    db = DatabaseConnector()
    
    # Add data to database
    for learner in learners:
        db.add_learner(learner)
    for speaker in speakers:
        db.add_speaker(speaker)
    
    # Create matching service
    service = LanguageTribeMatchingService(db)
    
    print(f"Database initialized with:")
    print(f"- {len(learners)} language learners")
    print(f"- {len(speakers)} native speakers")
    print()
    
    # Demonstrate matching for each learner
    for i, learner in enumerate(learners, 1):
        print(f"{'='*50}")
        print(f"LEARNER {i}: {learner.name}")
        print(f"{'='*50}")
        print(f"Age: {learner.age}")
        print(f"Target Language: {learner.target_language}")
        print(f"Lesson Preference: {learner.lesson_type_preference.value}")
        print(f"Location: {learner.location.city if learner.location else 'Not specified'}")
        print(f"Max Distance: {learner.max_distance_km} km" if learner.max_distance_km else "Max Distance: N/A (online)")
        print("Availability:")
        for slot in learner.availability:
            print(f"  - {format_time_slot(slot)}")
        print()
        
        # Find matches
        try:
            matches = service.find_matches_for_learner(learner.id, min_score=0.3, max_matches=5)
            
            if matches:
                print(f"Found {len(matches)} compatible matches:")
                print()
                
                for j, match in enumerate(matches, 1):
                    summary = service.get_match_summary(match)
                    speaker = match.speaker
                    
                    print(f"  MATCH {j}: {speaker.name}")
                    print(f"  Compatibility Score: {summary['compatibility_score']:.1%}")
                    print(f"  Rate: £{summary['hourly_rate']}/hour")
                    print(f"  Experience: {summary['years_experience']} years")
                    print(f"  Age Difference: {summary['age_difference']} years")
                    if summary['distance_km']:
                        print(f"  Distance: {summary['distance_km']} km")
                    print(f"  Time Overlap: {summary['time_overlap_hours']} hours")
                    print(f"  Lesson Types: {', '.join([lt.value for lt in speaker.lesson_types_offered])}")
                    print("  Match Reasons:")
                    for reason in summary['reasons']:
                        print(f"    • {reason}")
                    print()
            else:
                print("❌ No compatible matches found with current criteria.")
                print("Consider adjusting preferences or expanding search parameters.")
                print()
        
        except Exception as e:
            print(f"❌ Error finding matches: {e}")
            print()


def demonstrate_custom_weights():
    """Demonstrate how different weighting affects matching results"""
    
    print("=" * 60)
    print("CUSTOM WEIGHTING DEMONSTRATION")
    print("=" * 60)
    print()
    
    learners, speakers = create_sample_data()
    
    # Set up database
    db = DatabaseConnector()
    for learner in learners:
        db.add_learner(learner)
    for speaker in speakers:
        db.add_speaker(speaker)
    
    # Test with different weight configurations
    weight_configs = [
        ("Balanced (Default)", MatchingWeights()),
        ("Experience-Focused", MatchingWeights(
            language_match=30.0,
            time_overlap=20.0, 
            age_compatibility=10.0,
            location_proximity=10.0,
            experience=30.0
        )),
        ("Time-Priority", MatchingWeights(
            language_match=30.0,
            time_overlap=40.0,
            age_compatibility=10.0, 
            location_proximity=15.0,
            experience=5.0
        ))
    ]
    
    # Test with first learner
    test_learner = learners[0]  # Emma Thompson
    print(f"Testing different weights for: {test_learner.name}")
    print(f"Target: {test_learner.target_language}, {test_learner.lesson_type_preference.value}")
    print()
    
    for config_name, weights in weight_configs:
        print(f"--- {config_name} ---")
        
        matcher = LanguageMatcher(weights)
        service = LanguageTribeMatchingService(db, matcher)
        
        matches = service.find_matches_for_learner(test_learner.id, min_score=0.3)
        
        print("Top 3 matches:")
        for i, match in enumerate(matches[:3], 1):
            summary = service.get_match_summary(match)
            print(f"  {i}. {match.speaker.name}: {summary['compatibility_score']:.1%}")
        print()


def main():
    """Main demonstration function"""
    try:
        demonstrate_matching()
        demonstrate_custom_weights()
        
        print("=" * 60)
        print("INTEGRATION NOTES")
        print("=" * 60)
        print("""
To integrate this algorithm into your application:

1. DATABASE INTEGRATION:
   - Replace DatabaseConnector with your actual database (PostgreSQL, MySQL, etc.)
   - Implement proper ORM models (SQLAlchemy, Django ORM, etc.)
   - Add database indexes for better performance

2. API INTEGRATION:
   - Create REST API endpoints using Flask/FastAPI/Django
   - Add authentication and authorization
   - Implement rate limiting and caching

3. REAL-TIME FEATURES:
   - Add WebSocket support for real-time match notifications
   - Implement background job processing for large datasets
   - Add matching result caching

4. SCALABILITY:
   - Use database indexes on frequently queried fields
   - Consider using Redis for caching frequently accessed data
   - Implement pagination for large result sets

5. MONITORING:
   - Add logging for match quality metrics
   - Track user satisfaction with matches
   - Monitor algorithm performance and adjust weights accordingly

Example API endpoint structure:
GET /api/matches/{learner_id}?min_score=0.5&max_results=10
POST /api/learners (to add new learner)
POST /api/speakers (to add new speaker)
        """)
        
    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()