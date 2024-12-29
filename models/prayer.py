from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Prayer:
    """Represents a prayer made by a person"""

    content: str  # The actual prayer text
    timestamp: datetime  # When the prayer was made
    urgency: float  # How urgent the prayer is (0.0 to 1.0)
    answered: bool = False  # Whether the prayer has been answered
    answer_timestamp: Optional[datetime] = None  # When the prayer was answered
    answer_type: Optional[str] = (
        None  # How the prayer was answered (accepted/denied/delayed)
    )

    @property
    def age(self) -> float:
        """Returns the age of the prayer in seconds"""
        return (datetime.now() - self.timestamp).total_seconds()

    def answer(self, answer_type: str):
        """Mark the prayer as answered"""
        self.answered = True
        self.answer_timestamp = datetime.now()
        self.answer_type = answer_type
