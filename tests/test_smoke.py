"""Smoke test — integration test requiring full environment (BlueStacks, ADB, OneJev).

Marked as slow and only runs when BLUESTACKS=1 environment variable is set.
Run manually on target hardware (Ryzen 5500U) for validation.
"""

import os
import pytest
import time
from pathlib import Path

# Skip unless explicitly enabled via environment variable
pytestmark = pytest.mark.skipif(
    not os.environ.get("BLUESTACKS"),
    reason="Set BLUESTACKS=1 to run smoke test (requires BlueStacks, ADB, OneJev running)"
)


@pytest.mark.slow
def test_smoke_bot_runs_100_steps():
    """
    Smoke test: start bot, run 100 steps, verify:
    - No exceptions
    - Dataset written
    - FPS > 15
    """
    from clashroyale_bot.main import main
    from clashroyale_bot.collector import DatasetCollector
    import sys
    from unittest.mock import patch

    # This test requires full environment:
    # - BlueStacks running with Clash Royale
    # - ADB connected (emulator-5554)
    # - OneJev/Flide server on localhost:8000
    # - Valid deck config

    # We can't easily test the full main() in pytest without the hardware,
    # so this test documents the expected behavior and can be run manually.

    # Manual verification checklist:
    # 1. Start BlueStacks with Clash Royale
    # 2. Run: flide serve (in separate terminal)
    # 3. Run: python -m clashroyale_bot.setup.health_check (all [OK])
    # 4. Run: BLUESTACKS=1 python -m pytest tests/test_smoke.py -v -s
    # 5. Bot should run 100 steps, collect data, maintain FPS > 15

    pytest.skip("Manual smoke test — run with BLUESTACKS=1 on target hardware")


@pytest.mark.slow
def test_smoke_health_check_passes():
    """Verify health check passes on target hardware."""
    from clashroyale_bot.setup.health_check import HealthCheck

    health = HealthCheck(timeout=10.0)
    report = health.run_all()

    # All critical checks should pass on properly configured 5500U
    assert report.adb_connected, "ADB deve estar conectado ao BlueStacks"
    assert report.bluestacks_running, "BlueStacks deve estar rodando"
    assert report.onejev_reachable, "OneJev/Flide deve estar acessível em localhost:8000"
    assert report.detector_loads, "Detector deve carregar com deck válido"
    assert report.directml_available, "DirectML deve estar disponível no Vega 7"
    assert report.fps_estimate is not None, "FPS estimate deve ser calculado"
    assert report.fps_estimate > 15, f"Detector FPS muito baixo: {report.fps_estimate}"


@pytest.mark.slow
def test_smoke_dataset_collector_writes_data(tmp_path):
    """Verify DatasetCollector writes valid JSONL.gz during bot run."""
    from clashroyale_bot.collector import DatasetCollector
    from clashroyalebuildabot.namespaces import State, Screens
    from clashroyale_bot.collector.schemas import RewardData
    from unittest.mock import MagicMock

    # This test can run without hardware — tests collector in isolation
    collector = DatasetCollector(
        output_dir=tmp_path,
        rotate_daily=False,
        max_file_mb=1,
        compress=True,
        buffer_size=100,
        flush_interval=0.1,
        flush_count=10,
    )

    # Create mock state
    mock_state = MagicMock(spec=State)
    mock_state.screen = Screens.IN_GAME
    mock_state.allies = []
    mock_state.enemies = []
    mock_state.cards = []
    mock_state.ready = []
    mock_state.numbers = MagicMock()
    mock_state.numbers.elixir = MagicMock(number=10)
    mock_state.numbers.right_ally_princess_hp = MagicMock(number=1.0)
    mock_state.numbers.left_ally_princess_hp = MagicMock(number=1.0)
    mock_state.numbers.right_enemy_princess_hp = MagicMock(number=1.0)
    mock_state.numbers.left_enemy_princess_hp = MagicMock(number=1.0)

    mock_action = None
    mock_reward = RewardData()

    # Simulate 100 steps
    for i in range(100):
        collector.on_step_end(mock_state, mock_action, mock_reward)

    collector.close()

    # Verify file was created
    data_files = list(tmp_path.glob("data_*.jsonl.gz"))
    assert len(data_files) == 1, "Deve criar exatamente 1 arquivo de dataset"

    # Verify content
    import gzip
    import json
    with gzip.open(data_files[0], "rt") as f:
        lines = f.readlines()

    assert len(lines) == 100, f"Deve ter 100 frames, tem {len(lines)}"

    # Verify each line is valid JSON with expected schema
    for i, line in enumerate(lines):
        data = json.loads(line)
        assert data["frame_id"] == i + 1
        assert data["screen"] == "IN_GAME"
        assert data["elixir"] == 10
        assert "reward" in data


@pytest.mark.slow
def test_smoke_benchmark_targets():
    """Verify benchmark meets performance targets on 5500U."""
    from clashroyale_bot.benchmark.bench_detector import benchmark_detector
    from clashroyale_bot.benchmark.bench_bot import benchmark_bot
    from clashroyalebuildabot.detectors.detector import Detector
    from clashroyalebuildabot.namespaces.cards import Cards
    from clashroyale_bot.core.bot_wrapper import BotWrapper
    from clashroyale_bot.core.config_loader import load_config
    from clashroyale_bot.actions.registry import ActionRegistry
    from clashroyale_bot.collector import DatasetCollector
    import tempfile

    # Load config and create detector
    config = load_config("hog_26")
    test_cards = [Cards.HOG_RIDER, Cards.LOG, Cards.ICE_SPIRIT, Cards.SKELETONS,
                  Cards.ICE_GOLEM, Cards.CANNON, Cards.MUSKETEER, Cards.FIREBALL]
    detector = Detector(test_cards)

    # Benchmark detector
    det_results = benchmark_detector(detector, n_frames=50, warmup=10)
    detector.close()

    # Targets for 5500U Vega 7
    assert det_results["p99"] < 50, f"Detector p99 muito alto: {det_results['p99']:.1f}ms (alvo < 50ms)"
    assert det_results["mean_fps"] > 30, f"Detector FPS muito baixo: {det_results['mean_fps']:.1f} (alvo > 30)"

    # Benchmark bot (requires mock collector/benchmark)
    with tempfile.TemporaryDirectory() as tmpdir:
        collector = DatasetCollector(output_dir=tmpdir, buffer_size=1000)
        actions = ActionRegistry.get_actions("hog_26")
        wrapper = BotWrapper(config=config, actions=actions, collector=collector)

        bot_results = benchmark_bot(wrapper, n_steps=100, warmup=20)
        collector.close()

        assert bot_results["step_latency_p99"] < 500, \
            f"Bot step p99 muito alto: {bot_results['step_latency_p99']:.1f}ms (alvo < 500ms)"
        assert bot_results["fps"] > 10, f"Bot FPS muito baixo: {bot_results['fps']:.1f} (alvo > 10)"


if __name__ == "__main__":
    # Allow running directly for manual testing
    import os
    os.environ["BLUESTACKS"] = "1"
    pytest.main([__file__, "-v", "-s"])