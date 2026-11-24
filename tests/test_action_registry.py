"""Tests for action registry module."""

from clashroyale_bot.actions.registry import ActionRegistry


def test_registry_loads_hog_26_actions():
    """Test that registry loads all 8 actions for hog_26 deck."""
    actions = ActionRegistry.get_actions("hog_26")
    assert len(actions) == 8
    card_names = {a.CARD.name for a in actions}
    # Card names are lowercase in the original (e.g., "hog_rider", "log")
    expected = {
        "hog_rider", "log", "ice_spirit", "skeletons",
        "ice_golem", "cannon", "musketeer", "fireball"
    }
    assert card_names == expected


def test_registry_validates_unique_cards():
    """Test that registry validates unique CARD attributes."""
    # This will be tested implicitly by get_actions
    actions = ActionRegistry.get_actions("hog_26")
    card_names = [a.CARD.name for a in actions]
    assert len(card_names) == len(set(card_names))  # All unique


def test_registry_validates_card_in_namespace():
    """Test that all action cards exist in Cards namespace."""
    from clashroyalebuildabot.namespaces.cards import NAME2CARD

    actions = ActionRegistry.get_actions("hog_26")
    for action in actions:
        assert action.CARD.name in NAME2CARD


def test_registry_raises_for_unknown_deck():
    """Test that registry raises for unknown deck name."""
    try:
        ActionRegistry.get_actions("unknown_deck")
        assert False, "Should have raised"
    except (ImportError, ValueError, FileNotFoundError):
        pass  # Expected