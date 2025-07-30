#!/usr/bin/env python3
"""
Language Tribe - Web Application
Flask-based front-end for the language matching system with integrated booking.
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from datetime import datetime, time, timedelta
import json
from models import (
    LanguageLearner, NativeSpeaker, Location, Availability, 
    LessonType, DayOfWeek, TimeSlot
)
from database import LanguageTribeDatabase
from matching_algorithm import LanguageMatchingAlgorithm

# Import booking system
from booking_models import BookingStatus, PaymentStatus, LessonType as BookingLessonType
from booking_database import BookingDatabase
from booking_service import BookingService

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Initialize databases and services
db = LanguageTribeDatabase("language_tribe_demo.db")
booking_db = BookingDatabase("language_tribe_booking.db")
algorithm = LanguageMatchingAlgorithm()
booking_service = BookingService(booking_db, db)

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

# ==================== BOOKING SYSTEM ROUTES ====================

@app.route('/book/<int:speaker_id>')
def book_lesson(speaker_id):
    """Show booking page for a specific speaker."""
    speaker = db.get_native_speaker(speaker_id)
    if not speaker:
        flash('Speaker not found!', 'error')
        return redirect(url_for('speakers'))
    
    # Get learner ID from session (in real app, you'd have user authentication)
    learner_id = request.args.get('learner_id', 1, type=int)
    learner = db.get_language_learner(learner_id)
    
    if not learner:
        flash('Please log in to book lessons', 'error')
        return redirect(url_for('learners'))
    
    return render_template('booking/book_lesson.html', speaker=speaker, learner=learner)

@app.route('/api/available-slots/<int:speaker_id>')
def api_available_slots(speaker_id):
    """API endpoint to get available slots for a speaker."""
    date_from_str = request.args.get('date_from')
    date_to_str = request.args.get('date_to')
    
    if not date_from_str or not date_to_str:
        return jsonify({"error": "Missing date parameters"}), 400
    
    try:
        date_from = datetime.fromisoformat(date_from_str)
        date_to = datetime.fromisoformat(date_to_str)
    except ValueError:
        return jsonify({"error": "Invalid date format"}), 400
    
    slots = booking_service.get_available_slots(speaker_id, date_from, date_to)
    return jsonify({"slots": slots})

@app.route('/api/create-booking', methods=['POST'])
def api_create_booking():
    """API endpoint to create a new booking."""
    data = request.get_json()
    
    required_fields = ['learner_id', 'speaker_id', 'lesson_date', 'duration_minutes']
    if not all(field in data for field in required_fields):
        return jsonify({"success": False, "error": "Missing required fields"}), 400
    
    try:
        lesson_date = datetime.fromisoformat(data['lesson_date'])
        lesson_type = BookingLessonType.SINGLE  # Default to single lesson
        
        result = booking_service.create_booking(
            learner_id=data['learner_id'],
            speaker_id=data['speaker_id'],
            lesson_date=lesson_date,
            duration_minutes=data['duration_minutes'],
            lesson_type=lesson_type,
            booking_notes=data.get('notes'),
            lesson_topic=data.get('topic')
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/process-payment', methods=['POST'])
def api_process_payment():
    """API endpoint to process payment for a booking."""
    data = request.get_json()
    
    if 'booking_id' not in data or 'payment_method_id' not in data:
        return jsonify({"success": False, "error": "Missing required fields"}), 400
    
    result = booking_service.process_payment(
        booking_id=data['booking_id'],
        payment_method_id=data['payment_method_id']
    )
    
    return jsonify(result)

@app.route('/bookings/learner/<int:learner_id>')
def learner_bookings(learner_id):
    """Show all bookings for a learner."""
    learner = db.get_language_learner(learner_id)
    if not learner:
        flash('Learner not found!', 'error')
        return redirect(url_for('learners'))
    
    bookings = booking_service.get_learner_bookings(learner_id)
    return render_template('booking/learner_bookings.html', learner=learner, bookings=bookings)

@app.route('/bookings/speaker/<int:speaker_id>')
def speaker_bookings(speaker_id):
    """Show all bookings for a speaker."""
    speaker = db.get_native_speaker(speaker_id)
    if not speaker:
        flash('Speaker not found!', 'error')
        return redirect(url_for('speakers'))
    
    bookings = booking_service.get_speaker_bookings(speaker_id)
    return render_template('booking/speaker_bookings.html', speaker=speaker, bookings=bookings)

@app.route('/booking/<booking_id>')
def booking_details(booking_id):
    """Show detailed booking information."""
    booking = booking_db.get_booking(booking_id)
    if not booking:
        flash('Booking not found!', 'error')
        return redirect(url_for('dashboard'))
    
    learner = db.get_language_learner(booking.learner_id)
    speaker = db.get_native_speaker(booking.speaker_id)
    
    return render_template('booking/booking_details.html', 
                         booking=booking, learner=learner, speaker=speaker)

@app.route('/api/cancel-booking', methods=['POST'])
def api_cancel_booking():
    """API endpoint to cancel a booking."""
    data = request.get_json()
    
    if 'booking_id' not in data:
        return jsonify({"success": False, "error": "Missing booking_id"}), 400
    
    result = booking_service.cancel_booking(
        booking_id=data['booking_id'],
        cancelled_by=data.get('cancelled_by', 'user'),
        reason=data.get('reason')
    )
    
    return jsonify(result)

@app.route('/api/complete-lesson', methods=['POST'])
def api_complete_lesson():
    """API endpoint to mark a lesson as completed."""
    data = request.get_json()
    
    if 'booking_id' not in data:
        return jsonify({"success": False, "error": "Missing booking_id"}), 400
    
    result = booking_service.complete_lesson(data['booking_id'])
    return jsonify(result)

# ==================== EXISTING ROUTES ====================

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
    
    # Get booking statistics
    booking_stats = {
        'total_bookings': 0,
        'confirmed_bookings': 0,
        'completed_bookings': 0,
        'revenue': 0
    }
    
    # In a real app, you'd query the booking database for these stats
    
    dashboard_data = {
        'speakers': speakers,
        'learners': learners,
        'languages': languages,
        'lesson_types': lesson_types,
        'experience_ranges': experience_ranges,
        'total_speakers': len(speakers),
        'total_learners': len(learners),
        'booking_stats': booking_stats
    }
    
    return render_template('dashboard.html', data=dashboard_data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)