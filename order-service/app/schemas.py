from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class OrderCreate(BaseModel):
    account_id: str = Field(..., alias="accountId", min_length=1)
    symbol: str = Field(..., min_length=1)
    side: Literal["BUY", "SELL"]
    quantity: int = Field(..., gt=0)
    price: float = Field(..., gt=0)

    model_config = ConfigDict(populate_by_name=True)


class ErrorResponse(BaseModel):
    errorCode: str
    message: str
    details: dict = Field(default_factory=dict)

