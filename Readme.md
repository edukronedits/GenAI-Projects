 # GenAI Projects

 Three separate, runnable reference applications based on the proposed retail, healthcare, and banking architectures.

 ## Projects

 | Project | Port | Focus |
 | --- | ---: | --- |
 | [Retail Assistant](retail-assistant/README.md) | 8001 | Catalog search, image matching, support intent routing |
 | [Healthcare Copilot](healthcare-copilot/README.md) | 8002 | Authorization-first patient records, lab trends, evidence |
 | [Banking Assistant](banking-assistant/README.md) | 8003 | Authenticated self-service, transactions, confirmation-gated actions |

 Each folder is independently deployable with its own `requirements.txt`, `Dockerfile`, FastAPI backend, static client, health endpoint, and API documentation at `/docs`.

 ## Run one project

 ```bash
 cd retail-assistant # or healthcare-copilot / banking-assistant
 python -m venv .venv
 . .venv/bin/activate
 pip install -r requirements.txt
 uvicorn app.main:app --reload --port 8001
 ```

 Use the port listed above for the selected project. These are production-oriented foundations with in-memory demo adapters; connect real models, vector stores, identity, audit storage, FHIR/EHR, order, and banking APIs behind the documented service seams before production use.

