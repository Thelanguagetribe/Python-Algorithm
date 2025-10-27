# The Language Tribe - Matching Algorithm

A sophisticated Python algorithm for matching language learners with native speakers based on multiple compatibility factors including language, lesson type preferences, location proximity, age similarity, and time availability.

## 🌟 Features

- **Multi-criteria Matching**: Evaluates language compatibility, lesson type preferences, location proximity, age similarity, and time availability
- **Flexible Lesson Types**: Supports in-person, online, and hybrid lesson preferences
- **Geographic Proximity**: Calculates distances using the Haversine formula for accurate location-based matching
- **Time Overlap Detection**: Finds overlapping availability between learners and speakers
- **Customizable Scoring**: Adjustable weights for different matching criteria
- **Scalable Design**: Modular architecture suitable for integration with web applications and databases

## 📁 Project Structure

```
├── models.py              # Data models for learners, speakers, and matches
├── utils.py               # Utility functions for distance and time calculations
├── language_matcher.py    # Core matching algorithm and database connector
├── demo.py               # Comprehensive demonstration with sample data
├── script.py             # Quick start script to run the demo
├── requirements.txt      # Python dependencies (optional for enhanced features)
└── README.md            # This file
```

## 🚀 Quick Start

1. **Clone or download the project files**
2. **Run the demo**:
   ```bash
   python script.py
   ```
   or
   ```bash
   python demo.py
   ```

## 📊 Algorithm Overview

### Matching Criteria

The algorithm evaluates compatibility based on five key factors:

1. **Language Match (40% weight)**: Must teach the target language
2. **Time Overlap (25% weight)**: Amount of overlapping availability
3. **Age Compatibility (15% weight)**: Age difference within acceptable range (default: 10 years)
4. **Location Proximity (15% weight)**: Distance for in-person lessons
5. **Teaching Experience (5% weight)**: Years of teaching experience

### Scoring System

- **Compatibility scores** range from 0.0 to 1.0
- **Minimum thresholds** can be set to filter low-quality matches
- **Custom weights** allow prioritizing different criteria based on business needs

## 💻 Usage Example

```python
from datetime import datetime, time
from models import LanguageLearner, NativeSpeaker, Location, TimeSlot, LessonType, DayOfWeek
from language_matcher import LanguageTribeMatchingService, DatabaseConnector

# Create database and service
db = DatabaseConnector()
service = LanguageTribeMatchingService(db)

# Add a language learner
learner = LanguageLearner(
    id="learner_001",
    name="Emma Thompson",
    age=28,
    target_language="Spanish",
    lesson_type_preference=LessonType.IN_PERSON,
    location=Location(51.5074, -0.1278, "London", "UK"),
    availability=[
        TimeSlot(DayOfWeek.TUESDAY, time(19, 0), time(21, 0)),
        TimeSlot(DayOfWeek.SATURDAY, time(9, 0), time(12, 0))
    ],
    max_distance_km=25.0,
    created_at=datetime.now()
)

# Add a native speaker
speaker = NativeSpeaker(
    id="speaker_001",
    name="Carlos Rodriguez",
    age=30,
    native_language="Spanish",
    teaching_languages=["Spanish"],
    lesson_types_offered=[LessonType.IN_PERSON, LessonType.ONLINE],
    location=Location(51.5074, -0.1278, "London", "UK"),
    availability=[
        TimeSlot(DayOfWeek.TUESDAY, time(19, 0), time(21, 0)),
        TimeSlot(DayOfWeek.SATURDAY, time(9, 0), time(12, 0))
    ],
    hourly_rate=35.0,
    years_experience=5,
    bio="Experienced Spanish teacher",
    is_verified=True,
    is_available=True,
    created_at=datetime.now()
)

# Add to database
db.add_learner(learner)
db.add_speaker(speaker)

# Find matches
matches = service.find_matches_for_learner("learner_001", min_score=0.5)

# Display results
for match in matches:
    summary = service.get_match_summary(match)
    print(f"Match: {match.speaker.name}")
    print(f"Compatibility: {summary['compatibility_score']:.1%}")
    print(f"Rate: £{summary['hourly_rate']}/hour")
```

## 🎯 Customizing Match Weights

```python
from language_matcher import MatchingWeights, LanguageMatcher

# Create custom weights (experience-focused)
custom_weights = MatchingWeights(
    language_match=30.0,      # Language compatibility
    time_overlap=20.0,        # Time availability  
    age_compatibility=10.0,   # Age similarity
    location_proximity=10.0,  # Location proximity
    experience=30.0           # Teaching experience
)

# Use custom matcher
matcher = LanguageMatcher(custom_weights)
service = LanguageTribeMatchingService(db, matcher)
```

## 🗄️ Database Integration

The current implementation uses an in-memory database connector for demonstration. For production use:

### PostgreSQL Example
```python
# Install: pip install psycopg2-binary SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('postgresql://user:password@localhost/languagetribe')
Session = sessionmaker(bind=engine)
```

### MySQL Example
```python
# Install: pip install PyMySQL SQLAlchemy
from sqlalchemy import create_engine

engine = create_engine('mysql+pymysql://user:password@localhost/languagetribe')
```

## 🌐 API Integration

### Flask Example
```python
from flask import Flask, jsonify, request
from language_matcher import LanguageTribeMatchingService

app = Flask(__name__)
service = LanguageTribeMatchingService(db)

@app.route('/api/matches/<learner_id>')
def get_matches(learner_id):
    min_score = request.args.get('min_score', 0.5, type=float)
    max_results = request.args.get('max_results', 10, type=int)
    
    matches = service.find_matches_for_learner(
        learner_id, 
        min_score=min_score, 
        max_matches=max_results
    )
    
    return jsonify([service.get_match_summary(match) for match in matches])
```

### FastAPI Example
```python
from fastapi import FastAPI, Query
from typing import List

app = FastAPI()

@app.get("/api/matches/{learner_id}")
async def get_matches(
    learner_id: str,
    min_score: float = Query(0.5, ge=0.0, le=1.0),
    max_results: int = Query(10, ge=1, le=50)
):
    matches = service.find_matches_for_learner(
        learner_id, 
        min_score=min_score, 
        max_matches=max_results
    )
    return [service.get_match_summary(match) for match in matches]
```

## 📈 Performance Optimization

For production deployments:

1. **Database Indexing**:
   ```sql
   CREATE INDEX idx_speakers_language ON speakers(teaching_languages);
   CREATE INDEX idx_speakers_location ON speakers(latitude, longitude);
   CREATE INDEX idx_learners_active ON learners(is_active);
   ```

2. **Caching with Redis**:
   ```python
   import redis
   r = redis.Redis(host='localhost', port=6379, db=0)
   
   # Cache frequent matches
   cache_key = f"matches:{learner_id}:{min_score}"
   cached_result = r.get(cache_key)
   ```

3. **Background Processing**:
   ```python
   from celery import Celery
   
   app = Celery('language_tribe')
   
   @app.task
   def generate_matches_async(learner_id):
       return service.find_matches_for_learner(learner_id)
   ```

## 🧪 Testing

Run the demonstration to see the algorithm in action:

```bash
python demo.py
```

The demo includes:
- Sample learners and speakers with realistic data
- Multiple matching scenarios
- Custom weight demonstrations
- Performance analytics

## 📋 Requirements

- **Python 3.7+** (uses dataclasses)
- **No external dependencies** for core functionality
- **Optional dependencies** in `requirements.txt` for web frameworks, databases, and enhanced features

## 🚀 Production Deployment

1. **Environment Setup**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Database Migration**:
   - Convert models to SQLAlchemy/Django ORM models
   - Create database tables and indexes

3. **API Deployment**:
   - Use gunicorn/uwsgi for production WSGI
   - Implement authentication and rate limiting
   - Add monitoring and logging

4. **Scaling Considerations**:
   - Use database connection pooling
   - Implement result caching
   - Consider microservices architecture for high load

## 🤝 Contributing

This algorithm is designed for "The Language Tribe" business. For modifications or enhancements:

1. Adjust matching weights in `MatchingWeights` class
2. Add new criteria in the `_evaluate_match` method
3. Extend data models for additional features
4. Implement custom distance calculations for specific regions

## 📄 License

Created for The Language Tribe business by Afreen. All rights reserved.

---

**The Language Tribe** - Connecting language learners with native speakers in their communities.
