from decimal import Decimal

import strawberry
from strawberry.schema.config import StrawberryConfig

from app.database import SessionLocal
from app.models import Account, Position
from app.service import get_portfolio_record, update_risk_limit


@strawberry.type
class PositionType:
    symbol: str
    quantity: int
    average_price: float
    market_value: float


@strawberry.type
class PortfolioType:
    account_id: str
    cash_balance: float
    risk_limit: float
    used_limit: float
    available_limit: float
    positions: list[PositionType]


def _decimal_to_float(value: Decimal | float | int) -> float:
    return float(value)


def _position_to_type(position: Position) -> PositionType:
    return PositionType(
        symbol=position.symbol,
        quantity=position.quantity,
        average_price=_decimal_to_float(position.average_price),
        market_value=_decimal_to_float(position.market_value),
    )


def _portfolio_to_type(account: Account, positions: list[Position]) -> PortfolioType:
    used_limit = sum(_decimal_to_float(position.market_value) for position in positions)
    risk_limit = _decimal_to_float(account.risk_limit)
    return PortfolioType(
        account_id=account.account_id,
        cash_balance=_decimal_to_float(account.cash_balance),
        risk_limit=risk_limit,
        used_limit=used_limit,
        available_limit=risk_limit - used_limit,
        positions=[_position_to_type(position) for position in positions],
    )


@strawberry.type
class Query:
    @strawberry.field
    def portfolio(self, account_id: str) -> PortfolioType:
        with SessionLocal() as db:
            account, positions = get_portfolio_record(db, account_id)
            return _portfolio_to_type(account, positions)


@strawberry.type
class Mutation:
    @strawberry.mutation
    def update_risk_limit(self, account_id: str, limit: float) -> PortfolioType:
        with SessionLocal() as db:
            account, positions = update_risk_limit(db, account_id, limit)
            return _portfolio_to_type(account, positions)


schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    config=StrawberryConfig(auto_camel_case=True),
)

