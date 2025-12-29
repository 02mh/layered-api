from typing import Any

from sqlalchemy import Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, DeclarativeBase


class Base(DeclarativeBase):
    pass


def to_dict(obj: Base | None) -> dict[str, Any]:
    if obj is None:
        return {}
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}


class DBCustomer(Base):
    __tablename__ = "customer"
    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(250), nullable=False)
    last_name = Column(String(250), nullable=False)
    email_address = Column(String(250), nullable=False)


class DBRoom(Base):
    __tablename__ = "room"
    id = Column(Integer, primary_key=True, autoincrement=True)
    number = Column(String(250), nullable=False)
    size = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)


class DBBooking(Base):
    __tablename__ = "booking"
    id = Column(Integer, primary_key=True, autoincrement=True)
    from_date = Column(Date, nullable=False)
    to_date = Column(Date, nullable=False)
    price = Column(Integer, nullable=False)

    customer_id = Column(Integer, ForeignKey("customer.id"))
    customer = relationship(DBCustomer)
    room_id = Column(Integer, ForeignKey("room.id"))
    room = relationship(DBRoom)
