"""Mock Detector for testing."""

from clashroyalebuildabot.namespaces import State, Screens
from clashroyalebuildabot.namespaces.cards import Card


class Detector:
    """Mock Detector."""

    def __init__(self, cards):
        self.cards = cards
        self.card_detector = None
        self.number_detector = None
        self.unit_detector = None
        self.screen_detector = None

    def run(self, image) -> State | None:
        """Mock detection."""
        return State(
            allies=[],
            enemies=[],
            numbers=None,
            cards=[],
            ready=[],
            screen=Screens.IN_GAME,
        )

    def close(self):
        """Mock close."""
        pass