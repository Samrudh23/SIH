/**
 * Main Top Navigation Header for SIH26034
 * Government Legal Metrology enforcement theme with live/mock mode switcher.
 */

import { apiService } from "../services/api.js";

export function renderNavbar(activeRoute = "dashboard") {
  const currentMode = apiService.getMode();
  const isLive = currentMode === "live";

  const navLinks = [
    { route: "dashboard", label: "Dashboard", icon: `<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/></svg>` },
    { route: "new", label: "New Inspection", icon: `<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>` },
    { route: "compliance", label: "Compliance Engine", icon: `<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"/></svg>` },
    { route: "review", label: "Manual Review", icon: `<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></svg>` },
    { route: "history", label: "Inspection History", icon: `<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>` },
  ];

  return `
    <header class="bg-slate-900 border-b border-slate-800 text-white sticky top-0 z-40 shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          
          <!-- Logo & System Branding -->
          <div class="flex items-center gap-3">
            <a href="#/dashboard" class="flex items-center gap-3 text-white hover:text-slate-100 transition-colors">
              <div class="w-9 h-9 rounded-lg bg-blue-600 border border-blue-400 flex items-center justify-center font-bold text-white shadow-sm">
                <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/></svg>
              </div>
              <div>
                <div class="flex items-center gap-2">
                  <span class="font-bold text-sm tracking-tight">SIH26034</span>
                  <span class="text-[10px] uppercase font-mono px-1.5 py-0.2 bg-slate-800 text-blue-300 border border-slate-700 rounded">PCR 2011</span>
                </div>
                <div class="text-[11px] text-slate-400">Legal Metrology Compliance Scanner</div>
              </div>
            </a>
          </div>

          <!-- Primary Navigation Tabs -->
          <nav class="hidden md:flex items-center space-x-1">
            ${navLinks
              .map((link) => {
                const isActive = activeRoute === link.route;
                const activeClass = isActive
                  ? "bg-slate-800 text-white font-semibold border-b-2 border-blue-500"
                  : "text-slate-300 hover:bg-slate-800 hover:text-white font-medium";
                return `
                <a href="#/${link.route}" 
                   class="flex items-center gap-1.5 px-3 py-2 rounded-md text-xs transition-colors ${activeClass}">
                  ${link.icon}
                  <span>${link.label}</span>
                </a>
              `;
              })
              .join("")}
          </nav>

          <!-- System Status & Mode Toggle -->
          <div class="flex items-center gap-3">
            
            <!-- Live vs Mock Mode Switcher -->
            <div class="flex items-center bg-slate-800 border border-slate-700 rounded-lg p-0.5 text-[11px] font-mono">
              <button id="toggle-mock-btn" 
                      class="px-2.5 py-1 rounded transition-colors ${!isLive ? "bg-blue-600 text-white font-bold shadow" : "text-slate-400 hover:text-slate-200"}"
                      title="11 Realistic Compliance Mock Fixtures">
                Mock Data
              </button>
              <button id="toggle-live-btn" 
                      class="px-2.5 py-1 rounded transition-colors ${isLive ? "bg-emerald-600 text-white font-bold shadow" : "text-slate-400 hover:text-slate-200"}"
                      title="Connect directly to P3 FastAPI at localhost:8000/api">
                Live Backend
              </button>
            </div>

            <!-- Inspector Badge -->
            <div class="hidden sm:flex items-center gap-1.5 px-2.5 py-1 bg-slate-800/80 rounded-md border border-slate-700 text-xs text-slate-300 font-mono">
              <span class="w-2 h-2 rounded-full ${apiService.isBackendOnline ? "bg-emerald-400" : "bg-amber-400"}"></span>
              <span>insp_delhi_01</span>
            </div>

          </div>

        </div>
      </div>
    </header>
  `;
}
