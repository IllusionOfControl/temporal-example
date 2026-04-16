from pydantic import BaseModel, Field

__all__ = ["KYCResponse", "OrderRequest", "ReviewRequest", "UserCreateRequest"]


class OrderRequest(BaseModel):
    order_id: str
    item_name: str
    amount: float
    email: str


class UserCreateRequest(BaseModel):
    user_id: str
    name: str = Field(..., min_length=2)
    email: str


class KYCResponse(BaseModel):
    user_id: str
    status: str
    score: float = 0.0


class ReviewRequest(BaseModel):
    text: str = Field(..., min_length=5, description="Текст отзыва клиента")
