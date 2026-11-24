"""Health check for Clash Royale Bot dependencies."""

import logging
import subprocess
import time
from dataclasses import dataclass
from typing import Optional

import requests

logger = logging.getLogger(__name__)


@dataclass
class HealthReport:
    """Health check report with all dependency statuses."""

    adb_connected: bool
    bluestacks_running: bool
    onejev_reachable: bool
    detector_loads: bool
    directml_available: bool
    fps_estimate: Optional[float]


class HealthCheck:
    """Performs health checks on all bot dependencies."""

    def __init__(self, timeout: float = 5.0):
        """
        Initialize health check.

        Args:
            timeout: Timeout in seconds for each check.
        """
        self.timeout = timeout

    def run_all(self) -> HealthReport:
        """
        Run all health checks and return aggregated report.

        Returns:
            HealthReport with all check results.
        """
        logger.info("Running health checks...")

        adb_connected = self._check_adb()
        bluestacks_running = self._check_bluestacks()
        onejev_reachable = self._check_onejev()
        detector_loads = self._check_detector()
        directml_available = self._check_directml()
        fps_estimate = self._estimate_fps() if detector_loads else None

        report = HealthReport(
            adb_connected=adb_connected,
            bluestacks_running=bluestacks_running,
            onejev_reachable=onejev_reachable,
            detector_loads=detector_loads,
            directml_available=directml_available,
            fps_estimate=fps_estimate,
        )

        self._log_report(report)
        return report

    def _log_report(self, report: HealthReport) -> None:
        """Log health report summary."""
        ok = "[OK]"
        fail = "[FAIL]"
        logger.info("Health check complete:")
        logger.info("  ADB Connected:        %s", ok if report.adb_connected else fail)
        logger.info("  BlueStacks Running:   %s", ok if report.bluestacks_running else fail)
        logger.info("  OneJev Reachable:     %s", ok if report.onejev_reachable else fail)
        logger.info("  Detector Loads:       %s", ok if report.detector_loads else fail)
        logger.info("  DirectML Available:   %s", ok if report.directml_available else fail)
        logger.info("  FPS Estimate:         %s", f"{report.fps_estimate:.1f}" if report.fps_estimate else "N/A")

    def _check_adb(self) -> bool:
        """Check if ADB is connected to a device."""
        try:
            result = subprocess.run(
                ["adb", "devices"],
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
            if result.returncode != 0:
                logger.warning("ADB command failed: %s", result.stderr)
                return False

            # Parse output for connected devices
            lines = result.stdout.strip().split("\n")
            devices = [line for line in lines[1:] if line.strip() and "device" in line and "unauthorized" not in line]
            connected = len(devices) > 0

            if connected:
                logger.info("ADB connected: %d device(s)", len(devices))
            else:
                logger.warning("ADB: no authorized devices connected")

            return connected

        except subprocess.TimeoutExpired:
            logger.warning("ADB check timed out")
            return False
        except FileNotFoundError:
            logger.warning("ADB not found in PATH")
            return False
        except Exception as e:
            logger.warning("ADB check failed: %s", e)
            return False

    def _check_bluestacks(self) -> bool:
        """Check if BlueStacks is running."""
        try:
            # Check for BlueStacks processes on Windows
            result = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq BlueStacks.exe"],
                capture_output=True,
                text=True,
                encoding="cp1252",  # Windows default encoding
                errors="replace",  # Replace undecodable bytes
                timeout=self.timeout,
            )
            running = "BlueStacks.exe" in result.stdout

            if running:
                logger.info("BlueStacks is running")
            else:
                logger.warning("BlueStacks not detected")

            return running

        except Exception as e:
            logger.warning("BlueStacks check failed: %s", e)
            return False

    def _check_onejev(self) -> bool:
        """Check if OneJev screen detector server is reachable."""
        try:
            # Default OneJev URL from config
            response = requests.get(
                "http://localhost:8000",
                timeout=self.timeout,
            )
            reachable = response.status_code == 200

            if reachable:
                logger.info("OneJev server reachable at http://localhost:8000")
            else:
                logger.warning("OneJev server returned status %d", response.status_code)

            return reachable

        except requests.Timeout:
            logger.warning("OneJev server connection timed out")
            return False
        except requests.ConnectionError:
            logger.warning("OneJev server not reachable (connection refused)")
            return False
        except Exception as e:
            logger.warning("OneJev check failed: %s", e)
            return False

    def _check_detector(self) -> bool:
        """Check if detector can be loaded."""
        try:
            from clashroyalebuildabot.detectors.detector import Detector
            from clashroyalebuildabot.namespaces.cards import Cards

            # Create detector with minimal cards (just need valid deck size)
            test_cards = [Cards.ARCHERS] * 8  # 8 cards for deck
            detector = Detector(test_cards)
            detector.close()

            logger.info("Detector loads successfully")
            return True

        except Exception as e:
            logger.warning("Detector load failed: %s", e)
            return False

    def _check_directml(self) -> bool:
        """Check if DirectML is available via patched OnnxDetector."""
        try:
            from clashroyalebuildabot.detectors.onnx_detector import OnnxDetector

            # Check if patch was applied
            if hasattr(OnnxDetector, "_patched_providers"):
                providers = OnnxDetector._patched_providers  # type: ignore[attr-defined]
                return "DmlExecutionProvider" in providers

            return False

        except Exception as e:
            logger.warning("DirectML check failed: %s", e)
            return False

    def _estimate_fps(self) -> Optional[float]:
        """Estimate detector FPS by running on dummy frames."""
        try:
            import numpy as np
            from PIL import Image
            from clashroyalebuildabot.detectors.detector import Detector
            from clashroyalebuildabot.namespaces.cards import Cards

            # Create detector
            test_cards = [Cards.ARCHERS] * 8
            detector = Detector(test_cards)

            # Create dummy frames (screenshot size: 368x652)
            dummy_frames = [
                Image.fromarray(np.random.randint(0, 255, (652, 368, 3), dtype=np.uint8))
                for _ in range(10)
            ]

            # Warmup
            for frame in dummy_frames[:2]:
                detector.run(frame)

            # Benchmark
            times = []
            for frame in dummy_frames[2:]:
                start = time.perf_counter()
                detector.run(frame)
                times.append(time.perf_counter() - start)

            detector.close()

            if times:
                median_time = sorted(times)[len(times) // 2]
                fps = 1.0 / median_time
                logger.info("Estimated detector FPS: %.1f", fps)
                return fps

            return None

        except Exception as e:
            logger.warning("FPS estimation failed: %s", e)
            return None


def main() -> int:
    """Main entry point for health check CLI."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    check = HealthCheck()
    report = check.run_all()

    # Print summary
    print("\n=== Health Check Report ===")
    print(f"ADB Connected:        {'✓' if report.adb_connected else '✗'}")
    print(f"BlueStacks Running:   {'✓' if report.bluestacks_running else '✗'}")
    print(f"OneJev Reachable:     {'✓' if report.onejev_reachable else '✗'}")
    print(f"Detector Loads:       {'✓' if report.detector_loads else '✗'}")
    print(f"DirectML Available:   {'✓' if report.directml_available else '✗'}")
    print(f"FPS Estimate:         {report.fps_estimate:.1f}" if report.fps_estimate else "FPS Estimate:         N/A")

    # Return non-zero if critical checks fail
    critical = [report.adb_connected, report.detector_loads]
    return 0 if all(critical) else 1


if __name__ == "__main__":
    exit(main())