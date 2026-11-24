"""Tests for validate_dataset module."""

import gzip
import json
from pathlib import Path

import pytest

from clashroyale_bot.collector.validate_dataset import validate_dataset


def test_validate_dataset_detects_class_imbalance(tmp_path):
    """Test that validate_dataset detects class imbalance (e.g., 90% no-action)."""
    # Create a skewed dataset with 90% no-action frames
    data_file = tmp_path / "data.jsonl.gz"

    frames = []
    for i in range(100):
        if i < 90:
            # No action (most frames)
            action = None
        else:
            # Some actions
            action = {
                "card": "hog_rider",
                "tile_x": 7,
                "tile_y": 13,
                "score": [1.0, 2.0]
            }

        frame = {
            "timestamp": "2026-01-01T00:00:00Z",
            "frame_id": i + 1,
            "screen": "IN_GAME",
            "elixir": 10,
            "ally_princess_hp": [1.0, 1.0],
            "enemy_princess_hp": [1.0, 1.0],
            "allies": [],
            "enemies": [],
            "hand": [],
            "action": action,
            "reward": {
                "elixir_delta": 0.0,
                "tower_dmg_dealt": 0.0,
                "tower_dmg_taken": 0.0,
                "unit_value_killed": 0.0,
                "unit_value_lost": 0.0,
                "win_bonus": 0.0,
                "loss_penalty": 0.0,
            }
        }
        frames.append(frame)

    with gzip.open(data_file, "wt") as f:
        for frame in frames:
            f.write(json.dumps(frame) + "\n")

    report = validate_dataset(data_file)

    # Should detect high no-action ratio
    assert report["class_balance"]["no_action"] > 0.8
    assert len(report["warnings"]) > 0


def test_validate_dataset_computes_stats(tmp_path):
    """Test that validate_dataset computes basic statistics."""
    data_file = tmp_path / "data.jsonl.gz"

    frames = []
    for i in range(10):
        frame = {
            "timestamp": "2026-01-01T00:00:00Z",
            "frame_id": i + 1,
            "screen": "IN_GAME",
            "elixir": 10 - i,
            "ally_princess_hp": [1.0, 1.0],
            "enemy_princess_hp": [1.0, 1.0],
            "allies": [],
            "enemies": [],
            "hand": [],
            "action": None,
            "reward": {
                "elixir_delta": -1.0,
                "tower_dmg_dealt": 0.0,
                "tower_dmg_taken": 0.0,
                "unit_value_killed": 0.0,
                "unit_value_lost": 0.0,
                "win_bonus": 0.0,
                "loss_penalty": 0.0,
            }
        }
        frames.append(frame)

    with gzip.open(data_file, "wt") as f:
        for frame in frames:
            f.write(json.dumps(frame) + "\n")

    report = validate_dataset(data_file)

    assert report["frame_count"] == 10
    assert "reward_stats" in report
    assert "screen_distribution" in report
    assert "action_distribution" in report


def test_validate_dataset_detects_missing_frames(tmp_path):
    """Test that validate_dataset detects missing/duplicate frame_ids."""
    data_file = tmp_path / "data.jsonl.gz"

    frames = []
    # Missing frame_id 3, duplicate frame_id 5
    for i in [1, 2, 4, 5, 5, 6, 7, 8, 9, 10]:
        frame = {
            "timestamp": "2026-01-01T00:00:00Z",
            "frame_id": i,
            "screen": "IN_GAME",
            "elixir": 10,
            "ally_princess_hp": [1.0, 1.0],
            "enemy_princess_hp": [1.0, 1.0],
            "allies": [],
            "enemies": [],
            "hand": [],
            "action": None,
            "reward": {
                "elixir_delta": 0.0,
                "tower_dmg_dealt": 0.0,
                "tower_dmg_taken": 0.0,
                "unit_value_killed": 0.0,
                "unit_value_lost": 0.0,
                "win_bonus": 0.0,
                "loss_penalty": 0.0,
            }
        }
        frames.append(frame)

    with gzip.open(data_file, "wt") as f:
        for frame in frames:
            f.write(json.dumps(frame) + "\n")

    report = validate_dataset(data_file)

    assert "missing_frames" in report
    assert 3 in report["missing_frames"]
    assert "duplicate_frames" in report
    assert 5 in report["duplicate_frames"]