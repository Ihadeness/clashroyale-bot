"""Mock OnnxDetector for testing."""

class OnnxDetector:
    """Mock ONNX detector."""

    _patched_providers = ["CPUExecutionProvider"]

    def __init__(self, model_path: str):
        self.model_path = model_path
        # Use patched providers if available
        providers = getattr(self.__class__, "_patched_providers", ["CPUExecutionProvider"])
        self.providers = providers
        self.sess = None
        self.output_name = "output"
        self.input_name = "input"
        self.model_height = 352
        self.model_width = 480

    def run(self, image):
        """Mock inference."""
        return [[0.0] * 4 for _ in range(10)]