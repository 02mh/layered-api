from typing import Literal
from fastapi import APIRouter, Path, Query, Request
from hotel.db.db_interface import DBInterface
from hotel.db.models import DBBooking, DBRoom
from hotel.operations.bookings import (
    create_booking,
    delete_booking,
    read_all_bookings,
    read_booking,
)
from hotel.operations.models import BookingCreateData, BookingResult
from hotel.middleware.rate_limiter import limiter
from hotel.config import settings

router = APIRouter()


@router.get("/bookings")
@limiter.limit(settings.rate_limit_search)
def api_read_all_bookings(
    request: Request,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    customer_id: int | None = Query(None, gt=0, description="Filter by customer ID"),
    room_id: int | None = Query(None, gt=0, description="Filter by room ID"),
    sort_by: Literal["id", "check_in", "check_out"] = Query(
        "id", description="Field to sort by"
    ),
    order: Literal["asc", "desc"] = Query("asc", description="Sort order"),
) -> list[BookingResult]:
    booking_interface = DBInterface(DBBooking)
    return read_all_bookings(
        booking_interface,
        skip=skip,
        limit=limit,
        customer_id=customer_id,
        room_id=room_id,
        sort_by=sort_by,
        order=order,
    )


@router.get("/booking/{booking_id}")
@limiter.limit(settings.rate_limit_read)
def api_read_booking(
    request: Request,
    booking_id: int = Path(..., gt=0, description="Booking ID must be positive")
) -> BookingResult:
    booking_interface = DBInterface(DBBooking)
    return read_booking(booking_id, booking_interface)


@router.post("/booking")
@limiter.limit(settings.rate_limit_write)
def api_create_booking(request: Request, data: BookingCreateData):
    room_interface = DBInterface(DBRoom)
    booking_interface = DBInterface(DBBooking)
    return create_booking(data, room_interface, booking_interface)


@router.delete("/booking/{booking_id}")
@limiter.limit(settings.rate_limit_delete)
def api_delete_booking(
    request: Request,
    booking_id: int = Path(..., gt=0, description="Booking ID must be positive")
) -> BookingResult:
    booking_interface = DBInterface(DBBooking)
    return delete_booking(booking_id, booking_interface)
