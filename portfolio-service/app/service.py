from decimal import Decimal

from graphql import GraphQLError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Account, Position


def seed_portfolios(db: Session) -> None:
    existing = db.scalar(select(Account).limit(1))
    if existing:
        return

    db.add_all(
        [
            Account(account_id="ACC001", cash_balance=Decimal("1250000.00"), risk_limit=Decimal("3000000.00")),
            Account(account_id="ACC002", cash_balance=Decimal("860000.00"), risk_limit=Decimal("1500000.00")),
            Account(account_id="ACC003", cash_balance=Decimal("540000.00"), risk_limit=Decimal("1000000.00")),
        ]
    )
    db.add_all(
        [
            Position(
                account_id="ACC001",
                symbol="LME-CA",
                quantity=100,
                average_price=Decimal("9080.5000"),
                market_value=Decimal("908050.00"),
            ),
            Position(
                account_id="ACC001",
                symbol="LME-AL",
                quantity=200,
                average_price=Decimal("2365.0000"),
                market_value=Decimal("473000.00"),
            ),
            Position(
                account_id="ACC002",
                symbol="LME-ZN",
                quantity=120,
                average_price=Decimal("2722.2500"),
                market_value=Decimal("326670.00"),
            ),
            Position(
                account_id="ACC003",
                symbol="LME-NI",
                quantity=30,
                average_price=Decimal("18520.0000"),
                market_value=Decimal("555600.00"),
            ),
        ]
    )
    db.commit()


def get_portfolio_record(db: Session, account_id: str) -> tuple[Account, list[Position]]:
    account = db.scalar(select(Account).where(Account.account_id == account_id))
    if not account:
        raise GraphQLError(f"Account {account_id} not found")
    positions = list(db.scalars(select(Position).where(Position.account_id == account_id)).all())
    return account, positions


def update_risk_limit(db: Session, account_id: str, limit: float) -> tuple[Account, list[Position]]:
    if limit <= 0:
        raise GraphQLError("Risk limit must be greater than 0")
    account, _ = get_portfolio_record(db, account_id)
    account.risk_limit = Decimal(str(limit))
    db.commit()
    db.refresh(account)
    return get_portfolio_record(db, account_id)

