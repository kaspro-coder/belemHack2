"use client";

import { DependencyLayer } from "@/lib/types";
import DependencyNode from "./DependencyNode";

interface DependencyGraphProps {
  layers: DependencyLayer[];
  onNodeClick: (layerId: string) => void;
  onReset: () => void;
  disabled: boolean;
}

export default function DependencyGraph({
  layers,
  onNodeClick,
  onReset,
  disabled,
}: DependencyGraphProps) {
  const nodeHeight = 44;
  const gap = 16;
  const nodeWidth = 320;
  const svgWidth = nodeWidth;
  const totalHeight = layers.length * nodeHeight + (layers.length - 1) * gap;

  return (
    <section className="border border-black p-6 mb-6">
      <div className="flex justify-between items-start mb-1">
        <div>
          <h2 className="text-lg font-bold">PROTOCOL DEPENDENCY MAP</h2>
          <p className="text-xs mb-4">5-LAYER RISK PROPAGATION MODEL</p>
        </div>
        <button
          onClick={onReset}
          disabled={disabled}
          className="border border-black px-4 py-1 text-xs font-bold
                     bg-white text-black
                     hover:bg-black hover:text-white
                     disabled:opacity-50 transition-colors"
        >
          [ RESET ]
        </button>
      </div>

      <div className="flex justify-center">
        <div className="relative" style={{ width: nodeWidth }}>
          {/* SVG connector lines behind nodes */}
          <svg
            className="absolute top-0 left-0 pointer-events-none"
            width={svgWidth}
            height={totalHeight}
            aria-hidden="true"
          >
            {layers.slice(0, -1).map((_, i) => {
              const y1 = i * (nodeHeight + gap) + nodeHeight;
              const y2 = (i + 1) * (nodeHeight + gap);
              return (
                <line
                  key={i}
                  x1={svgWidth / 2}
                  y1={y1}
                  x2={svgWidth / 2}
                  y2={y2}
                  stroke="#000000"
                  strokeWidth={1}
                />
              );
            })}
          </svg>

          {/* Nodes */}
          <div
            className="relative flex flex-col"
            style={{ gap: `${gap}px` }}
          >
            {layers.map((layer) => (
              <DependencyNode
                key={layer.id}
                layer={layer}
                onClick={onNodeClick}
                disabled={disabled}
              />
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
