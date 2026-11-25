"""Custom exceptions. The CLI catches these and prints a friendly message."""


class ImpanoError(Exception):
    """Base class for every expected, user-facing error."""


class ValidationError(ImpanoError):
    """The user typed something invalid."""


class NotFoundError(ImpanoError):
    """The requested record does not exist."""


class PermissionDeniedError(ImpanoError):
    """The current user's role is not allowed to do this."""


class AuthenticationError(ImpanoError):
    """Wrong username or password."""
