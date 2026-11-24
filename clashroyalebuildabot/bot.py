"""Mock Bot class for clashroyalebuildabot."""

import logging
from typing import Any, List, Optional

from clashroyalebuildabot.namespaces import State, Action, Card, Screens as Screen

logger = logging.getLogger(__name__)


class MockDetector:
    """Mock detector for testing."""

    def run(self, frame):
        """Mock detector run."""
        from clashroyalebuildabot.namespaces import State, Screens, Numbers, NumberDetection
        return State(
            allies=[],
            enemies=[],
            numbers=Numbers(
                elixir=NumberDetection((0,0,10,10), 10.0),
                right_ally_princess_hp=NumberDetection((0,0,10,10), 1.0),
                left_ally_princess_hp=NumberDetection((0,0,10,10), 1.0),
                right_enemy_princess_hp=NumberDetection((0,0,10,10), 1.0),
                left_enemy_princess_hp=NumberDetection((0,0,10,10), 1.0),
            ),
            cards=[],
            ready=[],
            screen=Screens.IN_GAME,
        )


class Bot:
    """Mock Bot base class."""

    def __init__(
        self,
        config: dict,
        actions: List[type],
        emulator: Optional[Any] = None,
        detector: Optional[Any] = None,
        **kwargs,
    ):
        """
        Initialize Bot.

        Args:
            config: Configuration dictionary.
            actions: List of action classes.
            emulator: Emulator instance.
            detector: Detector instance.
            **kwargs: Additional keyword arguments.
        """
        self.config = config
        self.action_classes = actions
        self.emulator = emulator
        self.detector = detector or MockDetector()
        self._last_action = None
        self._running = True

        # Initialize actions with parameters from config
        self.actions = self._create_actions(actions)

    def _create_actions(self, action_classes: List[type]) -> List[Action]:
        """Create action instances with parameters from config."""
        actions = []
        action_params = self.config.get("actions", {})

        for i, action_cls in enumerate(action_classes):
            # Get action-specific config
            card_name = action_cls.CARD.name.lower()
            params = action_params.get(card_name, {})

            # Determine tile position from config
            tile_x = params.get("bridge_tiles_x", [7, 10])[0] if "bridge_tiles_x" in params else 7
            tile_y = params.get("bridge_tile_y", 13)

            # For spell actions, use default position
            if hasattr(action_cls, 'CARD') and action_cls.CARD.target_anywhere:
                tile_x = 9  # Center
                tile_y = 14  # Near bridge

            try:
                action = action_cls(index=i, tile_x=tile_x, tile_y=tile_y)
                action.bot = self  # Set bot reference
                actions.append(action)
            except TypeError:
                # Fallback: try with just bot
                try:
                    action = action_cls(self)
                    actions.append(action)
                except Exception as e:
                    logger.warning("Failed to create action %s: %s", action_cls.__name__, e)

        return actions

    def step(self, state: State) -> Optional[State]:
        """
        Execute one step of the bot loop.

        Args:
            state: Current game state.

        Returns:
            Next state or None.
        """
        # Simple implementation: just return the state
        # In reality, this would run action selection and execution
        for action in self.actions:
            if action.can_execute(state):
                self._last_action = action
                # Execute action (mock)
                action.execute(state)
                break
        return state

    def run(self) -> None:
        """Run the bot loop."""
        logger.info("Bot started")
        while self._running:
            # In real implementation, this would get state from detector/emulator
            pass

    def stop(self) -> None:
        """Stop the bot."""
        self._running = False
        logger.info("Bot stopped")