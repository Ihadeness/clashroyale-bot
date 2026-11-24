"""Skeletons action for 2.6 Hog Cycle."""

import math
from clashroyale_bot.actions.hog_26.generic_action import CycleAction
from clashroyalebuildabot.namespaces.cards import Cards
from clashroyalebuildabot.namespaces import Units


class SkeletonsAction(CycleAction):
    """Skeletons - Distract single-target, kite, cycle."""

    CARD = Cards.SKELETONS

    def calculate_score(self, state):
        score = [0]

        # Cycle when at max elixir
        if state.numbers.elixir.number == 10:
            score = [0.5]

        # Defensive: distract single-target units
        for det in state.enemies:
            if det.unit.name in (
                "MINI_PEKKA", "PEKKA", "MEGA_KNIGHT", "SPARKY", "INFERNO_DRAGON",
                "INFERNO_TOWER", "PRINCE", "DARK_PRINCE", "BATTLE_RAM"
            ):
                dist = math.hypot(self.tile_x - det.position.tile_x, self.tile_y - det.position.tile_y)
                if dist <= 4:
                    score = [1, -dist]  # Distract
                    break

        # Kite: place between enemy and our tower
        for det in state.enemies:
            if det.unit.name in ("GIANT", "ROYAL_GIANT", "GOLEM", "LAVA_HOUND"):
                # Place skeletons to pull
                if self.tile_y <= 12 and self.tile_y >= 8:
                    score = [max(score[0], 0.7), 12 - self.tile_y]
                    break

        # Cycle play: place at bridge when cycling
        if state.numbers.elixir.number >= 8 and self.tile_y in (13, 14):
            score = [max(score[0], 0.3), score[1] if len(score) > 1 else 0]

        return score