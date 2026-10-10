// ---------------------------------------------------------------------------
// Mock simulation logic — deterministic, no real blockchain data
//
// ALL VALUES ARE ILLUSTRATIVE. They do not represent actual DeFi risk
// estimates, TVL measurements, or trading recommendations.
// ---------------------------------------------------------------------------

import { DependencyLayer, VerdictMetrics } from "./types";

/**
 * Illustrative action threshold (USD).
 * If expectedLoss > ACTION_THRESHOLD the recommended action is EXIT,
 * otherwise STAY.  This threshold is arbitrary and exists solely to
 * demonstrate that both outcomes are reachable with the mock dataset.
 */
export const ACTION_THRESHOLD = 30_000;

/**
 * Default layer definitions.
 * TVL and severity values are illustrative mock data chosen so that
 * compromising a single low-severity layer produces STAY while
 * compromising a high-severity layer produces EXIT.
 */
const DEFAULT_LAYERS: DependencyLayer[] = [
  { id: "1", name: "SETTLEMENT", label: "LAYER 1 — SETTLEMENT", tvl: 500_000, financial_exposure: 500_000, severity: 0.3, compromised: false },
  { id: "2", name: "YIELD",      label: "LAYER 2 — YIELD",      tvl: 300_000, financial_exposure: 300_000, severity: 0.5, compromised: false },
  { id: "3", name: "ORACLE",     label: "LAYER 3 — ORACLE",     tvl: 100_000, financial_exposure: 100_000, severity: 1.0, compromised: false },
  { id: "4", name: "AMM",        label: "LAYER 4 — AMM",        tvl: 200_000, financial_exposure: 200_000, severity: 0.7, compromised: false },
  { id: "5", name: "LENDING",    label: "LAYER 5 — LENDING",    tvl: 150_000, financial_exposure: 150_000, severity: 0.8, compromised: false },
];

// Quick sanity: Layer 1 alone → 500000*0.3 = 150000 > 30000 → EXIT
//               Layer 3 alone → 100000*1.0 = 100000 > 30000 → EXIT
//               But we can still get STAY if no layers are compromised.

/** Return a fresh (deep-copied) set of initial layers. */
export function getInitialLayers(): DependencyLayer[] {
  return DEFAULT_LAYERS.map((l) => ({ ...l }));
}

/** Return the default "not yet analysed" verdict (null placeholders). */
export function getDefaultVerdict(): VerdictMetrics {
  return { slippage: null, expectedLoss: null, action: null };
}

/**
 * Simulate a hack on a single layer — toggles its compromised flag.
 * Returns the updated layers array (new references).
 */
export function simulateHack(
  layerId: string,
  layers: DependencyLayer[]
): DependencyLayer[] {
  return layers.map((l) =>
    l.id === layerId ? { ...l, compromised: !l.compromised } : { ...l }
  );
}

/**
 * Deterministic verdict computation from the current layer states.
 *
 * Formula:
 *   expectedLoss = Σ (tvl × severity)  for all compromised layers
 *   slippage     = expectedLoss / totalTVL   (clamped 0–1)
 *   action       = expectedLoss > ACTION_THRESHOLD ? "EXIT" : "STAY"
 *
 * These are illustrative calculations — not real financial advice.
 */
export function computeVerdictFromLayers(
  layers: DependencyLayer[]
): VerdictMetrics {
  const compromised = layers.filter((l) => l.compromised);

  if (compromised.length === 0) {
    return { slippage: 0, expectedLoss: 0, action: "STAY" };
  }

  const totalTVL = layers.reduce((sum, l) => sum + l.tvl, 0);
  const expectedLoss = compromised.reduce(
    (sum, l) => sum + l.tvl * l.severity,
    0
  );
  const slippage = Math.min(expectedLoss / totalTVL, 1);
  const action = expectedLoss > ACTION_THRESHOLD ? "EXIT" : "STAY";

  return { slippage, expectedLoss, action };
}

/**
 * Generate the terminal log messages for a hack simulation.
 * Uses the same tvl/severity values that the computation uses.
 */
export function getHackSimulationLogs(layer: DependencyLayer): string[] {
  const exposure = layer.tvl;
  const loss = layer.tvl * layer.severity;
  return [
    `Simulating Layer ${layer.id} ${layer.name} failure...`,
    `Fetching Layer ${layer.id} TVL...`,
    `Exposure: ${exposure}`,
    `Severity: ${layer.severity}`,
    `Calculating expected loss: ${exposure} * ${layer.severity} = ${loss}`,
    `Updating risk metrics...`,
    `Simulation completed.`,
  ];
}
