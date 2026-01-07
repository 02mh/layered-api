"""
Health check endpoints for monitoring and orchestration systems.

Provides endpoints for liveness and readiness probes used by Kubernetes,
Docker Swarm, load balancers, and monitoring systems.

Note: Health check endpoints are intentionally exempt from rate limiting
to ensure monitoring systems can always check service status.
"""
from fastapi import APIRouter, status
from sqlalchemy import text

from hotel.db.engine import DBSession

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/", status_code=status.HTTP_200_OK)
def health_check():
    """
    Basic health check endpoint.

    Returns a simple status indicating the service is running.
    Use this for liveness probes in Kubernetes.

    Returns:
        dict: Service status
    """
    return {
        "status": "healthy",
        "service": "hotel-api"
    }


@router.get("/ready", status_code=status.HTTP_200_OK)
def readiness_check():
    """
    Readiness check endpoint with database connectivity test.

    Verifies the service can connect to and query the database.
    Use this for readiness probes in Kubernetes.

    Returns:
        dict: Service readiness status with database connectivity

    Raises:
        HTTPException: 503 if database is not accessible
    """
    try:
        # Test database connectivity
        session = DBSession()
        session.execute(text("SELECT 1"))
        session.close()

        return {
            "status": "ready",
            "service": "hotel-api",
            "database": "connected"
        }
    except Exception as e:
        # Return 503 Service Unavailable if DB is down
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database not ready: {str(e)}"
        )
