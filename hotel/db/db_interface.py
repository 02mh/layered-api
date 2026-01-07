from typing import Any

from hotel.db.engine import DBSession
from hotel.db.models import Base, to_dict
from hotel.exceptions import ResourceNotFoundException

DataObject = dict[str, Any]


class DBInterface:
    def __init__(self, db_class: type[Base]):
        self.db_class = db_class

    def read_by_id(self, id: int) -> DataObject:
        session = DBSession()
        data: Base | None = session.query(self.db_class).get(id)
        session.close()

        if data is None:
            raise ResourceNotFoundException(
                resource_type=self.db_class.__name__.replace("DB", ""),
                resource_id=id
            )

        return to_dict(data)

    def read_all(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: dict[str, Any] | None = None,
        sort_by: str = "id",
        order: str = "asc",
    ) -> list[DataObject]:
        session = DBSession()
        query = session.query(self.db_class)

        # Apply filters
        if filters:
            for key, value in filters.items():
                if value is not None:
                    query = query.filter(getattr(self.db_class, key) == value)

        # Apply sorting
        sort_column = getattr(self.db_class, sort_by, None)
        if sort_column is not None:
            if order == "desc":
                query = query.order_by(sort_column.desc())
            else:
                query = query.order_by(sort_column.asc())

        # Apply pagination
        query = query.offset(skip).limit(limit)

        data: list[Base] = query.all()
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

        if item is None:
            session.close()
            raise ResourceNotFoundException(
                resource_type=self.db_class.__name__.replace("DB", ""),
                resource_id=id
            )

        for key, value in data.items():
            setattr(item, key, value)
        session.commit()
        result = to_dict(item)
        session.close()
        return result

    def delete(self, id: int) -> DataObject:
        session = DBSession()
        item: Base | None = session.query(self.db_class).get(id)

        if item is None:
            session.close()
            raise ResourceNotFoundException(
                resource_type=self.db_class.__name__.replace("DB", ""),
                resource_id=id
            )

        result = to_dict(item)
        session.delete(item)
        session.commit()
        session.close()
        return result
