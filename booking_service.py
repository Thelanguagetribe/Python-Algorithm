import uuid
import stripe
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from booking_models import (
    Booking, Payment, TimeSlot, Notification, BookingSettings,
    BookingStatus, PaymentStatus, LessonType, NotificationType
)
from booking_database import BookingDatabase
from database import LanguageTribeDatabase

# Set your Stripe secret key (in production, use environment variables)
stripe.api_key = "sk_test_your_stripe_secret_key_here"

class BookingService:
    def __init__(self, booking_db: BookingDatabase, main_db: LanguageTribeDatabase):
        self.booking_db = booking_db
        self.main_db = main_db
    
    def create_booking(self, learner_id: int, speaker_id: int, 
                      lesson_date: datetime, duration_minutes: int,
                      lesson_type: LessonType, booking_notes: Optional[str] = None,
                      lesson_topic: Optional[str] = None) -> Dict[str, Any]:
        """Create a new lesson booking."""
        
        # Get speaker details for pricing
        speaker = self.main_db.get_native_speaker(speaker_id)
        if not speaker:
            return {"success": False, "error": "Speaker not found"}
        
        # Check if speaker is available at the requested time
        available_slots = self.booking_db.get_available_slots(
            speaker_id, lesson_date, lesson_date + timedelta(minutes=duration_minutes)
        )
        
        if not available_slots:
            return {"success": False, "error": "Speaker not available at requested time"}
        
        # Calculate total amount
        total_amount = speaker.hourly_rate * (duration_minutes / 60)
        
        # Create booking
        booking = Booking(
            id=str(uuid.uuid4()),
            learner_id=learner_id,
            speaker_id=speaker_id,
            lesson_date=lesson_date,
            duration_minutes=duration_minutes,
            lesson_type=lesson_type,
            status=BookingStatus.PENDING,
            total_amount=total_amount,
            currency="GBP",
            payment_status=PaymentStatus.PENDING,
            booking_notes=booking_notes,
            lesson_topic=lesson_topic,
            meeting_link=None,
            meeting_location=None,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Save booking to database
        booking_id = self.booking_db.create_booking(booking)
        
        # Create confirmation notification for learner
        self._create_booking_notification(
            booking_id, learner_id, "learner", 
            NotificationType.BOOKING_CONFIRMATION
        )
        
        # Create notification for speaker
        self._create_booking_notification(
            booking_id, speaker_id, "speaker",
            NotificationType.BOOKING_CONFIRMATION
        )
        
        return {
            "success": True, 
            "booking_id": booking_id,
            "total_amount": total_amount,
            "currency": "GBP"
        }
    
    def process_payment(self, booking_id: str, payment_method_id: str) -> Dict[str, Any]:
        """Process payment for a booking using Stripe."""
        
        booking = self.booking_db.get_booking(booking_id)
        if not booking:
            return {"success": False, "error": "Booking not found"}
        
        if booking.payment_status == PaymentStatus.PAID:
            return {"success": False, "error": "Booking already paid"}
        
        try:
            # Create Stripe payment intent
            intent = stripe.PaymentIntent.create(
                amount=int(booking.total_amount * 100),  # Stripe uses cents
                currency=booking.currency.lower(),
                payment_method=payment_method_id,
                confirmation_method='manual',
                confirm=True,
                metadata={
                    'booking_id': booking_id,
                    'learner_id': str(booking.learner_id),
                    'speaker_id': str(booking.speaker_id)
                }
            )
            
            if intent.status == 'succeeded':
                # Calculate fees (Stripe typically charges 2.9% + 30p)
                transaction_fee = (booking.total_amount * 0.029) + 0.30
                net_amount = booking.total_amount - transaction_fee
                
                # Create payment record
                payment = Payment(
                    id=str(uuid.uuid4()),
                    booking_id=booking_id,
                    amount=booking.total_amount,
                    currency=booking.currency,
                    payment_method="stripe",
                    payment_intent_id=intent.id,
                    status=PaymentStatus.PAID,
                    transaction_fee=transaction_fee,
                    net_amount=net_amount,
                    processed_at=datetime.now(),
                    created_at=datetime.now()
                )
                
                self.booking_db.create_payment(payment)
                
                # Update booking status
                self.booking_db.update_booking_status(booking_id, BookingStatus.CONFIRMED)
                
                # Generate meeting link for online lessons
                if booking.lesson_type in [LessonType.SINGLE, LessonType.TRIAL]:
                    meeting_link = self._generate_meeting_link(booking_id)
                    # Update booking with meeting link (you'd implement this method)
                
                # Send payment confirmation notifications
                self._create_payment_notification(booking_id, booking.learner_id, "learner")
                self._create_payment_notification(booking_id, booking.speaker_id, "speaker")
                
                # Schedule lesson reminder (24 hours before)
                reminder_time = booking.lesson_date - timedelta(hours=24)
                if reminder_time > datetime.now():
                    self._create_lesson_reminder(booking_id, reminder_time)
                
                return {
                    "success": True,
                    "payment_id": payment.id,
                    "booking_status": BookingStatus.CONFIRMED.value
                }
            
            else:
                return {"success": False, "error": f"Payment failed: {intent.status}"}
                
        except stripe.error.StripeError as e:
            return {"success": False, "error": f"Payment error: {str(e)}"}
    
    def cancel_booking(self, booking_id: str, cancelled_by: str, 
                      reason: Optional[str] = None) -> Dict[str, Any]:
        """Cancel a booking and handle refunds if applicable."""
        
        booking = self.booking_db.get_booking(booking_id)
        if not booking:
            return {"success": False, "error": "Booking not found"}
        
        if booking.status == BookingStatus.CANCELLED:
            return {"success": False, "error": "Booking already cancelled"}
        
        # Check cancellation policy
        hours_until_lesson = (booking.lesson_date - datetime.now()).total_seconds() / 3600
        
        # Get speaker's cancellation policy (default 24 hours)
        cancellation_policy_hours = 24  # You could get this from booking_settings
        
        refund_amount = 0
        if booking.payment_status == PaymentStatus.PAID:
            if hours_until_lesson >= cancellation_policy_hours:
                # Full refund
                refund_amount = booking.total_amount
            elif hours_until_lesson >= 6:
                # Partial refund (50%)
                refund_amount = booking.total_amount * 0.5
            # else: No refund for cancellations less than 6 hours before
        
        # Process refund if applicable
        if refund_amount > 0:
            refund_result = self._process_refund(booking_id, refund_amount, reason)
            if not refund_result["success"]:
                return refund_result
        
        # Update booking status
        self.booking_db.update_booking_status(
            booking_id, BookingStatus.CANCELLED, reason
        )
        
        # Send cancellation notifications
        self._create_cancellation_notification(booking_id, booking.learner_id, "learner")
        self._create_cancellation_notification(booking_id, booking.speaker_id, "speaker")
        
        return {
            "success": True,
            "refund_amount": refund_amount,
            "cancellation_policy_applied": hours_until_lesson < cancellation_policy_hours
        }
    
    def get_available_slots(self, speaker_id: int, date_from: datetime, 
                           date_to: datetime) -> List[Dict[str, Any]]:
        """Get available time slots for booking."""
        
        slots = self.booking_db.get_available_slots(speaker_id, date_from, date_to)
        
        return [{
            "start_time": slot.start_time.isoformat(),
            "end_time": slot.end_time.isoformat(),
            "is_available": slot.is_available
        } for slot in slots]
    
    def get_learner_bookings(self, learner_id: int) -> List[Dict[str, Any]]:
        """Get all bookings for a learner."""
        
        bookings = self.booking_db.get_bookings_by_learner(learner_id)
        result = []
        
        for booking in bookings:
            speaker = self.main_db.get_native_speaker(booking.speaker_id)
            result.append({
                "booking_id": booking.id,
                "speaker_name": speaker.name if speaker else "Unknown",
                "lesson_date": booking.lesson_date.isoformat(),
                "duration_minutes": booking.duration_minutes,
                "status": booking.status.value,
                "payment_status": booking.payment_status.value,
                "total_amount": booking.total_amount,
                "currency": booking.currency,
                "lesson_topic": booking.lesson_topic,
                "meeting_link": booking.meeting_link,
                "can_cancel": self._can_cancel_booking(booking),
                "can_reschedule": self._can_reschedule_booking(booking)
            })
        
        return result
    
    def get_speaker_bookings(self, speaker_id: int) -> List[Dict[str, Any]]:
        """Get all bookings for a speaker."""
        
        bookings = self.booking_db.get_bookings_by_speaker(speaker_id)
        result = []
        
        for booking in bookings:
            learner = self.main_db.get_language_learner(booking.learner_id)
            result.append({
                "booking_id": booking.id,
                "learner_name": learner.name if learner else "Unknown",
                "lesson_date": booking.lesson_date.isoformat(),
                "duration_minutes": booking.duration_minutes,
                "status": booking.status.value,
                "payment_status": booking.payment_status.value,
                "total_amount": booking.total_amount,
                "currency": booking.currency,
                "lesson_topic": booking.lesson_topic,
                "booking_notes": booking.booking_notes,
                "learner_level": learner.experience_level if learner else None
            })
        
        return result
    
    def complete_lesson(self, booking_id: str) -> Dict[str, Any]:
        """Mark a lesson as completed and trigger rating requests."""
        
        booking = self.booking_db.get_booking(booking_id)
        if not booking:
            return {"success": False, "error": "Booking not found"}
        
        # Update booking status
        self.booking_db.update_booking_status(booking_id, BookingStatus.COMPLETED)
        
        # Send rating request notifications (after 1 hour)
        rating_time = datetime.now() + timedelta(hours=1)
        self._create_rating_request(booking_id, booking.learner_id, "learner", rating_time)
        self._create_rating_request(booking_id, booking.speaker_id, "speaker", rating_time)
        
        return {"success": True}
    
    def _create_booking_notification(self, booking_id: str, recipient_id: int, 
                                   recipient_type: str, notification_type: NotificationType):
        """Create a booking-related notification."""
        
        booking = self.booking_db.get_booking(booking_id)
        if not booking:
            return
        
        if recipient_type == "learner":
            speaker = self.main_db.get_native_speaker(booking.speaker_id)
            title = f"Booking Confirmation with {speaker.name if speaker else 'Teacher'}"
            message = f"Your lesson on {booking.lesson_date.strftime('%B %d, %Y at %H:%M')} has been created. Payment required to confirm."
        else:
            learner = self.main_db.get_language_learner(booking.learner_id)
            title = f"New Booking Request from {learner.name if learner else 'Student'}"
            message = f"You have a new lesson request for {booking.lesson_date.strftime('%B %d, %Y at %H:%M')}."
        
        notification = Notification(
            id=str(uuid.uuid4()),
            recipient_id=recipient_id,
            recipient_type=recipient_type,
            notification_type=notification_type,
            title=title,
            message=message,
            booking_id=booking_id,
            send_at=datetime.now(),
            created_at=datetime.now()
        )
        
        self.booking_db.create_notification(notification)
    
    def _create_payment_notification(self, booking_id: str, recipient_id: int, recipient_type: str):
        """Create payment confirmation notification."""
        
        notification = Notification(
            id=str(uuid.uuid4()),
            recipient_id=recipient_id,
            recipient_type=recipient_type,
            notification_type=NotificationType.PAYMENT_CONFIRMATION,
            title="Payment Confirmed",
            message="Your lesson payment has been processed successfully.",
            booking_id=booking_id,
            send_at=datetime.now(),
            created_at=datetime.now()
        )
        
        self.booking_db.create_notification(notification)
    
    def _create_lesson_reminder(self, booking_id: str, reminder_time: datetime):
        """Create lesson reminder notifications."""
        
        booking = self.booking_db.get_booking(booking_id)
        if not booking:
            return
        
        # Reminder for learner
        learner_notification = Notification(
            id=str(uuid.uuid4()),
            recipient_id=booking.learner_id,
            recipient_type="learner",
            notification_type=NotificationType.LESSON_REMINDER,
            title="Lesson Reminder",
            message=f"Your lesson is tomorrow at {booking.lesson_date.strftime('%H:%M')}",
            booking_id=booking_id,
            send_at=reminder_time,
            created_at=datetime.now()
        )
        
        # Reminder for speaker
        speaker_notification = Notification(
            id=str(uuid.uuid4()),
            recipient_id=booking.speaker_id,
            recipient_type="speaker",
            notification_type=NotificationType.LESSON_REMINDER,
            title="Lesson Reminder",
            message=f"You have a lesson tomorrow at {booking.lesson_date.strftime('%H:%M')}",
            booking_id=booking_id,
            send_at=reminder_time,
            created_at=datetime.now()
        )
        
        self.booking_db.create_notification(learner_notification)
        self.booking_db.create_notification(speaker_notification)
    
    def _create_rating_request(self, booking_id: str, recipient_id: int, 
                             recipient_type: str, send_time: datetime):
        """Create rating request notification."""
        
        notification = Notification(
            id=str(uuid.uuid4()),
            recipient_id=recipient_id,
            recipient_type=recipient_type,
            notification_type=NotificationType.RATING_REQUEST,
            title="Rate Your Lesson",
            message="How was your lesson? Please rate your experience.",
            booking_id=booking_id,
            send_at=send_time,
            created_at=datetime.now()
        )
        
        self.booking_db.create_notification(notification)
    
    def _create_cancellation_notification(self, booking_id: str, recipient_id: int, recipient_type: str):
        """Create cancellation notification."""
        
        notification = Notification(
            id=str(uuid.uuid4()),
            recipient_id=recipient_id,
            recipient_type=recipient_type,
            notification_type=NotificationType.LESSON_CANCELLED,
            title="Lesson Cancelled",
            message="Your lesson has been cancelled. Any applicable refunds will be processed.",
            booking_id=booking_id,
            send_at=datetime.now(),
            created_at=datetime.now()
        )
        
        self.booking_db.create_notification(notification)
    
    def _process_refund(self, booking_id: str, refund_amount: float, 
                       reason: Optional[str] = None) -> Dict[str, Any]:
        """Process a refund through Stripe."""
        
        # This is a simplified version - in production you'd need to:
        # 1. Get the original payment intent ID
        # 2. Create a refund through Stripe
        # 3. Update the payment record
        
        return {"success": True, "refund_id": str(uuid.uuid4())}
    
    def _generate_meeting_link(self, booking_id: str) -> str:
        """Generate a meeting link for online lessons."""
        
        # This would integrate with Zoom, Google Meet, or your preferred platform
        # For now, return a placeholder
        return f"https://meet.languagetribe.com/room/{booking_id}"
    
    def _can_cancel_booking(self, booking: Booking) -> bool:
        """Check if a booking can be cancelled."""
        
        if booking.status in [BookingStatus.CANCELLED, BookingStatus.COMPLETED]:
            return False
        
        # Allow cancellation up to 1 hour before lesson
        hours_until_lesson = (booking.lesson_date - datetime.now()).total_seconds() / 3600
        return hours_until_lesson >= 1
    
    def _can_reschedule_booking(self, booking: Booking) -> bool:
        """Check if a booking can be rescheduled."""
        
        if booking.status in [BookingStatus.CANCELLED, BookingStatus.COMPLETED]:
            return False
        
        # Allow rescheduling up to 6 hours before lesson
        hours_until_lesson = (booking.lesson_date - datetime.now()).total_seconds() / 3600
        return hours_until_lesson >= 6