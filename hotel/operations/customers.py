from hotel.db.engine import DBSession
from hotel.db.models import DBCustomer, to_dict
from hotel.operations.models import (
    CustomerCreateData,
    CustomerResult,
    CustomerUpdateData,
)
from hotel.exceptions import CustomerNotFoundException


def read_all_customers(
    skip: int = 0,
    limit: int = 100,
    name: str | None = None,
    email: str | None = None,
    sort_by: str = "id",
    order: str = "asc",
) -> list[CustomerResult]:
    with DBSession() as session:
        query = session.query(DBCustomer)

        # Apply filters
        if name is not None:
            query = query.filter(DBCustomer.first_name.ilike(f"%{name}%"))
        if email is not None:
            query = query.filter(DBCustomer.email_address.ilike(f"%{email}%"))

        # Apply sorting
        sort_column = getattr(DBCustomer, sort_by, None)
        if sort_column is not None:
            if order == "desc":
                query = query.order_by(sort_column.desc())
            else:
                query = query.order_by(sort_column.asc())

        # Apply pagination
        query = query.offset(skip).limit(limit)

        customers: list[DBCustomer] = query.all()
        session.close()
        return [CustomerResult(**to_dict(c)) for c in customers]


def read_customer(customer_id: int) -> CustomerResult:
    with DBSession() as session:
        customer = session.query(DBCustomer).get(customer_id)

        if customer is None:
            session.close()
            raise CustomerNotFoundException(customer_id)

        result = CustomerResult(**to_dict(customer))
        session.close()
        return result


def create_customer(data: CustomerCreateData) -> CustomerResult:
    with DBSession() as session:
        customer = DBCustomer(**data.model_dump()) # Replaced dict with model_dump, since dict deprecated
        session.add(customer)
        session.commit()
        result = CustomerResult(**to_dict(customer))
        session.close()
        return result


def update_customer(customer_id: int, data: CustomerUpdateData) -> CustomerResult:
    with DBSession() as session:
        customer = session.query(DBCustomer).get(customer_id)

        if customer is None:
            session.close()
            raise CustomerNotFoundException(customer_id)

        for key, value in data.model_dump(exclude_none=True).items(): # Replaced dict with model_dump, since dict deprecated
            setattr(customer, key, value)
        session.commit()
        result = CustomerResult(**to_dict(customer))
        session.close()
        return result
