from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
from datetime import datetime
import uuid

app = FastAPI(title="Mock E-commerce APIs", version="1.0.0")

# Mock data
products_db = [
    {
        "id": "1",
        "name": "Wireless Bluetooth Headphones",
        "category": "electronics",
        "price": 89.99,
        "brand": "TechSound",
        "rating": 4.5,
        "description": "High-quality wireless headphones with noise cancellation",
        "features": ["Bluetooth 5.0", "Noise Cancellation", "30-hour battery"],
        "in_stock": True
    },
    {
        "id": "2", 
        "name": "Smart Fitness Watch",
        "category": "electronics",
        "price": 199.99,
        "brand": "FitTech",
        "rating": 4.3,
        "description": "Advanced fitness tracking with heart rate monitoring",
        "features": ["Heart Rate Monitor", "GPS", "Water Resistant"],
        "in_stock": True
    },
    {
        "id": "3",
        "name": "Organic Cotton T-Shirt",
        "category": "clothing",
        "price": 24.99,
        "brand": "EcoWear",
        "rating": 4.7,
        "description": "Comfortable organic cotton t-shirt",
        "features": ["100% Organic", "Breathable", "Multiple Colors"],
        "in_stock": True
    },
    {
        "id": "4",
        "name": "Running Shoes",
        "category": "footwear",
        "price": 129.99,
        "brand": "RunFast",
        "rating": 4.6,
        "description": "Professional running shoes with cushioning",
        "features": ["Lightweight", "Cushioned", "Breathable"],
        "in_stock": True
    }
]

users_db = {
    "user123": {
        "id": "user123",
        "name": "John Doe",
        "preferences": {
            "categories": ["electronics", "footwear"],
            "budget_range": {"min": 50, "max": 300},
            "brands": ["TechSound", "FitTech"]
        },
        "purchase_history": [
            {"product_id": "1", "date": "2024-01-15", "amount": 89.99}
        ]
    }
}

orders_db = {}

# Pydantic models
class ProductSearchRequest(BaseModel):
    query: Optional[str] = None
    category: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    brand: Optional[str] = None

class UserPreferences(BaseModel):
    categories: List[str] = []
    budget_range: Dict[str, float] = {}
    brands: List[str] = []

class CheckoutRequest(BaseModel):
    user_id: str
    product_id: str
    quantity: int = 1

class OrderResponse(BaseModel):
    order_id: str
    user_id: str
    product_id: str
    quantity: int
    total_amount: float
    status: str
    created_at: str

# Product API endpoints
@app.get("/api/products")
async def search_products(
    query: Optional[str] = None,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    brand: Optional[str] = None
):
    """Search products based on criteria"""
    filtered_products = products_db.copy()
    
    if query:
        filtered_products = [p for p in filtered_products if query.lower() in p["name"].lower() or query.lower() in p["description"].lower()]
    
    if category:
        filtered_products = [p for p in filtered_products if p["category"] == category]
    
    if min_price is not None:
        filtered_products = [p for p in filtered_products if p["price"] >= min_price]
    
    if max_price is not None:
        filtered_products = [p for p in filtered_products if p["price"] <= max_price]
    
    if brand:
        filtered_products = [p for p in filtered_products if p["brand"] == brand]
    
    return {"products": filtered_products, "count": len(filtered_products)}

@app.get("/api/products/{product_id}")
async def get_product(product_id: str):
    """Get product details by ID"""
    product = next((p for p in products_db if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# User API endpoints
@app.get("/api/users/{user_id}")
async def get_user(user_id: str):
    """Get user profile and preferences"""
    user = users_db.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/api/users/{user_id}/preferences")
async def update_user_preferences(user_id: str, preferences: UserPreferences):
    """Update user preferences"""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    users_db[user_id]["preferences"] = preferences.dict()
    return {"message": "Preferences updated successfully"}

# Checkout API endpoints
@app.post("/api/checkout")
async def create_order(checkout_request: CheckoutRequest):
    """Create a new order"""
    # Validate user exists
    if checkout_request.user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Validate product exists
    product = next((p for p in products_db if p["id"] == checkout_request.product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Create order
    order_id = str(uuid.uuid4())
    total_amount = product["price"] * checkout_request.quantity
    
    order = {
        "order_id": order_id,
        "user_id": checkout_request.user_id,
        "product_id": checkout_request.product_id,
        "quantity": checkout_request.quantity,
        "total_amount": total_amount,
        "status": "confirmed",
        "created_at": datetime.now().isoformat()
    }
    
    orders_db[order_id] = order
    
    return OrderResponse(**order)

# Order tracking API endpoints
@app.get("/api/orders/{order_id}")
async def get_order(order_id: str):
    """Get order details"""
    order = orders_db.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.get("/api/orders/user/{user_id}")
async def get_user_orders(user_id: str):
    """Get all orders for a user"""
    user_orders = [order for order in orders_db.values() if order["user_id"] == user_id]
    return {"orders": user_orders}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8015) 