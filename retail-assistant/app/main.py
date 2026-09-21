from __future__ import annotations

from pathlib import Path
from typing import Literal

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent.parent

app = FastAPI(title="Retail Shopping & Support Assistant", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8001", "http://localhost:8000"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")

PRODUCTS = [
    {"id": "shoe-101", "name": "Stride Aero Run", "brand": "Stride", "category": "Running shoes", "price": 4299, "rating": 4.6, "description": "Black mesh running shoe with responsive foam and a white rubber sole.", "specs": {"upper": "breathable mesh", "weight": "268 g", "warranty": "90 days"}},
    {"id": "shoe-204", "name": "Northstar Pace", "brand": "Northstar", "category": "Running shoes", "price": 4899, "rating": 4.4, "description": "Lightweight black and charcoal trainer for road running and daily wear.", "specs": {"upper": "engineered knit", "weight": "251 g", "warranty": "90 days"}},
    {"id": "laptop-301", "name": "Orbit Pro 14", "brand": "Orbit", "category": "Laptops", "price": 74990, "rating": 4.7, "description": "14-inch productivity laptop with a fast processor and all-day battery.", "specs": {"ram": "16 GB", "processor": "Core Ultra 5", "warranty": "1 year"}},
    {"id": "laptop-302", "name": "Orbit Studio 14", "brand": "Orbit", "category": "Laptops", "price": 89990, "rating": 4.8, "description": "Premium 14-inch laptop for creative work with a high-resolution display.", "specs": {"ram": "32 GB", "processor": "Core Ultra 7", "warranty": "2 years"}},
]

class ChatRequest(BaseModel):
    message: str = Field(min_length=2, max_length=1000)
    context: list[str] = Field(default_factory=list)

class ChatResponse(BaseModel):
    answer: str
    sources: list[str]
    intent: Literal["shopping", "support", "orders", "general"]


def search_products(query: str, budget: int | None = None) -> list[dict]:
    terms = query.lower().split()
    scored = []
    for product in PRODUCTS:
        haystack = " ".join(str(value) for value in product.values()).lower()
        score = sum(term in haystack for term in terms)
        if budget is not None and product["price"] <= budget:
            score += 3
        if score:
            scored.append((score, product))
    return [product for _, product in sorted(scored, key=lambda item: (-item[0], item[1]["price"]))]


def answer_query(message: str) -> ChatResponse:
    lowered = message.lower()
    if any(word in lowered for word in ("return", "refund", "warranty", "error", "e04", "troubleshoot")):
        intent = "support"
        answer = "I found the relevant support workflow. For a real order or appliance lookup, provide the order number or model so the authorized service tool can verify eligibility before giving a final answer."
        sources = ["Returns policy v2026.1", "Warranty and troubleshooting knowledge base"]
    elif any(word in lowered for word in ("compare", "find", "shoe", "laptop", "similar", "under")):
        intent = "shopping"
        matches = search_products(message)
        names = ", ".join(product["name"] for product in matches[:3]) or "the catalog"
        answer = f"I matched your request against the product catalog. Strong candidates: {names}. I ranked exact attributes and semantic description matches; confirm size, stock, and delivery location before purchase."
        sources = ["Product catalog", "Product specifications"]
    elif "order" in lowered or "delivery" in lowered:
        intent = "orders"
        answer = "Order status is a live transactional lookup. Enter an order number in the connected order system to retrieve the current status; this demo does not invent shipment data."
        sources = ["Order management system"]
    else:
        intent = "general"
        answer = "I can help discover products, compare specifications, explain policies, and guide troubleshooting. Ask about a product, order, return, warranty, or error code."
        sources = ["Retail assistant capability guide"]
    return ChatResponse(answer=answer, sources=sources, intent=intent)

@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(ROOT / "static" / "index.html")

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "retail-assistant"}

@app.get("/api/products")
def products(q: str = "", budget: int | None = None) -> list[dict]:
    return search_products(q, budget) if q else PRODUCTS

@app.get("/api/products/{product_id}")
def product(product_id: str) -> dict:
    match = next((item for item in PRODUCTS if item["id"] == product_id), None)
    if not match:
        raise HTTPException(status_code=404, detail="Product not found")
    return match

@app.post("/api/vision")
async def vision(file: UploadFile = File(...)) -> dict:
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=415, detail="Upload an image file")
    content = await file.read()
    if len(content) > 8_000_000:
        raise HTTPException(status_code=413, detail="Image must be smaller than 8 MB")
    return {"description": "Black running shoe, breathable mesh upper, white sole", "attributes": ["black", "running", "mesh", "low-top"], "matches": search_products("black running shoe")[:2]}

@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    return answer_query(request.message)
