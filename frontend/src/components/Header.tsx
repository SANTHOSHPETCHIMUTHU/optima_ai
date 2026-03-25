"use client";

import ModelSelector from "./ModelSelector";

interface HeaderProps {
  fileName?: string;                      // Current active dataset filename (if any)
  onMobileMenuToggle: () => void;         // Opens/closes sidebar on mobile
  isSidebarOpen: boolean;
  theme: "dark" | "light";
  onThemeToggle: () => void;
  onLogout: () => void;
  user?: any;
}

export default function Header({ fileName, onMobileMenuToggle, theme, onThemeToggle, onLogout, user }: HeaderProps) {
  const userName = user?.user_metadata?.full_name || user?.email?.split("@")[0] || "User";
  const userAvatar = user?.user_metadata?.avatar_url;

  return (
    <header className="h-[64px] flex items-center justify-between px-4 md:px-6 bg-[#0d1117] border-b border-white/5 flex-shrink-0 z-10">

      {/* ── Left Side: Mobile menu + breadcrumb ── */}
      <div className="flex items-center gap-3">
        {/* Mobile-only hamburger */}
        <button
          onClick={onMobileMenuToggle}
          className="p-2 rounded-lg text-slate-500 hover:text-slate-300 hover:bg-white/5 transition-colors md:hidden"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>

        {/* Breadcrumb: "Data Refinery" > filename if active */}
        <div className="flex items-center gap-2 text-[13px]">
          <span className="font-semibold text-slate-200">Data Refinery</span>
          {fileName && (
            <>
              <svg className="w-3.5 h-3.5 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7" />
              </svg>
              <span className="text-slate-400 bg-white/5 px-2 py-0.5 rounded-md border border-white/5 font-mono text-[11px] max-w-[160px] truncate">
                {fileName}
              </span>
            </>
          )}
        </div>
      </div>

      {/* ── Right Side ── */}
      <div className="flex items-center gap-3">
        {/* Theme Toggle */}
        <button
          onClick={onThemeToggle}
          title={theme === "dark" ? "Switch to Light Mode" : "Switch to Dark Mode"}
          className="p-1.5 rounded-lg text-slate-500 hover:text-slate-300 hover:bg-white/5 transition-colors"
        >
          {theme === "dark" ? (
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364-6.364l-.707.707M6.343 17.657l-.707.707m12.728 0l-.707-.707M6.343 6.343l-.707-.707M12 5a7 7 0 100 14 7 7 0 000-14z" />
            </svg>
          ) : (
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
            </svg>
          )}
        </button>

        {/* User Profile */}
        <div className="flex items-center gap-2 pl-2 border-l border-white/5">
          {userAvatar ? (
            <img src={userAvatar} alt={userName} className="w-6 h-6 rounded-full border border-white/10" />
          ) : (
            <div className="w-6 h-6 rounded-full bg-gradient-to-br from-purple-500/20 to-blue-500/20 border border-white/10 flex items-center justify-center">
              <span className="text-[10px] font-bold text-slate-400 capitalize">{userName.charAt(0)}</span>
            </div>
          )}
          <span className="text-[11px] font-medium text-slate-400 hidden lg:block max-w-[100px] truncate">
            {userName}
          </span>
        </div>

        {/* Logout Button */}
        <button
          onClick={onLogout}
          title="Sign Out"
          className="p-1.5 rounded-lg text-slate-500 hover:text-red-400 hover:bg-red-500/10 transition-colors"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
          </svg>
        </button>

        {/* Status indicator dot */}
        <div className="flex items-center gap-1.5 text-[11px] text-slate-500 ml-2">
          <span className={`w-1.5 h-1.5 rounded-full ${fileName ? "bg-emerald-500 animate-pulse" : "bg-slate-600"}`} />
          {fileName ? "Active" : "Ready"}
        </div>
      </div>
    </header>
  );
}
