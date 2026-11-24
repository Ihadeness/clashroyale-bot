"""Mock namespaces for testing."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Position:
    bbox: tuple[int, int, int, int]
    tile_x: int
    tile_y: int


@dataclass
class UnitDetection:
    unit: "Unit"
    position: Position
    hp: float


@dataclass
class NumberDetection:
    bbox: tuple[int, int, int, int]
    number: float


@dataclass
class Numbers:
    elixir: NumberDetection
    right_ally_princess_hp: NumberDetection
    left_ally_princess_hp: NumberDetection
    right_enemy_princess_hp: NumberDetection
    left_enemy_princess_hp: NumberDetection


@dataclass
class Card:
    name: str
    target_anywhere: bool
    cost: int
    units: list
    id_: int


class Unit:
    def __init__(self, name: str):
        self.name = name


class Action:
    """Mock Action base class."""
    def __init__(self, bot):
        self.bot = bot

    def can_execute(self, state: State) -> bool:
        return True

    def execute(self, state: State) -> None:
        pass


class Units:
    # 2.6 Hog Cycle units
    ARCHER = Unit("ARCHER")
    HOG_RIDER = Unit("HOG_RIDER")
    LOG = Unit("LOG")
    ICE_SPIRIT = Unit("ICE_SPIRIT")
    SKELETON = Unit("SKELETON")
    SKELETONS = Unit("SKELETONS")
    ICE_GOLEM = Unit("ICE_GOLEM")
    CANNON = Unit("CANNON")
    MUSKETEER = Unit("MUSKETEER")
    FIREBALL = Unit("FIREBALL")

    # Enemy units for targeting
    KNIGHT = Unit("KNIGHT")
    MINI_PEKKA = Unit("MINI_PEKKA")
    PEKKA = Unit("PEKKA")
    MEGA_KNIGHT = Unit("MEGA_KNIGHT")
    GIANT = Unit("GIANT")
    ROYAL_GIANT = Unit("ROYAL_GIANT")
    GOLEM = Unit("GOLEM")
    ELITE_BARBARIAN = Unit("ELITE_BARBARIAN")
    BARBARIAN = Unit("BARBARIAN")
    DARK_PRINCE = Unit("DARK_PRINCE")
    PRINCE = Unit("PRINCE")
    BATTLE_RAM = Unit("BATTLE_RAM")
    LAVA_HOUND = Unit("LAVA_HOUND")
    SPARKY = Unit("SPARKY")
    INFERNO_DRAGON = Unit("INFERNO_DRAGON")
    INFERNO_TOWER = Unit("INFERNO_TOWER")
    BOMB_TOWER = Unit("BOMB_TOWER")
    FURNACE = Unit("FURNACE")
    GOBLIN_HUT = Unit("GOBLIN_HUT")
    BARBARIAN_HUT = Unit("BARBARIAN_HUT")
    TESLA = Unit("TESLA")

    # Air units
    MINION = Unit("MINION")
    BAT = Unit("BAT")
    BALLOON = Unit("BALLOON")
    MINION_HORDE = Unit("MINION_HORDE")
    BABY_DRAGON = Unit("BABY_DRAGON")
    FLYING_MACHINE = Unit("FLYING_MACHINE")
    MEGA_MINION = Unit("MEGA_MINION")
    INFERNO_DRAGON = Unit("INFERNO_DRAGON")
    ELECTRO_DRAGON = Unit("ELECTRO_DRAGON")

    # Swarm units
    SPEAR_GOBLIN = Unit("SPEAR_GOBLIN")
    GOBLIN = Unit("GOBLIN")
    FIRE_SPIRIT = Unit("FIRE_SPIRIT")
    HEAL_SPIRIT = Unit("HEAL_SPIRIT")
    ELECTRO_SPIRIT = Unit("ELECTRO_SPIRIT")
    ICE_SPIRIT = Unit("ICE_SPIRIT")
    WALL_BREAKER = Unit("WALL_BREAKER")

    # Other units
    WIZARD = Unit("WIZARD")
    WITCH = Unit("WITCH")
    EXECUTIONER = Unit("EXECUTIONER")
    ELECTRO_WIZARD = Unit("ELECTRO_WIZARD")
    MAGIC_ARCHER = Unit("MAGIC_ARCHER")
    PRINCESS = Unit("PRINCESS")
    DART_GOBLIN = Unit("DART_GOBLIN")
    ICE_WIZARD = Unit("ICE_WIZARD")
    HUNTER = Unit("HUNTER")


class Cards:
    ARCHERS = Card("archers", False, 3, [Units.ARCHER], 26000001)
    HOG_RIDER = Card("hog_rider", False, 4, [Units.HOG_RIDER], 26000002)
    LOG = Card("log", True, 2, [], 28000001)
    ICE_SPIRIT = Card("ice_spirit", False, 1, [Units.ICE_SPIRIT], 26000003)
    SKELETONS = Card("skeletons", False, 1, [Units.SKELETON], 26000004)
    ICE_GOLEM = Card("ice_golem", False, 2, [Units.ICE_GOLEM], 26000005)
    CANNON = Card("cannon", False, 3, [Units.CANNON], 26000006)
    MUSKETEER = Card("musketeer", False, 4, [Units.MUSKETEER], 26000007)
    FIREBALL = Card("fireball", True, 4, [], 28000002)


class Screens:
    UNKNOWN = "UNKNOWN"
    IN_GAME = "IN_GAME"
    LOBBY = "LOBBY"
    END_OF_GAME = "END_OF_GAME"
    BYPASS_END_OF_GAME = "BYPASS_END_OF_GAME"


@dataclass
class State:
    allies: list[UnitDetection]
    enemies: list[UnitDetection]
    numbers: Optional[Numbers]
    cards: list[Card]
    ready: list[int]
    screen: str