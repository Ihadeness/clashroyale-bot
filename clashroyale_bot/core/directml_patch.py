"""DirectML patch for ONNX Runtime on AMD iGPU (Ryzen 5500U Vega 7)."""

import logging
from typing import Any

logger = logging.getLogger(__name__)

# Track if patch has been applied
_patch_applied = False
_directml_available = False


def apply_directml_patch() -> bool:
    """
    Apply DirectML provider patch to OnnxDetector.

    Tries to use DmlExecutionProvider for AMD iGPU acceleration.
    Falls back to CPUExecutionProvider if DirectML not available.

    Returns:
        True if DirectML is available and patched, False if using CPU fallback.
    """
    global _patch_applied, _directml_available

    if _patch_applied:
        return _directml_available

    _patch_applied = True

    try:
        import onnxruntime as ort
    except ImportError:
        logger.warning("onnxruntime not installed, cannot apply DirectML patch")
        _directml_available = False
        _patch_onnx_detector(["CPUExecutionProvider"])
        return False

    available_providers = ort.get_available_providers()

    if "DmlExecutionProvider" in available_providers:
        # DirectML available - use it first, then CPU fallback
        providers = ["DmlExecutionProvider", "CPUExecutionProvider"]
        _directml_available = True
        logger.info("DirectML provider available, using DmlExecutionProvider for AMD iGPU acceleration")
    else:
        # DirectML not available - use CPU only
        providers = ["CPUExecutionProvider"]
        _directml_available = False
        logger.warning("DirectML provider not available, falling back to CPUExecutionProvider")

    _patch_onnx_detector(providers)
    return _directml_available


def _patch_onnx_detector(providers: list[str]) -> None:
    """
    Monkey-patch OnnxDetector to use specified providers.

    Args:
        providers: List of provider names in priority order.
    """
    try:
        from clashroyalebuildabot.detectors.onnx_detector import OnnxDetector
    except ImportError:
        logger.warning("Could not import OnnxDetector, patch not applied")
        return

    # Store patched providers on class for verification
    OnnxDetector._patched_providers = providers  # type: ignore[attr-defined]

    # Save original __init__
    original_init = OnnxDetector.__init__

    def patched_init(self: Any, model_path: str) -> None:
        # Call original but with our providers
        self.model_path = model_path
        self.sess = ort.InferenceSession(
            self.model_path,
            providers=providers,
        )
        self.output_name = self.sess.get_outputs()[0].name
        input_ = self.sess.get_inputs()[0]
        self.input_name = input_.name
        self.model_height, self.model_width = input_.shape[2:]

    # Replace __init__
    OnnxDetector.__init__ = patched_init  # type: ignore[method-assign]

    # Also patch the providers property if it exists
    if hasattr(OnnxDetector, "providers"):
        OnnxDetector.providers = providers  # type: ignore[attr-defined]


def is_directml_available() -> bool:
    """Check if DirectML is available (after patch applied)."""
    return _directml_available