import math
from typing import List, Dict, Tuple, Optional
from datetime import datetime, time
from models import (
    LanguageLearner, NativeSpeaker, Match, Location, 
    Availability, LessonType, DayOfWeek, TimeSlot
)

class LanguageMatchingAlgorithm:
    def __init__(self):
        self.weights = {
            'language_match': 0.30,      # 30% - Must match exact language
            'lesson_type': 0.20,         # 20% - In-person vs online preference
            'proximity': 0.20,           # 20% - Distance for in-person lessons
            'age_compatibility': 0.15,   # 15% - Age similarity
            'availability': 0.10,        # 10% - Schedule overlap
            'budget_compatibility': 0.05 # 5% - Price within budget
        }
        self.max_distance_km = 50  # Maximum distance for in-person lessons
        self.age_range_years = 10  # Preferred age range
    
    def find_matches(self, learner: LanguageLearner, speakers: List[NativeSpeaker], 
                    max_matches: int = 10) -> List[Match]:
        """
        Find the best matches for a language learner from available native speakers.
        
        Args:
            learner: The language learner seeking a teacher
            speakers: List of available native speakers
            max_matches: Maximum number of matches to return
            
        Returns:
            List of Match objects sorted by compatibility score (highest first)
        """
        potential_matches = []
        
        for speaker in speakers:
            # Skip inactive or unavailable speakers
            if not speaker.is_active or speaker.current_students >= speaker.max_students:
                continue
                
            # Calculate compatibility score
            score = self._calculate_compatibility_score(learner, speaker)
            
            # Only include matches above minimum threshold (60%)
            if score >= 0.6:
                match = self._create_match(learner, speaker, score)
                potential_matches.append(match)
        
        # Sort by compatibility score (descending)
        potential_matches.sort(key=lambda m: m.compatibility_score, reverse=True)
        
        return potential_matches[:max_matches]
    
    def _calculate_compatibility_score(self, learner: LanguageLearner, 
                                     speaker: NativeSpeaker) -> float:
        """Calculate overall compatibility score between learner and speaker."""
        
        # 1. Language Match Score (Must match)
        language_score = self._calculate_language_score(learner, speaker)
        if language_score == 0:  # No language match, skip this speaker
            return 0.0
        
        # 2. Lesson Type Compatibility
        lesson_type_score = self._calculate_lesson_type_score(learner, speaker)
        
        # 3. Proximity Score (for in-person lessons)
        proximity_score = self._calculate_proximity_score(learner, speaker)
        
        # 4. Age Compatibility
        age_score = self._calculate_age_score(learner, speaker)
        
        # 5. Availability Overlap
        availability_score = self._calculate_availability_score(learner, speaker)
        
        # 6. Budget Compatibility
        budget_score = self._calculate_budget_score(learner, speaker)
        
        # Calculate weighted total score
        total_score = (
            language_score * self.weights['language_match'] +
            lesson_type_score * self.weights['lesson_type'] +
            proximity_score * self.weights['proximity'] +
            age_score * self.weights['age_compatibility'] +
            availability_score * self.weights['availability'] +
            budget_score * self.weights['budget_compatibility']
        )
        
        return min(total_score, 1.0)  # Cap at 1.0
    
    def _calculate_language_score(self, learner: LanguageLearner, 
                                speaker: NativeSpeaker) -> float:
        """Check if speaker's native language matches learner's target language."""
        if speaker.native_language.lower() == learner.target_language.lower():
            return 1.0
        elif learner.target_language.lower() in [lang.lower() for lang in speaker.secondary_languages]:
            return 0.8  # Secondary language, still good but not perfect
        else:
            return 0.0  # No match
    
    def _calculate_lesson_type_score(self, learner: LanguageLearner, 
                                   speaker: NativeSpeaker) -> float:
        """Calculate compatibility based on lesson type preferences."""
        learner_pref = learner.lesson_type_preference
        speaker_offers = speaker.lesson_types_offered
        
        # Perfect match
        if learner_pref in speaker_offers:
            return 1.0
        
        # Both prefer "both" (flexible)
        if (learner_pref == LessonType.BOTH and 
            any(lt in [LessonType.IN_PERSON, LessonType.ONLINE] for lt in speaker_offers)):
            return 0.9
        
        # Speaker offers "both" but learner has specific preference
        if LessonType.BOTH in speaker_offers:
            return 0.8
        
        return 0.0  # No compatibility
    
    def _calculate_proximity_score(self, learner: LanguageLearner, 
                                 speaker: NativeSpeaker) -> float:
        """Calculate proximity score for in-person lessons."""
        # If both prefer online only, proximity doesn't matter
        if (learner.lesson_type_preference == LessonType.ONLINE and 
            speaker.lesson_types_offered == [LessonType.ONLINE]):
            return 1.0
        
        # If either wants in-person lessons, check proximity
        needs_proximity = (
            learner.lesson_type_preference in [LessonType.IN_PERSON, LessonType.BOTH] or
            LessonType.IN_PERSON in speaker.lesson_types_offered or
            LessonType.BOTH in speaker.lesson_types_offered
        )
        
        if not needs_proximity:
            return 1.0
        
        # Both need location for in-person lessons
        if not learner.location or not speaker.location:
            return 0.0
        
        distance_km = self._calculate_distance(learner.location, speaker.location)
        
        if distance_km <= 5:  # Very close
            return 1.0
        elif distance_km <= 15:  # Close
            return 0.8
        elif distance_km <= 30:  # Moderate distance
            return 0.6
        elif distance_km <= self.max_distance_km:  # Maximum acceptable distance
            return 0.4
        else:  # Too far
            return 0.0
    
    def _calculate_distance(self, loc1: Location, loc2: Location) -> float:
        """Calculate distance between two locations using Haversine formula."""
        # Convert latitude and longitude from degrees to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [loc1.latitude, loc1.longitude, 
                                                   loc2.latitude, loc2.longitude])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Radius of earth in kilometers
        r = 6371
        
        return c * r
    
    def _calculate_age_score(self, learner: LanguageLearner, 
                           speaker: NativeSpeaker) -> float:
        """Calculate age compatibility score."""
        age_diff = abs(learner.age - speaker.age)
        
        if age_diff <= 5:  # Very similar age
            return 1.0
        elif age_diff <= self.age_range_years:  # Within preferred range
            return 0.8
        elif age_diff <= 15:  # Moderate age difference
            return 0.6
        elif age_diff <= 25:  # Large age difference but acceptable
            return 0.4
        else:  # Too large age difference
            return 0.2
    
    def _calculate_availability_score(self, learner: LanguageLearner, 
                                    speaker: NativeSpeaker) -> float:
        """Calculate availability overlap score."""
        learner_slots = self._get_time_slots(learner.availability)
        speaker_slots = self._get_time_slots(speaker.availability)
        
        # Find overlapping time slots
        overlap = learner_slots.intersection(speaker_slots)
        total_learner_slots = len(learner_slots)
        
        if total_learner_slots == 0:
            return 0.0
        
        overlap_ratio = len(overlap) / total_learner_slots
        return overlap_ratio
    
    def _get_time_slots(self, availability: List[Availability]) -> set:
        """Convert availability to a set of time slots for easy comparison."""
        slots = set()
        for avail in availability:
            slot_key = f"{avail.day.value}_{avail.time_slot.value}"
            slots.add(slot_key)
        return slots
    
    def _calculate_budget_score(self, learner: LanguageLearner, 
                              speaker: NativeSpeaker) -> float:
        """Calculate budget compatibility score."""
        if speaker.hourly_rate <= learner.budget_per_hour:
            # Calculate how much of budget is used (lower is better for learner)
            usage_ratio = speaker.hourly_rate / learner.budget_per_hour
            return 1.0 - (usage_ratio - 0.5) * 0.4  # Prefer rates around 50-70% of budget
        else:
            # Rate exceeds budget
            excess_ratio = speaker.hourly_rate / learner.budget_per_hour
            if excess_ratio <= 1.2:  # Up to 20% over budget might be acceptable
                return 0.3
            else:
                return 0.0
    
    def _create_match(self, learner: LanguageLearner, speaker: NativeSpeaker, 
                     score: float) -> Match:
        """Create a Match object with calculated details."""
        # Calculate distance if both have locations
        distance_km = None
        if learner.location and speaker.location:
            distance_km = self._calculate_distance(learner.location, speaker.location)
        
        # Find availability overlap
        availability_overlap = self._find_availability_overlap(learner, speaker)
        
        # Determine lesson type for this match
        lesson_type = self._determine_lesson_type(learner, speaker)
        
        return Match(
            learner_id=learner.id,
            speaker_id=speaker.id,
            compatibility_score=score,
            language=learner.target_language,
            lesson_type=lesson_type,
            distance_km=distance_km,
            age_difference=abs(learner.age - speaker.age),
            availability_overlap=availability_overlap,
            created_at=datetime.now(),
            is_confirmed=False
        )
    
    def _find_availability_overlap(self, learner: LanguageLearner, 
                                 speaker: NativeSpeaker) -> List[Availability]:
        """Find overlapping availability between learner and speaker."""
        learner_slots = {f"{a.day.value}_{a.time_slot.value}": a for a in learner.availability}
        speaker_slots = {f"{a.day.value}_{a.time_slot.value}": a for a in speaker.availability}
        
        overlap = []
        for slot_key in learner_slots:
            if slot_key in speaker_slots:
                overlap.append(learner_slots[slot_key])
        
        return overlap
    
    def _determine_lesson_type(self, learner: LanguageLearner, 
                             speaker: NativeSpeaker) -> LessonType:
        """Determine the lesson type for this specific match."""
        learner_pref = learner.lesson_type_preference
        speaker_offers = speaker.lesson_types_offered
        
        # If learner has specific preference and speaker offers it
        if learner_pref in speaker_offers:
            return learner_pref
        
        # If both are flexible, prefer in-person if close enough
        if (learner_pref == LessonType.BOTH and LessonType.BOTH in speaker_offers):
            if (learner.location and speaker.location and 
                self._calculate_distance(learner.location, speaker.location) <= 15):
                return LessonType.IN_PERSON
            else:
                return LessonType.ONLINE
        
        # Otherwise, find common lesson type
        if LessonType.ONLINE in speaker_offers:
            return LessonType.ONLINE
        elif LessonType.IN_PERSON in speaker_offers:
            return LessonType.IN_PERSON
        else:
            return speaker_offers[0]  # Default to first offered type