"""Benchmark for detector FPS."""

import time
import statistics
from typing import Dict, Any
from PIL import Image
import numpy as np


def benchmark_detector(
    detector,
    n_frames: int = 100,
    warmup: int = 20,
) -> Dict[str, float]:
    """
    Benchmark detector FPS.

    Args:
        detector: Detector instance with run(image) method.
        n_frames: Number of frames to benchmark.
        warmup: Number of warmup frames (not counted).

    Returns:
        Dict with p50, p95, p99 latency (ms) and mean FPS.
    """
    # Create dummy frames (screenshot size: 368x652)
    dummy_frames = [
        Image.fromarray(np.random.randint(0, 255, (652, 368, 3), dtype=np.uint8))
        for _ in range(n_frames + warmup)
    ]

    # Warmup
    for frame in dummy_frames[:warmup]:
        detector.run(frame)

    # Benchmark
    latencies = []
    for frame in dummy_frames[warmup:]:
        start = time.perf_counter()
        detector.run(frame)
        latencies.append((time.perf_counter() - start) * 1000)  # ms

    if not latencies:
        return {"p50": 0.0, "p95": 0.0, "p99": 0.0, "mean_fps": 0.0}

    latencies.sort()
    n = len(latencies)
    p50 = latencies[n // 2]
    p95 = latencies[int(n * 0.95)]
    p99 = latencies[int(n * 0.99)]
    mean_latency = statistics.mean(latencies)
    mean_fps = 1000.0 / mean_latency if mean_latency > 0 else 0.0

    return {
        "p50": p50,
        "p95": p95,
        "p99": p99,
        "mean_fps": mean_fps,
    }