from fastapi import APIRouter
from hotel.operations.models import RoomResult
from hotel.operations.rooms import read_all_rooms, read_room

router = APIRouter()


@router.get("/rooms")
def api_read_all_rooms() -> list[RoomResult]:
    return read_all_rooms()


@router.get("/room/{room_id}")
def api_read_room(room_id: int) -> RoomResult:
    return read_room(room_id)
