# Contract Intelligence AI

AI-powered contract analysis platform using the CUAD dataset (510 real SEC-filed corporate contracts, 41 annotated clause types). Built with Microsoft Agent Framework, Azure OpenAI, FastAPI, React/Fluent UI, and Azure Cosmos DB.

## Quick Start

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # Edit with your Azure credentials
uvicorn app.api.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### CUAD Dataset
```bash
cd backend
python scripts/download_cuad.py
```

## Architecture

- **Backend:** FastAPI + Microsoft Agent Framework + Azure OpenAI
- **Frontend:** React + Fluent UI + TypeScript
- **Database:** Azure Cosmos DB
- **Storage:** Azure Blob Storage (local filesystem fallback)
- **Document Parsing:** Azure AI Document Intelligence (local .txt fallback)

## Agent Pipeline

```
DataExtractor → RiskAnalyst → ObligationTracker → Summarizer
```

Each agent processes the contract sequentially via `WorkflowBuilder`, producing structured analysis results covering extracted data, risk flags, obligations, and an executive summary.
