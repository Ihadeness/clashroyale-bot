"""Mock Cards namespace for testing."""

from clashroyalebuildabot.namespaces import Card, Units

# Re-export for compatibility
__all__ = ["Card", "Cards", "NAME2CARD"]


class _CardsNamespace:
    ARCHERS = Card("archers", False, 3, [Units.ARCHER], 26000001)
    LOG = Card("log", True, 2, [], 28000001)
    ICE_SPIRIT = Card("ice_spirit", False, 1, [Units.ARCHER], 26000002)
    SKELETONS = Card("skeletons", False, 1, [Units.ARCHER], 26000003)
    ICE_GOLEM = Card("ice_golem", False, 2, [Units.ARCHER], 26000004)
    CANNON = Card("cannon", False, 3, [Units.ARCHER], 26000005)
    MUSKETEER = Card("musketeer", False, 4, [Units.ARCHER], 26000006)
    FIREBALL = Card("fireball", True, 4, [], 28000002)
    HOG_RIDER = Card("hog_rider", False, 4, [Units.ARCHER], 26000007)


Cards = _CardsNamespace()
NAME2CARD = {c.name: c for c in [
    Cards.ARCHERS, Cards.LOG, Cards.ICE_SPIRIT, Cards.SKELETONS,
    Cards.ICE_GOLEM, Cards.CANNON, Cards.MUSKETEER, Cards.FIREBALL,
    Cards.HOG_RIDER,
]}