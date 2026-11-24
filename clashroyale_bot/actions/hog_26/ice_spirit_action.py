"""Ice Spirit action for 2.6 Hog Cycle."""

import math
from clashroyale_bot.actions.hog_26.generic_action import CycleAction
from clashroyalebuildabot.namespaces.cards import Cards
from clashroyalebuildabot.namespaces import Units


class IceSpiritAction(CycleAction):
    """Ice Spirit - Cycle/defense, kite melee, stall at bridge."""

    CARD = Cards.ICE_SPIRIT

    def calculate_score(self, state):
        score = [0]

        # Cycle when at max elixir
        if state.numbers.elixir.number == 10:
            score = [0.5]

        # Defensive: kite melee units
        for det in state.enemies:
            if det.unit.name in (
                "KNIGHT", "MINI_PEKKA", "PEKKA", "MEGA_KNIGHT", "GIANT",
                "ROYAL_GIANT", "GOLEM", "ELITE_BARBARIAN", "BARBARIAN",
                "DARK_PRINCE", "PRINCE", "BATTLE_RAM", "HOG_RIDER"
            ):
                dist = math.hypot(self.tile_x - det.position.tile_x, self.tile_y - det.position.tile_y)
                if dist <= 4:
                    score = [1, -dist]  # Stall/kite
                    break

        # Bridge stall (tile_y 13-14)
        if self.tile_y in (13, 14) and self.tile_x in (7, 10):
            score = [max(score[0], 0.3), score[1] if len(score) > 1 else 0]

        return score