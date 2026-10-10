// ---------------------------------------------------------------------------
// API communication utilities
// ---------------------------------------------------------------------------

import { AnalyzeRequest, AnalyzeResponse } from "./types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

/**
 * POST /api/analyze — send a token address for risk analysis.
 * Returns the parsed AnalyzeResponse or throws on failure.
 */
export async function analyzeToken(
  address: string
): Promise<AnalyzeResponse> {
  const body: AnalyzeRequest = { token_address: address };

  const res = await fetch(`${API_BASE_URL}/api/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Backend error (${res.status}): ${text}`);
  }

  return res.json() as Promise<AnalyzeResponse>;
}

/**
 * GET /api/health — simple liveness check.
 */
export async function checkHealth(): Promise<{ status: string }> {
  const res = await fetch(`${API_BASE_URL}/api/health`);

  if (!res.ok) {
    throw new Error(`Health check failed (${res.status})`);
  }

  return res.json() as Promise<{ status: string }>;
}
