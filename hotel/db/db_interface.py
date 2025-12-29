from typing import Any

from hotel.db.engine import DBSession
from hotel.db.models import Base, to_dict

DataObject = dict[str, Any]


class DBInterface:
    def __init__(self, db_class: type[Base]):
        self.db_class = db_class

    def read_by_id(self, id: int) -> DataObject:
        session = DBSession()
        data: Base | None = session.query(self.db_class).get(id)
        session.close()
        return to_dict(data)

    def read_all(self) -> list[DataObject]:
        session = DBSession()
        data: list[Base] = session.query(self.db_class).all()
        session.close()
        return [to_dict(item) for item in data]

    def create(self, data: DataObject) -> DataObject:
        session = DBSession()
        item: Base = self.db_class(**data)
        session.add(item)
        session.commit()
        result = to_dict(item)
        session.close()
        return result

    def update(self, id: int, data: DataObject) -> DataObject:
        session = DBSession()
        item: Base | None = session.query(self.db_class).get(id)
        for key, value in data.items():
            setattr(item, key, value)
        session.commit()
        session.close()
        return to_dict(item)

    def delete(self, id: int) -> DataObject:
        session = DBSession()
        item: Base | None = session.query(self.db_class).get(id)
        result = to_dict(item)
        session.delete(item)
        session.commit()
        session.close()
        return result
