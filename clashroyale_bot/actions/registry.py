"""Action registry for loading deck-specific actions."""

import importlib
from typing import Any

from clashroyalebuildabot.actions.generic.action import Action
from clashroyalebuildabot.namespaces.cards import NAME2CARD


class ActionRegistry:
    """Registry for loading and validating deck actions."""

    _cache: dict[str, list[type[Action]]] = {}

    @classmethod
    def get_actions(cls, deck_name: str) -> list[type[Action]]:
        """
        Load actions for a deck.

        Args:
            deck_name: Name of the deck (e.g., "hog_26")

        Returns:
            List of Action classes for the deck.

        Raises:
            ImportError: If deck module not found.
            ValueError: If validation fails.
        """
        if deck_name in cls._cache:
            return cls._cache[deck_name]

        # Import deck module
        try:
            module = importlib.import_module(f"clashroyale_bot.actions.{deck_name}")
        except ImportError as e:
            raise ImportError(f"Deck '{deck_name}' not found: {e}")

        # Collect action classes (classes with CARD attribute)
        actions = []
        for name in dir(module):
            obj = getattr(module, name)
            if isinstance(obj, type) and issubclass(obj, Action) and hasattr(obj, "CARD"):
                actions.append(obj)

        # Validate
        cls._validate_actions(actions, deck_name)

        cls._cache[deck_name] = actions
        return actions

    @classmethod
    def _validate_actions(cls, actions: list[type[Action]], deck_name: str) -> None:
        """Validate action list."""
        if len(actions) != 8:
            raise ValueError(f"Deck '{deck_name}' must have exactly 8 actions, got {len(actions)}")

        # Check unique cards by name (Card objects may not be hashable)
        card_names = [a.CARD.name for a in actions]
        if len(card_names) != len(set(card_names)):
            raise ValueError(f"Deck '{deck_name}' has duplicate CARD attributes")

        # Check all cards exist in NAME2CARD
        for action in actions:
            if action.CARD.name not in NAME2CARD:
                raise ValueError(f"Action {action.__name__} uses unknown card: {action.CARD.name}")

    @classmethod
    def clear_cache(cls) -> None:
        """Clear the action cache (useful for testing)."""
        cls._cache.clear()