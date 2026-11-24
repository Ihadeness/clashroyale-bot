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


class Units:
    ARCHER = Unit("ARCHER")


class Cards:
    ARCHERS = Card("archers", False, 3, [Units.ARCHER], 26000001)


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