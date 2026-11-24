"""Benchmark for full bot loop latency."""

import time
import statistics
from typing import Dict, Any


def benchmark_bot(
    wrapper,
    n_steps: int = 300,
    warmup: int = 50,
) -> Dict[str, float]:
    """
    Benchmark full bot loop latency.

    Args:
        wrapper: BotWrapper instance with step(state) method.
        n_steps: Number of steps to benchmark.
        warmup: Number of warmup steps (not counted).

    Returns:
        Dict with step_latency p50, p95, p99 (ms) and FPS.
    """
    from clashroyalebuildabot.namespaces import State, Screens, Numbers, NumberDetection

    # Create initial state
    initial_state = State(
        allies=[],
        enemies=[],
        numbers=Numbers(
            elixir=NumberDetection((0, 0, 10, 10), 10.0),
            right_ally_princess_hp=NumberDetection((0, 0, 10, 10), 1.0),
            left_ally_princess_hp=NumberDetection((0, 0, 10, 10), 1.0),
            right_enemy_princess_hp=NumberDetection((0, 0, 10, 10), 1.0),
            left_enemy_princess_hp=NumberDetection((0, 0, 10, 10), 1.0),
        ),
        cards=[],
        ready=[],
        screen=Screens.IN_GAME,
    )

    # Warmup
    state = initial_state
    for _ in range(warmup):
        result = wrapper.step(state)
        if result is not None:
            state = result

    # Benchmark
    latencies = []
    state = initial_state
    for _ in range(n_steps):
        start = time.perf_counter()
        result = wrapper.step(state)
        latencies.append((time.perf_counter() - start) * 1000)  # ms
        if result is not None:
            state = result

    if not latencies:
        return {
            "step_latency_p50": 0.0,
            "step_latency_p95": 0.0,
            "step_latency_p99": 0.0,
            "fps": 0.0,
        }

    latencies.sort()
    n = len(latencies)
    p50 = latencies[n // 2]
    p95 = latencies[int(n * 0.95)]
    p99 = latencies[int(n * 0.99)]
    mean_latency = statistics.mean(latencies)
    fps = 1000.0 / mean_latency if mean_latency > 0 else 0.0

    return {
        "step_latency_p50": p50,
        "step_latency_p95": p95,
        "step_latency_p99": p99,
        "fps": fps,
    }