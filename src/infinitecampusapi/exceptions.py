"""Exceptions raised by the Infinite Campus API client."""


class InfiniteCampusError(Exception):
    """Base exception for all client errors."""


class TransportError(InfiniteCampusError):
    """Raised when an HTTP request cannot be completed."""


class APIError(InfiniteCampusError):
    """Raised when the API returns an unsuccessful HTTP response."""

    def __init__(self, message: str, *, status_code: int, endpoint: str):
        super().__init__(message)
        self.status_code = status_code
        self.endpoint = endpoint


class AuthenticationError(APIError):
    """Raised when authentication fails."""


class ResponseDecodeError(InfiniteCampusError):
    """Raised when an API response is not valid JSON."""
