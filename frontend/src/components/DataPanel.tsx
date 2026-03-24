"use client";

/**
 * DataPanel.tsx — Right Pane: Tabbed Data Workspace
 *
 * PURPOSE: Orchestrates the full right-column workspace. Shows 5 tabs matching the UX spec:
 *   1. Diagnosis   — AI health report (always available after upload)
 *   2. Plan        — Cleaning plan action cards (available after cleaning)
 *   3. Preview     — Side-by-side raw vs cleaned (available after cleaning)
 *   4. Metrics     — F1/Accuracy or MAE/R² (available after cleaning + target)
 *   5. Downloads   — Handled by the DownloadBar pinned to the bottom
 *
 * PATTERN: "Lifting state up" — all data state lives in page.tsx (parent).
 *   This component is purely presentational: it receives data as props and
 *   calls callbacks to request changes.
 */

import CleaningPlanPane from "./CleaningPlanPane";
import PreviewComparePane from "./PreviewComparePane";
import MetricsPane from "./MetricsPane";
import KnowledgeBasePane from "./KnowledgeBasePane";
import DownloadBar from "./DownloadBar";
import { TabId } from "@/lib/schemas";
import * as api from "@/lib/api";

type TabIdLocal = TabId; // avoid collision if needed

interface DataPanelProps {
  activeTab: TabId;
  onTabChange: (tab: TabId) => void;
  activeDataset: any;
  cleanedDataset: any;
  generatedPlan: { plan: any; explanation: string } | null; // plan before execution
  diagnosticReport: string | null;
  isAnalyzing: boolean;
  isPlanLoading: boolean;     // spinner for Approve & Clean
  isCleaning: boolean;
  onRunDiagnostics: () => void;
  onGeneratePlan: () => void; // Step 1: generate plan only
  onRunRefinery: (enabledActions: string[]) => void; // Step 2: execute plan
  onClose: () => void;
  showAdvanced?: boolean;
  usedKb?: boolean;
}

// ── Tab strip button ────────────────────────────────────────────────────────────
interface TabButtonProps {
  id: TabId; label: string; activeTab: TabId;
  color: "blue" | "orange" | "emerald" | "purple" | "violet";
  onClick: (id: TabId) => void;
  disabled?: boolean;
  badge?: string;
}

function TabButton({ id, label, activeTab, color, onClick, disabled, badge }: TabButtonProps) {
  const isActive = activeTab === id;
  const colorMap: Record<typeof color, string> = {
    blue:    isActive ? "border-blue-500 text-blue-300"    : "border-transparent text-slate-500 hover:text-slate-300",
    orange:  isActive ? "border-orange-500 text-orange-300" : "border-transparent text-slate-500 hover:text-slate-300",
    emerald: isActive ? "border-emerald-500 text-emerald-300" : "border-transparent text-slate-500 hover:text-slate-300",
    purple:  isActive ? "border-purple-500 text-purple-300" : "border-transparent text-slate-500 hover:text-slate-300",
    violet:  isActive ? "border-violet-500 text-violet-300" : "border-transparent text-slate-500 hover:text-slate-300",
  };
  return (
    <button
      onClick={() => !disabled && onClick(id)}
      disabled={disabled}
      className={`py-2.5 px-3 text-[11px] font-semibold border-b-2 whitespace-nowrap tracking-wide uppercase transition-all relative disabled:opacity-30 disabled:cursor-not-allowed ${colorMap[color]}`}
      aria-selected={isActive}
      role="tab"
    >
      {label}
      {badge && (
        <span className="absolute -top-0.5 -right-1.5 w-1.5 h-1.5 rounded-full bg-emerald-400" />
      )}
    </button>
  );
}

export default function DataPanel({
  activeTab, onTabChange,
  activeDataset, cleanedDataset,
  generatedPlan,
  diagnosticReport, isAnalyzing, isPlanLoading, isCleaning,
  onRunDiagnostics, onGeneratePlan, onRunRefinery, onClose,
  showAdvanced = false,
  usedKb = false,
}: DataPanelProps) {

  const isPostClean = !!cleanedDataset;
  const columns: string[] = activeDataset?.fingerprint?.columns ?? [];

  return (
    <div className="flex flex-col h-full overflow-hidden bg-[#0b1120]">

      {/* ── Tab Strip ── */}
      <div
        role="tablist"
        className="flex items-center gap-0.5 px-3 border-b border-white/5 bg-[#0d1117] flex-shrink-0 overflow-x-auto"
      >
        <TabButton id="diagnostics" label="Diagnosis"  activeTab={activeTab} color="blue"    onClick={onTabChange} />
        <TabButton id="plan"        label="Plan"        activeTab={activeTab} color="orange"  onClick={onTabChange} badge={isPostClean ? "new" : undefined} />
        <TabButton id="dashboard"   label="Dashboard 📊" activeTab={activeTab} color="emerald" onClick={onTabChange} />
        <TabButton id="metrics"     label="Metrics"     activeTab={activeTab} color="violet"  onClick={onTabChange} />
        <TabButton id="code"        label="Code 💻"     activeTab={activeTab} color="purple"  onClick={onTabChange} />

        {/* Spacer + Close button */}
        <div className="flex-1" />
        <button
          onClick={onClose}
          className="p-1 rounded text-slate-600 hover:text-slate-400 transition-colors"
          aria-label="Close data panel"
        >
          ✕
        </button>
      </div>

      {/* ── Tab Content (fills remaining height) ── */}
      <div className="flex-1 overflow-hidden flex flex-col">

        {/* ════ TAB: DIAGNOSIS ════ */}
        {activeTab === "diagnostics" && (
          <div className="flex-1 flex flex-col overflow-hidden p-4 gap-3">
            {/* Header row */}
            <div className="flex items-center justify-between flex-shrink-0">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-blue-500" />
                <span className="text-[12px] font-semibold text-slate-300">AI Health Report</span>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20 font-mono">
                  {activeDataset?.shape?.[0]?.toLocaleString() ?? "?"} rows × {activeDataset?.shape?.[1] ?? "?"} cols
                </span>
              </div>
              {!diagnosticReport && !isAnalyzing && (
                <button
                  onClick={onRunDiagnostics}
                  id="run-diagnosis-btn"
                  className="flex items-center gap-1.5 px-3 py-1.5 text-[11px] bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-all font-medium"
                >
                  🔬 Run Diagnosis
                </button>
              )}
              {diagnosticReport && (
                <button
                  onClick={onGeneratePlan}
                  disabled={isPlanLoading}
                  className="flex items-center gap-1.5 px-3 py-1.5 text-[11px] bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white rounded-lg transition-all font-semibold shadow-lg shadow-blue-600/20"
                >
                  {isPlanLoading ? (
                    <span className="w-3 h-3 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  ) : (
                    <>🚀 {"Approve & Clean"}</>
                  )}
                </button>
              )}
            </div>
            {/* Report or placeholder */}
            <div className="flex-1 overflow-y-auto custom-scrollbar">
              {isAnalyzing ? (
                <div className="flex flex-col items-center justify-center h-full gap-3">
                  <div className="flex gap-1">
                    {[0, 0.15, 0.3].map((d, i) => (
                      <div key={i} className="w-2 h-2 rounded-full bg-blue-500 animate-bounce" style={{ animationDelay: `${d}s` }} />
                    ))}
                  </div>
                  <p className="text-[11px] text-slate-500">Analyzing dataset patterns...</p>
                </div>
              ) : diagnosticReport ? (
                <div className="p-4 bg-[#070d18] rounded-xl border border-white/5">
                  <pre className="text-[11px] text-slate-300 leading-relaxed whitespace-pre-wrap font-mono">
                    {diagnosticReport}
                  </pre>

                  {/* CTA: start cleaning moved to top right */}
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center h-full gap-3 text-center">
                  <div className="w-10 h-10 rounded-full bg-blue-500/10 flex items-center justify-center text-xl">🔬</div>
                  <p className="text-[12px] text-slate-500">Run the AI Diagnostic to see a health report</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ════ TAB: PLAN ════ */}
        {activeTab === "plan" && (
          <CleaningPlanPane
            cleaningReport={
              generatedPlan?.plan
                ? JSON.stringify(generatedPlan.plan)
                : cleanedDataset?.plan
                ? JSON.stringify(cleanedDataset.plan)
                : null
            }
            explanation={generatedPlan?.explanation ?? cleanedDataset?.explanation ?? null}
            onApprove={onRunRefinery}
            isCleaning={isCleaning}
            showJsonPlan={showAdvanced}
            pythonCode={cleanedDataset?.python_code ?? null}
          />
        )}

        {/* ════ TAB: DASHBOARD ════ */}
        {activeTab === "dashboard" && (
          <PreviewComparePane
            rawDataset={activeDataset}
            cleanedDataset={cleanedDataset}
            explanation={cleanedDataset?.explanation ?? null}
          />
        )}

        {/* ════ TAB: METRICS ════ */}
        {activeTab === "metrics" && (
          <MetricsPane
            cleanedFilePath={cleanedDataset?.file_path ?? null}
            showAdvanced={showAdvanced}
          />
        )}

        {/* ════ TAB: KB (BRAIN) ════ */}
        {activeTab === "kb" && (
          <KnowledgeBasePane />
        )}

        {/* ════ TAB: CODE ════ */}
        {activeTab === "code" && (
          <div className="flex-1 flex flex-col overflow-hidden p-4 gap-3">
            <div className="flex items-center justify-between flex-shrink-0">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-purple-500" />
                <span className="text-[12px] font-semibold text-slate-300">Python Cleaning Script</span>
                {usedKb && (
                  <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 font-mono flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                    KB MATCH
                  </span>
                )}
              </div>
              
              {cleanedDataset?.python_code && !usedKb && (
                <button
                  onClick={async () => {
                    try {
                      await api.learnPattern(
                        activeDataset?.fingerprint?.columns ?? [],
                        cleanedDataset.python_code,
                        "Learned custom cleaning pattern",
                        activeDataset?.fileName ?? "unknown"
                      );
                      alert("Pattern staged for review! Once verified, it will be reused for similar files.");
                    } catch (err: any) {
                      alert("Error teaching AI: " + err.message);
                    }
                  }}
                  className="px-2 py-1 bg-purple-600/20 hover:bg-purple-600/40 text-purple-300 text-[10px] font-semibold rounded border border-purple-500/30 transition-all flex items-center gap-1"
                >
                  🧠 Teach AI this logic
                </button>
              )}
            </div>

            <div className="flex-1 overflow-auto bg-[#070d18] border border-white/5 rounded-xl p-4 custom-scrollbar">
              {cleanedDataset?.python_code ? (
                <pre className="text-[11px] text-emerald-400/80 leading-relaxed whitespace-pre font-mono">
                  {cleanedDataset.python_code}
                </pre>
              ) : (
                <div className="flex flex-col items-center justify-center h-full gap-3 text-center">
                  <div className="w-10 h-10 rounded-full bg-purple-500/10 flex items-center justify-center text-xl">💻</div>
                  <p className="text-[12px] text-slate-500">No cleaning code found. Run the refinery first.</p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* ── DownloadBar — always pinned to bottom ── */}
      <DownloadBar
        cleanedFilePath={cleanedDataset?.file_path ?? null}
        pythonScript={cleanedDataset?.python_code ?? null}
        diagnosticReport={diagnosticReport}
        cleanedExplanation={cleanedDataset?.explanation ?? null}
      />
    </div>
  );
}
