"""Tests for directml_patch module."""

import sys
from unittest.mock import MagicMock, patch


def test_directml_patch_sets_providers(monkeypatch):
    """Test that apply_directml_patch sets providers when DmlExecutionProvider is available."""
    # Mock onnxruntime to have DmlExecutionProvider
    mock_ort = MagicMock()
    mock_ort.get_available_providers.return_value = [
        "CPUExecutionProvider",
        "DmlExecutionProvider",
        "CUDAExecutionProvider",
    ]
    monkeypatch.setitem(sys.modules, "onnxruntime", mock_ort)

    # Import and apply patch
    from clashroyale_bot.core.directml_patch import apply_directml_patch

    result = apply_directml_patch()

    # Should return True when DirectML is available
    assert result is True

    # Verify OnnxDetector was patched
    from clashroyalebuildabot.detectors.onnx_detector import OnnxDetector

    assert hasattr(OnnxDetector, "_patched_providers")
    assert OnnxDetector._patched_providers == [
        "DmlExecutionProvider",
        "CPUExecutionProvider",
    ]


def test_directml_patch_fallback_cpu(monkeypatch):
    """Test that apply_directml_patch returns False and uses CPU when DirectML not available."""
    # Mock onnxruntime without DmlExecutionProvider
    mock_ort = MagicMock()
    mock_ort.get_available_providers.return_value = [
        "CPUExecutionProvider",
        "CUDAExecutionProvider",
    ]
    monkeypatch.setitem(sys.modules, "onnxruntime", mock_ort)

    # Need to reimport to test fresh
    if "clashroyale_bot.core.directml_patch" in sys.modules:
        del sys.modules["clashroyale_bot.core.directml_patch"]
    if "clashroyalebuildabot.detectors.onnx_detector" in sys.modules:
        del sys.modules["clashroyalebuildabot.detectors.onnx_detector"]

    from clashroyale_bot.core.directml_patch import apply_directml_patch

    result = apply_directml_patch()

    # Should return False when DirectML not available
    assert result is False

    # Verify OnnxDetector was patched with CPU only
    from clashroyalebuildabot.detectors.onnx_detector import OnnxDetector

    assert hasattr(OnnxDetector, "_patched_providers")
    assert OnnxDetector._patched_providers == ["CPUExecutionProvider"]


def test_directml_patch_onnxruntime_not_installed(monkeypatch):
    """Test that apply_directml_patch handles missing onnxruntime gracefully."""
    # Remove onnxruntime from modules
    monkeypatch.delitem(sys.modules, "onnxruntime", raising=False)

    if "clashroyale_bot.core.directml_patch" in sys.modules:
        del sys.modules["clashroyale_bot.core.directml_patch"]
    if "clashroyalebuildabot.detectors.onnx_detector" in sys.modules:
        del sys.modules["clashroyalebuildabot.detectors.onnx_detector"]

    from clashroyale_bot.core.directml_patch import apply_directml_patch

    result = apply_directml_patch()

    # Should return False when onnxruntime not installed
    assert result is False