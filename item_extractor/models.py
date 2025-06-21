from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Curse:
    description: str
    disadvantage: Optional[List[str]] = None

@dataclass
class ItemData:
    name: str
    type: str
    rarity: str
    attunement: bool
    curse: Optional[str]
    description: str
    image_path: Optional[str] = None

@dataclass
class Item:
    name: str
    description: str

@dataclass()
class BoundingBox:
    """
    Represents a rectangular region in an image.
    Coordinates: (left, upper, right, lower)
    """
    left: int
    upper: int
    right: int
    lower: int
    size: int = None 
    def __post_init__(self):
        if not self.size:
            self.size = (self.right -self.left) * (self.lower - self.upper)

    def __lt__(self, other):
        return self.size < other.size

    def __le__(self, other):
        return self.size <= other.size

    def __eq__(self, other):
        return self.size == other.size

    def __ne__(self, other):
        return self.size != other.size

    def __gt__(self, other):
        return self.size > other.size

    def __ge__(self, other):
        return self.size >= other.size