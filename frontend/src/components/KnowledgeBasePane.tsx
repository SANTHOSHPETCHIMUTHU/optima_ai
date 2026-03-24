"use client";

import { useEffect, useState } from "react";
import * as api from "@/lib/api";

export default function KnowledgeBasePane() {
  const [patterns, setPatterns] = useState<{ verified_patterns: any[]; staged_patterns: any[] }>({
    verified_patterns: [],
    staged_patterns: [],
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchPatterns = async () => {
    try {
      setLoading(true);
      const data = await api.getPatterns();
      setPatterns(data);
      setError(null);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPatterns();
  }, []);

  const handleVerify = async (patternId: string) => {
    try {
      await api.verifyPattern(patternId);
      alert("Pattern logic verified and promoted to production!");
      fetchPatterns();
    } catch (err: any) {
      alert("Verification failed: " + err.message);
    }
  };

  if (loading && patterns.staged_patterns.length === 0) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin w-6 h-6 border-2 border-blue-500/30 border-t-blue-500 rounded-full" />
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col overflow-hidden p-6 custom-scrollbar">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <span className="text-xl">🧠</span> Knowledge Base (The Brain)
          </h2>
          <p className="text-[12px] text-slate-500">Manage learned cleaning patterns and logic.</p>
        </div>
        <button 
          onClick={fetchPatterns}
          className="p-2 hover:bg-white/5 rounded-lg text-slate-400 transition-colors"
          title="Refresh patterns"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>
      </div>

      <div className="flex-1 overflow-y-auto space-y-8 pr-2">
        {/* ── Staged Patterns ── */}
        <section>
          <div className="flex items-center gap-2 mb-4">
            <span className="text-[10px] uppercase font-bold tracking-widest text-orange-500 bg-orange-500/10 px-2 py-0.5 rounded border border-orange-500/20">
              Staged for Review ({patterns.staged_patterns.length})
            </span>
          </div>

          {patterns.staged_patterns.length === 0 ? (
            <div className="bg-[#0d1117] border border-dashed border-white/5 rounded-xl p-8 text-center">
              <p className="text-[13px] text-slate-600 italic">No new patterns awaiting review.</p>
            </div>
          ) : (
            <div className="grid gap-4">
              {patterns.staged_patterns.map((p) => (
                <div key={p.id} className="bg-[#1a2235] border border-white/5 rounded-xl overflow-hidden group">
                  <div className="p-4 border-b border-white/5 flex items-center justify-between">
                    <div>
                      <h3 className="text-[13px] font-semibold text-slate-200">{p.description}</h3>
                      <p className="text-[11px] text-slate-500 font-mono">Source: {p.source_file} • ID: {p.id}</p>
                    </div>
                    <button
                      onClick={() => handleVerify(p.id)}
                      className="px-4 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white text-[11px] font-bold rounded-lg transition-all shadow-lg shadow-emerald-600/20 flex items-center gap-1.5"
                    >
                      ✅ Verify & Promote
                    </button>
                  </div>
                  <div className="p-4 bg-black/40">
                    <p className="text-[10px] text-slate-600 uppercase font-bold mb-2 tracking-wider">Applicable Columns</p>
                    <div className="flex flex-wrap gap-1.5 mb-4">
                      {p.columns.map((col: string) => (
                        <span key={col} className="px-2 py-0.5 bg-white/5 text-slate-400 text-[10px] rounded font-mono border border-white/5">
                          {col}
                        </span>
                      ))}
                    </div>
                    <p className="text-[10px] text-slate-600 uppercase font-bold mb-2 tracking-wider">Generated Logic (Python)</p>
                    <pre className="bg-[#0d1117] p-3 rounded-lg text-[11px] font-mono text-blue-300 overflow-x-auto border border-white/5 max-h-40 custom-scrollbar">
                      {p.fix_code}
                    </pre>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* ── Verified Patterns ── */}
        <section>
          <div className="flex items-center gap-2 mb-4">
             <span className="text-[10px] uppercase font-bold tracking-widest text-emerald-500 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
              Verified & Active ({patterns.verified_patterns.length})
            </span>
          </div>

          {patterns.verified_patterns.length === 0 ? (
            <div className="bg-[#0d1117] border border-dashed border-white/5 rounded-xl p-8 text-center text-slate-600">
              No verified patterns in the active knowledge base.
            </div>
          ) : (
            <div className="grid gap-3 opacity-80 hover:opacity-100 transition-opacity">
              {patterns.verified_patterns.map((p) => (
                <div key={p.id} className="bg-[#111827] border border-white/5 rounded-xl p-3 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-emerald-500/10 flex items-center justify-center text-emerald-400">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                    <div>
                      <p className="text-[12px] font-medium text-slate-300">{p.description}</p>
                      <p className="text-[10px] text-slate-600 font-mono">Matched to {p.columns.length} columns</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                     <span className="text-[10px] text-slate-700 font-mono">{p.id}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
