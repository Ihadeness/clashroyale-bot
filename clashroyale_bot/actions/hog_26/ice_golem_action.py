"""Ice Golem action for 2.6 Hog Cycle."""

import math
from clashroyale_bot.actions.hog_26.generic_action import UnitAction
from clashroyalebuildabot.namespaces.cards import Cards
from clashroyalebuildabot.namespaces import Units


class IceGolemAction(UnitAction):
    """Ice Golem - Tank for Musketeer, kite, death nova value."""

    CARD = Cards.ICE_GOLEM

    def calculate_score(self, state):
        score = [0]

        # Tank for Musketeer: place in front of our Musketeer
        for det in state.allies:
            if det.unit == Units.MUSKETEER:
                # Place ice golem slightly in front (lower tile_y)
                if self.tile_x == det.position.tile_x and self.tile_y == det.position.tile_y + 1:
                    score = [1, 0]
                    break

        # Kite: pull heavy units
        for det in state.enemies:
            if det.unit.name in ("GIANT", "ROYAL_GIANT", "GOLEM", "MEGA_KNIGHT", "PEKKA", "LAVA_HOUND"):
                dist = math.hypot(self.tile_x - det.position.tile_x, self.tile_y - det.position.tile_y)
                if dist <= 5:
                    score = [1, -dist]
                    break

        # Death nova value: place where it will hit multiple enemies on death
        # (simplified: place near enemy group)
        enemy_groups = {}
        for det in state.enemies:
            key = (det.position.tile_x // 3, det.position.tile_y // 3)
            enemy_groups.setdefault(key, []).append(det)

        for group in enemy_groups.values():
            if len(group) >= 2:
                avg_x = sum(d.position.tile_x for d in group) // len(group)
                avg_y = sum(d.position.tile_y for d in group) // len(group)
                if self.tile_x == avg_x and self.tile_y == avg_y:
                    score = [max(score[0], 0.8), score[1] if len(score) > 1 else 0]
                    break

        # Don't play at max elixir unless defensive
        if state.numbers.elixir.number == 10 and score[0] < 0.5:
            score = [0.2]

        return score