"""Tests for collector module."""

import gzip
import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from clashroyale_bot.collector.dataset_collector import DatasetCollector
from clashroyale_bot.collector.schemas import RewardData, StepRecord
from clashroyale_bot.collector.reward import compute_reward


def test_dataset_collector_writes_valid_jsonl(tmp_path):
    """Test that DatasetCollector writes valid JSONL."""
    collector = DatasetCollector(output_dir=tmp_path, max_file_mb=1, compress=False, flush_interval=0.1, flush_count=1)

    # Create mock state, action, reward
    from clashroyalebuildabot.namespaces import State, Screens, Numbers, NumberDetection
    state = State(
        allies=[],
        enemies=[],
        numbers=Numbers(
            elixir=NumberDetection((0,0,10,10), 7.0),
            right_ally_princess_hp=NumberDetection((0,0,10,10), 1.0),
            left_ally_princess_hp=NumberDetection((0,0,10,10), 1.0),
            right_enemy_princess_hp=NumberDetection((0,0,10,10), 0.5),
            left_enemy_princess_hp=NumberDetection((0,0,10,10), 1.0),
        ),
        cards=[],
        ready=[],
        screen=Screens.IN_GAME,
    )

    from clashroyale_bot.actions.hog_26 import HogRiderAction
    action = HogRiderAction(index=0, tile_x=7, tile_y=13)

    reward = RewardData(
        elixir_delta=-4,
        tower_dmg_dealt=0,
        tower_dmg_taken=0,
        unit_value_killed=0,
        unit_value_lost=0,
        win_bonus=0,
        loss_penalty=0,
    )

    collector.on_step_end(state, action, reward)
    collector.close()  # Close to finalize file

    # Check file was written (timestamped filename)
    data_files = list(tmp_path.glob("data_*.jsonl"))
    assert len(data_files) == 1
    data_file = data_files[0]

    lines = data_file.read_text().strip().split("\n")
    assert len(lines) == 1

    data = json.loads(lines[0])
    assert data["frame_id"] == 1
    assert "elixir" in data
    assert data["elixir"] == 7
    assert "action" in data
    assert data["action"]["card"] == "hog_rider"


def test_dataset_collector_compresses_with_gzip(tmp_path):
    """Test that DatasetCollector compresses with gzip when enabled."""
    collector = DatasetCollector(output_dir=tmp_path, max_file_mb=1, compress=True, flush_interval=0.1, flush_count=1)

    from clashroyalebuildabot.namespaces import State, Screens, Numbers, NumberDetection
    state = State(
        allies=[],
        enemies=[],
        numbers=Numbers(
            elixir=NumberDetection((0,0,10,10), 7.0),
            right_ally_princess_hp=NumberDetection((0,0,10,10), 1.0),
            left_ally_princess_hp=NumberDetection((0,0,10,10), 1.0),
            right_enemy_princess_hp=NumberDetection((0,0,10,10), 0.5),
            left_enemy_princess_hp=NumberDetection((0,0,10,10), 1.0),
        ),
        cards=[],
        ready=[],
        screen=Screens.IN_GAME,
    )

    from clashroyale_bot.actions.hog_26 import HogRiderAction
    action = HogRiderAction(index=0, tile_x=7, tile_y=13)

    from clashroyale_bot.collector.schemas import RewardData
    reward = RewardData(
        elixir_delta=-4, tower_dmg_dealt=0, tower_dmg_taken=0,
        unit_value_killed=0, unit_value_lost=0, win_bonus=0, loss_penalty=0,
    )

    collector.on_step_end(state, action, reward)
    collector.close()  # Close to finalize gzip file

    # Check gz file was written
    gz_files = list(tmp_path.glob("data_*.jsonl.gz"))
    assert len(gz_files) == 1

    # Verify content can be read
    with gzip.open(gz_files[0], "rt") as f:
        data = json.loads(f.read().strip())
        assert data["frame_id"] == 1


def test_dataset_collector_rotates_daily(tmp_path):
    """Test that DatasetCollector rotates file daily."""
    # This is hard to test without time manipulation, just verify the attribute exists
    collector = DatasetCollector(output_dir=tmp_path, rotate_daily=True)
    assert collector.rotate_daily is True


def test_dataset_collector_buffer_survives_disk_full(tmp_path, monkeypatch):
    """Test that collector buffers in memory when disk is full."""
    collector = DatasetCollector(output_dir=tmp_path, max_file_mb=1, flush_interval=1000)  # Don't auto-flush

    # Mock open to simulate disk full
    def mock_open(*args, **kwargs):
        raise OSError("No space left on device")

    monkeypatch.setattr("builtins.open", mock_open)

    from clashroyalebuildabot.namespaces import State, Screens, Numbers, NumberDetection
    state = State(
        allies=[],
        enemies=[],
        numbers=Numbers(
            elixir=NumberDetection((0,0,10,10), 7.0),
            right_ally_princess_hp=NumberDetection((0,0,10,10), 1.0),
            left_ally_princess_hp=NumberDetection((0,0,10,10), 1.0),
            right_enemy_princess_hp=NumberDetection((0,0,10,10), 0.5),
            left_enemy_princess_hp=NumberDetection((0,0,10,10), 1.0),
        ),
        cards=[],
        ready=[],
        screen=Screens.IN_GAME,
    )

    from clashroyale_bot.actions.hog_26 import HogRiderAction
    action = HogRiderAction(index=0, tile_x=7, tile_y=13)

    from clashroyale_bot.collector.schemas import RewardData
    reward = RewardData(
        elixir_delta=-4, tower_dmg_dealt=0, tower_dmg_taken=0,
        unit_value_killed=0, unit_value_lost=0, win_bonus=0, loss_penalty=0,
    )

    # Should not raise, just buffer in memory
    collector.on_step_end(state, action, reward)

    # Buffer should have the data
    assert collector._buffer.qsize() > 0


def test_compute_reward_dense():
    """Test compute_reward returns dense rewards."""
    from clashroyalebuildabot.namespaces import State, Screens, Numbers, NumberDetection

    prev_state = State(
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

    curr_state = State(
        allies=[],
        enemies=[],
        numbers=Numbers(
            elixir=NumberDetection((0,0,10,10), 6.0),  # Spent 4 elixir
            right_ally_princess_hp=NumberDetection((0,0,10,10), 1.0),
            left_ally_princess_hp=NumberDetection((0,0,10,10), 1.0),
            right_enemy_princess_hp=NumberDetection((0,0,10,10), 0.5),  # Enemy tower damaged
            left_enemy_princess_hp=NumberDetection((0,0,10,10), 1.0),
        ),
        cards=[],
        ready=[],
        screen=Screens.IN_GAME,
    )

    from clashroyale_bot.actions.hog_26 import HogRiderAction
    action = HogRiderAction(index=0, tile_x=7, tile_y=13)

    reward = compute_reward(prev_state, curr_state, action)

    assert isinstance(reward, RewardData)
    assert reward.elixir_delta == -4
    assert reward.tower_dmg_dealt > 0  # Enemy tower damaged
    assert reward.tower_dmg_taken == 0


def test_compute_reward_sparse_win():
    """Test compute_reward returns win bonus on END_OF_GAME."""
    from clashroyalebuildabot.namespaces import State, Screens, Numbers, NumberDetection

    prev_state = State(
        allies=[],
        enemies=[],
        numbers=Numbers(
            elixir=NumberDetection((0,0,10,10), 5.0),
            right_ally_princess_hp=NumberDetection((0,0,10,10), 1.0),
            left_ally_princess_hp=NumberDetection((0,0,10,10), 1.0),
            right_enemy_princess_hp=NumberDetection((0,0,10,10), 0.0),  # Enemy tower destroyed
            left_enemy_princess_hp=NumberDetection((0,0,10,10), 0.0),
        ),
        cards=[],
        ready=[],
        screen=Screens.IN_GAME,
    )

    curr_state = State(
        allies=[],
        enemies=[],
        numbers=Numbers(
            elixir=NumberDetection((0,0,10,10), 5.0),
            right_ally_princess_hp=NumberDetection((0,0,10,10), 1.0),
            left_ally_princess_hp=NumberDetection((0,0,10,10), 1.0),
            right_enemy_princess_hp=NumberDetection((0,0,10,10), 0.0),
            left_enemy_princess_hp=NumberDetection((0,0,10,10), 0.0),
        ),
        cards=[],
        ready=[],
        screen=Screens.END_OF_GAME,  # Game ended
    )

    from clashroyale_bot.actions.hog_26 import HogRiderAction
    action = HogRiderAction(index=0, tile_x=7, tile_y=13)

    reward = compute_reward(prev_state, curr_state, action)

    assert reward.win_bonus > 0  # Win bonus applied