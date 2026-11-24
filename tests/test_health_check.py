"""Tests for health_check module."""

from dataclasses import is_dataclass
from unittest.mock import MagicMock, patch

import pytest


def test_health_report_is_dataclass():
    """Test that HealthReport is a dataclass with expected fields."""
    from clashroyale_bot.setup.health_check import HealthReport

    assert is_dataclass(HealthReport)
    fields = {f.name for f in HealthReport.__dataclass_fields__.values()}
    expected = {
        "adb_connected",
        "bluestacks_running",
        "onejev_reachable",
        "detector_loads",
        "directml_available",
        "fps_estimate",
    }
    assert fields == expected


def test_health_check_detects_adb(monkeypatch):
    """Test that HealthCheck.run_all() returns report with adb_connected bool."""
    from clashroyale_bot.setup.health_check import HealthCheck, HealthReport

    # Mock subprocess.run for adb check
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="emulator-5554\tdevice")

        report = HealthCheck().run_all()

        assert isinstance(report, HealthReport)
        assert hasattr(report, "adb_connected")
        assert isinstance(report.adb_connected, bool)


def test_health_check_runs_all_checks(monkeypatch):
    """Test that HealthCheck runs all checks and returns populated report."""
    from clashroyale_bot.setup.health_check import HealthCheck, HealthReport

    with patch("subprocess.run") as mock_run:
        # Mock adb devices
        mock_run.return_value = MagicMock(returncode=0, stdout="emulator-5554\tdevice")

        # Mock requests.get for OneJev
        with patch("requests.get") as mock_get:
            mock_get.return_value = MagicMock(status_code=200)

            # Mock detector loading
            with patch("clashroyalebuildabot.detectors.detector.Detector") as mock_detector:
                mock_detector_instance = MagicMock()
                mock_detector.return_value = mock_detector_instance

                report = HealthCheck().run_all()

                assert isinstance(report, HealthReport)
                assert isinstance(report.adb_connected, bool)
                assert isinstance(report.bluestacks_running, bool)
                assert isinstance(report.onejev_reachable, bool)
                assert isinstance(report.detector_loads, bool)
                assert isinstance(report.directml_available, bool)
                assert isinstance(report.fps_estimate, (int, float)) or report.fps_estimate is None