"""Benchmark report generation with HTML output."""

import argparse
import base64
import io
import json
import sys
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt


def generate_report(results: dict[str, Any], output_path: Path) -> Path:
    """
    Generate an HTML benchmark report with embedded charts.

    Args:
        results: Dictionary with 'detector' and 'bot' benchmark results.
        output_path: Path to write the HTML report.

    Returns:
        Path to the generated HTML file.
    """
    # Create charts
    detector_chart_b64 = _create_detector_chart(results.get("detector", {}))
    bot_chart_b64 = _create_bot_chart(results.get("bot", {}))

    # Generate HTML
    html = _generate_html(results, detector_chart_b64, bot_chart_b64)

    output_path.write_text(html, encoding="utf-8")
    return output_path


def _create_detector_chart(detector_results: dict[str, float]) -> str:
    """Create detector benchmark chart and return as base64 PNG."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

    # Latency percentiles
    latencies = ["p50", "p95", "p99"]
    latency_values = [detector_results.get(k, 0) for k in latencies]

    ax1.bar(latencies, latency_values, color=["#4CAF50", "#FF9800", "#F44336"])
    ax1.set_title("Detector Latency Percentiles (ms)")
    ax1.set_ylabel("Latency (ms)")
    ax1.grid(axis="y", alpha=0.3)

    # FPS
    mean_fps = detector_results.get("mean_fps", 0)
    ax2.bar(["Mean FPS"], [mean_fps], color="#2196F3")
    ax2.set_title("Detector Throughput")
    ax2.set_ylabel("FPS")
    ax2.grid(axis="y", alpha=0.3)

    plt.tight_layout()

    # Save to base64
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=100, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)

    return base64.b64encode(buf.read()).decode("utf-8")


def _create_bot_chart(bot_results: dict[str, float]) -> str:
    """Create bot benchmark chart and return as base64 PNG."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

    # Step latency percentiles
    latencies = ["step_latency_p50", "step_latency_p95", "step_latency_p99"]
    latency_values = [bot_results.get(k, 0) for k in latencies]

    ax1.bar(latencies, latency_values, color=["#4CAF50", "#FF9800", "#F44336"])
    ax1.set_title("Bot Step Latency Percentiles (ms)")
    ax1.set_ylabel("Latency (ms)")
    ax1.grid(axis="y", alpha=0.3)

    # Bot FPS
    fps = bot_results.get("fps", 0)
    ax2.bar(["Bot FPS"], [fps], color="#2196F3")
    ax2.set_title("Bot Loop Throughput")
    ax2.set_ylabel("FPS")
    ax2.grid(axis="y", alpha=0.3)

    plt.tight_layout()

    # Save to base64
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=100, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)

    return base64.b64encode(buf.read()).decode("utf-8")


def _generate_html(results: dict[str, Any], detector_chart_b64: str, bot_chart_b64: str) -> str:
    """Generate HTML report with embedded charts."""
    detector = results.get("detector", {})
    bot = results.get("bot", {})

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Clash Royale Bot - Benchmark Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        h1 {{
            color: #333;
            border-bottom: 2px solid #2196F3;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #555;
            margin-top: 30px;
        }}
        .section {{
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        .metric-card {{
            background: #f8f9fa;
            border-radius: 6px;
            padding: 15px;
            text-align: center;
            border-left: 4px solid #2196F3;
        }}
        .metric-label {{
            font-size: 0.9em;
            color: #666;
            margin-bottom: 5px;
        }}
        .metric-value {{
            font-size: 1.5em;
            font-weight: bold;
            color: #333;
        }}
        .chart-container {{
            text-align: center;
            margin: 20px 0;
        }}
        .chart-container img {{
            max-width: 100%;
            height: auto;
            border-radius: 4px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .warning {{
            background: #fff3e0;
            border-left: 4px solid #FF9800;
            padding: 15px;
            border-radius: 4px;
            margin: 20px 0;
        }}
        .good {{
            background: #e8f5e9;
            border-left: 4px solid #4CAF50;
            padding: 15px;
            border-radius: 4px;
            margin: 20px 0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }}
        th, td {{
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }}
        th {{
            background: #f5f5f5;
            font-weight: 600;
        }}
    </style>
</head>
<body>
    <h1>Clash Royale Bot - Benchmark Report</h1>

    <div class="section">
        <h2>Detector Benchmark</h2>
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">p50 Latency</div>
                <div class="metric-value">{detector.get("p50", 0):.1f} ms</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">p95 Latency</div>
                <div class="metric-value">{detector.get("p95", 0):.1f} ms</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">p99 Latency</div>
                <div class="metric-value">{detector.get("p99", 0):.1f} ms</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Mean FPS</div>
                <div class="metric-value">{detector.get("mean_fps", 0):.1f}</div>
            </div>
        </div>
        <div class="chart-container">
            <img src="data:image/png;base64,{detector_chart_b64}" alt="Detector Benchmark Chart">
        </div>
        {_detector_assessment(detector)}
    </div>

    <div class="section">
        <h2>Bot Benchmark</h2>
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">Step Latency p50</div>
                <div class="metric-value">{bot.get("step_latency_p50", 0):.1f} ms</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Step Latency p95</div>
                <div class="metric-value">{bot.get("step_latency_p95", 0):.1f} ms</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Step Latency p99</div>
                <div class="metric-value">{bot.get("step_latency_p99", 0):.1f} ms</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Bot FPS</div>
                <div class="metric-value">{bot.get("fps", 0):.1f}</div>
            </div>
        </div>
        <div class="chart-container">
            <img src="data:image/png;base64,{bot_chart_b64}" alt="Bot Benchmark Chart">
        </div>
        {_bot_assessment(bot)}
    </div>
</body>
</html>"""

    return html


def _detector_assessment(detector: dict[str, float]) -> str:
    """Generate assessment for detector results."""
    mean_fps = detector.get("mean_fps", 0)
    p99 = detector.get("p99", 0)

    if mean_fps >= 30 and p99 <= 50:
        return '<div class="good"><strong>✓ Good:</strong> Detector meets real-time requirements (FPS > 30, p99 < 50ms).</div>'
    elif mean_fps >= 15:
        return '<div class="warning"><strong>⚠ Acceptable:</strong> Detector runs but may struggle with fast gameplay. Consider optimization.</div>'
    else:
        return '<div class="warning"><strong>⚠ Slow:</strong> Detector FPS below 15. Check DirectML configuration and model size.</div>'


def _bot_assessment(bot: dict[str, float]) -> str:
    """Generate assessment for bot results."""
    fps = bot.get("fps", 0)
    p99 = bot.get("step_latency_p99", 0)

    if fps >= 10 and p99 <= 300:
        return '<div class="good"><strong>✓ Good:</strong> Bot loop meets latency budget (< 500ms p99).</div>'
    elif fps >= 5:
        return '<div class="warning"><strong>⚠ Acceptable:</strong> Bot loop runs but close to latency budget.</div>'
    else:
        return '<div class="warning"><strong>⚠ Slow:</strong> Bot loop exceeds 500ms p99. Check action scoring and emulator latency.</div>'


def main() -> int:
    """Main entry point for benchmark report CLI."""
    parser = argparse.ArgumentParser(description="Generate HTML benchmark report")
    parser.add_argument("--results", type=Path, required=True, help="Path to JSON file with benchmark results")
    parser.add_argument("-o", "--output", type=Path, default=Path("benchmark_report.html"), help="Output HTML file path")
    args = parser.parse_args()

    if not args.results.exists():
        print(f"Error: Results file not found: {args.results}", file=sys.stderr)
        return 1

    try:
        with open(args.results) as f:
            results = json.load(f)
    except Exception as e:
        print(f"Error reading results file: {e}", file=sys.stderr)
        return 1

    try:
        generate_report(results, args.output)
        print(f"Report generated: {args.output}")
    except Exception as e:
        print(f"Error generating report: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())