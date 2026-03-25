import { useState, useRef, useEffect } from "react";

/**
 * ModelSelector.tsx — Groq Model Dropdown
 *
 * PURPOSE: Lets the user pick which free Groq AI model to use.
 *   The selection is persisted in sessionStorage so it survives navigation
 *   but resets on a new tab.
 *
 * PROPS:
 *   value    — currently selected model ID string
 *   onChange — callback when user picks a different model
 */

export const FREE_MODELS = [
  // --- Groq Models ---
  {
    id: "llama-3.3-70b-versatile",
    label: "Llama 3.3 70B",
    provider: "Groq",
    desc: "Powerful reasoning — best for structured JSON plans",
    badge: "Recommended",
    color: "text-emerald-400",
  },
  {
    id: "llama-3.1-8b-instant",
    label: "Llama 3.1 8B",
    provider: "Groq",
    desc: "Lightning fast — perfect for quick data chats",
    badge: "Fast",
    color: "text-blue-400",
  },
  {
    id: "mixtral-8x7b-32768",
    label: "Mixtral 8x7B",
    provider: "Groq",
    desc: "Strong MoE capability",
    badge: null,
    color: "text-purple-400",
  },
  // --- OpenRouter Models ---
  {
    id: "google/gemini-2.0-flash-exp:free",
    label: "Gemini 2.0 Flash",
    provider: "OpenRouter",
    desc: "Google's next-gen multimodal model",
    badge: "New",
    color: "text-blue-500",
  },
  {
    id: "stepfun/step-1-8k",
    label: "Step-1 (Step-Fun)",
    provider: "OpenRouter",
    desc: "Step-Fun's balanced reasoning model",
    badge: "Step-Fun",
    color: "text-orange-500",
  },
  {
    id: "deepseek/deepseek-chat",
    label: "DeepSeek Chat",
    provider: "OpenRouter",
    desc: "High-performance chat model",
    badge: "Popular",
    color: "text-cyan-400",
  },
  {
    id: "meta-llama/llama-3.1-405b-instruct:free",
    label: "Llama 3.1 405B",
    provider: "OpenRouter",
    desc: "Massive scale open models",
    badge: "Elite",
    color: "text-emerald-500",
  },
];

interface ModelSelectorProps {
  value: string;
  onChange: (modelId: string) => void;
  /** If true, renders as a compact inline pill instead of a full dropdown */
  compact?: boolean;
}

export default function ModelSelector({ value, onChange, compact = false }: ModelSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const current = FREE_MODELS.find((m) => m.id === value) ?? FREE_MODELS[0];

  // Close when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  if (compact) {
    // Compact mode: used inside Chat header
    return (
      <div className="relative" ref={containerRef}>
        <button 
          onClick={() => setIsOpen(!isOpen)}
          className={`flex items-center gap-1.5 px-2 py-1 bg-white/5 border rounded-lg text-[11px] transition-all select-none active:scale-95 ${
            isOpen ? "border-blue-500/50 bg-blue-500/10 text-slate-100" : "border-white/10 text-slate-300 hover:text-slate-100 hover:bg-white/10 hover:border-white/20"
          }`}
        >
          <span className={`w-1.5 h-1.5 rounded-full bg-current ${current.color}`} />
          <span className="font-semibold">{current.label}</span>
          <svg className={`w-3 h-3 text-slate-500 transition-transform duration-200 ${isOpen ? "rotate-180 text-blue-400" : ""}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        {/* Dropdown — appears on click */}
        {isOpen && (
          <div className="absolute top-full right-0 mt-1.5 z-[100] w-[260px] bg-[#111827] border border-white/10 rounded-xl shadow-[0_20px_50px_rgba(0,0,0,0.5)] overflow-hidden animate-in fade-in slide-in-from-top-1 duration-200 backdrop-blur-md">
            {FREE_MODELS.map((model) => (
              <button
                key={model.id}
                onClick={() => {
                  onChange(model.id);
                  setIsOpen(false);
                }}
                className={`w-full text-left px-3 py-2.5 hover:bg-white/5 transition-colors flex items-start gap-2.5 border-b border-white/5 last:border-0 ${
                  value === model.id ? "bg-white/10" : ""
                }`}
              >
                <span className={`w-1.5 h-1.5 rounded-full mt-1.5 flex-shrink-0 ${model.color}`} />
                <div className="min-w-0">
                  <div className="flex items-center gap-1.5">
                    <span className="text-[11px] font-semibold text-slate-200">{model.label}</span>
                    {model.badge && (
                      <span className="text-[9px] px-1.5 py-0.5 bg-emerald-500/15 text-emerald-400 rounded font-medium">
                        {model.badge}
                      </span>
                    )}
                  </div>
                  <p className="text-[10px] text-slate-600 mt-0.5">{model.desc}</p>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>
    );
  }

  // Full mode: used in Settings or Landing
  return (
    <div className="flex flex-col gap-2">
      <label className="text-[11px] font-semibold text-slate-500 uppercase tracking-wide">AI Model</label>
      <div className="grid gap-2">
        {FREE_MODELS.map((model) => (
          <button
            key={model.id}
            onClick={() => onChange(model.id)}
            className={`flex items-center gap-3 px-3 py-2.5 rounded-xl border text-left transition-all ${
              value === model.id
                ? "border-blue-500/30 bg-blue-500/5 shadow-[0_0_20px_rgba(59,130,246,0.1)]"
                : "border-white/5 bg-white/[0.02] hover:bg-white/[0.04]"
            }`}
          >
            <span className={`w-2 h-2 rounded-full flex-shrink-0 ${model.color} ${value === model.id ? "ring-2 ring-offset-1 ring-offset-[#0d1117] ring-current shadow-[0_0_10px_currentColor]" : ""}`} />
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2">
                <span className="text-[12px] font-semibold text-slate-200">{model.label}</span>
                {model.badge && (
                  <span className="text-[9px] px-1.5 py-0.5 bg-emerald-500/15 text-emerald-400 rounded font-medium">
                    {model.badge}
                  </span>
                )}
              </div>
              <p className="text-[11px] text-slate-500">{model.desc}</p>
            </div>
            {value === model.id && (
              <svg className="w-4 h-4 text-blue-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M5 13l4 4L19 7" />
              </svg>
            )}
          </button>
        ))}
      </div>
    </div>
  );
}
