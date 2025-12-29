from datetime import date
from typing import Optional

from pydantic import BaseModel


class CustomerCreateData(BaseModel):
    first_name: str
    last_name: str
    email_address: str


class CustomerUpdateData(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    email_address: Optional[str]


class BookingCreateData(BaseModel):
    room_id: int
    customer_id: int
    from_date: date
    to_date: date


class BookingResult(BaseModel):
    id: int
    room_id: int
    customer_id: int
    price: int
    from_date: date
    to_date: date


class CustomerResult(BaseModel):
    id: int
    first_name: str
    last_name: str
    email_address: str


class RoomResult(BaseModel):
    id: int
    number: str
    size: int
    price: int
