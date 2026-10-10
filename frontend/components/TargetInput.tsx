"use client";

import { useState } from "react";

interface TargetInputProps {
  onAnalyze: (address: string) => Promise<void>;
  disabled: boolean;
}

export default function TargetInput({ onAnalyze, disabled }: TargetInputProps) {
  const [address, setAddress] = useState("");

  const handleSubmit = async () => {
    const trimmed = address.trim();
    if (!trimmed) return;
    await onAnalyze(trimmed);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !disabled) {
      handleSubmit();
    }
  };

  return (
    <section className="border border-black p-6 mb-6">
      <h1 className="text-2xl font-bold mb-2 tracking-wide">
        DEFI RISK DEPENDENCY ANALYZER
      </h1>
      <p className="text-sm mb-6">
        Analyze risk propagation across interconnected DeFi protocol layers.
        All outputs are illustrative — not financial advice.
      </p>

      <label htmlFor="token-address" className="block text-xs font-bold mb-1">
        TOKEN CONTRACT ADDRESS
      </label>
      <div className="flex gap-0">
        <input
          id="token-address"
          type="text"
          value={address}
          onChange={(e) => setAddress(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Enter Target Address"
          disabled={disabled}
          className="flex-1 border border-black px-3 py-2 text-sm
                     bg-white text-black placeholder-black/40
                     focus:outline focus:outline-1 focus:outline-black"
        />
        <button
          onClick={handleSubmit}
          disabled={disabled || !address.trim()}
          className="border border-black border-l-0 px-6 py-2 text-sm font-bold
                     bg-black text-white
                     hover:bg-white hover:text-black
                     disabled:opacity-50 disabled:hover:bg-black disabled:hover:text-white
                     transition-colors"
        >
          {disabled ? "[ ANALYZING... ]" : "[ ANALYZE ]"}
        </button>
      </div>
    </section>
  );
}
