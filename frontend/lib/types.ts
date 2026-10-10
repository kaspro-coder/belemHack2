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
  slippage: number;
  expected_loss: number;
  action: string;
}

/** A single dependency layer in the 5-layer model */
export interface DependencyLayer {
  id: number;
  name: string;
  label: string;
  tvl: number; // mock Total Value Locked (illustrative)
  severity: number; // 0.0 – 1.0  (illustrative)
  compromised: boolean;
}

/** Aggregated risk verdict metrics */
export interface VerdictMetrics {
  slippage: number | null;
  expectedLoss: number | null;
  action: string | null;
}

/** A single terminal log entry */
export interface TerminalLogEntry {
  id: number;
  timestamp: number; // Date.now()
  message: string;
}
