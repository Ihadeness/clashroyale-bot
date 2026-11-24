"""Mock Action base class for testing."""

from abc import ABC, abstractmethod
from clashroyalebuildabot.namespaces.cards import Card


class Action(ABC):
    """Base action class."""
    CARD: Card

    def __init__(self, index: int, tile_x: int, tile_y: int):
        self.index = index
        self.tile_x = tile_x
        self.tile_y = tile_y

    def __repr__(self):
        return f"{self.CARD.name} at ({self.tile_x}, {self.tile_y})"

    def can_execute(self, state):
        """Check if action can be executed."""
        return True

    @abstractmethod
    def calculate_score(self, state):
        pass

    def execute(self, state):
        """Execute the action."""
        pass