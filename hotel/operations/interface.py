from typing import Any, Protocol

DataObject = dict[str, Any]


class DataInterface(Protocol):
    def read_by_id(self, id: int) -> DataObject: ...

    def read_all(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: dict[str, Any] | None = None,
        sort_by: str = "id",
        order: str = "asc",
    ) -> list[DataObject]: ...

    def create(self, data: DataObject) -> DataObject: ...

    def update(self, id: int, data: DataObject) -> DataObject: ...

    def delete(self, id: int) -> DataObject: ...
