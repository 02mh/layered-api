"""
Provides domain-specific exceptions with proper HTTP status code mapping
for consistent error handling across all application layers.
"""
from typing import Any


class HotelAPIException(Exception):
    """
    Base exception for all errors.

    All custom exceptions should inherit from this class to enable
    centralized exception handling and monitoring.
    """

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        """
        Initialize the exception.

        Args:
            message: Human-readable error message
            details: Optional additional context about the error
        """
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ResourceNotFoundException(HotelAPIException):
    """
    Raised when a requested resource does not exist.

    Maps to HTTP 404 Not Found.
    """

    def __init__(self, resource_type: str, resource_id: int | str, details: dict[str, Any] | None = None):
        """
        Initialize the exception.

        Args:
            resource_type: Type of resource (e.g., booking, customer, room)
            resource_id: Identifier of the missing resource
            details: Optional additional context
        """
        self.resource_type = resource_type
        self.resource_id = resource_id
        message = f"{resource_type} with ID {resource_id} not found"
        super().__init__(message, details)


class BookingNotFoundException(ResourceNotFoundException):
    """Raised when a booking does not exist. Maps to HTTP 404."""

    def __init__(self, booking_id: int, details: dict[str, Any] | None = None):
        super().__init__("Booking", booking_id, details)


class CustomerNotFoundException(ResourceNotFoundException):
    """Raised when a customer does not exist. Maps to HTTP 404."""

    def __init__(self, customer_id: int, details: dict[str, Any] | None = None):
        super().__init__("Customer", customer_id, details)


class RoomNotFoundException(ResourceNotFoundException):
    """Raised when a room does not exist. Maps to HTTP 404."""

    def __init__(self, room_id: int, details: dict[str, Any] | None = None):
        super().__init__("Room", room_id, details)


class ValidationException(HotelAPIException):
    """
    Raised when business logic validation fails.

    Maps to HTTP 422 Unprocessable Entity.
    """
    pass


class InvalidDateRangeException(ValidationException):
    """
    Raised when booking date range is invalid.

    Examples:
        - Check-out date is before or equal to check-in date
        - Dates are in the past
        - Date range exceeds maximum allowed duration
    """

    def __init__(self, message: str = "Invalid date range for booking", details: dict[str, Any] | None = None):
        super().__init__(message, details)


class InvalidDataException(ValidationException):
    """
    Raised when provided data fails business logic validation.

    Examples:
        - Attempting to book an unavailable room
        - Invalid price or quantity values
        - Conflicting data relationships
    """
    pass


class DatabaseException(HotelAPIException):
    """
    Raised when database operations fail.

    Maps to HTTP 500 Internal Server Error.
    Wraps SQLAlchemy and database driver exceptions.
    """

    def __init__(self, message: str = "Database operation failed", original_exception: Exception | None = None, details: dict[str, Any] | None = None):
        """
        Initialize the exception.

        Args:
            message: Human-readable error message
            original_exception: The underlying database exception
            details: Optional additional context
        """
        self.original_exception = original_exception
        if original_exception and not details:
            details = {"original_error": str(original_exception)}
        super().__init__(message, details)


class ForeignKeyViolationException(DatabaseException):
    """
    Raised when a foreign key constraint is violated.

    Maps to HTTP 422 Unprocessable Entity.
    Ex:
        - Creating a booking with non-existent room_id or customer_id
    """

    def __init__(self, message: str = "Referenced resource does not exist", details: dict[str, Any] | None = None):
        super().__init__(message, details=details)
