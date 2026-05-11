from typing import Any


class OutputFormatError(Exception):
    """Raise if output format does not match expected format."""

    def __init__(self, value: Any) -> None:  # noqa: ANN401
        """Initialize error."""
        self.message = f"Unsupported type returned: {type(value)}.\nReturned value: {value}"

        super().__init__(self.message)


class MissingPlanError(Exception):
    """Raise if Plan in State has not been set yet."""

    def __init__(self) -> None:
        """Initialize error."""
        self.message = "No plan has been set yet."

        super().__init__(self.message)
