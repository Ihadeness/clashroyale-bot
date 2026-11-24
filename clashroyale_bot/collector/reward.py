"""Reward computation for RL training."""

from clashroyale_bot.collector.schemas import RewardData
from clashroyalebuildabot.namespaces import State, Screens


# Unit values for reward computation (approximate elixir cost)
UNIT_VALUES = {
    # Low value (1-2 elixir)
    "SKELETON": 0.5, "BAT": 0.5, "SPEAR_GOBLIN": 0.5, "GOBLIN": 1.0,
    "FIRE_SPIRIT": 1.0, "HEAL_SPIRIT": 1.0, "ELECTRO_SPIRIT": 1.0, "ICE_SPIRIT": 1.0,
    "WALL_BREAKER": 1.5,

    # Medium value (3-4 elixir)
    "ARCHER": 2.0, "MUSKETEER": 3.0, "WIZARD": 3.5, "WITCH": 3.5,
    "EXECUTIONER": 3.5, "ICE_WIZARD": 3.0, "DART_GOBLIN": 2.5,
    "PRINCESS": 3.0, "MAGIC_ARCHER": 3.5, "ELECTRO_WIZARD": 4.0,
    "HUNTER": 3.0, "BABY_DRAGON": 3.0, "MEGA_MINION": 3.0,
    "FLYING_MACHINE": 3.0, "INFERNO_DRAGON": 4.0, "ELECTRO_DRAGON": 4.0,
    "MINION": 1.5, "BAT": 0.5, "MINION_HORDE": 3.0,

    # High value (5+ elixir)
    "KNIGHT": 2.5, "MINI_PEKKA": 3.0, "PEKKA": 5.0, "MEGA_KNIGHT": 5.0,
    "GIANT": 4.0, "ROYAL_GIANT": 4.0, "GOLEM": 5.0, "LAVA_HOUND": 5.0,
    "DARK_PRINCE": 3.0, "PRINCE": 3.0, "BATTLE_RAM": 3.0,
    "ELITE_BARBARIAN": 4.0, "BARBARIAN": 2.0,

    # Buildings
    "CANNON": 2.0, "TESLA": 3.0, "INFERNO_TOWER": 4.0, "BOMB_TOWER": 3.0,
    "FURNACE": 3.0, "GOBLIN_HUT": 3.0, "BARBARIAN_HUT": 3.0,
}


def get_unit_value(unit_name: str) -> float:
    """Get approximate elixir value of a unit."""
    return UNIT_VALUES.get(unit_name, 2.0)  # Default 2.0


def compute_tower_damage(prev_hp: float, curr_hp: float) -> float:
    """Compute tower damage dealt/taken (0.0 to 1.0)."""
    return max(0.0, prev_hp - curr_hp)


def get_tower_hp(state: State, side: str, tower: str) -> float:
    """Get tower HP (0.0 to 1.0)."""
    if not state.numbers:
        return 1.0
    # Numbers uses format: {tower}_{side}_princess_hp (e.g., right_enemy_princess_hp)
    attr = f"{tower}_{side}_princess_hp"
    detection = getattr(state.numbers, attr, None)
    return detection.number if detection else 1.0


def compute_reward(prev_state: State, curr_state: State, action) -> RewardData:
    """
    Compute reward for RL training.

    Dense rewards (every step):
    - elixir_delta: negative when spending elixir
    - tower_dmg_dealt: damage to enemy towers
    - tower_dmg_taken: damage to own towers
    - unit_value_killed: value of enemy units killed
    - unit_value_lost: value of own units lost

    Sparse rewards (end of game):
    - win_bonus: +100 for win
    - loss_penalty: -100 for loss
    """
    # Elixir delta (negative when spending)
    prev_elixir = prev_state.numbers.elixir.number if prev_state.numbers.elixir else 10
    curr_elixir = curr_state.numbers.elixir.number if curr_state.numbers.elixir else 10
    elixir_delta = curr_elixir - prev_elixir  # Negative = spent

    # Tower HP changes
    # Enemy tower damage dealt
    prev_enemy_right = get_tower_hp(prev_state, "enemy", "right")
    curr_enemy_right = get_tower_hp(curr_state, "enemy", "right")
    prev_enemy_left = get_tower_hp(prev_state, "enemy", "left")
    curr_enemy_left = get_tower_hp(curr_state, "enemy", "left")

    tower_dmg_dealt = (
        compute_tower_damage(prev_enemy_right, curr_enemy_right) +
        compute_tower_damage(prev_enemy_left, curr_enemy_left)
    )

    # Own tower damage taken
    prev_ally_right = get_tower_hp(prev_state, "ally", "right")
    curr_ally_right = get_tower_hp(curr_state, "ally", "right")
    prev_ally_left = get_tower_hp(prev_state, "ally", "left")
    curr_ally_left = get_tower_hp(curr_state, "ally", "left")

    tower_dmg_taken = (
        compute_tower_damage(prev_ally_right, curr_ally_right) +
        compute_tower_damage(prev_ally_left, curr_ally_left)
    )

    # Unit value killed (enemy units that disappeared)
    prev_enemy_names = {d.unit.name for d in prev_state.enemies}
    curr_enemy_names = {d.unit.name for d in curr_state.enemies}
    killed_units = prev_enemy_names - curr_enemy_names
    unit_value_killed = sum(get_unit_value(name) for name in killed_units)

    # Unit value lost (ally units that disappeared)
    prev_ally_names = {d.unit.name for d in prev_state.allies}
    curr_ally_names = {d.unit.name for d in curr_state.allies}
    lost_units = prev_ally_names - curr_ally_names
    unit_value_lost = sum(get_unit_value(name) for name in lost_units)

    # Sparse rewards on end of game
    win_bonus = 0.0
    loss_penalty = 0.0
    if curr_state.screen in (Screens.END_OF_GAME, Screens.BYPASS_END_OF_GAME):
        # Determine win/loss from tower HP
        ally_hp = get_tower_hp(curr_state, "ally", "right") + get_tower_hp(curr_state, "ally", "left")
        enemy_hp = get_tower_hp(curr_state, "enemy", "right") + get_tower_hp(curr_state, "enemy", "left")

        if enemy_hp <= 0.001 and ally_hp > 0.001:
            win_bonus = 100.0
        elif ally_hp <= 0.001 and enemy_hp > 0.001:
            loss_penalty = -100.0
        elif enemy_hp <= 0.001 and ally_hp <= 0.001:
            loss_penalty = -50.0  # Draw = slight penalty

    return RewardData(
        elixir_delta=elixir_delta,
        tower_dmg_dealt=tower_dmg_dealt,
        tower_dmg_taken=tower_dmg_taken,
        unit_value_killed=unit_value_killed,
        unit_value_lost=unit_value_lost,
        win_bonus=win_bonus,
        loss_penalty=loss_penalty,
    )