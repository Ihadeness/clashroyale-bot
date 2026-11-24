"""Configuration loader with YAML extends support."""

import os
from pathlib import Path
from typing import Any

import yaml


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """
    Recursively merge override into base.

    Lists are replaced (not merged). Nested dicts are merged recursively.
    Returns a new dict (does not mutate inputs).
    """
    result = base.copy()

    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value

    return result


def _find_original_default_config() -> Path:
    """
    Find the original clashroyalebuildabot default_config.yaml.

    Tries multiple locations:
    1. Installed package location
    2. Relative to this file (if original repo cloned alongside)
    3. Environment variable override
    """
    # 1. Check environment variable
    env_path = os.environ.get("CLASHROYALE_ORIGINAL_CONFIG")
    if env_path:
        path = Path(env_path)
        if path.exists():
            return path

    # 2. Try imported package
    try:
        import clashroyalebuildabot
        pkg_path = Path(clashroyalebuildabot.__file__).parent / "default_config.yaml"
        if pkg_path.exists():
            return pkg_path
    except ImportError:
        pass

    # 3. Try relative to this file (original repo cloned as sibling)
    this_file = Path(__file__).resolve()
    # Go up to find clashroyalebuildabot sibling
    for parent in this_file.parents:
        candidate = parent / "clashroyalebuildabot" / "default_config.yaml"
        if candidate.exists():
            return candidate

    # 4. Fallback: create a minimal default inline (for testing without original)
    raise FileNotFoundError(
        "Could not find original clashroyalebuildabot/default_config.yaml. "
        "Set CLASHROYALE_ORIGINAL_CONFIG env var or install the original package."
    )


def load_config(deck_name: str) -> dict[str, Any]:
    """
    Load and merge configuration for a deck.

    Args:
        deck_name: Name of the deck (e.g., "hog_26")

    Returns:
        Merged configuration dict with all keys resolved.

    The deck config file (config/{deck_name}.yaml) must have an 'extends' key
    pointing to the base config (original default_config.yaml).
    """
    # Find deck config
    config_dir = Path(__file__).resolve().parent.parent / "config"
    deck_config_path = config_dir / f"{deck_name}.yaml"

    if not deck_config_path.exists():
        raise FileNotFoundError(f"Deck config not found: {deck_config_path}")

    # Load deck config
    with open(deck_config_path, "r", encoding="utf-8") as f:
        deck_config = yaml.safe_load(f) or {}

    # Get base config path from 'extends' key
    extends = deck_config.pop("extends", None)
    if not extends:
        raise ValueError(f"Deck config {deck_name}.yaml must have 'extends' key")

    # Resolve base config path
    if Path(extends).is_absolute():
        base_config_path = Path(extends)
    else:
        # Relative to deck config directory
        base_config_path = (deck_config_path.parent / extends).resolve()

    # If base config doesn't exist, try to find original
    if not base_config_path.exists():
        base_config_path = _find_original_default_config()

    # Load base config
    with open(base_config_path, "r", encoding="utf-8") as f:
        base_config = yaml.safe_load(f) or {}

    # Merge: deck overrides base
    merged = deep_merge(base_config, deck_config)

    return merged