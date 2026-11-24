"""Bot wrapper with collector and benchmark hooks."""

import logging
import time
from typing import Any, Optional, List

from clashroyalebuildabot.bot import Bot
from clashroyalebuildabot.namespaces import State, Screens as Screen

from clashroyale_bot.collector import DatasetCollector
from clashroyale_bot.benchmark import benchmark_detector, benchmark_bot
from clashroyale_bot.collector.schemas import RewardData

logger = logging.getLogger(__name__)


class BotWrapper(Bot):
    """Extended Bot with collector and benchmark hooks."""

    def __init__(
        self,
        config: dict,
        actions: List[type],
        collector: Optional[DatasetCollector] = None,
        benchmark: Optional[Any] = None,
        **kwargs,
    ):
        """
        Initialize BotWrapper.

        Args:
            config: Configuration dict.
            actions: List of action classes.
            collector: DatasetCollector instance (optional).
            benchmark: Benchmark instance (optional).
            **kwargs: Additional arguments passed to parent Bot.
        """
        super().__init__(config, actions, **kwargs)

        self.collector = collector
        self.benchmark = benchmark
        self._prev_state: Optional[State] = None
        self._step_count = 0

    def step(self, state: State) -> Optional[State]:
        """
        Execute one bot step with hooks.

        Args:
            state: Current game state.

        Returns:
            Next state from parent step, or None.
        """
        step_start = time.perf_counter()

        # Call parent step
        next_state = super().step(state)

        # Calculate step latency
        step_latency_ms = (time.perf_counter() - step_start) * 1000

        # Record benchmark latency
        if self.benchmark and hasattr(self.benchmark, 'record_latency'):
            self.benchmark.record_latency(step_latency_ms)

        # Compute reward and collect data
        if self.collector and self._prev_state is not None:
            try:
                # Get the action that was taken (from parent's internal state)
                action = self._get_last_action()
                if action:
                    reward = self._compute_reward(self._prev_state, state, action)
                    self.collector.on_step_end(self._prev_state, action, reward)
            except Exception as e:
                logger.warning("Collector error: %s", e)

        # Update previous state
        self._prev_state = state
        self._step_count += 1

        return next_state

    def _get_last_action(self) -> Optional[Any]:
        """Get the last action taken by the bot."""
        # The parent Bot stores the last action in _last_action or similar
        # We'll try to access it from the internal state
        if hasattr(self, '_last_action'):
            return self._last_action
        if hasattr(self, 'last_action'):
            return self.last_action
        return None

    def _compute_reward(self, prev_state: State, curr_state: State, action) -> RewardData:
        """Compute reward for the transition."""
        from clashroyale_bot.collector.reward import compute_reward
        return compute_reward(prev_state, curr_state, action)

    def run_benchmark_detector(self, n_frames: int = 100, warmup: int = 20) -> dict:
        """Run detector benchmark."""
        return benchmark_detector(self.detector, n_frames=n_frames, warmup=warmup)

    def run_benchmark_bot(self, n_steps: int = 300, warmup: int = 50) -> dict:
        """Run full bot benchmark."""
        return benchmark_bot(self, n_steps=n_steps, warmup=warmup)

    def stop(self) -> None:
        """Stop bot and flush collector."""
        if self.collector:
            self.collector.flush()
        super().stop()