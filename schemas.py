"""
Database Schemas for BotBuy

Each Pydantic model represents a collection in MongoDB. Collection name is the lowercase of the class name.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class User(BaseModel):
    name: Optional[str] = Field(None)
    email: str = Field(...)
    avatar_url: Optional[str] = None
    provider: Optional[str] = Field(None, description="google | discord | email")
    provider_id: Optional[str] = None
    role: str = Field("client", description="client | owner | admin")
    is_active: bool = True

class Product(BaseModel):
    title: str
    description: Optional[str] = None
    price: float = Field(..., ge=0)
    category: str = Field("bots")
    sku: Optional[str] = None
    images: List[str] = []
    highlights: List[str] = []
    status: str = Field("active")

class OrderItem(BaseModel):
    product_id: str
    title: str
    price: float
    quantity: int = 1

class Order(BaseModel):
    user_id: Optional[str] = None
    items: List[OrderItem]
    total_amount: float
    status: str = Field("pending", description="pending|paid|failed|refunded")
    payment: Dict[str, Any] = Field(default_factory=lambda: {
        "provider": "paypal",
        "status": "created",
        "order_id": None,
        "capture_id": None
    })
    notes: Optional[str] = None
