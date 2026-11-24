"""Musketeer action for 2.6 Hog Cycle."""

import math
from clashroyale_bot.actions.hog_26.generic_action import UnitAction
from clashroyalebuildabot.namespaces.cards import Cards
from clashroyalebuildabot.namespaces import Units


class MusketeerAction(UnitAction):
    """Musketeer - Backline DPS, protect with Ice Golem, punish overcommit."""

    CARD = Cards.MUSKETEER

    def calculate_score(self, state):
        score = [0]

        # Backline DPS: place behind our towers (tile_y <= 8)
        if self.tile_y <= 8:
            score = [0.5]

            # Protect with Ice Golem: if we have Ice Golem in hand, place Musketeer behind it
            has_ice_golem = any(c == Cards.ICE_GOLEM for c in state.cards[1:])  # In hand
            if has_ice_golem:
                score = [0.7]

        # Punish overcommit: if enemy has no air defense and we have elixir
        enemy_air_defense = any(
            d.unit.name in ("MUSKETEER", "ARCHERS", "WIZARD", "EXECUTIONER", "ELECTRO_WIZARD",
                           "MAGIC_ARCHER", "PRINCESS", "DART_GOBLIN", "INFERNO_DRAGON", "MEGA_MINION",
                           "BABY_DRAGON", "MINION", "BAT", "FLYING_MACHINE")
            for d in state.enemies + state.allies
        )

        if not enemy_air_defense and state.numbers.elixir.number >= 7:
            # Place in safe spot
            if self.tile_y <= 9:
                score = [max(score[0], 0.8)]

        # Defensive: shoot down air units / high value targets
        for det in state.enemies:
            if det.unit.name in ("BALLOON", "LAVA_HOUND", "INFERNO_DRAGON", "MEGA_MINION",
                                "BABY_DRAGON", "MINION_HORDE", "MINION", "BAT"):
                dist = math.hypot(self.tile_x - det.position.tile_x, self.tile_y - det.position.tile_y)
                if dist <= 7:  # Musketeer range
                    score = [1, -dist]
                    break

        # Counter-push: after defending, place Musketeer for counter
        if state.numbers.elixir.number >= 8 and self.tile_y <= 9:
            score = [max(score[0], 0.6)]

        # Elixir management
        if state.numbers.elixir.number < 6:
            score = [s * 0.5 for s in score]

        return score