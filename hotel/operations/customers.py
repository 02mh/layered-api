from hotel.db.engine import DBSession
from hotel.db.models import DBCustomer, to_dict
from hotel.operations.models import (
    CustomerCreateData,
    CustomerResult,
    CustomerUpdateData,
)


def read_all_customers() -> list[CustomerResult]:
    with DBSession() as session:
        customers: list[DBCustomer] = session.query(DBCustomer).all()
        session.close()
        return [CustomerResult(**to_dict(c)) for c in customers]


def read_customer(customer_id: int) -> CustomerResult:
    with DBSession() as session:
        customer = session.query(DBCustomer).get(customer_id)
        result = CustomerResult(**to_dict(customer))
        session.close()
        return result


def create_customer(data: CustomerCreateData) -> CustomerResult:
    with DBSession() as session:
        customer = DBCustomer(**data.dict())
        session.add(customer)
        session.commit()
        result = CustomerResult(**to_dict(customer))
        session.close()
        return result


def update_customer(customer_id: int, data: CustomerUpdateData) -> CustomerResult:
    with DBSession() as session:
        customer = session.query(DBCustomer).get(customer_id)
        for key, value in data.dict(exclude_none=True).items():
            setattr(customer, key, value)
        session.commit()
        result = CustomerResult(**to_dict(customer))
        session.close()
        return result
