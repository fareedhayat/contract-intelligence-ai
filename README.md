# Contract Intelligence AI

AI-powered contract analysis platform using the CUAD dataset (510 real SEC-filed corporate contracts, 41 annotated clause types). Built with Microsoft Agent Framework, Azure OpenAI, FastAPI, React/Fluent UI, and Azure Cosmos DB.

## What It Does

- **Instant Analysis** — upload any contract and get structured extraction of parties, dates, financial terms, and governing law
- **Risk Highlighter** — flags uncapped liability, one-sided termination, IP assignment risks, hidden auto-renewals, and more
- **Obligation Tracker** — extracts every deadline, renewal date, and notice period into a timeline
- **Plain-English Summary** — converts legal language into a brief any stakeholder can read
- **Compare Contracts** — side-by-side clause-level comparison of two contracts

---

## Prerequisites

- Python 3.11+
- Node.js 18+
- Azure OpenAI resource with a `gpt-4o` deployment
- Azure Cosmos DB Emulator (for local dev) **or** an Azure Cosmos DB account
- CUAD v1 dataset extracted to `backend/data/` (download from [Zenodo](https://zenodo.org/records/4595826))

---

## Local Setup

### 1. Backend

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` with your credentials. Minimum required for local dev:

```env
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT=gpt-4o

# Cosmos DB Emulator defaults — no changes needed if using emulator
COSMOS_ENDPOINT=https://localhost:8081
COSMOS_KEY=C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b4RfZPcFVI5JAXVNiW24p/CxuF5Pg==

# Keep these true for local dev (uses filesystem + .txt files instead of Azure services)
USE_LOCAL_STORAGE=true
USE_LOCAL_PARSER=true
```

Start the backend:

```bash
uvicorn app.api.main:app --reload
# API docs: http://localhost:8000/docs
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
# App: http://localhost:5173
```

### 3. CUAD Dataset

Download `CUAD_v1.zip` from [https://zenodo.org/records/4595826](https://zenodo.org/records/4595826) and extract it so the structure looks like:

```
backend/data/
  full_contract_txt/    # 510 .txt contracts
  full_contract_pdf/    # 510 .pdf contracts
  master_clauses.csv    # ground truth annotations
```

### 4. Seed Demo Data

With the backend running and CUAD dataset in place:

```bash
cd backend
python scripts/seed_demo_data.py
```

This imports 50 contracts (2 per contract type) and runs the full AI analysis pipeline on each. Takes 15–30 minutes depending on Azure OpenAI throughput.

---

## Demo Walkthrough

1. Open `http://localhost:5173`
2. **Dashboard** — shows portfolio stats: total contracts, risk breakdown, analysis status
3. **Upload** — drag and drop a contract PDF or TXT; analysis runs automatically in the background
4. **Contract Detail** — view the full analysis: summary, extracted data, risk flags, obligations
5. **Compare** — select two contracts and get a side-by-side clause-level diff with negotiation recommendations
6. **Obligations** — filter obligations by date range to see upcoming renewal deadlines and deliverables

---

## Running Tests

```bash
cd backend
pytest tests/ -v
```

Tests validate AI extraction accuracy against CUAD ground truth annotations:

| Metric | Target |
|---|---|
| Entity extraction accuracy | > 85% |
| Risk detection precision | > 80% |
| Risk detection recall | > 75% |
| Date extraction accuracy | > 90% |

---

## Architecture

```
Contract (PDF / Word / TXT)
        │
        ▼
Azure AI Document Intelligence  ← parse text + tables
        │
        ▼
Agent Framework WorkflowBuilder Pipeline
  DataExtractorAgent  → parties, dates, financial terms
  RiskAnalysisAgent   → flagged clauses with severity
  ObligationAgent     → deadlines, renewals, notice periods
  SummaryAgent        → plain-English brief
        │
        ▼
Azure Cosmos DB  ← store structured JSON results
        │
        ▼
FastAPI REST API  ← serve analysis data
        │
        ▼
React + Fluent UI  ← interactive dashboard
```

### Agent Pipeline (Microsoft Agent Framework)

```python
workflow = (
    WorkflowBuilder()
    .set_start_executor(extractor)
    .add_edge(extractor, risk_analyst)
    .add_edge(risk_analyst, obligation_tracker)
    .add_edge(obligation_tracker, summarizer)
    .build()
)
```

Each agent receives structured output from the previous agent and uses `response_format` (Pydantic model) for typed output — no string parsing.

---

## Tech Stack

| Layer | Technology |
|---|---|
| AI Orchestration | Microsoft Agent Framework (Python) |
| LLM | Azure OpenAI Service (GPT-4o) |
| Document Parsing | Azure AI Document Intelligence |
| Backend API | FastAPI (Python) |
| Frontend | React + Fluent UI + TypeScript |
| Database | Azure Cosmos DB |
| Document Storage | Azure Blob Storage (local filesystem fallback) |
| Dataset | CUAD v1 — 510 contracts, 41 clause categories |

---

## Dataset

CUAD (Contract Understanding Atticus Dataset) — 510 real corporate contracts from SEC EDGAR, annotated by trained law students across 41 clause categories. Licensed CC BY 4.0.

- Download: [https://zenodo.org/records/4595826](https://zenodo.org/records/4595826)
- Paper: [https://arxiv.org/abs/2103.06268](https://arxiv.org/abs/2103.06268)

---

## Project Structure

```
contract-intelligence-ai/
├── backend/
│   ├── app/
│   │   ├── agents/          # Agent definitions, prompts, tools, pipeline
│   │   ├── api/             # FastAPI app, routes, error handlers
│   │   ├── core/            # Pydantic models and settings
│   │   └── services/        # Storage, document parsing, Cosmos DB, CUAD loader
│   ├── scripts/
│   │   └── seed_demo_data.py
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── components/      # Layout, ErrorBoundary
│       ├── pages/           # Dashboard, Upload, ContractDetail, Compare, Obligations
│       ├── services/        # API client
│       └── types/           # TypeScript interfaces
└── data/                    # CUAD dataset (not committed)
```
