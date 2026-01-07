from typing import Literal
from fastapi import APIRouter, Path, Query, Request
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
from hotel.middleware.rate_limiter import limiter
from hotel.config import settings

router = APIRouter()


@router.get("/customers")
@limiter.limit(settings.rate_limit_search)
def api_read_all_customers(
    request: Request,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    name: str | None = Query(None, min_length=1, description="Filter by name (partial match)"),
    email: str | None = Query(None, min_length=1, description="Filter by email (partial match)"),
    sort_by: Literal["id", "name", "email"] = Query(
        "id", description="Field to sort by"
    ),
    order: Literal["asc", "desc"] = Query("asc", description="Sort order"),
) -> list[CustomerResult]:
    return read_all_customers(
        skip=skip,
        limit=limit,
        name=name,
        email=email,
        sort_by=sort_by,
        order=order,
    )


@router.get("/customer/{customer_id}")
@limiter.limit(settings.rate_limit_read)
def api_read_customer(
    request: Request,
    customer_id: int = Path(..., gt=0, description="Customer ID must be positive")
) -> CustomerResult:
    return read_customer(customer_id)


@router.post("/customer")
@limiter.limit(settings.rate_limit_write)
def api_create_customer(request: Request, customer: CustomerCreateData) -> CustomerResult:
    return create_customer(customer)


@router.patch("/customer/{customer_id}")
@limiter.limit(settings.rate_limit_write)
def api_update_customer(
    request: Request,
    customer_id: int = Path(..., gt=0, description="Customer ID must be positive"),
    customer: CustomerUpdateData = ...,
) -> CustomerResult:
    return update_customer(customer_id, customer)
