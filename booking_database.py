import sqlite3
import json
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from booking_models import (
    Booking, Payment, Calendar, TimeSlot, LessonPackage,
    Notification, Review, Coupon, BookingSettings,
    BookingStatus, PaymentStatus, LessonType, NotificationType
)

class BookingDatabase:
    def __init__(self, db_path: str = "language_tribe_booking.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the booking database with all required tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Bookings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id TEXT PRIMARY KEY,
                learner_id INTEGER NOT NULL,
                speaker_id INTEGER NOT NULL,
                lesson_date TEXT NOT NULL,
                duration_minutes INTEGER NOT NULL,
                lesson_type TEXT NOT NULL,
                status TEXT NOT NULL,
                total_amount REAL NOT NULL,
                currency TEXT NOT NULL,
                payment_status TEXT NOT NULL,
                booking_notes TEXT,
                lesson_topic TEXT,
                meeting_link TEXT,
                meeting_location TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                cancelled_at TEXT,
                cancellation_reason TEXT,
                rating_learner REAL,
                rating_speaker REAL,
                feedback_learner TEXT,
                feedback_speaker TEXT,
                FOREIGN KEY (learner_id) REFERENCES language_learners (id),
                FOREIGN KEY (speaker_id) REFERENCES native_speakers (id)
            )
        """)
        
        # Payments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id TEXT PRIMARY KEY,
                booking_id TEXT NOT NULL,
                amount REAL NOT NULL,
                currency TEXT NOT NULL,
                payment_method TEXT NOT NULL,
                payment_intent_id TEXT,
                status TEXT NOT NULL,
                transaction_fee REAL NOT NULL,
                net_amount REAL NOT NULL,
                processed_at TEXT,
                refund_amount REAL,
                refund_reason TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (booking_id) REFERENCES bookings (id)
            )
        """)
        
        # Calendars table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS calendars (
                id TEXT PRIMARY KEY,
                speaker_id INTEGER NOT NULL,
                available_slots TEXT NOT NULL,  -- JSON
                booked_slots TEXT NOT NULL,     -- JSON
                blocked_slots TEXT NOT NULL,    -- JSON
                timezone TEXT NOT NULL,
                auto_confirm BOOLEAN DEFAULT 1,
                buffer_time_minutes INTEGER DEFAULT 15,
                max_lessons_per_day INTEGER DEFAULT 8,
                advance_booking_days INTEGER DEFAULT 30,
                FOREIGN KEY (speaker_id) REFERENCES native_speakers (id)
            )
        """)
        
        # Lesson packages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lesson_packages (
                id TEXT PRIMARY KEY,
                speaker_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                total_lessons INTEGER NOT NULL,
                lessons_used INTEGER DEFAULT 0,
                price_per_lesson REAL NOT NULL,
                total_price REAL NOT NULL,
                discount_percentage REAL NOT NULL,
                valid_until TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                created_at TEXT NOT NULL,
                FOREIGN KEY (speaker_id) REFERENCES native_speakers (id)
            )
        """)
        
        # Notifications table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id TEXT PRIMARY KEY,
                recipient_id INTEGER NOT NULL,
                recipient_type TEXT NOT NULL,
                notification_type TEXT NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                booking_id TEXT,
                is_read BOOLEAN DEFAULT 0,
                is_sent BOOLEAN DEFAULT 0,
                send_at TEXT NOT NULL,
                sent_at TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (booking_id) REFERENCES bookings (id)
            )
        """)
        
        # Reviews table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                id TEXT PRIMARY KEY,
                booking_id TEXT NOT NULL,
                reviewer_id INTEGER NOT NULL,
                reviewer_type TEXT NOT NULL,
                reviewee_id INTEGER NOT NULL,
                rating REAL NOT NULL,
                comment TEXT,
                is_anonymous BOOLEAN DEFAULT 0,
                is_verified BOOLEAN DEFAULT 1,
                created_at TEXT NOT NULL,
                FOREIGN KEY (booking_id) REFERENCES bookings (id)
            )
        """)
        
        # Coupons table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS coupons (
                id TEXT PRIMARY KEY,
                code TEXT UNIQUE NOT NULL,
                description TEXT NOT NULL,
                discount_type TEXT NOT NULL,
                discount_value REAL NOT NULL,
                minimum_amount REAL,
                max_uses INTEGER,
                current_uses INTEGER DEFAULT 0,
                valid_from TEXT NOT NULL,
                valid_until TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                applicable_to TEXT DEFAULT 'all'
            )
        """)
        
        # Booking settings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS booking_settings (
                speaker_id INTEGER PRIMARY KEY,
                cancellation_policy_hours INTEGER DEFAULT 24,
                late_cancellation_fee_percent REAL DEFAULT 50.0,
                no_show_fee_percent REAL DEFAULT 100.0,
                auto_confirm_bookings BOOLEAN DEFAULT 1,
                require_payment_upfront BOOLEAN DEFAULT 1,
                allow_reschedule BOOLEAN DEFAULT 1,
                reschedule_limit_hours INTEGER DEFAULT 6,
                buffer_time_minutes INTEGER DEFAULT 15,
                max_advance_booking_days INTEGER DEFAULT 30,
                FOREIGN KEY (speaker_id) REFERENCES native_speakers (id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def create_booking(self, booking: Booking) -> str:
        """Create a new booking."""
        if not booking.id:
            booking.id = str(uuid.uuid4())
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO bookings (
                id, learner_id, speaker_id, lesson_date, duration_minutes,
                lesson_type, status, total_amount, currency, payment_status,
                booking_notes, lesson_topic, meeting_link, meeting_location,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            booking.id, booking.learner_id, booking.speaker_id,
            booking.lesson_date.isoformat(), booking.duration_minutes,
            booking.lesson_type.value, booking.status.value,
            booking.total_amount, booking.currency, booking.payment_status.value,
            booking.booking_notes, booking.lesson_topic,
            booking.meeting_link, booking.meeting_location,
            booking.created_at.isoformat(), booking.updated_at.isoformat()
        ))
        
        conn.commit()
        conn.close()
        return booking.id
    
    def get_booking(self, booking_id: str) -> Optional[Booking]:
        """Retrieve a booking by ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM bookings WHERE id = ?", (booking_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return self._row_to_booking(row)
    
    def get_bookings_by_learner(self, learner_id: int) -> List[Booking]:
        """Get all bookings for a specific learner."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM bookings WHERE learner_id = ? ORDER BY lesson_date DESC",
            (learner_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_booking(row) for row in rows]
    
    def get_bookings_by_speaker(self, speaker_id: int) -> List[Booking]:
        """Get all bookings for a specific speaker."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM bookings WHERE speaker_id = ? ORDER BY lesson_date DESC",
            (speaker_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_booking(row) for row in rows]
    
    def update_booking_status(self, booking_id: str, status: BookingStatus,
                            cancellation_reason: Optional[str] = None) -> bool:
        """Update booking status."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        update_time = datetime.now().isoformat()
        
        if status == BookingStatus.CANCELLED:
            cursor.execute("""
                UPDATE bookings 
                SET status = ?, updated_at = ?, cancelled_at = ?, cancellation_reason = ?
                WHERE id = ?
            """, (status.value, update_time, update_time, cancellation_reason, booking_id))
        else:
            cursor.execute("""
                UPDATE bookings 
                SET status = ?, updated_at = ?
                WHERE id = ?
            """, (status.value, update_time, booking_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success
    
    def create_payment(self, payment: Payment) -> str:
        """Create a payment record."""
        if not payment.id:
            payment.id = str(uuid.uuid4())
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO payments (
                id, booking_id, amount, currency, payment_method,
                payment_intent_id, status, transaction_fee, net_amount,
                processed_at, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            payment.id, payment.booking_id, payment.amount, payment.currency,
            payment.payment_method, payment.payment_intent_id, payment.status.value,
            payment.transaction_fee, payment.net_amount,
            payment.processed_at.isoformat() if payment.processed_at else None,
            payment.created_at.isoformat()
        ))
        
        conn.commit()
        conn.close()
        return payment.id
    
    def get_available_slots(self, speaker_id: int, date_from: datetime, 
                          date_to: datetime) -> List[TimeSlot]:
        """Get available time slots for a speaker in a date range."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get speaker's calendar
        cursor.execute("SELECT * FROM calendars WHERE speaker_id = ?", (speaker_id,))
        calendar_row = cursor.fetchone()
        
        if not calendar_row:
            conn.close()
            return []
        
        # Get booked slots in the date range
        cursor.execute("""
            SELECT lesson_date, duration_minutes FROM bookings 
            WHERE speaker_id = ? AND lesson_date BETWEEN ? AND ? 
            AND status NOT IN ('cancelled', 'no_show')
        """, (speaker_id, date_from.isoformat(), date_to.isoformat()))
        
        booked_times = cursor.fetchall()
        conn.close()
        
        # Parse calendar data
        available_slots_data = json.loads(calendar_row[2])  # available_slots column
        blocked_slots_data = json.loads(calendar_row[4])    # blocked_slots column
        
        # Convert to TimeSlot objects and filter by availability
        available_slots = []
        for slot_data in available_slots_data:
            slot_start = datetime.fromisoformat(slot_data['start_time'])
            slot_end = datetime.fromisoformat(slot_data['end_time'])
            
            # Check if slot is in requested range
            if date_from <= slot_start <= date_to:
                # Check if slot conflicts with booked times
                is_available = True
                for booked_time, duration in booked_times:
                    booked_start = datetime.fromisoformat(booked_time)
                    booked_end = booked_start + timedelta(minutes=duration)
                    
                    # Check for overlap
                    if (slot_start < booked_end and slot_end > booked_start):
                        is_available = False
                        break
                
                if is_available:
                    available_slots.append(TimeSlot(
                        start_time=slot_start,
                        end_time=slot_end,
                        is_available=True
                    ))
        
        return available_slots
    
    def create_notification(self, notification: Notification) -> str:
        """Create a notification."""
        if not notification.id:
            notification.id = str(uuid.uuid4())
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO notifications (
                id, recipient_id, recipient_type, notification_type,
                title, message, booking_id, send_at, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            notification.id, notification.recipient_id, notification.recipient_type,
            notification.notification_type.value, notification.title,
            notification.message, notification.booking_id,
            notification.send_at.isoformat(), notification.created_at.isoformat()
        ))
        
        conn.commit()
        conn.close()
        return notification.id
    
    def get_pending_notifications(self) -> List[Notification]:
        """Get notifications that need to be sent."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        cursor.execute("""
            SELECT * FROM notifications 
            WHERE is_sent = 0 AND send_at <= ?
            ORDER BY send_at ASC
        """, (now,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_notification(row) for row in rows]
    
    def _row_to_booking(self, row) -> Booking:
        """Convert database row to Booking object."""
        return Booking(
            id=row[0],
            learner_id=row[1],
            speaker_id=row[2],
            lesson_date=datetime.fromisoformat(row[3]),
            duration_minutes=row[4],
            lesson_type=LessonType(row[5]),
            status=BookingStatus(row[6]),
            total_amount=row[7],
            currency=row[8],
            payment_status=PaymentStatus(row[9]),
            booking_notes=row[10],
            lesson_topic=row[11],
            meeting_link=row[12],
            meeting_location=row[13],
            created_at=datetime.fromisoformat(row[14]),
            updated_at=datetime.fromisoformat(row[15]),
            cancelled_at=datetime.fromisoformat(row[16]) if row[16] else None,
            cancellation_reason=row[17],
            rating_learner=row[18],
            rating_speaker=row[19],
            feedback_learner=row[20],
            feedback_speaker=row[21]
        )
    
    def _row_to_notification(self, row) -> Notification:
        """Convert database row to Notification object."""
        return Notification(
            id=row[0],
            recipient_id=row[1],
            recipient_type=row[2],
            notification_type=NotificationType(row[3]),
            title=row[4],
            message=row[5],
            booking_id=row[6],
            is_read=bool(row[7]),
            is_sent=bool(row[8]),
            send_at=datetime.fromisoformat(row[9]),
            sent_at=datetime.fromisoformat(row[10]) if row[10] else None,
            created_at=datetime.fromisoformat(row[11])
        )