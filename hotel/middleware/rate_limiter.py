"""
Provides rate limiting functionality to protect against abuse and DDoS attacks.
Uses slowapi with in-memory storage for development environments.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request

from hotel.config import settings


def get_identifier(request: Request) -> str:
    """
    Get the identifier for rate limiting.

    Checks whitelist first, then returns IP address.
    Whitelisted IPs bypass rate limiting.

    Args:
        request: FastAPI request object

    Returns:
        Client identifier (IP address or "whitelisted")
    """
    client_ip = get_remote_address(request)

    # Check if IP is whitelisted
    whitelist = [ip.strip() for ip in settings.rate_limit_whitelist.split(",")]
    if client_ip in whitelist:
        return "whitelisted"

    return client_ip


# Initialize the limiter with configuration
limiter = Limiter(
    key_func=get_identifier,
    storage_uri=settings.rate_limit_storage,
    enabled=settings.rate_limit_enabled,
    default_limits=[],  # No default limits, apply per-endpoint
)
