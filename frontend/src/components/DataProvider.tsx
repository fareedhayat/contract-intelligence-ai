import { createContext, useContext, useState, useCallback, useEffect, ReactNode } from "react";
import { getDashboardStats, listContracts, getAnalysis } from "../services/api";
import type { DashboardStats, ContractDocument, AnalysisResult } from "../types";

interface DataContextType {
  // State
  stats: DashboardStats | null;
  contracts: ContractDocument[];
  totalContracts: number;
  analysisCache: Map<string, AnalysisResult>;
  loading: boolean;

  // Actions
  refreshAll: () => Promise<void>;
  refreshStats: () => Promise<void>;
  refreshContracts: () => Promise<void>;
  getContractAnalysis: (contractId: string, forceRefresh?: boolean) => Promise<AnalysisResult | null>;
  invalidateAnalysis: (contractId: string) => void;
}

const DataContext = createContext<DataContextType | null>(null);

export function DataProvider({ children }: { children: ReactNode }) {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [contracts, setContracts] = useState<ContractDocument[]>([]);
  const [totalContracts, setTotalContracts] = useState(0);
  const [analysisCache, setAnalysisCache] = useState<Map<string, AnalysisResult>>(new Map());
  const [loading, setLoading] = useState(true);

  const refreshStats = useCallback(async () => {
    try {
      const data = await getDashboardStats();
      setStats(data);
    } catch (err) {
      console.error("Failed to fetch stats:", err);
    }
  }, []);

  const refreshContracts = useCallback(async () => {
    try {
      const data = await listContracts(0, 50);
      setContracts(data.contracts);
      setTotalContracts(data.total);
    } catch (err) {
      console.error("Failed to fetch contracts:", err);
    }
  }, []);

  const refreshAll = useCallback(async () => {
    setLoading(true);
    await Promise.all([refreshStats(), refreshContracts()]);
    setLoading(false);
  }, [refreshStats, refreshContracts]);

  const getContractAnalysis = useCallback(async (contractId: string, forceRefresh = false): Promise<AnalysisResult | null> => {
    // Return cached if available and not forcing refresh
    if (!forceRefresh && analysisCache.has(contractId)) {
      const cached = analysisCache.get(contractId)!;
      // Only use cache if analysis is completed or failed (not pending/in_progress)
      if (cached.status === "completed" || cached.status === "failed") {
        return cached;
      }
    }

    try {
      const analysis = await getAnalysis(contractId);
      setAnalysisCache(prev => new Map(prev).set(contractId, analysis));
      return analysis;
    } catch {
      return null;
    }
  }, [analysisCache]);

  const invalidateAnalysis = useCallback((contractId: string) => {
    setAnalysisCache(prev => {
      const next = new Map(prev);
      next.delete(contractId);
      return next;
    });
  }, []);

  // Initial load
  useEffect(() => {
    refreshAll();
  }, [refreshAll]);

  // Auto-refresh every 10 seconds if there are pending analyses
  useEffect(() => {
    const hasPending = contracts.some(c => c.status === "pending" || c.status === "in_progress");
    if (!hasPending) return;

    const interval = setInterval(() => {
      refreshAll();
    }, 10000);

    return () => clearInterval(interval);
  }, [contracts, refreshAll]);

  return (
    <DataContext.Provider
      value={{
        stats,
        contracts,
        totalContracts,
        analysisCache,
        loading,
        refreshAll,
        refreshStats,
        refreshContracts,
        getContractAnalysis,
        invalidateAnalysis,
      }}
    >
      {children}
    </DataContext.Provider>
  );
}

export function useData() {
  const context = useContext(DataContext);
  if (!context) {
    throw new Error("useData must be used within a DataProvider");
  }
  return context;
}
