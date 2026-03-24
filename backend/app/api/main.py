from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import contracts, analysis, compare, obligations, cuad
from app.api.error_handlers import add_error_handlers

app = FastAPI(
    title="Contract Intelligence AI",
    description="AI-powered contract analysis platform using CUAD dataset and Microsoft Agent Framework",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(contracts.router, prefix="/api/contracts", tags=["Contracts"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["Analysis"])
app.include_router(compare.router, prefix="/api/compare", tags=["Compare"])
app.include_router(obligations.router, prefix="/api/obligations", tags=["Obligations"])
app.include_router(cuad.router, prefix="/api/cuad", tags=["CUAD Dataset"])

add_error_handlers(app)


@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "healthy", "service": "contract-intelligence-ai"}
