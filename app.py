#!/usr/bin/env python3
"""
Language Tribe - Web Application
Flask-based front-end for the language matching system.
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from datetime import datetime, time
import json
from models import (
    LanguageLearner, NativeSpeaker, Location, Availability, 
    LessonType, DayOfWeek, TimeSlot
)
from database import LanguageTribeDatabase
from matching_algorithm import LanguageMatchingAlgorithm

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Initialize database and algorithm
db = LanguageTribeDatabase("language_tribe_demo.db")
algorithm = LanguageMatchingAlgorithm()

@app.route('/')
def index():
    """Home page showing overview of the platform."""
    # Get statistics
    speakers = db.get_all_active_speakers()
    
    # Calculate language statistics
    languages = {}
    total_rating = 0
    for speaker in speakers:
        lang = speaker.native_language
        languages[lang] = languages.get(lang, 0) + 1
        total_rating += speaker.rating
    
    avg_rating = total_rating / len(speakers) if speakers else 0
    
    stats = {
        'total_speakers': len(speakers),
        'languages_available': len(languages),
        'avg_rating': avg_rating,
        'languages': languages
    }
    
    return render_template('index.html', stats=stats)

@app.route('/learners')
def learners():
    """Show all language learners."""
    # For demo purposes, we'll get learners by trying IDs 1-10
    learner_list = []
    for i in range(1, 11):
        learner = db.get_language_learner(i)
        if learner:
            learner_list.append(learner)
    
    return render_template('learners.html', learners=learner_list)

@app.route('/speakers')
def speakers():
    """Show all native speakers."""
    speaker_list = db.get_all_active_speakers()
    return render_template('speakers.html', speakers=speaker_list)

@app.route('/find-matches/<int:learner_id>')
def find_matches(learner_id):
    """Find and display matches for a specific learner."""
    learner = db.get_language_learner(learner_id)
    if not learner:
        flash('Learner not found!', 'error')
        return redirect(url_for('learners'))
    
    # Get all speakers and find matches
    all_speakers = db.get_all_active_speakers()
    matches = algorithm.find_matches(learner, all_speakers, max_matches=10)
    
    # Get speaker details for each match
    match_details = []
    for match in matches:
        speaker = db.get_native_speaker(match.speaker_id)
        match_details.append({
            'match': match,
            'speaker': speaker
        })
    
    return render_template('matches.html', learner=learner, matches=match_details)

@app.route('/speaker/<int:speaker_id>')
def speaker_profile(speaker_id):
    """Show detailed speaker profile."""
    speaker = db.get_native_speaker(speaker_id)
    if not speaker:
        flash('Speaker not found!', 'error')
        return redirect(url_for('speakers'))
    
    return render_template('speaker_profile.html', speaker=speaker)

@app.route('/learner/<int:learner_id>')
def learner_profile(learner_id):
    """Show detailed learner profile."""
    learner = db.get_language_learner(learner_id)
    if not learner:
        flash('Learner not found!', 'error')
        return redirect(url_for('learners'))
    
    return render_template('learner_profile.html', learner=learner)

@app.route('/api/search-speakers')
def api_search_speakers():
    """API endpoint to search speakers by language."""
    language = request.args.get('language', '').strip()
    
    if language:
        speakers = db.search_speakers_by_language(language)
    else:
        speakers = db.get_all_active_speakers()
    
    # Convert speakers to JSON-serializable format
    speakers_data = []
    for speaker in speakers:
        speakers_data.append({
            'id': speaker.id,
            'name': speaker.name,
            'native_language': speaker.native_language,
            'secondary_languages': speaker.secondary_languages,
            'rating': speaker.rating,
            'hourly_rate': speaker.hourly_rate,
            'teaching_experience_years': speaker.teaching_experience_years,
            'bio': speaker.bio,
            'city': speaker.location.city if speaker.location else 'Online only',
            'lesson_types': [lt.value for lt in speaker.lesson_types_offered]
        })
    
    return jsonify(speakers_data)

@app.route('/dashboard')
def dashboard():
    """Admin dashboard showing system overview."""
    # Get all data
    speakers = db.get_all_active_speakers()
    learners = []
    for i in range(1, 11):
        learner = db.get_language_learner(i)
        if learner:
            learners.append(learner)
    
    # Calculate statistics
    languages = {}
    lesson_types = {'in_person': 0, 'online': 0, 'both': 0}
    
    for speaker in speakers:
        lang = speaker.native_language
        languages[lang] = languages.get(lang, 0) + 1
        
        for lt in speaker.lesson_types_offered:
            lesson_types[lt.value] += 1
    
    experience_ranges = {'0-2': 0, '3-5': 0, '6-10': 0, '10+': 0}
    for speaker in speakers:
        exp = speaker.teaching_experience_years
        if exp <= 2:
            experience_ranges['0-2'] += 1
        elif exp <= 5:
            experience_ranges['3-5'] += 1
        elif exp <= 10:
            experience_ranges['6-10'] += 1
        else:
            experience_ranges['10+'] += 1
    
    dashboard_data = {
        'speakers': speakers,
        'learners': learners,
        'languages': languages,
        'lesson_types': lesson_types,
        'experience_ranges': experience_ranges,
        'total_speakers': len(speakers),
        'total_learners': len(learners)
    }
    
    return render_template('dashboard.html', data=dashboard_data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)