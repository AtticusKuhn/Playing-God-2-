from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime, timedelta
from .prayer import Prayer
import random


@dataclass
class PersonAttributes:
    """Extensible container for person attributes"""

    # Basic attributes
    name: str = ""
    age: int = 0
    
    # Spiritual attributes
    faith: float = 0.5  # 0.0 to 1.0, representing faith level
    last_prayer_time: Optional[datetime] = None
    prayers: List[Prayer] = field(default_factory=list)
    prayer_frequency: float = 0.3  # Average prayers per day
    
    # Mental attributes that affect prayer
    emotional_state: float = 0.5  # 0.0 (distressed) to 1.0 (joyful)
    life_satisfaction: float = 0.5  # 0.0 (unsatisfied) to 1.0 (satisfied)
    
    def can_pray(self) -> bool:
        """Determine if enough time has passed for a new prayer"""
        if self.last_prayer_time is None:
            return True
            
        # Base time between prayers (in hours) is influenced by prayer_frequency
        base_hours = 24 / self.prayer_frequency
        
        # Modify base time based on emotional state and faith
        # More frequent prayers when distressed or highly faithful
        modifier = 2.0 - (self.emotional_state + self.faith) / 2
        required_hours = base_hours * modifier
        
        time_since_last = datetime.now() - self.last_prayer_time
        return time_since_last > timedelta(hours=required_hours)
    
    def generate_prayer(self) -> Optional[Prayer]:
        """Generate a new prayer based on current attributes"""
        if not self.can_pray():
            return None
            
        # Prayer urgency increases with lower emotional state and life satisfaction
        urgency = 1.0 - (self.emotional_state + self.life_satisfaction) / 2
        
        # Simple prayer content generation (placeholder for more complex generation)
        content = self._generate_prayer_content()
        
        prayer = Prayer(
            content=content,
            timestamp=datetime.now(),
            urgency=urgency
        )
        
        self.prayers.append(prayer)
        self.last_prayer_time = prayer.timestamp
        return prayer
    
    def _generate_prayer_content(self) -> str:
        """Generate prayer content based on current state"""
        if self.emotional_state < 0.3:
            return "Please help me in these difficult times."
        elif self.life_satisfaction < 0.3:
            return "I seek your guidance to improve my life."
        elif random.random() < self.faith:
            return "Thank you for your blessings."
        else:
            return "Please watch over me and my loved ones."
