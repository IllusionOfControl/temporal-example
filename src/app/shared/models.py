from pydantic import BaseModel, EmailStr, Field

class OrderRequest(BaseModel):
    order_id: str
    item_name: str
    amount: float
    email: str

class UserCreateRequest(BaseModel):
    user_id: str
    name: str = Field(..., min_length=2)
    email: EmailStr

class KYCResponse(BaseModel):
    user_id: str
    status: str
    score: float = 0.0