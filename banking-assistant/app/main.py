from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Literal
from uuid import uuid4
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent.parent
app = FastAPI(title="Agentic Banking Self-Service Assistant", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:8003"], allow_methods=["GET", "POST"], allow_headers=["*"])
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")

ACCOUNT = {"name": "Maya Rao", "masked": "•••• 4821", "type": "Everyday account", "available": 184250.75, "currency": "INR"}
TRANSACTIONS = [{"id": "TX-77102", "date": "2026-09-20", "merchant": "Northline Electronics", "amount": 12500, "status": "Completed", "category": "Shopping"}, {"id": "TX-77091", "date": "2026-09-19", "merchant": "Metro Grocers", "amount": 2480, "status": "Completed", "category": "Groceries"}, {"id": "TX-77040", "date": "2026-09-17", "merchant": "StreamFlix", "amount": 649, "status": "Completed", "category": "Subscription"}]
POLICIES = {"balance": "The minimum monthly balance for this account is ₹10,000. Fees and eligibility depend on the account variant and current schedule of charges.", "dispute": "Card transaction disputes can be raised for eligible card-present or card-not-present transactions. The transaction must be reviewed and the customer must confirm the selected transaction before submission."}

class ChatRequest(BaseModel):
    message: str = Field(min_length=2, max_length=1000)

class ActionRequest(BaseModel):
    action: Literal["block_card", "create_dispute"]
    transaction_id: str | None = None
    confirmation: bool = False

class ActionResponse(BaseModel):
    state: Literal["confirmation_required", "completed"]
    message: str
    reference: str | None = None

@app.get("/", include_in_schema=False)
def index() -> FileResponse: return FileResponse(ROOT / "static" / "index.html")
@app.get("/health")
def health() -> dict[str, str]: return {"status": "ok", "service": "banking-assistant"}

@app.get("/api/account")
def account(x_session_token: str | None = Header(default=None)) -> dict:
    if not x_session_token: raise HTTPException(status_code=401, detail="Authenticated session required")
    return ACCOUNT

@app.get("/api/transactions")
def transactions(x_session_token: str | None = Header(default=None)) -> list[dict]:
    if not x_session_token: raise HTTPException(status_code=401, detail="Authenticated session required")
    return TRANSACTIONS

@app.post("/api/chat")
def chat(request: ChatRequest, x_session_token: str | None = Header(default=None)) -> dict:
    if not x_session_token: raise HTTPException(status_code=401, detail="Authenticated session required")
    text = request.message.lower()
    if "minimum balance" in text or "balance" in text:
        return {"intent": "knowledge", "answer": POLICIES["balance"], "sources": ["Schedule of charges · effective 2026-08-01"]}
    if "unrecogn" in text or "dispute" in text:
        return {"intent": "transaction", "answer": "I found your recent transactions. Select the transaction you want to review; no dispute will be created until you confirm it.", "sources": ["Transaction service", "Dispute policy"]}
    if "block" in text or "lost" in text:
        return {"intent": "transaction", "answer": "Blocking a card is a high-impact action. I can prepare the workflow, then ask for explicit confirmation before execution.", "sources": ["Card management policy"]}
    return {"intent": "general", "answer": "I can explain banking policies, show recent transactions, start a dispute review, or prepare a card-block workflow. Actions require authentication and explicit confirmation.", "sources": ["Banking assistant guide"]}

@app.post("/api/actions", response_model=ActionResponse)
def action(request: ActionRequest, x_session_token: str | None = Header(default=None)) -> ActionResponse:
    if not x_session_token: raise HTTPException(status_code=401, detail="Authenticated session required")
    if request.action == "create_dispute":
        if not request.transaction_id or not any(item["id"] == request.transaction_id for item in TRANSACTIONS): raise HTTPException(status_code=404, detail="Select a valid transaction")
        selected = next(item for item in TRANSACTIONS if item["id"] == request.transaction_id)
        if not request.confirmation: return ActionResponse(state="confirmation_required", message=f"Confirm dispute for {selected['merchant']} on {selected['date']} for ₹{selected['amount']:,}.")
    if request.action == "block_card" and not request.confirmation: return ActionResponse(state="confirmation_required", message="Confirm that you want to block the card ending in 4821. This action cannot be undone here.")
    reference = f"SR-{uuid4().hex[:8].upper()}"
    return ActionResponse(state="completed", message="The request was accepted by the controlled banking workflow.", reference=reference)
