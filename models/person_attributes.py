from dataclasses import dataclass


@dataclass
class PersonAttributes:
    """Extensible container for person attributes"""

    # Basic attributes - more can be added later
    name: str = ""
    age: int = 0
    # Add more attributes here as needed
