"use client";

/**
 * WorkflowLayout.tsx — Main Desktop Two-Pane Layout
 *
 * PURPOSE: Houses the Chat (left) and Data panels (right) side by side.
 *   Also provides global keyboard shortcuts and the Help modal.
 *
 * KEYBOARD SHORTCUTS:
 *   U — focus / trigger upload (calls onUploadTrigger)
 *   C — start cleaning (calls onClean)
 *   D — toggle Preview diff (switches to preview tab)
 *   ? — open Help modal
 *   Esc — close Help modal
 */

import { useEffect, useCallback, useState } from "react";
import HelpModal from "./HelpModal";

interface WorkflowLayoutProps {
  left: React.ReactNode;
  right: React.ReactNode;
  onUploadTrigger?: () => void;
  onClean?: () => void;
  onToggleDiff?: () => void;
}

export default function WorkflowLayout({
  left,
  right,
  onUploadTrigger,
  onClean,
  onToggleDiff,
}: WorkflowLayoutProps) {
  const [helpOpen, setHelpOpen] = useState(false);

  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      // Don't fire shortcuts when user is typing in an input/textarea
      const target = e.target as HTMLElement;
      if (["INPUT", "TEXTAREA", "SELECT"].includes(target.tagName)) return;

      switch (e.key) {
        case "?":
          e.preventDefault();
          setHelpOpen((v) => !v);
          break;
        case "Escape":
          setHelpOpen(false);
          break;
        case "u":
        case "U":
          if (e.altKey) {
            e.preventDefault();
            onUploadTrigger?.();
          }
          break;
        case "c":
        case "C":
          if (e.altKey) {
            e.preventDefault();
            onClean?.();
          }
          break;
        case "d":
        case "D":
          if (e.altKey) {
            e.preventDefault();
            onToggleDiff?.();
          }
          break;
      }
    },
    [onUploadTrigger, onClean, onToggleDiff]
  );

  useEffect(() => {
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [handleKeyDown]);

  const [leftWidth, setLeftWidth] = useState(380);
  const [isResizing, setIsResizing] = useState(false);

  const startResizing = useCallback(() => {
    setIsResizing(true);
  }, []);

  const stopResizing = useCallback(() => {
    setIsResizing(false);
  }, []);

  const resize = useCallback(
    (e: MouseEvent) => {
      if (!isResizing) return;
      const newWidth = e.clientX - 240; // Sidebar is ~240 or 60
      if (newWidth > 300 && newWidth < 800) {
        setLeftWidth(newWidth);
      }
    },
    [isResizing]
  );

  useEffect(() => {
    if (isResizing) {
      window.addEventListener("mousemove", resize);
      window.addEventListener("mouseup", stopResizing);
    } else {
      window.removeEventListener("mousemove", resize);
      window.removeEventListener("mouseup", stopResizing);
    }
    return () => {
      window.removeEventListener("mousemove", resize);
      window.removeEventListener("mouseup", stopResizing);
    };
  }, [isResizing, resize, stopResizing]);

  return (
    <>
      <HelpModal isOpen={helpOpen} onClose={() => setHelpOpen(false)} />

      <div className={`flex flex-1 overflow-hidden ${isResizing ? "select-none cursor-col-resize" : ""}`}>
        {/* LEFT: Chat */}
        <div 
          className="flex flex-col min-h-0 flex-shrink-0"
          style={{ width: `${leftWidth}px` }}
        >
          {left}
        </div>

        {/* RESIZER DIVIDER */}
        <div
          onMouseDown={startResizing}
          className={`
            w-1 hover:w-1.5 transition-all cursor-col-resize flex-shrink-0 bg-white/5 
            hover:bg-blue-500/50 z-10
            ${isResizing ? "bg-blue-500/50 w-1.5" : ""}
          `}
        />

        {/* RIGHT: Data Panels */}
        <div className="flex flex-col min-h-0 flex-1 overflow-hidden border-l border-white/5">
          {right}
        </div>
      </div>

      {/* Keyboard hints bar — visible at bottom */}
      <div className="flex-shrink-0 hidden md:flex items-center gap-4 px-4 py-1.5 border-t border-white/5 bg-[#080e1a]">
        {[
          { key: "Alt+U", label: "Upload" },
          { key: "Alt+C", label: "Clean" },
          { key: "Alt+D", label: "Diff" },
          { key: "?", label: "Help" },
        ].map(({ key, label }) => (
          <div key={key} className="flex items-center gap-1">
            <kbd className="px-1.5 py-0.5 text-[9px] font-bold bg-white/5 border border-white/10 rounded text-slate-500 font-mono">{key}</kbd>
            <span className="text-[10px] text-slate-700">{label}</span>
          </div>
        ))}
      </div>
    </>
  );
}
