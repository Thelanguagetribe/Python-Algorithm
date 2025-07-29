from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from models import LanguageLearner, NativeSpeaker, Match, LessonType
from utils import (
    calculate_distance_km, 
    calculate_total_time_overlap, 
    calculate_age_compatibility_score,
    is_within_distance
)


@dataclass
class MatchingWeights:
    """Weights for different matching criteria"""
    language_match: float = 40.0  # Language compatibility is most important
    time_overlap: float = 25.0    # Time availability is crucial
    age_compatibility: float = 15.0  # Age similarity is moderately important
    location_proximity: float = 15.0  # Location matters for in-person lessons
    experience: float = 5.0       # Teacher experience adds value


class LanguageMatcher:
    """Main class for matching language learners with native speakers"""
    
    def __init__(self, weights: Optional[MatchingWeights] = None):
        self.weights = weights or MatchingWeights()
    
    def find_matches(self, 
                    learner: LanguageLearner, 
                    speakers: List[NativeSpeaker],
                    min_score: float = 0.5,
                    max_matches: int = 10) -> List[Match]:
        """
        Find compatible native speakers for a language learner.
        
        Args:
            learner: The language learner seeking a teacher
            speakers: List of available native speakers
            min_score: Minimum compatibility score (0.0 to 1.0)
            max_matches: Maximum number of matches to return
            
        Returns:
            List of matches sorted by compatibility score (highest first)
        """
        matches = []
        
        for speaker in speakers:
            if not speaker.is_available or not speaker.is_verified:
                continue
                
            match = self._evaluate_match(learner, speaker)
            
            if match.compatibility_score >= min_score:
                matches.append(match)
        
        # Sort by compatibility score (descending)
        matches.sort(key=lambda m: m.compatibility_score, reverse=True)
        
        return matches[:max_matches]
    
    def _evaluate_match(self, learner: LanguageLearner, speaker: NativeSpeaker) -> Match:
        """
        Evaluate compatibility between a learner and speaker.
        
        Args:
            learner: Language learner
            speaker: Native speaker
            
        Returns:
            Match object with compatibility score and details
        """
        # Initialize match components
        language_match = self._check_language_compatibility(learner, speaker)
        lesson_type_match = self._check_lesson_type_compatibility(learner, speaker)
        age_score = calculate_age_compatibility_score(learner.age, speaker.age)
        time_overlap = calculate_total_time_overlap(learner.availability, speaker.availability)
        
        # Location and distance
        distance_km = None
        location_score = 1.0  # Default for online lessons
        
        if learner.lesson_type_preference == LessonType.IN_PERSON:
            if learner.location and speaker.location:
                distance_km = calculate_distance_km(learner.location, speaker.location)
                if learner.max_distance_km:
                    # Score decreases linearly with distance
                    if distance_km <= learner.max_distance_km:
                        location_score = 1.0 - (distance_km / learner.max_distance_km) * 0.5
                    else:
                        location_score = 0.0
                else:
                    # No max distance specified, use reasonable default scoring
                    location_score = max(0.0, 1.0 - (distance_km / 50.0))  # 50km as reasonable distance
            else:
                location_score = 0.0  # Can't do in-person without locations
        
        # Experience score (normalized)
        experience_score = min(1.0, speaker.years_experience / 10.0)  # Max score at 10+ years
        
        # Time overlap score (normalized)
        time_score = min(1.0, time_overlap / 10.0)  # Max score at 10+ hours overlap
        
        # Calculate weighted total score
        total_score = 0.0
        max_possible = 0.0
        reasons = []
        
        # Language compatibility (binary - must match)
        if language_match:
            total_score += self.weights.language_match
            reasons.append(f"Teaches {learner.target_language}")
        else:
            reasons.append(f"Does not teach {learner.target_language}")
        max_possible += self.weights.language_match
        
        # Lesson type compatibility (binary - must match)
        if lesson_type_match:
            reasons.append(f"Offers {learner.lesson_type_preference.value} lessons")
        else:
            reasons.append(f"Does not offer {learner.lesson_type_preference.value} lessons")
        
        # Only include other factors if basic requirements are met
        if language_match and lesson_type_match:
            # Time availability
            total_score += self.weights.time_overlap * time_score
            max_possible += self.weights.time_overlap
            reasons.append(f"{time_overlap:.1f} hours of overlapping availability")
            
            # Age compatibility
            total_score += self.weights.age_compatibility * age_score
            max_possible += self.weights.age_compatibility
            age_diff = abs(learner.age - speaker.age)
            reasons.append(f"Age difference: {age_diff} years")
            
            # Location proximity (for in-person lessons)
            if learner.lesson_type_preference == LessonType.IN_PERSON:
                total_score += self.weights.location_proximity * location_score
                max_possible += self.weights.location_proximity
                if distance_km is not None:
                    reasons.append(f"Distance: {distance_km:.1f} km")
            else:
                # For online lessons, location doesn't matter - give full score
                total_score += self.weights.location_proximity
                max_possible += self.weights.location_proximity
                reasons.append("Online lesson - location not relevant")
            
            # Experience
            total_score += self.weights.experience * experience_score
            max_possible += self.weights.experience
            reasons.append(f"{speaker.years_experience} years teaching experience")
        
        # Normalize score to 0-1 range
        compatibility_score = total_score / max_possible if max_possible > 0 else 0.0
        
        return Match(
            learner=learner,
            speaker=speaker,
            compatibility_score=compatibility_score,
            language_match=language_match,
            lesson_type_match=lesson_type_match,
            age_compatibility=age_score,
            location_distance_km=distance_km,
            time_overlap_hours=time_overlap,
            reasons=reasons
        )
    
    def _check_language_compatibility(self, learner: LanguageLearner, speaker: NativeSpeaker) -> bool:
        """Check if speaker can teach the language learner wants to learn"""
        return learner.target_language.lower() in [lang.lower() for lang in speaker.teaching_languages]
    
    def _check_lesson_type_compatibility(self, learner: LanguageLearner, speaker: NativeSpeaker) -> bool:
        """Check if speaker offers the type of lesson learner wants"""
        if learner.lesson_type_preference == LessonType.BOTH:
            return True
        
        return (learner.lesson_type_preference in speaker.lesson_types_offered or 
                LessonType.BOTH in speaker.lesson_types_offered)


class DatabaseConnector:
    """
    Mock database connector - replace with actual database implementation
    In a real application, this would connect to your database (PostgreSQL, MySQL, etc.)
    """
    
    def __init__(self):
        self.learners: List[LanguageLearner] = []
        self.speakers: List[NativeSpeaker] = []
    
    def add_learner(self, learner: LanguageLearner):
        """Add a language learner to the database"""
        self.learners.append(learner)
    
    def add_speaker(self, speaker: NativeSpeaker):
        """Add a native speaker to the database"""
        self.speakers.append(speaker)
    
    def get_active_learners(self) -> List[LanguageLearner]:
        """Get all active language learners"""
        return [l for l in self.learners if l.is_active]
    
    def get_available_speakers(self, language: Optional[str] = None) -> List[NativeSpeaker]:
        """Get all available native speakers, optionally filtered by language"""
        speakers = [s for s in self.speakers if s.is_available and s.is_verified]
        
        if language:
            speakers = [s for s in speakers if language.lower() in [lang.lower() for lang in s.teaching_languages]]
        
        return speakers
    
    def get_learner_by_id(self, learner_id: str) -> Optional[LanguageLearner]:
        """Get a learner by their ID"""
        for learner in self.learners:
            if learner.id == learner_id:
                return learner
        return None
    
    def get_speaker_by_id(self, speaker_id: str) -> Optional[NativeSpeaker]:
        """Get a speaker by their ID"""
        for speaker in self.speakers:
            if speaker.id == speaker_id:
                return speaker
        return None


class LanguageTribeMatchingService:
    """
    Main service class that orchestrates the matching process
    """
    
    def __init__(self, database: DatabaseConnector, matcher: Optional[LanguageMatcher] = None):
        self.db = database
        self.matcher = matcher or LanguageMatcher()
    
    def find_matches_for_learner(self, learner_id: str, **kwargs) -> List[Match]:
        """Find matches for a specific learner"""
        learner = self.db.get_learner_by_id(learner_id)
        if not learner:
            raise ValueError(f"Learner with ID {learner_id} not found")
        
        speakers = self.db.get_available_speakers(learner.target_language)
        return self.matcher.find_matches(learner, speakers, **kwargs)
    
    def get_match_summary(self, match: Match) -> Dict[str, Any]:
        """Get a summary of a match for API responses"""
        return {
            "speaker_id": match.speaker.id,
            "speaker_name": match.speaker.name,
            "compatibility_score": round(match.compatibility_score, 3),
            "hourly_rate": match.speaker.hourly_rate,
            "years_experience": match.speaker.years_experience,
            "distance_km": round(match.location_distance_km, 2) if match.location_distance_km else None,
            "time_overlap_hours": round(match.time_overlap_hours, 1),
            "age_difference": abs(match.learner.age - match.speaker.age),
            "reasons": match.reasons
        }