// ---------------------------------------------------------------------------
// Shared TypeScript types for the DeFi Risk Dependency Analyzer
// ---------------------------------------------------------------------------

/** POST /api/analyze request body */
export interface AnalyzeRequest {
  token_address: string;
}

/** POST /api/analyze response body */
export interface AnalyzeResponse {
  status: string;
  token_address: string;
  slippage: number | null;
  expected_loss: number;
  action: string;
  warnings: string[];
  data_provenance: string | Record<string, string>;
  nodes: DependencyLayer[];
  edges: DependencyEdge[];
}

/** A single dependency layer / node */
export interface DependencyLayer {
  id: string; // "L1", "L2", etc
  name: string;
  label: string;
  tvl: number; // metadata
  financial_exposure: number;
  severity: number;
  compromised?: boolean; // Managed locally
}

export interface DependencyEdge {
  source_id: string;
  target_id: string;
  exposure_weight: number;
}

/** Aggregated risk verdict metrics */
export interface VerdictMetrics {
  slippage: number | null;
  expectedLoss: number | null;
  action: string | null;
  warnings?: string[];
  dataProvenance?: string | Record<string, string> | null;
}

/** A single terminal log entry */
export interface TerminalLogEntry {
  id: number;
  timestamp: number; // Date.now()
  message: string;
}
