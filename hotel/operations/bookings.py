
from hotel.operations.interface import DataInterface
from hotel.operations.models import BookingCreateData, BookingResult
from hotel.exceptions import InvalidDateRangeException


def read_all_bookings(
    booking_interface: DataInterface,
    skip: int = 0,
    limit: int = 100,
    customer_id: int | None = None,
    room_id: int | None = None,
    sort_by: str = "id",
    order: str = "asc",
) -> list[BookingResult]:
    bookings = booking_interface.read_all(
        skip=skip,
        limit=limit,
        filters={"customer_id": customer_id, "room_id": room_id},
        sort_by=sort_by,
        order=order,
    )
    return [BookingResult(**b) for b in bookings]


def read_booking(booking_id: int, booking_interface: DataInterface) -> BookingResult:
    booking = booking_interface.read_by_id(booking_id)
    return BookingResult(**booking)


def create_booking(
    data: BookingCreateData,
    room_interface: DataInterface,
    booking_interface: DataInterface,
) -> BookingResult:
    # retrieve the room
    room = room_interface.read_by_id(data.room_id)

    days = (data.to_date - data.from_date).days
    if days <= 0:
        raise InvalidDateRangeException(
            message="Check-out date must be after check-in date",
            details={
                "check_in": str(data.from_date),
                "check_out": str(data.to_date),
                "days": days
            }
        )

    booking_dict = data.model_dump() # Replaced dict with model_dump, since dict deprecated
    booking_dict["price"] = room["price"] * days

    booking = booking_interface.create(booking_dict)
    return BookingResult(**booking)


def delete_booking(booking_id: int, booking_interface: DataInterface) -> BookingResult:
    booking = booking_interface.delete(booking_id)
    return BookingResult(**booking)
