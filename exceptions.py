"""
Domain exceptions for the JobsFind application.
Provides a clear, structured exception hierarchy for enterprise error handling.
"""


class JobsFindError(Exception):
    """Base exception for all errors raised within JobsFind."""
    pass


class ProfileError(JobsFindError):
    """Base exception for candidate profile errors."""
    pass


class ProfileNotFoundError(ProfileError):
    """Raised when the candidate profile file cannot be found."""
    pass


class ProfileValidationError(ProfileError):
    """Raised when the candidate profile JSON is invalid or missing required fields."""
    pass


class DatabaseError(JobsFindError):
    """Raised when a database connection or query execution fails."""
    pass


class ExternalAPIError(JobsFindError):
    """Raised when an external job feed or network service request fails."""
    pass
