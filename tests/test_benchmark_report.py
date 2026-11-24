"""Tests for benchmark report module."""

import tempfile
from pathlib import Path

import pytest

from clashroyale_bot.benchmark.report import generate_report


def test_benchmark_report_generates_html(tmp_path):
    """Test that generate_report creates an HTML file with expected content."""
    results = {
        "detector": {
            "p50": 30.5,
            "p95": 45.2,
            "p99": 60.8,
            "mean_fps": 33.1,
        },
        "bot": {
            "step_latency_p50": 120.5,
            "step_latency_p95": 180.3,
            "step_latency_p99": 250.7,
            "fps": 8.3,
        },
    }

    output_path = tmp_path / "report.html"
    html_path = generate_report(results, output_path)

    assert html_path.exists()
    assert html_path == output_path

    content = html_path.read_text(encoding="utf-8")
    assert "<html" in content
    assert "</html>" in content
    assert "Detector Benchmark" in content
    assert "Bot Benchmark" in content
    assert "30.5" in content  # detector p50
    assert "120.5" in content  # bot step_latency_p50


def test_benchmark_report_includes_charts(tmp_path):
    """Test that the HTML report includes embedded chart images."""
    results = {
        "detector": {
            "p50": 30.0,
            "p95": 45.0,
            "p99": 60.0,
            "mean_fps": 33.0,
        },
        "bot": {
            "step_latency_p50": 100.0,
            "step_latency_p95": 150.0,
            "step_latency_p99": 200.0,
            "fps": 10.0,
        },
    }

    output_path = tmp_path / "report.html"
    generate_report(results, output_path)

    content = output_path.read_text(encoding="utf-8")
    # Should have base64 encoded PNG images
    assert "data:image/png;base64," in content


def test_benchmark_report_handles_missing_keys(tmp_path):
    """Test that generate_report handles partial results gracefully."""
    results = {
        "detector": {
            "p50": 30.0,
        },
        "bot": {},
    }

    output_path = tmp_path / "report.html"
    generate_report(results, output_path)

    content = output_path.read_text(encoding="utf-8")
    assert "<html" in content
    assert "30.0" in content