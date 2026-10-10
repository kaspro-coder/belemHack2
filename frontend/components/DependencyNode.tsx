"use client";

import { DependencyLayer } from "@/lib/types";

interface DependencyNodeProps {
  layer: DependencyLayer;
  onClick: (layerId: string) => void;
  disabled: boolean;
}

export default function DependencyNode({
  layer,
  onClick,
  disabled,
}: DependencyNodeProps) {
  return (
    <button
      onClick={() => onClick(layer.id)}
      disabled={disabled}
      title="Click to simulate hack"
      className={`w-full border border-black px-4 py-3 text-sm font-bold
                  text-left transition-colors
                  ${
                    layer.compromised
                      ? "bg-black text-white"
                      : "bg-white text-black hover:bg-black hover:text-white"
                  }
                  disabled:opacity-50`}
    >
      {layer.label}
      {layer.compromised && (
        <span className="ml-2 text-xs">[COMPROMISED]</span>
      )}
    </button>
  );
}
