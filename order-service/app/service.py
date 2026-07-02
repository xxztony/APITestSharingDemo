from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Order
from app.schemas import OrderCreate


def order_to_dict(order: Order) -> dict:
    return {
        "orderId": order.order_id,
        "accountId": order.account_id,
        "product": order.symbol,
        "side": order.side,
        "quantity": order.quantity,
        "price": float(order.price),
        "status": order.status,
        "rejectReason": order.reject_reason,
        "createdAt": order.created_at.isoformat() if order.created_at else None,
        "updatedAt": order.updated_at.isoformat() if order.updated_at else None,
    }


def seed_orders(db: Session) -> None:
    existing = db.scalar(select(Order).limit(1))
    if existing:
        return

    samples = [
        Order(
            order_id="ORD-SEED-001",
            account_id="ACC001",
            symbol="LME-CA",
            side="BUY",
            quantity=120,
            price=Decimal("9124.5000"),
            status="ACCEPTED",
        ),
        Order(
            order_id="ORD-SEED-002",
            account_id="ACC001",
            symbol="LME-AL",
            side="SELL",
            quantity=60,
            price=Decimal("2380.2500"),
            status="CANCELLED",
        ),
        Order(
            order_id="ORD-SEED-003",
            account_id="ACC002",
            symbol="LME-ZN",
            side="BUY",
            quantity=15000,
            price=Decimal("2740.0000"),
            status="REJECTED",
            reject_reason="Quantity exceeds limit",
        ),
        Order(
            order_id="ORD-SEED-004",
            account_id="ACC003",
            symbol="LME-NI",
            side="BUY",
            quantity=25,
            price=Decimal("18550.7500"),
            status="ACCEPTED",
        ),
    ]
    db.add_all(samples)
    db.commit()


def create_order(db: Session, payload: OrderCreate) -> dict:
    status = "ACCEPTED"
    reject_reason = None
    if payload.quantity > 10000:
        status = "REJECTED"
        reject_reason = "Quantity exceeds limit"
    elif payload.price > 100000:
        status = "REJECTED"
        reject_reason = "Price exceeds limit"

    order = Order(
        order_id=f"ORD-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{uuid4().hex[:8].upper()}",
        account_id=payload.account_id,
        symbol=payload.product,
        side=payload.side,
        quantity=payload.quantity,
        price=Decimal(str(payload.price)),
        status=status,
        reject_reason=reject_reason,
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order_to_dict(order)


def list_orders(db: Session, account_id: str | None = None, status: str | None = None, product: str | None = None) -> list[dict]:
    statement = select(Order).order_by(Order.created_at.desc())
    if account_id:
        statement = statement.where(Order.account_id == account_id)
    if status:
        statement = statement.where(Order.status == status)
    if product:
        statement = statement.where(Order.symbol == product)
    return [order_to_dict(order) for order in db.scalars(statement).all()]


def get_order_or_404(db: Session, order_id: str) -> Order:
    order = db.scalar(select(Order).where(Order.order_id == order_id))
    if not order:
        raise HTTPException(
            status_code=404,
            detail={"errorCode": "ORDER_NOT_FOUND", "message": "Order not found", "details": {"orderId": order_id}},
        )
    return order


def get_order(db: Session, order_id: str) -> dict:
    return order_to_dict(get_order_or_404(db, order_id))


def cancel_order(db: Session, order_id: str) -> dict:
    order = get_order_or_404(db, order_id)
    if order.status == "REJECTED":
        raise HTTPException(
            status_code=409,
            detail={
                "errorCode": "ORDER_CANNOT_BE_CANCELLED",
                "message": "Rejected orders cannot be cancelled",
                "details": {"orderId": order_id, "status": order.status},
            },
        )
    if order.status in {"ACCEPTED", "NEW"}:
        order.status = "CANCELLED"
        db.commit()
        db.refresh(order)
    return order_to_dict(order)
