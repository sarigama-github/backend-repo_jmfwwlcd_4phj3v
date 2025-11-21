import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import User, Product, Order, OrderItem

app = FastAPI(title="BotBuy API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helpers
class ObjectIdStr(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    @classmethod
    def validate(cls, v):
        try:
            return str(ObjectId(v))
        except Exception:
            raise ValueError("Invalid ObjectId")

class CreateOrderRequest(BaseModel):
    items: List[OrderItem]
    user_id: Optional[str] = None
    notes: Optional[str] = None

@app.get("/")
def root():
    return {"service": "BotBuy API", "status": "ok"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Connected & Working"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name
            response["connection_status"] = "Connected"
            response["collections"] = db.list_collection_names()
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"
    return response

# Public catalog endpoints
@app.get("/api/products")
def list_products():
    prods = get_documents("product", {}, limit=None)
    for p in prods:
        p["_id"] = str(p["_id"])
    return prods

@app.post("/api/products")
def create_product_endpoint(product: Product):
    prod_id = create_document("product", product)
    return {"id": prod_id}

# Simplified auth profiles (uses provider IDs from env on frontend)
@app.post("/api/users")
def upsert_user(user: User):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    existing = db["user"].find_one({"email": user.email})
    if existing:
        db["user"].update_one({"_id": existing["_id"]}, {"$set": user.model_dump()})
        return {"id": str(existing["_id"]) }
    new_id = create_document("user", user)
    return {"id": new_id}

# Orders + PayPal skeleton
@app.post("/api/orders")
def create_order(req: CreateOrderRequest):
    total = sum(i.price * i.quantity for i in req.items)
    order = Order(items=req.items, total_amount=total, user_id=req.user_id)
    order_id = create_document("order", order)
    # Here we'd call PayPal using env secrets; we just echo for now.
    return {"id": order_id, "paypal": {"status": "created"}}

@app.get("/api/orders")
def list_orders():
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    orders = list(db["order"].find().limit(50))
    for o in orders:
        o["_id"] = str(o["_id"])
    return orders

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
