"""Tests for config_loader module."""

import tempfile
import yaml
from pathlib import Path

# We'll import after implementing
# from clashroyale_bot.core.config_loader import load_config, deep_merge


def test_deep_merge_basic():
    """Test deep_merge merges nested dicts recursively."""
    from clashroyale_bot.core.config_loader import deep_merge

    base = {"a": 1, "b": {"x": 10, "y": 20}}
    override = {"b": {"x": 100}, "c": 3}
    result = deep_merge(base, override)

    assert result == {"a": 1, "b": {"x": 100, "y": 20}, "c": 3}


def test_deep_merge_lists_replaced():
    """Test deep_merge replaces lists (does not merge them)."""
    from clashroyale_bot.core.config_loader import deep_merge

    base = {"list": [1, 2, 3]}
    override = {"list": [4, 5]}
    result = deep_merge(base, override)

    assert result == {"list": [4, 5]}


def test_config_loader_merges_deck_over_base():
    """Test load_config merges deck config over base config."""
    from clashroyale_bot.core.config_loader import load_config

    # This test will fail until we implement load_config and create the yaml files
    cfg = load_config("hog_26")
    assert cfg["deck"]["name"] == "hog_26"
    assert cfg["detector"]["providers"] == ["DmlExecutionProvider", "CPUExecutionProvider"]
    assert cfg["collector"]["enabled"] is True
    assert "bot" in cfg and "adb" in cfg  # inherited from base


def test_load_config_finds_deck_yaml():
    """Test load_config finds deck yaml in config/ directory."""
    from clashroyale_bot.core.config_loader import load_config

    # Should not raise FileNotFoundError
    cfg = load_config("hog_26")
    assert isinstance(cfg, dict)
    assert "deck" in cfg