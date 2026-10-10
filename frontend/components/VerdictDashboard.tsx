"use client";

import { VerdictMetrics } from "@/lib/types";

interface VerdictDashboardProps {
  verdict: VerdictMetrics;
}



export default function VerdictDashboard({ verdict }: VerdictDashboardProps) {
  return (
    <section className="border border-black p-6">
      <h2 className="text-lg font-bold mb-4">RISK ASSESSMENT / VERDICT</h2>
      <p className="text-xs mb-4 text-black">
        Illustrative mock output — not a real trading recommendation.
      </p>

      <div className="border border-black">
        {/* Row 1: Slippage */}
        <div className="border-b border-black px-4 py-3">
          <div className="text-xs font-bold mb-1">SLIPPAGE COST</div>
          <div className="text-xl font-mono font-bold">
            {verdict && verdict.slippage !== null ? `${(verdict.slippage * 100).toFixed(2)}%` : "N/A"}
          </div>
        </div>

        {/* Row 2: Expected Loss */}
        <div className="border-b border-black px-4 py-3">
          <div className="text-xs font-bold mb-1">EXPECTED LOSS</div>
          <div className="text-xl font-mono font-bold">
            {verdict && verdict.expectedLoss !== null ? `$${verdict.expectedLoss.toLocaleString("en-US", { minimumFractionDigits: 0 })}` : "N/A"}
          </div>
        </div>

        {/* Row 3: Action */}
        <div className="px-4 py-3 border-b border-black">
          <div className="text-xs font-bold mb-1">RECOMMENDED ACTION</div>
          <div className="text-xl font-mono font-bold">
            {verdict && verdict.action ? verdict.action : "N/A"}
          </div>
        </div>
      </div>

      {/* Row 4: Warnings & Provenance (Transparency Section) */}
      {(verdict.warnings?.length || verdict.dataProvenance) ? (
        <div className="mt-6 border border-black px-4 py-3">
          
          {verdict.dataProvenance && (
            <div className="mb-4">
              <div className="text-xs font-bold mb-2">[ DATA PROVENANCE ]</div>
              {typeof verdict.dataProvenance === "string" ? (
                <div className="text-sm font-mono font-bold">{verdict.dataProvenance}</div>
              ) : (
                <ul className="text-sm font-mono font-bold space-y-1">
                  {Object.entries(verdict.dataProvenance).map(([key, val]) => (
                    <li key={key}>
                      <span className="uppercase">{key}:</span> {val}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )}

          {verdict.warnings && verdict.warnings.length > 0 && (
            <div>
              <div className="text-xs font-bold mb-2">[ SYSTEM WARNINGS ]</div>
              <ul className="list-disc list-inside text-xs text-black font-mono">
                {verdict.warnings.map((w, i) => (
                  <li key={i} className="mb-1">{w}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      ) : null}
    </section>
  );
}
