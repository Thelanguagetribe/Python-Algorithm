#!/usr/bin/env python3
"""
The Language Tribe - Flask API Example
This shows how to integrate the matching algorithm with a Flask web API.

To run this example:
1. Install Flask: pip install Flask
2. Run: python api_example.py
3. Test endpoints:
   - GET /api/matches/learner_001
   - GET /api/learners
   - GET /api/speakers
"""

from flask import Flask, jsonify, request
from datetime import datetime, time
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import LanguageLearner, NativeSpeaker, Location, TimeSlot, LessonType, DayOfWeek
from language_matcher import LanguageTribeMatchingService, DatabaseConnector, MatchingWeights

app = Flask(__name__)

# Initialize the service with sample data
def initialize_service():
    """Initialize the service with sample data"""
    db = DatabaseConnector()
    
    # Create sample locations
    london = Location(51.5074, -0.1278, "London", "UK")
    manchester = Location(53.4808, -2.2426, "Manchester", "UK")
    birmingham = Location(52.4862, -1.8904, "Birmingham", "UK")
    
    # Create sample learners
    learners = [
        LanguageLearner(
            id="learner_001",
            name="Emma Thompson",
            email="emma@email.com",
            age=28,
            target_language="Spanish",
            lesson_type_preference=LessonType.IN_PERSON,
            location=london,
            availability=[
                TimeSlot(DayOfWeek.TUESDAY, time(19, 0), time(21, 0)),
                TimeSlot(DayOfWeek.SATURDAY, time(9, 0), time(12, 0))
            ],
            max_distance_km=25.0,
            created_at=datetime.now()
        ),
        LanguageLearner(
            id="learner_002",
            name="James Wilson",
            email="james@email.com",
            age=35,
            target_language="French",
            lesson_type_preference=LessonType.ONLINE,
            location=manchester,
            availability=[
                TimeSlot(DayOfWeek.SUNDAY, time(14, 0), time(17, 0)),
                TimeSlot(DayOfWeek.WEDNESDAY, time(9, 0), time(11, 0))
            ],
            max_distance_km=None,
            created_at=datetime.now()
        )
    ]
    
    # Create sample speakers
    speakers = [
        NativeSpeaker(
            id="speaker_001",
            name="Carlos Rodriguez",
            email="carlos@email.com",
            age=30,
            native_language="Spanish",
            teaching_languages=["Spanish"],
            lesson_types_offered=[LessonType.IN_PERSON, LessonType.ONLINE],
            location=london,
            availability=[
                TimeSlot(DayOfWeek.TUESDAY, time(19, 0), time(21, 0)),
                TimeSlot(DayOfWeek.SATURDAY, time(9, 0), time(12, 0))
            ],
            hourly_rate=35.0,
            years_experience=5,
            bio="Experienced Spanish teacher from Madrid",
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
            location=None,  # Online only
            availability=[
                TimeSlot(DayOfWeek.SUNDAY, time(14, 0), time(17, 0)),
                TimeSlot(DayOfWeek.WEDNESDAY, time(9, 0), time(11, 0))
            ],
            hourly_rate=40.0,
            years_experience=3,
            bio="French native speaker specializing in conversation",
            is_verified=True,
            is_available=True,
            created_at=datetime.now()
        )
    ]
    
    # Add to database
    for learner in learners:
        db.add_learner(learner)
    for speaker in speakers:
        db.add_speaker(speaker)
    
    return LanguageTribeMatchingService(db)

# Initialize service
service = initialize_service()

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "The Language Tribe Matching API"})

@app.route('/api/matches/<learner_id>')
def get_matches(learner_id):
    """Get matches for a specific learner"""
    try:
        # Get query parameters
        min_score = request.args.get('min_score', 0.5, type=float)
        max_results = request.args.get('max_results', 10, type=int)
        
        # Validate parameters
        if not 0.0 <= min_score <= 1.0:
            return jsonify({"error": "min_score must be between 0.0 and 1.0"}), 400
        if not 1 <= max_results <= 50:
            return jsonify({"error": "max_results must be between 1 and 50"}), 400
        
        # Find matches
        matches = service.find_matches_for_learner(
            learner_id,
            min_score=min_score,
            max_matches=max_results
        )
        
        # Format response
        return jsonify({
            "learner_id": learner_id,
            "total_matches": len(matches),
            "min_score": min_score,
            "matches": [service.get_match_summary(match) for match in matches]
        })
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/learners')
def get_learners():
    """Get all active learners"""
    try:
        learners = service.db.get_active_learners()
        return jsonify({
            "total_learners": len(learners),
            "learners": [
                {
                    "id": learner.id,
                    "name": learner.name,
                    "age": learner.age,
                    "target_language": learner.target_language,
                    "lesson_type_preference": learner.lesson_type_preference.value,
                    "location": {
                        "city": learner.location.city,
                        "country": learner.location.country
                    } if learner.location else None,
                    "max_distance_km": learner.max_distance_km
                }
                for learner in learners
            ]
        })
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/speakers')
def get_speakers():
    """Get all available speakers"""
    try:
        language = request.args.get('language')  # Optional filter
        speakers = service.db.get_available_speakers(language)
        
        return jsonify({
            "total_speakers": len(speakers),
            "filtered_by_language": language,
            "speakers": [
                {
                    "id": speaker.id,
                    "name": speaker.name,
                    "age": speaker.age,
                    "native_language": speaker.native_language,
                    "teaching_languages": speaker.teaching_languages,
                    "lesson_types_offered": [lt.value for lt in speaker.lesson_types_offered],
                    "hourly_rate": speaker.hourly_rate,
                    "years_experience": speaker.years_experience,
                    "location": {
                        "city": speaker.location.city,
                        "country": speaker.location.country
                    } if speaker.location else None,
                    "is_verified": speaker.is_verified
                }
                for speaker in speakers
            ]
        })
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/custom-matching/<learner_id>', methods=['POST'])
def custom_matching(learner_id):
    """Get matches with custom weights"""
    try:
        data = request.get_json()
        
        # Create custom weights from request
        weights = MatchingWeights(
            language_match=data.get('language_match', 40.0),
            time_overlap=data.get('time_overlap', 25.0),
            age_compatibility=data.get('age_compatibility', 15.0),
            location_proximity=data.get('location_proximity', 15.0),
            experience=data.get('experience', 5.0)
        )
        
        # Create custom service
        from language_matcher import LanguageMatcher
        custom_matcher = LanguageMatcher(weights)
        custom_service = LanguageTribeMatchingService(service.db, custom_matcher)
        
        # Get parameters
        min_score = data.get('min_score', 0.5)
        max_results = data.get('max_results', 10)
        
        # Find matches
        matches = custom_service.find_matches_for_learner(
            learner_id,
            min_score=min_score,
            max_matches=max_results
        )
        
        return jsonify({
            "learner_id": learner_id,
            "custom_weights": {
                "language_match": weights.language_match,
                "time_overlap": weights.time_overlap,
                "age_compatibility": weights.age_compatibility,
                "location_proximity": weights.location_proximity,
                "experience": weights.experience
            },
            "total_matches": len(matches),
            "matches": [custom_service.get_match_summary(match) for match in matches]
        })
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "Method not allowed"}), 405

if __name__ == '__main__':
    print("=" * 60)
    print("THE LANGUAGE TRIBE - API SERVER")
    print("=" * 60)
    print()
    print("Starting Flask API server...")
    print("Available endpoints:")
    print("- GET  /api/health")
    print("- GET  /api/learners")
    print("- GET  /api/speakers?language=Spanish")
    print("- GET  /api/matches/learner_001?min_score=0.5&max_results=10")
    print("- POST /api/custom-matching/learner_001")
    print()
    print("Example requests:")
    print("curl http://localhost:5000/api/matches/learner_001")
    print("curl http://localhost:5000/api/speakers?language=Spanish")
    print()
    
    app.run(debug=True, host='0.0.0.0', port=5000)