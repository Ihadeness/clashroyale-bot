"""Hog Rider action for 2.6 Hog Cycle."""

from clashroyale_bot.actions.hog_26.generic_action import UnitAction
from clashroyalebuildabot.namespaces.cards import Cards


class HogRiderAction(UnitAction):
    """Hog Rider - Bridge placement, punish when enemy building down."""

    CARD = Cards.HOG_RIDER

    def calculate_score(self, state):
        # Base score: only play at bridge positions
        score = [0]

        # Check if we have a valid bridge position
        if self.tile_x in (7, 10) and self.tile_y in (13, 14):
            score = [0.5]

            # Boost if enemy building is down (simplified: check for no enemy buildings)
            enemy_buildings = [
                d for d in state.enemies
                if d.unit.name in ("CANNON", "TESLA", "INFERNO_TOWER", "BOMB_TOWER", "FURNACE", "GOBLIN_HUT", "BARBARIAN_HUT")
            ]
            if not enemy_buildings:
                score = [1, 14 - self.tile_y]  # Prefer higher bridge (closer to enemy)

            # Punish if low elixir
            if state.numbers.elixir.number < 6:
                score[0] *= 0.5

        return score