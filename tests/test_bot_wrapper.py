"""Tests for bot_wrapper module."""

import pytest

from clashroyale_bot.core.bot_wrapper import BotWrapper
from clashroyale_bot.collector.schemas import RewardData
from clashroyalebuildabot.actions.generic.action import Action
from clashroyalebuildabot.namespaces.cards import Card


class MockCollector:
    """Mock collector for testing."""

    def __init__(self):
        self.called_with = None
        self.call_count = 0

    def on_step_end(self, state, action, reward):
        self.called_with = {"state": state, "action": action, "reward": reward}
        self.call_count += 1


class MockBenchmark:
    """Mock benchmark for testing."""

    def __init__(self):
        self.latencies = []

    def record_latency(self, latency_ms: float):
        self.latencies.append(latency_ms)


class MockAction(Action):
    """Mock action for testing."""

    CARD = Card("mock_card", False, 1, [], 1)

    def __init__(self, index: int = 0, tile_x: int = 0, tile_y: int = 0):
        super().__init__(index, tile_x, tile_y)

    def calculate_score(self, state):
        return [1.0, 2.0, 3.0]


def test_bot_wrapper_calls_collector_on_step():
    """Test that BotWrapper calls collector.on_step_end after each step."""
    collector = MockCollector()
    benchmark = MockBenchmark()

    # Mock config and actions
    config = {"bot": {}, "adb": {}}
    actions = [MockAction]

    # Create wrapper with real Bot (mock implementation)
    wrapper = BotWrapper(config, actions, collector=collector, benchmark=benchmark)

    # Create a mock state
    from clashroyalebuildabot.namespaces import State, Screens, Numbers, NumberDetection
    state = State(
        allies=[],
        enemies=[],
        numbers=Numbers(
            elixir=NumberDetection((0,0,10,10), 10.0),
            right_ally_princess_hp=NumberDetection((0,0,10,10), 1.0),
            left_ally_princess_hp=NumberDetection((0,0,10,10), 1.0),
            right_enemy_princess_hp=NumberDetection((0,0,10,10), 1.0),
            left_enemy_princess_hp=NumberDetection((0,0,10,10), 1.0),
        ),
        cards=[],
        ready=[],
        screen=Screens.IN_GAME,
    )

    # First step - no previous state, so no collector call
    wrapper.step(state)

    # Second step - should call collector
    state2 = State(
        allies=[],
        enemies=[],
        numbers=Numbers(
            elixir=NumberDetection((0,0,10,10), 6.0),
            right_ally_princess_hp=NumberDetection((0,0,10,10), 1.0),
            left_ally_princess_hp=NumberDetection((0,0,10,10), 1.0),
            right_enemy_princess_hp=NumberDetection((0,0,10,10), 0.5),
            left_enemy_princess_hp=NumberDetection((0,0,10,10), 1.0),
        ),
        cards=[],
        ready=[],
        screen=Screens.IN_GAME,
    )
    wrapper.step(state2)

    assert collector.called_with is not None
    assert "state" in collector.called_with
    assert "action" in collector.called_with
    assert "reward" in collector.called_with
    assert collector.call_count == 1


def test_bot_wrapper_validates_action_score():
    """Test that BotWrapper validates action score format."""
    collector = MockCollector()
    benchmark = MockBenchmark()
    config = {"bot": {}, "adb": {}}
    actions = [MockAction]

    wrapper = BotWrapper(config, actions, collector=collector, benchmark=benchmark)

    from clashroyalebuildabot.namespaces import State, Screens, Numbers, NumberDetection
    state = State(
        allies=[],
        enemies=[],
        numbers=Numbers(
            elixir=NumberDetection((0,0,10,10), 10.0),
            right_ally_princess_hp=NumberDetection((0,0,10,10), 1.0),
            left_ally_princess_hp=NumberDetection((0,0,10,10), 1.0),
            right_enemy_princess_hp=NumberDetection((0,0,10,10), 1.0),
            left_enemy_princess_hp=NumberDetection((0,0,10,10), 1.0),
        ),
        cards=[],
        ready=[],
        screen=Screens.IN_GAME,
    )

    # First step
    wrapper.step(state)

    # Second step - should call collector
    state2 = State(
        allies=[],
        enemies=[],
        numbers=Numbers(
            elixir=NumberDetection((0,0,10,10), 6.0),
            right_ally_princess_hp=NumberDetection((0,0,10,10), 1.0),
            left_ally_princess_hp=NumberDetection((0,0,10,10), 1.0),
            right_enemy_princess_hp=NumberDetection((0,0,10,10), 0.5),
            left_enemy_princess_hp=NumberDetection((0,0,10,10), 1.0),
        ),
        cards=[],
        ready=[],
        screen=Screens.IN_GAME,
    )
    wrapper.step(state2)

    # Should still call collector
    assert collector.called_with is not None
    reward = collector.called_with["reward"]
    assert isinstance(reward, RewardData)