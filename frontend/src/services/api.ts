import axios from "axios";
import type {
  AnalysisResult,
  AnalysisStatusResponse,
  BatchImportResult,
  ComparisonResult,
  ContractDocument,
  CuadContractList,
  CuadContractTypes,
  DashboardStats,
  ImportResult,
  PaginatedContracts,
  PaginatedObligations,
} from "../types";

const api = axios.create({ baseURL: "/api" });

// --- Contracts ---

export async function uploadContract(file: File): Promise<{ contract_id: string; filename: string }> {
  const form = new FormData();
  form.append("file", file);
  const { data } = await api.post("/contracts/upload", form);
  return data;
}

export async function listContracts(skip = 0, limit = 20): Promise<PaginatedContracts> {
  const { data } = await api.get("/contracts", { params: { skip, limit } });
  return data;
}

export async function getContract(contractId: string): Promise<ContractDocument> {
  const { data } = await api.get(`/contracts/${contractId}`);
  return data;
}

export async function deleteContract(contractId: string): Promise<void> {
  await api.delete(`/contracts/${contractId}`);
}

// --- Analysis ---

export async function triggerAnalysis(contractId: string): Promise<{ contract_id: string; status: string }> {
  const { data } = await api.post(`/analysis/${contractId}`);
  return data;
}

export async function getAnalysis(contractId: string): Promise<AnalysisResult> {
  const { data } = await api.get(`/analysis/${contractId}`);
  return data;
}

export async function getAnalysisStatus(contractId: string): Promise<AnalysisStatusResponse> {
  const { data } = await api.get(`/analysis/${contractId}/status`);
  return data;
}

export async function getDashboardStats(): Promise<DashboardStats> {
  const { data } = await api.get("/analysis/dashboard/stats");
  return data;
}

// --- Compare ---

export async function compareContracts(contractAId: string, contractBId: string): Promise<ComparisonResult> {
  const { data } = await api.post("/compare", {
    contract_a_id: contractAId,
    contract_b_id: contractBId,
  });
  return data;
}

export async function getComparison(comparisonId: string): Promise<ComparisonResult> {
  const { data } = await api.get(`/compare/${comparisonId}`);
  return data;
}

// --- Obligations ---

export async function listObligations(contractId?: string, skip = 0, limit = 50): Promise<PaginatedObligations> {
  const params: Record<string, unknown> = { skip, limit };
  if (contractId) params.contract_id = contractId;
  const { data } = await api.get("/obligations", { params });
  return data;
}

export async function getUpcomingObligations(days = 30): Promise<PaginatedObligations> {
  const { data } = await api.get("/obligations/upcoming", { params: { days } });
  return data;
}

// --- CUAD ---

export async function listCuadContracts(contractType?: string, skip = 0, limit = 50): Promise<CuadContractList> {
  const params: Record<string, unknown> = { skip, limit };
  if (contractType) params.contract_type = contractType;
  const { data } = await api.get("/cuad/contracts", { params });
  return data;
}

export async function listCuadContractTypes(): Promise<CuadContractTypes> {
  const { data } = await api.get("/cuad/contract-types");
  return data;
}

export async function importCuadContract(filename: string): Promise<ImportResult> {
  const { data } = await api.post(`/cuad/import/${encodeURIComponent(filename)}`);
  return data;
}

export async function importCuadBatch(contractType?: string, limit = 10): Promise<BatchImportResult> {
  const params: Record<string, unknown> = { limit };
  if (contractType) params.contract_type = contractType;
  const { data } = await api.post("/cuad/import-batch", null, { params });
  return data;
}
