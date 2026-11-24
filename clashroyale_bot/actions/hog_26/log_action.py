"""Log action for 2.6 Hog Cycle."""

import math
from clashroyale_bot.actions.hog_26.generic_action import SpellAction
from clashroyalebuildabot.namespaces.cards import Cards
from clashroyalebuildabot.namespaces import Units


class LogAction(SpellAction):
    """Log - SpellAction subclass, radius 3.5, targets swarms + chip tower."""

    CARD = Cards.LOG
    RADIUS = 3.5
    MIN_SCORE = 3
    UNIT_TO_SCORE = {
        Units.SKELETON: 2,
        Units.BAT: 2,
        Units.SPEAR_GOBLIN: 2,
        Units.GOBLIN: 2,
        Units.FIRE_SPIRIT: 3,
        Units.HEAL_SPIRIT: 3,
        Units.ELECTRO_SPIRIT: 3,
        Units.ICE_SPIRIT: 3,
        Units.WALL_BREAKER: 3,
    }

    def calculate_score(self, state):
        # Base spell scoring
        hit_score = 0
        max_distance = float("inf")

        for det in state.enemies:
            distance = math.hypot(
                self.tile_x - det.position.tile_x,
                self.tile_y - det.position.tile_y + 2,
            )
            if distance <= self.RADIUS - 1:
                hit_score += self.UNIT_TO_SCORE.get(det.unit, 2)
                max_distance = min(max_distance, -distance)

        # Bonus for chipping tower
        if self.tile_y >= 14:  # Near enemy tower
            hit_score += 1

        base = [1 if hit_score >= self.MIN_SCORE else 0, hit_score, max_distance]

        # Prefer when we have elixir advantage
        if state.numbers.elixir.number >= 8:
            base[0] = max(base[0], 0.5)

        return base