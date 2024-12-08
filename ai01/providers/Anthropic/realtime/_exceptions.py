from __future__ import annotations


class ModelError(Exception):
    """Base class for exceptions in the model integration."""
    message: str

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class ModelNotConnectedError(ModelError):
    """Exception raised when the model is not connected or available."""

    def __init__(
        self,
    ):
        super().__init__(
            """
            Model is not connected or not ready. Possible fixes:
            - Call the `model.connect()` before using the model.
            - Ensure the API key and other credentials are correct.
            """
        )


class ModelAPIError(ModelError):
    """Exception raised for errors in model API calls (e.g., network issues)."""

    def __init__(
        self,
    ):
        super().__init__(
            """
            Model API encountered an error. Possible fixes:
            - Check network connectivity.
            - Verify that the Anthropic API is reachable and your credentials are correct.
            """
        )

class ModelUsageError(ModelError):
    """Exception raised for invalid usage of the model."""

    def __init__(
        self,
        reason: str = "Invalid operation or parameters when using the model."
    ):
        super().__init__(reason)
