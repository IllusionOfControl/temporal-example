from dataclasses import dataclass

@dataclass
class OrderRequest:
    order_id: str
    item_name: str
    amount: float
    email: str