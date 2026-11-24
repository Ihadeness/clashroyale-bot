"""Generic action base classes for 2.6 Hog Cycle."""

import math
from clashroyalebuildabot.actions.generic.action import Action
from clashroyalebuildabot.actions.generic.spell_action import SpellAction
from clashroyalebuildabot.namespaces import Units


class UnitAction(Action):
    """Base class for unit deployment actions."""

    def __init__(self, index: int, tile_x: int, tile_y: int):
        super().__init__(index, tile_x, tile_y)


class BuildingAction(UnitAction):
    """Base class for building deployment actions."""

    pass


class CycleAction(UnitAction):
    """Base class for cheap cycle cards (1-2 elixir)."""

    def calculate_score(self, state):
        # Cycle cards: play when elixir is high or need cycle
        score = [0]
        if state.numbers.elixir.number >= 9:
            score = [0.3]
        elif state.numbers.elixir.number == 10:
            score = [0.5]
        return score


class DefensiveAction(UnitAction):
    """Base class for defensive actions."""

    def calculate_score(self, state):
        score = [0]
        # React to enemy units in range
        for det in state.enemies:
            dist = math.hypot(self.tile_x - det.position.tile_x, self.tile_y - det.position.tile_y)
            if dist <= 5:
                score = [1, -dist]  # Prefer closer enemies
                break
        return score