// --- Enums ---

export type RiskCategory =
  | "termination"
  | "liability"
  | "intellectual_property"
  | "confidentiality"
  | "indemnification"
  | "change_of_control"
  | "exclusivity"
  | "competition"
  | "insurance"
  | "audit";

export type Severity = "high" | "medium" | "low";

export type AnalysisStatus = "pending" | "in_progress" | "completed" | "failed";

// --- Models ---

export interface FinancialTerm {
  term_type: string;
  value: number | null;
  currency: string;
  description: string;
}

export interface ExtractedData {
  parties: string[];
  effective_date: string | null;
  expiration_date: string | null;
  governing_law: string | null;
  contract_type: string | null;
  financial_terms: FinancialTerm[];
}

export interface RiskFlag {
  category: RiskCategory;
  severity: Severity;
  clause_text: string;
  explanation: string;
  mitigation: string;
}

export interface Obligation {
  party: string;
  description: string;
  due_date: string | null;
  recurring: boolean;
  frequency: string | null;
  status: string;
}

export interface ContractSummary {
  executive_summary: string;
  key_provisions: string[];
  notable_clauses: string[];
}

export interface ContractDocument {
  id: string;
  filename: string;
  upload_date: string;
  file_path: string;
  contract_type: string | null;
  status: AnalysisStatus;
}

export interface AnalysisResult {
  id: string;
  contract_id: string;
  status: AnalysisStatus;
  extracted_data: ExtractedData | null;
  risk_flags: RiskFlag[];
  obligations: Obligation[];
  summary: ContractSummary | null;
  created_at: string;
  completed_at: string | null;
  error_message: string | null;
}

export interface TermComparison {
  term_name: string;
  contract_a_value: string;
  contract_b_value: string;
  difference: string;
  advantage: string;
}

export interface ComparisonResult {
  id: string;
  contract_a_id: string;
  contract_b_id: string;
  term_comparisons: TermComparison[];
  risk_diff: string;
  overall_assessment: string;
  created_at: string;
}

// --- API Responses ---

export interface PaginatedContracts {
  contracts: ContractDocument[];
  total: number;
}

export interface DashboardStats {
  total_contracts: number;
  analyzed: number;
  pending: number;
  failed: number;
  contracts_with_risks: number;
  high_risk: number;
  medium_risk: number;
  low_risk: number;
  total_obligations: number;
  most_common_risk: string | null;
  most_common_risk_count: number;
}

export interface ObligationWithContract extends Obligation {
  contract_id: string;
  filename?: string;
}

export interface PaginatedObligations {
  obligations: ObligationWithContract[];
  total: number;
}

export interface AnalysisStatusResponse {
  contract_id: string;
  status: AnalysisStatus;
  error_message: string | null;
}

export interface CuadContractList {
  contracts: string[];
  total: number;
}

export interface CuadContractTypes {
  types: string[];
}

export interface ImportResult {
  contract_id: string;
  filename: string;
  characters: number;
}

export interface BatchImportResult {
  imported: number;
  contracts: ImportResult[];
}
