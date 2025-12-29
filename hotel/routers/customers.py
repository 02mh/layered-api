from fastapi import APIRouter
from hotel.operations.customers import (
    create_customer,
    read_all_customers,
    read_customer,
    update_customer,
)
from hotel.operations.models import (
    CustomerCreateData,
    CustomerResult,
    CustomerUpdateData,
)

router = APIRouter()


@router.get("/customers")
def api_read_all_customers() -> list[CustomerResult]:
    return read_all_customers()


@router.get("/customer/{customer_id}")
def api_read_customer(customer_id: int) -> CustomerResult:
    return read_customer(customer_id)


@router.post("/customer")
def api_create_customer(customer: CustomerCreateData) -> CustomerResult:
    return create_customer(customer)


@router.patch("/customer/{customer_id}")
def api_update_customer(
    customer_id: int, customer: CustomerUpdateData
) -> CustomerResult:
    return update_customer(customer_id, customer)
