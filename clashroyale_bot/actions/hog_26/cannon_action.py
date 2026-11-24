"""Cannon action for 2.6 Hog Cycle."""

import math
from clashroyale_bot.actions.hog_26.generic_action import BuildingAction
from clashroyalebuildabot.namespaces.cards import Cards
from clashroyalebuildabot.namespaces import Units


class CannonAction(BuildingAction):
    """Cannon - Reactive defense (building targeting), pull Hog/Giant."""

    CARD = Cards.CANNON
    PULL_TARGETS = {
        Units.HOG_RIDER, Units.GIANT, Units.ROYAL_GIANT, Units.GOLEM,
        Units.BATTLE_RAM, Units.LAVA_HOUND, Units.MEGA_KNIGHT,
        Units.PEKKA, Units.ELITE_BARBARIAN
    }

    def calculate_score(self, state):
        score = [0]

        # Reactive defense: pull building-targeting units
        for det in state.enemies:
            if det.unit in self.PULL_TARGETS:
                dist = math.hypot(self.tile_x - det.position.tile_x, self.tile_y - det.position.tile_y)
                # Standard cannon placement: tile_x 8, tile_y 11 (center)
                if self.tile_x == 8 and self.tile_y == 11 and dist <= 8:
                    score = [1, -dist]
                    break

        # Anti-Hog specific: place to pull Hog to center
        for det in state.enemies:
            if det.unit == Units.HOG_RIDER:
                # Optimal cannon placement for Hog pull
                if self.tile_x in (7, 8, 9) and self.tile_y == 11:
                    dist = abs(self.tile_x - det.position.tile_x)
                    score = [1, -dist]
                    break

        # Don't place if we already have a building (simplified check)
        ally_buildings = [
            d for d in state.allies
            if d.unit.name in ("CANNON", "TESLA", "INFERNO_TOWER", "BOMB_TOWER", "FURNACE")
        ]
        if ally_buildings and score[0] < 0.8:
            score = [0.1]

        # Elixir management
        if state.numbers.elixir.number < 4:
            score = [max(s * 0.5 for s in score)]

        return score