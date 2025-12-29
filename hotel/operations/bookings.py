from hotel.operations.interface import DataInterface
from hotel.operations.models import BookingCreateData, BookingResult


def read_all_bookings(booking_interface: DataInterface) -> list[BookingResult]:
    bookings = booking_interface.read_all()
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
        raise ValueError("Invalid dates")

    booking_dict = data.dict()
    booking_dict["price"] = room["price"] * days

    booking = booking_interface.create(booking_dict)
    return BookingResult(**booking)


def delete_booking(booking_id: int, booking_interface: DataInterface) -> BookingResult:
    booking = booking_interface.delete(booking_id)
    return BookingResult(**booking)
