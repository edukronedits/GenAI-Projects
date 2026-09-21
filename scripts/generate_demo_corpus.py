from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CONFIG = {
    "retail-assistant": {
        "folder": "retail-documents", "prefix": "RET", "types": ["product", "manual", "policy", "review", "faq"],
        "titles": ["Stride Aero Run", "Orbit Pro 14", "Northstar Pace", "Orbit Studio 14", "Returns and refunds", "Warranty support"],
        "body": "This synthetic retail knowledge document supports catalog retrieval, product support, and policy grounding. Verify price, stock, policy version, and customer eligibility through the live system before taking action.",
    },
    "healthcare-copilot": {
        "folder": "clinical-documents", "prefix": "CLN", "types": ["clinical-note", "lab-summary", "guideline", "protocol", "medication"],
        "titles": ["Diabetes follow-up", "HbA1c trend review", "Medication reconciliation", "Inpatient glycemic management", "Discharge planning", "Blood pressure protocol"],
        "body": "This synthetic clinical knowledge document is for development and evaluation only. It contains no real patient data and must not be used for diagnosis, treatment, or clinical operations.",
    },
    "banking-assistant": {
        "folder": "banking-documents", "prefix": "BNK", "types": ["policy", "product", "faq", "transaction-rule", "service-workflow"],
        "titles": ["Minimum balance policy", "Card dispute workflow", "Lost card procedure", "Loan document checklist", "Transaction monitoring", "Account servicing"],
        "body": "This synthetic banking knowledge document is for development and evaluation only. It does not contain real customer, account, or transaction information. Production actions require authenticated APIs, risk validation, confirmation, and audit logging.",
    },
}

for project, config in CONFIG.items():
    project_root = ROOT / project
    docs_dir = project_root / "data" / config["folder"]
    docs_dir.mkdir(parents=True, exist_ok=True)
    records = []
    for number in range(1, 101):
        doc_type = config["types"][(number - 1) % len(config["types"])]
        title = config["titles"][(number - 1) % len(config["titles"])]
        doc_id = f"{config['prefix']}-{number:04d}"
        content = f"""# {title} — {doc_id}\n\nDocument type: {doc_type}\nVersion: {1 + (number % 3)}.0\nEffective date: 2026-{(number % 9) + 1:02d}-{(number % 27) + 1:02d}\nSource system: synthetic-{project}\n\n{config['body']}\n\n## Retrieval attributes\n- document_id: {doc_id}\n- domain: {project}\n- document_type: {doc_type}\n- access_scope: demo\n- review_status: approved-for-development\n- chunking_hint: section\n\n## Content\nThis record includes a controlled example for {title.lower()}. A production ingestion pipeline should preserve the source URI, checksum, owner, effective dates, ACL metadata, and provenance for every chunk.\n"""
        (docs_dir / f"{doc_id.lower()}.md").write_text(content, encoding="utf-8")
        records.append({"document_id": doc_id, "title": title, "document_type": doc_type, "path": f"data/{config['folder']}/{doc_id.lower()}.md", "access_scope": "demo", "status": "approved-for-development"})
    (project_root / "data" / "manifest.json").write_text(json.dumps({"project": project, "synthetic": True, "document_count": 100, "documents": records}, indent=2) + "\n", encoding="utf-8")
    (project_root / "data" / "README.md").write_text(f"# {project} demo data\n\nThis directory contains 100 synthetic, domain-specific Markdown documents and `manifest.json`. The corpus is safe for local development and retrieval evaluation; it is not real customer, patient, or banking data.\n", encoding="utf-8")

# Structured seed records used by the services and integration tests.
(ROOT / "retail-assistant" / "data" / "catalog.json").write_text(json.dumps({"synthetic": True, "products": [{"id": "shoe-101", "name": "Stride Aero Run", "price": 4299, "category": "Running shoes"}, {"id": "laptop-301", "name": "Orbit Pro 14", "price": 74990, "category": "Laptops"}]}, indent=2) + "\n", encoding="utf-8")
(ROOT / "healthcare-copilot" / "data" / "patients.json").write_text(json.dumps({"synthetic": True, "patients": [{"id": "PT-1042", "name": "Asha Mehta", "scope": "clinician-demo"}, {"id": "PT-2088", "name": "Daniel Brooks", "scope": "clinician-demo"}]}, indent=2) + "\n", encoding="utf-8")
(ROOT / "banking-assistant" / "data" / "transactions.json").write_text(json.dumps({"synthetic": True, "transactions": [{"id": "TX-77102", "merchant": "Northline Electronics", "amount": 12500, "currency": "INR"}, {"id": "TX-77091", "merchant": "Metro Grocers", "amount": 2480, "currency": "INR"}]}, indent=2) + "\n", encoding="utf-8")
print("Generated 100 synthetic documents for each project.")
