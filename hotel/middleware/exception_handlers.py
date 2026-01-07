"""
Provides centralized exception handling to ensure consistent error responses
across all endpoints. Converts domain exceptions to appropriate HTTP responses
with proper status codes and structured error messages.
"""
import logging
from fastapi import Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from hotel.exceptions import (
    HotelAPIException,
    ResourceNotFoundException,
    ValidationException,
    DatabaseException,
    ForeignKeyViolationException,
)

# Configure logger
logger = logging.getLogger(__name__)


def register_exception_handlers(app):
    """
    Register all exception handlers with the FastAPI application.

    Args:
        app: FastAPI application instance
    """

    @app.exception_handler(ResourceNotFoundException)
    async def resource_not_found_handler(request: Request, exc: ResourceNotFoundException):
        """
        Handle ResourceNotFoundException subclasses.

        Returns HTTP 404 with structured error response.
        """
        logger.warning(
            f"Resource not found: {exc.resource_type} ID {exc.resource_id}",
            extra={"path": request.url.path, "details": exc.details}
        )
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "error": "Resource Not Found",
                "message": exc.message,
                "resource_type": exc.resource_type,
                "resource_id": exc.resource_id,
                "details": exc.details,
            },
        )

    @app.exception_handler(ValidationException)
    async def validation_exception_handler(request: Request, exc: ValidationException):
        """
        Handle ValidationException subclasses.

        Returns HTTP 422 with structured error response.
        """
        logger.warning(
            f"Validation error: {exc.message}",
            extra={"path": request.url.path, "details": exc.details}
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "Validation Error",
                "message": exc.message,
                "details": exc.details,
            },
        )

    @app.exception_handler(ForeignKeyViolationException)
    async def foreign_key_violation_handler(request: Request, exc: ForeignKeyViolationException):
        """
        Handle ForeignKeyViolationException.

        Returns HTTP 422 indicating referenced resource DNE.
        """
        logger.warning(
            f"Foreign key violation: {exc.message}",
            extra={"path": request.url.path, "details": exc.details}
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "Foreign Key Violation",
                "message": exc.message,
                "details": exc.details,
            },
        )

    @app.exception_handler(DatabaseException)
    async def database_exception_handler(request: Request, exc: DatabaseException):
        """
        Handle DatabaseException.

        Returns HTTP 500 for database errors, logging full details.
        """
        logger.error(
            f"Database error: {exc.message}",
            extra={
                "path": request.url.path,
                "details": exc.details,
                "original_exception": str(exc.original_exception) if exc.original_exception else None
            },
            exc_info=exc.original_exception
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Database Error",
                "message": "An internal database error occurred",
                # Don't expose internal details in production
                "details": {} if not exc.details else exc.details,
            },
        )

    @app.exception_handler(IntegrityError)
    async def sqlalchemy_integrity_error_handler(request: Request, exc: IntegrityError):
        """
        Handle SQLAlchemy IntegrityError (foreign key, unique constraints, etc.).

        Converts to appropriate custom exception response.
        """
        error_msg = str(exc.orig) if hasattr(exc, 'orig') else str(exc)

        # Check if it's a foreign key violation
        if "foreign key" in error_msg.lower() or "constraint" in error_msg.lower():
            logger.warning(
                f"Integrity constraint violation: {error_msg}",
                extra={"path": request.url.path}
            )
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={
                    "error": "Integrity Constraint Violation",
                    "message": "Referenced resource does not exist or constraint violated",
                    "details": {},
                },
            )

        # Generic integrity error
        logger.error(
            f"Database integrity error: {error_msg}",
            extra={"path": request.url.path},
            exc_info=exc
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Database Integrity Error",
                "message": "An internal database error occurred",
                "details": {},
            },
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
        """
        Handle generic SQLAlchemy errors.

        Catches any SQLAlchemy errors not handled by more specific handlers.
        """
        logger.error(
            f"SQLAlchemy error: {str(exc)}",
            extra={"path": request.url.path},
            exc_info=exc
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Database Error",
                "message": "An internal database error occurred",
                "details": {},
            },
        )

    @app.exception_handler(HotelAPIException)
    async def hotel_api_exception_handler(request: Request, exc: HotelAPIException):
        """
        Handle generic HotelAPIException.

        Fallback handler for custom exceptions not caught by specific handlers.
        """
        logger.error(
            f"Hotel API error: {exc.message}",
            extra={"path": request.url.path, "details": exc.details},
            exc_info=exc
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal Error",
                "message": exc.message,
                "details": exc.details,
            },
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        """
        Handle any unhandled exceptions.

        Last resort handler to prevent raw error exposure.
        """
        logger.critical(
            f"Unhandled exception: {str(exc)}",
            extra={"path": request.url.path},
            exc_info=exc
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred",
                "details": {},
            },
        )
