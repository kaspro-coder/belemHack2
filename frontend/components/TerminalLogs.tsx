"use client";

import { useRef, useEffect, useState } from "react";
import { TerminalLogEntry } from "@/lib/types";

interface TerminalLogsProps {
  logs: TerminalLogEntry[];
  onClear: () => void;
}

export default function TerminalLogs({ logs, onClear }: TerminalLogsProps) {
  const bottomRef = useRef<HTMLDivElement>(null);
  const [isOpen, setIsOpen] = useState(false);

  // Auto-scroll to bottom when new logs arrive and the section is open
  useEffect(() => {
    if (isOpen && bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [logs, isOpen]);

  return (
    <section className="border border-black mb-6">
      <details
        open={isOpen}
        onToggle={(e) => setIsOpen((e.target as HTMLDetailsElement).open)}
      >
        <summary className="px-6 py-3 font-bold text-sm cursor-pointer select-none border-b border-black hover:bg-black hover:text-white transition-colors">
          {isOpen ? "[-] HIDE CALCULATION LOGS" : "[+] VIEW CALCULATION LOGS"}
        </summary>

        <div className="relative">
          {/* Clear button */}
          {logs.length > 0 && (
            <button
              onClick={onClear}
              className="absolute top-2 right-4 border border-black px-3 py-1
                         text-xs font-bold bg-white text-black
                         hover:bg-black hover:text-white transition-colors z-10"
            >
              [ CLEAR ]
            </button>
          )}

          <div className="px-6 py-4 max-h-64 overflow-y-auto bg-white">
            {logs.length === 0 ? (
              <p className="text-xs text-black/40">
                No logs yet. Run an analysis or simulate a hack.
              </p>
            ) : (
              <div className="space-y-0.5">
                {logs.map((entry) => (
                  <div key={entry.id} className="text-xs">
                    <span className="text-black/40 mr-2 select-none">
                      {new Date(entry.timestamp).toLocaleTimeString()}
                    </span>
                    <span>&gt; {entry.message}</span>
                  </div>
                ))}
              </div>
            )}
            <div ref={bottomRef} />
          </div>
        </div>
      </details>
    </section>
  );
}
