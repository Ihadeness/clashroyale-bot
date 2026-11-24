"""Tests for benchmark module."""

import time
from unittest.mock import MagicMock

import pytest

from clashroyale_bot.benchmark.bench_detector import benchmark_detector
from clashroyale_bot.benchmark.bench_bot import benchmark_bot


def test_benchmark_detector_returns_fps_stats():
    """Test benchmark_detector returns FPS statistics."""
    # Create mock detector
    mock_detector = MagicMock()
    mock_detector.run.return_value = MagicMock()

    # Run benchmark with small number of frames
    result = benchmark_detector(mock_detector, n_frames=10, warmup=2)

    assert "p50" in result
    assert "p95" in result
    assert "p99" in result
    assert "mean_fps" in result

    # All values should be positive
    assert result["p50"] > 0
    assert result["p95"] > 0
    assert result["p99"] > 0
    assert result["mean_fps"] > 0

    # p50 <= p95 <= p99
    assert result["p50"] <= result["p95"] <= result["p99"]


def test_benchmark_detector_warmup():
    """Test that warmup frames are run but not counted."""
    mock_detector = MagicMock()
    mock_detector.run.return_value = MagicMock()

    # Run with warmup
    result = benchmark_detector(mock_detector, n_frames=5, warmup=3)

    # Should have been called 8 times (5 + 3)
    assert mock_detector.run.call_count == 8


def test_benchmark_bot_returns_latency_stats():
    """Test benchmark_bot returns step latency statistics."""
    # Create mock wrapper
    mock_wrapper = MagicMock()

    def mock_step(state):
        time.sleep(0.001)  # Simulate 1ms step
        return None

    mock_wrapper.step.side_effect = mock_step

    # Create mock state
    from clashroyalebuildabot.namespaces import State, Screens, Numbers, NumberDetection
    initial_state = State(
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

    result = benchmark_bot(mock_wrapper, n_steps=10, warmup=2)

    assert "step_latency_p50" in result
    assert "step_latency_p95" in result
    assert "step_latency_p99" in result
    assert "fps" in result

    # All values should be positive
    assert result["step_latency_p50"] > 0
    assert result["step_latency_p95"] > 0
    assert result["step_latency_p99"] > 0
    assert result["fps"] > 0


def test_benchmark_bot_warmup():
    """Test that warmup steps are run but not counted."""
    mock_wrapper = MagicMock()
    mock_wrapper.step.return_value = None

    from clashroyalebuildabot.namespaces import State, Screens, Numbers, NumberDetection
    initial_state = State(
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

    benchmark_bot(mock_wrapper, n_steps=5, warmup=3)

    # Should have been called 8 times (5 + 3)
    assert mock_wrapper.step.call_count == 8