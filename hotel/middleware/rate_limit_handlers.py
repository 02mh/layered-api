"""
Provides consistent error responses when rate limits are exceeded.
"""
import logging
from fastapi import Request, status
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

logger = logging.getLogger(__name__)


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """
    Handle rate limit exceeded exceptions.

    Returns a structured JSON response with:
    - HTTP 429 (Too Many Requests)
    - Rate limit details
    - Retry-After header
    - X-RateLimit headers

    Args:
        request: FastAPI request object
        exc: RateLimitExceeded exception

    Returns:
        JSON response with rate limit information
    """
    # Extract rate limit info
    path = request.url.path
    client_ip = request.client.host if request.client else "unknown"

    # Log the violation
    logger.warning(
        f"Rate limit exceeded for {client_ip} on {path}",
        extra={
            "client_ip": client_ip,
            "path": path,
            "method": request.method
        }
    )

    # Parse limit string (e.g., "100 per 1 minute")
    limit_str = str(exc.detail).replace("per", "/").replace(" ", "")

    # Create response
    response = JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "error": "Rate Limit Exceeded",
            "message": "Too many requests. Please try again later.",
            "details": {
                "limit": str(exc.detail),
                "endpoint": path,
                "retry_after": 60  # Conservative, 1 minute
            }
        }
    )

    # Add rate limit headers
    response.headers["Retry-After"] = "60"
    response.headers["X-RateLimit-Limit"] = limit_str
    response.headers["X-RateLimit-Remaining"] = "0"

    return response
