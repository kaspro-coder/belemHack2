"use client";

import { useState, useCallback, useRef } from "react";
import TargetInput from "@/components/TargetInput";
import DependencyGraph from "@/components/DependencyGraph";
import TerminalLogs from "@/components/TerminalLogs";
import VerdictDashboard from "@/components/VerdictDashboard";
import { TerminalLogEntry, VerdictMetrics } from "@/lib/types";
import { analyzeToken } from "@/lib/api";
import {
  getInitialLayers,
  getDefaultVerdict,
  simulateHack,
  computeVerdictFromLayers,
  getHackSimulationLogs,
} from "@/lib/simulation";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

let logIdCounter = 0;

function makeLogEntry(message: string): TerminalLogEntry {
  return { id: ++logIdCounter, timestamp: Date.now(), message };
}

/**
 * Append messages to the terminal one-by-one with a short delay.
 * Returns a cleanup function to cancel pending timers.
 */
function appendLogsWithDelay(
  messages: string[],
  setLogs: React.Dispatch<React.SetStateAction<TerminalLogEntry[]>>,
  delayMs = 120
): { promise: Promise<void>; cancel: () => void } {
  const timers: ReturnType<typeof setTimeout>[] = [];
  let cancelled = false;

  const promise = new Promise<void>((resolve) => {
    messages.forEach((msg, i) => {
      const timer = setTimeout(() => {
        if (!cancelled) {
          setLogs((prev) => [...prev, makeLogEntry(msg)]);
        }
        if (i === messages.length - 1) resolve();
      }, delayMs * (i + 1));
      timers.push(timer);
    });

    if (messages.length === 0) resolve();
  });

  const cancel = () => {
    cancelled = true;
    timers.forEach(clearTimeout);
  };

  return { promise, cancel };
}

// ---------------------------------------------------------------------------
// Page component
// ---------------------------------------------------------------------------

export default function HomePage() {
  const [layers, setLayers] = useState(getInitialLayers);
  const [logs, setLogs] = useState<TerminalLogEntry[]>([]);
  const [verdict, setVerdict] = useState<VerdictMetrics>(getDefaultVerdict);

  // Stores the most recent successful backend analysis result.
  // Used to restore the verdict after a simulation reset.
  const [baselineVerdict, setBaselineVerdict] = useState<VerdictMetrics | null>(
    null
  );

  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isSimulating, setIsSimulating] = useState(false);

  // Keep a ref to cancel pending log timers on unmount / new action
  const cancelRef = useRef<(() => void) | null>(null);

  // ------ ANALYZE ------
  const handleAnalyze = useCallback(
    async (address: string) => {
      if (isAnalyzing || isSimulating) return;

      // Cancel any pending log timers from a previous action
      cancelRef.current?.();
      setIsAnalyzing(true);

      const preMessages = [
        "Initializing risk analysis...",
        `Target address: ${address}`,
        "Pinging FastAPI backend...",
        "Sending analysis request...",
      ];

      const { promise: preDone, cancel: preCancel } = appendLogsWithDelay(
        preMessages,
        setLogs
      );
      cancelRef.current = preCancel;
      await preDone;

      try {
        const response = await analyzeToken(address);

        const postMessages = [
          "Connection successful...",
          "Fetching dependency data...",
          "Calculating slippage...",
          "Calculating expected loss...",
          "Analysis completed.",
        ];

        const { promise: postDone, cancel: postCancel } = appendLogsWithDelay(
          postMessages,
          setLogs
        );
        cancelRef.current = postCancel;
        await postDone;

        const newVerdict: VerdictMetrics = {
          slippage: response.slippage,
          expectedLoss: response.expected_loss,
          action: response.action,
        };
        setVerdict(newVerdict);
        setBaselineVerdict(newVerdict);

        // Reset layers to clean state after a fresh analysis
        setLayers(getInitialLayers());
      } catch (err: unknown) {
        const errMsg =
          err instanceof Error ? err.message : "Unknown error occurred";
        setLogs((prev) => [
          ...prev,
          makeLogEntry(`ERROR: ${errMsg}`),
          makeLogEntry("Analysis failed. Check that the backend is running."),
        ]);
      } finally {
        setIsAnalyzing(false);
      }
    },
    [isAnalyzing, isSimulating]
  );

  // ------ HACK SIMULATION ------
  const handleNodeClick = useCallback(
    (layerId: number) => {
      if (isAnalyzing || isSimulating) return;
      setIsSimulating(true);

      cancelRef.current?.();

      const layer = layers.find((l) => l.id === layerId);
      if (!layer) {
        setIsSimulating(false);
        return;
      }

      const updatedLayers = simulateHack(layerId, layers);
      setLayers(updatedLayers);

      const simVerdict = computeVerdictFromLayers(updatedLayers);
      setVerdict(simVerdict);

      const logMessages = getHackSimulationLogs(layer);
      const { promise, cancel } = appendLogsWithDelay(logMessages, setLogs);
      cancelRef.current = cancel;
      promise.then(() => setIsSimulating(false));
    },
    [layers, isAnalyzing, isSimulating]
  );

  // ------ RESET ------
  const handleReset = useCallback(() => {
    if (isAnalyzing || isSimulating) return;

    cancelRef.current?.();
    setLayers(getInitialLayers());

    // Restore the baseline analysis verdict if one exists,
    // otherwise fall back to the default placeholder dashboard.
    if (baselineVerdict) {
      setVerdict(baselineVerdict);
    } else {
      setVerdict(getDefaultVerdict());
    }

    setLogs((prev) => [...prev, makeLogEntry("Simulation reset.")]);
  }, [baselineVerdict, isAnalyzing, isSimulating]);

  // ------ CLEAR LOGS ------
  const handleClearLogs = useCallback(() => {
    setLogs([]);
  }, []);

  const busy = isAnalyzing || isSimulating;

  return (
    <main className="max-w-3xl mx-auto px-4 py-8">
      <TargetInput onAnalyze={handleAnalyze} disabled={busy} />
      <DependencyGraph
        layers={layers}
        onNodeClick={handleNodeClick}
        onReset={handleReset}
        disabled={busy}
      />
      <TerminalLogs logs={logs} onClear={handleClearLogs} />
      <VerdictDashboard verdict={verdict} />
    </main>
  );
}
