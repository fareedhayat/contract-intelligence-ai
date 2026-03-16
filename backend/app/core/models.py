from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


# --- Enums ---

class RiskCategory(str, Enum):
    TERMINATION = "termination"
    LIABILITY = "liability"
    IP = "intellectual_property"
    CONFIDENTIALITY = "confidentiality"
    INDEMNIFICATION = "indemnification"
    CHANGE_OF_CONTROL = "change_of_control"
    EXCLUSIVITY = "exclusivity"
    COMPETITION = "competition"
    INSURANCE = "insurance"
    AUDIT = "audit"


class Severity(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class AnalysisStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


# --- Financial ---

class FinancialTerm(BaseModel):
    term_type: str
    value: float | None = None
    currency: str = "USD"
    description: str = ""


# --- Extraction ---

class ExtractedData(BaseModel):
    parties: list[str] = Field(default_factory=list)
    effective_date: str | None = None
    expiration_date: str | None = None
    governing_law: str | None = None
    contract_type: str | None = None
    financial_terms: list[FinancialTerm] = Field(default_factory=list)


# --- Risk ---

class RiskFlag(BaseModel):
    category: RiskCategory
    severity: Severity
    clause_text: str = ""
    explanation: str = ""
    mitigation: str = ""


# --- Obligations ---

class Obligation(BaseModel):
    party: str
    description: str
    due_date: str | None = None
    recurring: bool = False
    frequency: str | None = None
    status: str = "active"


# --- Summary ---

class ContractSummary(BaseModel):
    executive_summary: str = ""
    key_provisions: list[str] = Field(default_factory=list)
    notable_clauses: list[str] = Field(default_factory=list)


# --- Contract Document ---

class ContractDocument(BaseModel):
    id: str
    filename: str
    upload_date: datetime = Field(default_factory=datetime.utcnow)
    file_path: str = ""
    contract_type: str | None = None
    status: AnalysisStatus = AnalysisStatus.PENDING


# --- Analysis Result ---

class AnalysisResult(BaseModel):
    id: str
    contract_id: str
    status: AnalysisStatus = AnalysisStatus.PENDING
    extracted_data: ExtractedData | None = None
    risk_flags: list[RiskFlag] = Field(default_factory=list)
    obligations: list[Obligation] = Field(default_factory=list)
    summary: ContractSummary | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None
    error_message: str | None = None


# --- Comparison ---

class TermComparison(BaseModel):
    term_name: str
    contract_a_value: str = ""
    contract_b_value: str = ""
    difference: str = ""
    advantage: str = ""


class ComparisonResult(BaseModel):
    id: str
    contract_a_id: str
    contract_b_id: str
    term_comparisons: list[TermComparison] = Field(default_factory=list)
    risk_diff: str = ""
    overall_assessment: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)
