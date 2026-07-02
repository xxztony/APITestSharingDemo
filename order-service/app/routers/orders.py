from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import OrderCreate
from app.service import cancel_order, create_order, get_order, list_orders

router = APIRouter(tags=["orders"])


@router.post("/orders")
def create_order_endpoint(payload: OrderCreate, db: Session = Depends(get_db)) -> dict:
    return create_order(db, payload)


@router.get("/orders")
def list_orders_endpoint(
    account_id: str | None = None,
    status: str | None = None,
    symbol: str | None = None,
    db: Session = Depends(get_db),
) -> list[dict]:
    return list_orders(db, account_id=account_id, status=status, symbol=symbol)


@router.get("/orders/{order_id}")
def get_order_endpoint(order_id: str, db: Session = Depends(get_db)) -> dict:
    return get_order(db, order_id)


@router.patch("/orders/{order_id}/cancel")
def cancel_order_endpoint(order_id: str, db: Session = Depends(get_db)) -> dict:
    return cancel_order(db, order_id)

