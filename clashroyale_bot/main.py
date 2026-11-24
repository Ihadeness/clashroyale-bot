"""Main entry point for Clash Royale Bot."""

import argparse
import logging
import signal
import sys
from pathlib import Path

from clashroyale_bot.core.config_loader import load_config
from clashroyale_bot.core.directml_patch import apply_directml_patch
from clashroyale_bot.core.bot_wrapper import BotWrapper
from clashroyale_bot.actions.registry import ActionRegistry
from clashroyale_bot.collector import DatasetCollector
from clashroyale_bot.setup.health_check import HealthCheck
from clashroyale_bot.utils.logging import setup_logging


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Clash Royale Bot - 2.6 Hog Cycle")
    parser.add_argument(
        "--deck",
        default="hog_26",
        help="Deck name (default: hog_26)",
    )
    parser.add_argument(
        "--bench",
        action="store_true",
        help="Run benchmark instead of bot",
    )
    parser.add_argument(
        "--bench-detector",
        action="store_true",
        help="Run detector benchmark only",
    )
    parser.add_argument(
        "--bench-bot",
        action="store_true",
        help="Run full bot benchmark only",
    )
    parser.add_argument(
        "--health-check",
        action="store_true",
        help="Run health check and exit",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Log level (default: INFO)",
    )
    return parser.parse_args()


def main() -> int:
    """Main entry point."""
    args = parse_args()

    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)

    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        logger.info("Shutdown signal received")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # Load configuration
        logger.info("Loading configuration for deck: %s", args.deck)
        config = load_config(args.deck)

        # Apply DirectML patch for AMD iGPU
        logger.info("Applying DirectML patch...")
        directml_available = apply_directml_patch()
        if directml_available:
            logger.info("DirectML enabled for AMD iGPU acceleration")
        else:
            logger.warning("DirectML not available, using CPU fallback")

        # Run health check
        logger.info("Running health check...")
        health = HealthCheck()
        report = health.run_all()

        if args.health_check:
            # Print report and exit
            ok = "[OK]"
            fail = "[FAIL]"
            print("\n=== Health Check Report ===")
            print(f"ADB Connected:        {ok if report.adb_connected else fail}")
            print(f"BlueStacks Running:   {ok if report.bluestacks_running else fail}")
            print(f"OneJev Reachable:     {ok if report.onejev_reachable else fail}")
            print(f"Detector Loads:       {ok if report.detector_loads else fail}")
            print(f"DirectML Available:   {ok if report.directml_available else fail}")
            print(f"FPS Estimate:         {report.fps_estimate:.1f}" if report.fps_estimate else "FPS Estimate:         N/A")
            return 0 if report.adb_connected and report.detector_loads else 1

        # Run benchmarks if requested
        if args.bench or args.bench_detector or args.bench_bot:
            return run_benchmarks(args, config)

        # Create collector
        collector = None
        if config.get("collector", {}).get("enabled", False):
            collector = DatasetCollector(
                output_dir=config["collector"].get("output_dir", "data/"),
                rotate_daily=config["collector"].get("rotate_daily", True),
                max_file_mb=config["collector"].get("max_file_mb", 100),
                compress=config["collector"].get("compress", True),
            )
            logger.info("Dataset collector enabled: %s", config["collector"].get("output_dir", "data/"))

        # Load actions for deck
        logger.info("Loading actions for deck: %s", args.deck)
        actions = ActionRegistry.get_actions(args.deck)

        # Create and run bot
        logger.info("Starting bot...")
        bot = BotWrapper(
            config=config,
            actions=actions,
            collector=collector,
        )

        # Run bot loop
        bot.run()

    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        return 0
    except Exception as e:
        logger.exception("Fatal error: %s", e)
        return 1
    finally:
        # Cleanup
        if 'collector' in locals() and collector:
            collector.close()

    return 0


def run_benchmarks(args: argparse.Namespace, config: dict) -> int:
    """Run benchmarks and print results."""
    import json
    from clashroyale_bot.actions.registry import ActionRegistry
    from clashroyale_bot.collector import DatasetCollector
    from clashroyale_bot.core.bot_wrapper import BotWrapper

    logger = logging.getLogger(__name__)

    # Load actions
    actions = ActionRegistry.get_actions(args.deck)

    # Create bot wrapper (without collector for benchmarks)
    bot = BotWrapper(
        config=config,
        actions=actions,
        collector=None,
    )

    results = {}

    if args.bench or args.bench_detector:
        logger.info("Running detector benchmark...")
        det_result = bot.run_benchmark_detector(n_frames=100, warmup=20)
        results["detector"] = det_result
        logger.info("Detector: p50=%.1fms p95=%.1fms p99=%.1fms FPS=%.1f",
                   det_result["p50"], det_result["p95"], det_result["p99"], det_result["mean_fps"])

    if args.bench or args.bench_bot:
        logger.info("Running bot benchmark...")
        bot_result = bot.run_benchmark_bot(n_steps=300, warmup=50)
        results["bot"] = bot_result
        logger.info("Bot: p50=%.1fms p95=%.1fms p99=%.1fms FPS=%.1f",
                   bot_result["step_latency_p50"], bot_result["step_latency_p95"],
                   bot_result["step_latency_p99"], bot_result["fps"])

    # Save results
    output_path = Path("benchmark_results.json")
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    logger.info("Benchmark results saved to %s", output_path)

    return 0


if __name__ == "__main__":
    sys.exit(main())