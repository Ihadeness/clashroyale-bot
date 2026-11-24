"""Tests for 2.6 Hog Cycle actions."""

import pytest
from clashroyale_bot.actions.hog_26 import (
    HogRiderAction, LogAction, IceSpiritAction, SkeletonsAction,
    IceGolemAction, CannonAction, MusketeerAction, FireballAction
)
from clashroyalebuildabot.namespaces import State, Screens, Unit, Units
from clashroyalebuildabot.namespaces.cards import Cards
from clashroyalebuildabot.namespaces import NumberDetection, Numbers, UnitDetection, Position


# Mock state for testing
def create_mock_state(
    elixir: int = 10,
    screen: str = Screens.IN_GAME,
    allies: list = None,
    enemies: list = None,
    hand: list = None
) -> State:
    """Create a mock state for testing actions."""
    # Default empty lists
    if allies is None:
        allies = []
    if enemies is None:
        enemies = []
    if hand is None:
        hand = [Cards.HOG_RIDER, Cards.LOG, Cards.ICE_SPIRIT, Cards.SKELETONS]

    # Create numbers
    numbers = Numbers(
        elixir=NumberDetection((0, 0, 10, 10), float(elixir)),
        right_ally_princess_hp=NumberDetection((0, 0, 10, 10), 1.0),
        left_ally_princess_hp=NumberDetection((0, 0, 10, 10), 1.0),
        right_enemy_princess_hp=NumberDetection((0, 0, 10, 10), 1.0),
        left_enemy_princess_hp=NumberDetection((0, 0, 10, 10), 1.0),
    )

    return State(
        allies=allies,
        enemies=enemies,
        numbers=numbers,
        cards=hand,
        ready=[0, 1, 2, 3],
        screen=screen,
    )


def create_unit_detection(unit: Unit, tile_x: int, tile_y: int, hp: float = 1.0):
    """Create a UnitDetection for testing."""
    return UnitDetection(
        unit=unit,
        position=Position((tile_x * 34, tile_y * 27, (tile_x + 1) * 34, (tile_y + 1) * 27), tile_x, tile_y),
        hp=hp,
    )


class TestActionScoreStructure:
    """Test that all actions return valid score structure."""

    def test_hog_rider_action_score_structure(self):
        action = HogRiderAction(index=0, tile_x=7, tile_y=13)
        state = create_mock_state()
        score = action.calculate_score(state)
        assert isinstance(score, list)
        assert all(isinstance(v, (int, float)) for v in score)
        assert len(score) >= 1

    def test_log_action_score_structure(self):
        action = LogAction(index=1, tile_x=8, tile_y=14)
        state = create_mock_state()
        score = action.calculate_score(state)
        assert isinstance(score, list)
        assert all(isinstance(v, (int, float)) for v in score)
        assert len(score) >= 1

    def test_ice_spirit_action_score_structure(self):
        action = IceSpiritAction(index=2, tile_x=8, tile_y=13)
        state = create_mock_state()
        score = action.calculate_score(state)
        assert isinstance(score, list)
        assert all(isinstance(v, (int, float)) for v in score)
        assert len(score) >= 1

    def test_skeletons_action_score_structure(self):
        action = SkeletonsAction(index=3, tile_x=8, tile_y=13)
        state = create_mock_state()
        score = action.calculate_score(state)
        assert isinstance(score, list)
        assert all(isinstance(v, (int, float)) for v in score)
        assert len(score) >= 1

    def test_ice_golem_action_score_structure(self):
        action = IceGolemAction(index=4, tile_x=8, tile_y=12)
        state = create_mock_state()
        score = action.calculate_score(state)
        assert isinstance(score, list)
        assert all(isinstance(v, (int, float)) for v in score)
        assert len(score) >= 1

    def test_cannon_action_score_structure(self):
        action = CannonAction(index=5, tile_x=8, tile_y=11)
        state = create_mock_state()
        score = action.calculate_score(state)
        assert isinstance(score, list)
        assert all(isinstance(v, (int, float)) for v in score)
        assert len(score) >= 1

    def test_musketeer_action_score_structure(self):
        action = MusketeerAction(index=6, tile_x=8, tile_y=10)
        state = create_mock_state()
        score = action.calculate_score(state)
        assert isinstance(score, list)
        assert all(isinstance(v, (int, float)) for v in score)
        assert len(score) >= 1

    def test_fireball_action_score_structure(self):
        action = FireballAction(index=7, tile_x=8, tile_y=14)
        state = create_mock_state()
        score = action.calculate_score(state)
        assert isinstance(score, list)
        assert all(isinstance(v, (int, float)) for v in score)
        assert len(score) >= 1


class TestActionCardAssociation:
    """Test that actions are associated with correct cards."""

    def test_hog_rider_card(self):
        action = HogRiderAction(index=0, tile_x=7, tile_y=13)
        assert action.CARD == Cards.HOG_RIDER

    def test_log_card(self):
        action = LogAction(index=1, tile_x=8, tile_y=14)
        assert action.CARD == Cards.LOG

    def test_ice_spirit_card(self):
        action = IceSpiritAction(index=2, tile_x=8, tile_y=13)
        assert action.CARD == Cards.ICE_SPIRIT

    def test_skeletons_card(self):
        action = SkeletonsAction(index=3, tile_x=8, tile_y=13)
        assert action.CARD == Cards.SKELETONS

    def test_ice_golem_card(self):
        action = IceGolemAction(index=4, tile_x=8, tile_y=12)
        assert action.CARD == Cards.ICE_GOLEM

    def test_cannon_card(self):
        action = CannonAction(index=5, tile_x=8, tile_y=11)
        assert action.CARD == Cards.CANNON

    def test_musketeer_card(self):
        action = MusketeerAction(index=6, tile_x=8, tile_y=10)
        assert action.CARD == Cards.MUSKETEER

    def test_fireball_card(self):
        action = FireballAction(index=7, tile_x=8, tile_y=14)
        assert action.CARD == Cards.FIREBALL