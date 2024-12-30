from dataclasses import dataclass, field
from typing import List, Optional, Tuple
from datetime import datetime, timedelta
from .prayer import Prayer
import random
from openai import OpenAI
import threading


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

    walking_speed: float = field(init=False)

    lock: threading.Lock = threading.Lock()  # Class-level (static) lock for API calls

    client = OpenAI()
    # Prompt GPT to identify relevant topics

    life_record: List[Tuple[str, str]] = field(
        default_factory=list
    )  # List of life events (time/date, description)

    first_person: bool = True  # TODO: Set to False (just for testing)

    def __post_init__(self):
        assert self.age >= 18, "Age must be 18 or older"
        self.walking_speed = 20 * (18 / self.age)

    def can_pray(self) -> bool:
        """Determine if enough time has passed for a new prayer"""
        if random.random() < 0.2 and self.last_prayer_time is None:
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

        prayer = Prayer(content=content, urgency=urgency)
        # if prayer.content != "Hey":
        #     self.prayers.append(prayer)
        self.prayers.append(prayer)
        self.last_prayer_time = prayer.timestamp
        return prayer

    def _generate_prayer_content(self) -> str:
        """Generate prayer content using GPT's API based on current state"""
        with PersonAttributes.lock:
            if PersonAttributes.first_person:
                return "Hey"
                # """Generate prayer content based on current state"""
                # if self.emotional_state < 0.3:
                #     return "Please help me in these difficult times."
                # elif self.life_satisfaction < 0.3:
                #     return "I seek your guidance to improve my life."
                # elif random.random() < self.faith:
                #     return "Thank you for your blessings."
                # else:
                #     return "Please watch over me and my loved ones."
            PersonAttributes.first_person = True
        prompt = (
            "Generate a prayer to God for a person with the following attributes:\n"
            f"Name: {self.name}\n"
            f"Age: {self.age}\n"
            f"Emotional state: {self.emotional_state}\n"
            f"Life satisfaction: {self.life_satisfaction}\n"
            f"Faith: {self.faith}\n"
        )
        print("Generating prayer content")
        print(prompt)
        response = PersonAttributes.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=40,
            n=1,
            stop=None,
            temperature=0.7,
        )
        print(response.choices)
        prayer_content = response.choices[0].message.content.strip()
        return prayer_content
