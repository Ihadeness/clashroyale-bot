"""Dataset collector for RL training data."""

import gzip
import json
import logging
import os
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from queue import Queue, Full
from typing import Optional, Any

from clashroyale_bot.collector.schemas import StepRecord, RewardData, ActionData, UnitData, NumberData, CardData
from clashroyalebuildabot.namespaces import State, Screens

logger = logging.getLogger(__name__)


class DatasetCollector:
    """Collects step data for RL training."""

    def __init__(
        self,
        output_dir: str = "data/",
        rotate_daily: bool = True,
        max_file_mb: int = 100,
        compress: bool = True,
        buffer_size: int = 1000,
        flush_interval: float = 5.0,
        flush_count: int = 100,
    ):
        """
        Initialize dataset collector.

        Args:
            output_dir: Directory to save dataset files.
            rotate_daily: Create new file at midnight.
            max_file_mb: Max file size before rotation (MB).
            compress: Compress with gzip.
            buffer_size: Max frames to buffer in memory.
            flush_interval: Seconds between flushes.
            flush_count: Frames before forced flush.
        """
        self.output_dir = Path(output_dir)
        self.rotate_daily = rotate_daily
        self.max_file_mb = max_file_mb
        self.compress = compress
        self.buffer_size = buffer_size
        self.flush_interval = flush_interval
        self.flush_count = flush_count

        self.output_dir.mkdir(parents=True, exist_ok=True)

        self._buffer: Queue = Queue(maxsize=buffer_size)
        self._frame_id = 0
        self._current_file: Optional[Path] = None
        self._current_file_handle = None
        self._current_day = datetime.now().date()
        self._bytes_written = 0
        self._frames_since_flush = 0
        self._last_flush = time.time()
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._flush_thread = threading.Thread(target=self._flush_loop, daemon=True)
        self._flush_thread.start()

        # Open initial file
        self._rotate_file()

    def on_step_end(self, state: State, action: Any, reward: RewardData) -> None:
        """
        Called at end of each bot step to record data.

        Args:
            state: Current game state.
            action: Action taken (or None).
            reward: Computed reward.
        """
        self._frame_id += 1

        # Build step record
        record = self._build_record(state, action, reward, self._frame_id)

        # Add to buffer (non-blocking)
        try:
            self._buffer.put_nowait(record)
            self._frames_since_flush += 1
        except Full:
            logger.warning("Dataset buffer full, dropping frame %d", self._frame_id)

        # Check if we should force flush
        if self._frames_since_flush >= self.flush_count:
            self._trigger_flush()

    def _build_record(self, state: State, action: Any, reward: RewardDataDC, frame_id: int) -> StepRecord:
        """Build StepRecord from state, action, reward."""
        # Allies
        allies = [
            UnitData(
                unit=d.unit.name,
                tile_x=d.position.tile_x,
                tile_y=d.position.tile_y,
                hp=d.hp,
                bbox=list(d.position.bbox),
            )
            for d in state.allies
        ]

        # Enemies
        enemies = [
            UnitData(
                unit=d.unit.name,
                tile_x=d.position.tile_x,
                tile_y=d.position.tile_y,
                hp=d.hp,
                bbox=list(d.position.bbox),
            )
            for d in state.enemies
        ]

        # Numbers
        elixir = int(state.numbers.elixir.number) if state.numbers.elixir else 10
        ally_hp = [
            state.numbers.right_ally_princess_hp.number if state.numbers.right_ally_princess_hp else 1.0,
            state.numbers.left_ally_princess_hp.number if state.numbers.left_ally_princess_hp else 1.0,
        ]
        enemy_hp = [
            state.numbers.right_enemy_princess_hp.number if state.numbers.right_enemy_princess_hp else 1.0,
            state.numbers.left_enemy_princess_hp.number if state.numbers.left_enemy_princess_hp else 1.0,
        ]

        # Hand cards
        hand = []
        for i, card in enumerate(state.cards[1:] if len(state.cards) > 1 else []):  # Skip next card
            hand.append(CardData(
                name=card.name.lower(),
                ready=i in state.ready,
                position=i,
            ))

        # Action
        action_data = None
        if action:
            action_data = ActionData(
                card=action.CARD.name.lower(),
                tile_x=action.tile_x,
                tile_y=action.tile_y,
                score=action.calculate_score(state) if hasattr(action, 'calculate_score') else [],
            )

        # Reward (already a RewardData Pydantic model)
        return StepRecord(
            timestamp=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            frame_id=frame_id,
            screen=state.screen.value if hasattr(state.screen, 'value') else str(state.screen),
            elixir=elixir,
            ally_princess_hp=ally_hp,
            enemy_princess_hp=enemy_hp,
            allies=allies,
            enemies=enemies,
            hand=hand,
            action=action_data,
            reward=reward,
        )

    def _rotate_file(self) -> None:
        """Rotate to new file."""
        with self._lock:
            # Close current file
            if self._current_file_handle:
                try:
                    self._current_file_handle.close()
                except Exception:
                    pass
                self._current_file_handle = None

            # Create new filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            ext = ".jsonl.gz" if self.compress else ".jsonl"
            self._current_file = self.output_dir / f"data_{timestamp}{ext}"

            # Open new file
            if self.compress:
                self._current_file_handle = gzip.open(self._current_file, "wt", encoding="utf-8")
            else:
                self._current_file_handle = open(self._current_file, "w", encoding="utf-8")

            self._bytes_written = 0
            self._current_day = datetime.now().date()

            # Update latest symlink
            latest = self.output_dir / f"latest{ext}"
            try:
                if latest.exists() or latest.is_symlink():
                    latest.unlink()
                latest.symlink_to(self._current_file.name)
            except Exception:
                pass  # Symlinks may not work on all systems

            logger.info("Rotated dataset file: %s", self._current_file)

    def _trigger_flush(self) -> None:
        """Trigger immediate flush."""
        self._last_flush = time.time()
        self._frames_since_flush = 0

    def _flush_loop(self) -> None:
        """Background thread to flush buffer periodically."""
        while not self._stop_event.is_set():
            time.sleep(0.1)
            now = time.time()

            # Check for daily rotation
            if self.rotate_daily and datetime.now().date() > self._current_day:
                self._rotate_file()

            # Check for size rotation
            if self._bytes_written > self.max_file_mb * 1024 * 1024:
                self._rotate_file()

            # Periodic flush
            if now - self._last_flush >= self.flush_interval:
                self._flush_buffer()
                self._last_flush = now

    def _flush_buffer(self) -> None:
        """Flush buffer to file."""
        if self._buffer.empty():
            return

        with self._lock:
            if not self._current_file_handle:
                return

            try:
                while not self._buffer.empty():
                    record = self._buffer.get_nowait()
                    line = record.model_dump_json()
                    self._current_file_handle.write(line + "\n")
                    self._bytes_written += len(line) + 1

                self._current_file_handle.flush()
                self._frames_since_flush = 0
            except Exception as e:
                logger.error("Failed to flush dataset buffer: %s", e)
                # Re-queue items on error
                pass

    def flush(self) -> None:
        """Force flush buffer to disk."""
        self._flush_buffer()

    def close(self) -> None:
        """Close collector and flush remaining data."""
        self._stop_event.set()
        self._flush_thread.join(timeout=10)
        self._flush_buffer()

        with self._lock:
            if self._current_file_handle:
                try:
                    self._current_file_handle.close()
                except Exception:
                    pass
                self._current_file_handle = None