"use client";

import { VerdictMetrics } from "@/lib/types";

interface VerdictDashboardProps {
  verdict: VerdictMetrics;
}

function formatSlippage(value: number | null): string {
  if (value === null) return "—";
  return `${(value * 100).toFixed(2)}%`;
}

function formatLoss(value: number | null): string {
  if (value === null) return "—";
  return `$${value.toLocaleString("en-US", { minimumFractionDigits: 0 })}`;
}

function formatAction(value: string | null): string {
  if (value === null) return "—";
  return value;
}

export default function VerdictDashboard({ verdict }: VerdictDashboardProps) {
  return (
    <section className="border border-black p-6">
      <h2 className="text-lg font-bold mb-4">RISK ASSESSMENT / VERDICT</h2>
      <p className="text-xs mb-4 text-black/60">
        Illustrative mock output — not a real trading recommendation.
      </p>

      <div className="border border-black">
        {/* Row 1: Slippage */}
        <div className="border-b border-black px-4 py-3">
          <div className="text-xs font-bold mb-1">SLIPPAGE COST</div>
          <div className="text-xl font-bold">{formatSlippage(verdict.slippage)}</div>
        </div>

        {/* Row 2: Expected Loss */}
        <div className="border-b border-black px-4 py-3">
          <div className="text-xs font-bold mb-1">EXPECTED LOSS</div>
          <div className="text-xl font-bold">{formatLoss(verdict.expectedLoss)}</div>
        </div>

        {/* Row 3: Action */}
        <div className="px-4 py-3">
          <div className="text-xs font-bold mb-1">RECOMMENDED ACTION</div>
          <div className="text-xl font-bold">{formatAction(verdict.action)}</div>
        </div>
      </div>
    </section>
  );
}
