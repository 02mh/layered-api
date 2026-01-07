from typing import Literal
from fastapi import APIRouter, Path, Query, Request
from hotel.operations.models import RoomResult
from hotel.operations.rooms import read_all_rooms, read_room
from hotel.middleware.rate_limiter import limiter
from hotel.config import settings

router = APIRouter()


@router.get("/rooms")
@limiter.limit(settings.rate_limit_search)
def api_read_all_rooms(
    request: Request,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    available: bool | None = Query(None, description="Filter by availability"),
    min_price: float | None = Query(None, ge=0, description="Minimum price filter"),
    max_price: float | None = Query(None, ge=0, description="Maximum price filter"),
    sort_by: Literal["id", "price", "room_number"] = Query(
        "id", description="Field to sort by"
    ),
    order: Literal["asc", "desc"] = Query("asc", description="Sort order"),
) -> list[RoomResult]:
    return read_all_rooms(
        skip=skip,
        limit=limit,
        available=available,
        min_price=min_price,
        max_price=max_price,
        sort_by=sort_by,
        order=order,
    )


@router.get("/room/{room_id}")
@limiter.limit(settings.rate_limit_read)
def api_read_room(
    request: Request,
    room_id: int = Path(..., gt=0, description="Room ID must be positive")
) -> RoomResult:
    return read_room(room_id)
