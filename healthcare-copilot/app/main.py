from __future__ import annotations

from pathlib import Path
from typing import Literal
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent.parent
app = FastAPI(title="Clinical Knowledge & Patient Care Copilot", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:8002"], allow_methods=["GET", "POST"], allow_headers=["*"])
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")

PATIENTS = {
    "PT-1042": {"name": "Asha Mehta", "age": 58, "department": "Endocrinology", "condition": "Type 2 diabetes", "allergies": ["Penicillin"], "medications": ["Metformin 500 mg, twice daily"], "notes": ["2026-09-17: Follow-up. Reports improved adherence and no hypoglycemia.", "2026-08-12: Diabetes review. Continue current plan and repeat HbA1c."]},
    "PT-2088": {"name": "Daniel Brooks", "age": 43, "department": "Cardiology", "condition": "Hypertension", "allergies": [], "medications": ["Lisinopril 10 mg, daily"], "notes": ["2026-09-14: Blood pressure review. Home readings requested."]},
}
LABS = {"PT-1042": [{"date": "2026-06-01", "test": "HbA1c", "value": 8.1, "unit": "%", "range": "4.0-5.6", "flag": "high"}, {"date": "2026-09-17", "test": "HbA1c", "value": 7.2, "unit": "%", "range": "4.0-5.6", "flag": "high"}, {"date": "2026-09-17", "test": "Creatinine", "value": 0.9, "unit": "mg/dL", "range": "0.6-1.2", "flag": "normal"}]}
GUIDELINES = [{"id": "GL-042", "title": "Inpatient glycemic management", "department": "Endocrinology", "updated": "2026-08-20", "excerpt": "Use individualized targets and review hypoglycemia risk at each transition of care."}, {"id": "GL-017", "title": "Medication reconciliation", "department": "All services", "updated": "2026-07-11", "excerpt": "Reconcile prescribed, over-the-counter, and recently discontinued medicines."}]

class ChatRequest(BaseModel):
    patient_id: str = Field(min_length=3, max_length=20)
    question: str = Field(min_length=3, max_length=800)

class ChatResponse(BaseModel):
    answer: str
    evidence: list[dict]
    safety: Literal["grounded", "escalate"]

class User(BaseModel):
    user_id: str
    role: Literal["clinician", "viewer"]
    patient_scope: list[str]


def current_user(x_demo_user: str | None = Header(default=None)) -> User:
    if x_demo_user == "viewer":
        return User(user_id="viewer-01", role="viewer", patient_scope=["PT-2088"])
    return User(user_id="clinician-01", role="clinician", patient_scope=list(PATIENTS))


def authorized_patient(patient_id: str, user: User) -> dict:
    if patient_id not in user.patient_scope:
        raise HTTPException(status_code=403, detail="User is not authorized for this patient")
    patient = PATIENTS.get(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@app.get("/", include_in_schema=False)
def index() -> FileResponse: return FileResponse(ROOT / "static" / "index.html")
@app.get("/health")
def health() -> dict[str, str]: return {"status": "ok", "service": "healthcare-copilot"}

@app.get("/api/patients")
def patients(user: User = Depends(current_user)) -> list[dict]:
    return [{"id": pid, "name": PATIENTS[pid]["name"], "department": PATIENTS[pid]["department"], "condition": PATIENTS[pid]["condition"]} for pid in user.patient_scope]

@app.get("/api/patients/{patient_id}")
def patient(patient_id: str, user: User = Depends(current_user)) -> dict:
    record = authorized_patient(patient_id, user)
    return {"id": patient_id, **record, "labs": LABS.get(patient_id, [])}

@app.get("/api/guidelines")
def guidelines(user: User = Depends(current_user)) -> list[dict]:
    if user.role != "clinician":
        raise HTTPException(status_code=403, detail="Clinical guideline access requires clinician role")
    return GUIDELINES

@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest, user: User = Depends(current_user)) -> ChatResponse:
    patient = authorized_patient(request.patient_id, user)
    labs = LABS.get(request.patient_id, [])
    question = request.question.lower()
    if "lab" in question or "trend" in question or "history" in question:
        hba1c = [lab for lab in labs if lab["test"] == "HbA1c"]
        answer = f"Authorized record summary for {patient['name']}: {len(patient['notes'])} recent notes and {len(labs)} lab results are available. HbA1c changed from {hba1c[0]['value']}% on {hba1c[0]['date']} to {hba1c[-1]['value']}% on {hba1c[-1]['date']}; both are above the listed reference range. This is a trend summary, not a diagnosis or treatment recommendation."
        evidence = [{"type": "patient record", "label": note} for note in patient["notes"]] + [{"type": "lab result", "label": f"{lab['date']} {lab['test']}: {lab['value']} {lab['unit']} ({lab['flag']})"} for lab in labs]
    elif "guideline" in question or "protocol" in question:
        answer = "The relevant approved knowledge is listed in the evidence panel. Review the cited guideline in the hospital policy system before acting; this assistant does not replace clinical judgment."
        evidence = [{"type": "guideline", "label": f"{item['id']} · {item['title']} · updated {item['updated']}"} for item in GUIDELINES]
    else:
        answer = f"I can summarize authorized records for {patient['name']} and retrieve approved guidelines. Ask for recent history, lab trends, medications, or a relevant protocol."
        evidence = [{"type": "patient record", "label": f"Department: {patient['department']} · Condition: {patient['condition']}"}]
    return ChatResponse(answer=answer, evidence=evidence, safety="grounded")
