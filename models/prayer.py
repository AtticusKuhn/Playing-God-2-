from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Message:
    timestamp: datetime
    type: str
    content: Optional[str] = None
    urgency: Optional[float] = None
# @dataclass
class Prayer:
    """Represents a prayer made by a person"""
    outgoing_prayer: Message
    gods_reply: Optional[Message] = None

    def __init__(self, content, urgency):
        self.outgoing_prayer = Message(content=content, timestamp=datetime.now(), urgency=urgency, type="Prayer")
    @property
    def age(self) -> float:
        """Returns the age of the prayer in seconds"""
        return (datetime.now() - self.outgoing_message.timestamp).total_seconds()
    
    @property
    def was_answered(self) -> bool:
        """Returns True if the prayer has been answered"""
        return bool(self.gods_reply)
    
    @property
    def content(self) -> str:
        return self.outgoing_prayer.content
    
    @property
    def timestamp(self) -> datetime:
        return self.outgoing_prayer.timestamp
    
    @property
    def urgency(self) -> float:
        return self.outgoing_prayer.urgency
    
    def answer(self, response_type: str, response: Optional[str] = None) -> None:
        """Answer the prayer with a response"""
        self.gods_reply = Message(content=response, timestamp=datetime.now(), type=response_type)