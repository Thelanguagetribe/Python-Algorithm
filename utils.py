import math
from typing import List, Tuple
from datetime import time, timedelta
from models import Location, TimeSlot, DayOfWeek


def calculate_distance_km(loc1: Location, loc2: Location) -> float:
    """
    Calculate the great-circle distance between two points on Earth
    using the Haversine formula.
    
    Args:
        loc1: First location
        loc2: Second location
        
    Returns:
        Distance in kilometers
    """
    # Convert latitude and longitude from degrees to radians
    lat1, lon1 = math.radians(loc1.latitude), math.radians(loc1.longitude)
    lat2, lon2 = math.radians(loc2.latitude), math.radians(loc2.longitude)
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of Earth in kilometers
    R = 6371.0
    
    return R * c


def time_to_minutes(t: time) -> int:
    """Convert time object to minutes since midnight"""
    return t.hour * 60 + t.minute


def minutes_to_time(minutes: int) -> time:
    """Convert minutes since midnight to time object"""
    hours = minutes // 60
    mins = minutes % 60
    return time(hours, mins)


def calculate_time_overlap(slot1: TimeSlot, slot2: TimeSlot) -> float:
    """
    Calculate overlapping time in hours between two time slots on the same day.
    
    Args:
        slot1: First time slot
        slot2: Second time slot
        
    Returns:
        Overlap in hours (0 if different days or no overlap)
    """
    if slot1.day != slot2.day:
        return 0.0
    
    start1_min = time_to_minutes(slot1.start_time)
    end1_min = time_to_minutes(slot1.end_time)
    start2_min = time_to_minutes(slot2.start_time)
    end2_min = time_to_minutes(slot2.end_time)
    
    # Find overlap
    overlap_start = max(start1_min, start2_min)
    overlap_end = min(end1_min, end2_min)
    
    if overlap_start >= overlap_end:
        return 0.0
    
    overlap_minutes = overlap_end - overlap_start
    return overlap_minutes / 60.0  # Convert to hours


def calculate_total_time_overlap(availability1: List[TimeSlot], availability2: List[TimeSlot]) -> float:
    """
    Calculate total overlapping time in hours between two availability lists.
    
    Args:
        availability1: First person's availability
        availability2: Second person's availability
        
    Returns:
        Total overlap in hours
    """
    total_overlap = 0.0
    
    for slot1 in availability1:
        for slot2 in availability2:
            total_overlap += calculate_time_overlap(slot1, slot2)
    
    return total_overlap


def calculate_age_compatibility_score(age1: int, age2: int, max_age_difference: int = 10) -> float:
    """
    Calculate age compatibility score based on age difference.
    
    Args:
        age1: First person's age
        age2: Second person's age
        max_age_difference: Maximum acceptable age difference
        
    Returns:
        Compatibility score between 0.0 and 1.0
    """
    age_diff = abs(age1 - age2)
    
    if age_diff > max_age_difference:
        return 0.0
    
    # Linear decrease in score as age difference increases
    return 1.0 - (age_diff / max_age_difference)


def is_within_distance(learner_location: Location, speaker_location: Location, max_distance_km: float) -> bool:
    """
    Check if two locations are within the specified maximum distance.
    
    Args:
        learner_location: Learner's location
        speaker_location: Speaker's location
        max_distance_km: Maximum acceptable distance
        
    Returns:
        True if within distance, False otherwise
    """
    if not learner_location or not speaker_location:
        return False
    
    distance = calculate_distance_km(learner_location, speaker_location)
    return distance <= max_distance_km


def format_time_slot(slot: TimeSlot) -> str:
    """Format a time slot for display"""
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return f"{days[slot.day.value]} {slot.start_time.strftime('%H:%M')}-{slot.end_time.strftime('%H:%M')}"