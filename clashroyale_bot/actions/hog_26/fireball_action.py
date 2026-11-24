"""Fireball action for 2.6 Hog Cycle."""

import math
from clashroyale_bot.actions.hog_26.generic_action import SpellAction
from clashroyalebuildabot.namespaces.cards import Cards
from clashroyalebuildabot.namespaces import Units


class FireballAction(SpellAction):
    """Fireball - SpellAction radius 2.5, high value on 3+ elixir trades."""

    CARD = Cards.FIREBALL
    RADIUS = 2.5
    MIN_SCORE = 5
    UNIT_TO_SCORE = {
        Units.SKELETON: 1,
        Units.BAT: 1,
        Units.SPEAR_GOBLIN: 1,
        Units.GOBLIN: 2,
        Units.ARCHER: 3,
        Units.MUSKETEER: 5,
        Units.WIZARD: 6,
        Units.WITCH: 6,
        Units.EXECUTIONER: 6,
        Units.ELITE_BARBARIAN: 5,
        Units.DARK_PRINCE: 4,
        Units.PRINCE: 4,
        Units.BABY_DRAGON: 4,
        Units.MEGA_MINION: 4,
        Units.FLYING_MACHINE: 3,
        Units.ELECTRO_WIZARD: 6,
        Units.MAGIC_ARCHER: 5,
        Units.PRINCESS: 4,
        Units.DART_GOBLIN: 4,
        Units.ICE_WIZARD: 4,
        Units.HUNTER: 4,
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
            if distance <= self.RADIUS - 0.5:
                hit_score += self.UNIT_TO_SCORE.get(det.unit, 2)
                max_distance = min(max_distance, -distance)

        # Bonus for hitting enemy tower (chip damage)
        if self.tile_y >= 15:  # Near enemy princess tower
            hit_score += 2

        # High value on 3+ elixir trades
        base = [1 if hit_score >= self.MIN_SCORE else 0, hit_score, max_distance]

        # Prefer when we have elixir for positive trade
        if state.numbers.elixir.number >= 7:
            base[0] = max(base[0], 0.5)

        # Don't fireball at max elixir unless high value
        if state.numbers.elixir.number == 10 and hit_score < 8:
            base = [0.2, hit_score, max_distance]

        return base