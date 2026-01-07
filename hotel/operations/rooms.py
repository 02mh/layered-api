from hotel.db.engine import DBSession
from hotel.db.models import DBRoom, to_dict
from hotel.operations.models import RoomResult
from hotel.exceptions import RoomNotFoundException


def read_all_rooms(
    skip: int = 0,
    limit: int = 100,
    available: bool | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    sort_by: str = "id",
    order: str = "asc",
) -> list[RoomResult]:
    session = DBSession()
    query = session.query(DBRoom)

    # Apply filters
    if available is not None:
        query = query.filter(DBRoom.available == available)
    if min_price is not None:
        query = query.filter(DBRoom.price >= min_price)
    if max_price is not None:
        query = query.filter(DBRoom.price <= max_price)

    # Apply sorting
    sort_column = getattr(DBRoom, sort_by, None)
    if sort_column is not None:
        if order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

    # Apply pagination
    query = query.offset(skip).limit(limit)

    rooms: list[DBRoom] = query.all()
    session.close()
    return [RoomResult(**to_dict(r)) for r in rooms]


def read_room(room_id: int) -> RoomResult:
    session = DBSession()
    room: DBRoom = session.query(DBRoom).get(room_id)

    if room is None:
        session.close()
        raise RoomNotFoundException(room_id)

    result = RoomResult(**to_dict(room))
    session.close()
    return result
