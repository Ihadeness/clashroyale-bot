"""Pydantic schemas for dataset collection."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from dataclasses import dataclass


class UnitData(BaseModel):
    """Unit detection data."""
    unit: str
    tile_x: int
    tile_y: int
    hp: float
    bbox: List[int] = Field(default_factory=list)


class NumberData(BaseModel):
    """Number detection data (elixir, tower HP)."""
    bbox: List[int]
    number: float


class CardData(BaseModel):
    """Card in hand data."""
    name: str
    ready: bool
    position: int  # 0-3 for hand positions


class ActionData(BaseModel):
    """Action taken data."""
    card: str
    tile_x: int
    tile_y: int
    score: List[float]


class RewardData(BaseModel):
    """Reward data for RL training."""
    elixir_delta: float = 0.0
    tower_dmg_dealt: float = 0.0
    tower_dmg_taken: float = 0.0
    unit_value_killed: float = 0.0
    unit_value_lost: float = 0.0
    win_bonus: float = 0.0
    loss_penalty: float = 0.0


class StepRecord(BaseModel):
    """Complete step record for dataset."""
    timestamp: str
    frame_id: int
    screen: str
    elixir: int
    ally_princess_hp: List[float]
    enemy_princess_hp: List[float]
    allies: List[UnitData]
    enemies: List[UnitData]
    hand: List[CardData]
    action: Optional[ActionData] = None
    reward: Optional[RewardData] = None

    model_config = ConfigDict(use_enum_values=True)


# For backwards compatibility with existing code
@dataclass
class RewardDataDC:
    """Dataclass version of RewardData for internal use."""
    elixir_delta: float = 0.0
    tower_dmg_dealt: float = 0.0
    tower_dmg_taken: float = 0.0
    unit_value_killed: float = 0.0
    unit_value_lost: float = 0.0
    win_bonus: float = 0.0
    loss_penalty: float = 0.0