/**
 * Main Top Navigation Header for SIH26034
 * Professional regulatory inspection workstation shell.
 * Features responsive mobile drawer, mode toggles, and live P3 connection telemetry.
 */

import { apiService } from "../services/api.js";

export function renderNavbar(activeRoute = "dashboard") {
  const currentMode = apiService.getMode();
  const isLive = currentMode === "live";

  const navLinks = [
    {
      route: "dashboard",
      label: "Dashboard",
      icon: `<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/></svg>`,
    },
    {
      route: "new",
      label: "New Inspection",
      icon: `<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/></svg>`,
    },
    {
      route: "compliance",
      label: "Compliance Engine",
      icon: `<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"/></svg>`,
    },
    {
      route: "review",
      label: "Manual Review",
      icon: `<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></svg>`,
    },
    {
      route: "history",
      label: "Inspection History",
      icon: `<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>`,
    },
  ];

  return `
    <header class="bg-slate-900 border-b border-slate-800 text-white sticky top-0 z-40 shadow-sm" role="banner">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          
          <!-- System Branding & Identifier -->
          <div class="flex items-center gap-3">
            <a href="#/dashboard" 
               class="flex items-center gap-3 text-white hover:text-slate-100 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 rounded-lg p-1"
               aria-label="SIH26034 Legal Metrology Compliance Scanner Dashboard">
              <div class="w-9 h-9 rounded-lg bg-blue-700 border border-blue-500 flex items-center justify-center font-bold text-white shadow-sm flex-shrink-0" aria-hidden="true">
                <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
                </svg>
              </div>
              <div>
                <div class="flex items-center gap-2">
                  <span class="font-bold text-sm tracking-tight">SIH26034</span>
                  <span class="text-[10px] uppercase font-mono px-1.5 py-0.2 bg-slate-800 text-blue-300 border border-slate-700 rounded font-semibold">PCR 2011</span>
                </div>
                <div class="text-[11px] text-slate-400 truncate">Legal Metrology Compliance Scanner</div>
              </div>
            </a>
          </div>

          <!-- Desktop Navigation Links -->
          <nav class="hidden md:flex items-center space-x-1" aria-label="Primary Navigation">
            ${navLinks
              .map((link) => {
                const isActive = activeRoute === link.route;
                const activeClass = isActive
                  ? "bg-slate-800 text-white font-semibold border-b-2 border-blue-500"
                  : "text-slate-300 hover:bg-slate-800 hover:text-white font-medium";
                return `
                <a href="#/${link.route}" 
                   class="flex items-center gap-1.5 px-3 py-2 rounded-md text-xs transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 ${activeClass}"
                   ${isActive ? 'aria-current="page"' : ""}>
                  ${link.icon}
                  <span>${link.label}</span>
                </a>
              `;
              })
              .join("")}
          </nav>

          <!-- System Status & Controls -->
          <div class="flex items-center gap-2.5">
            
            <!-- Live vs Mock Mode Switcher -->
            ${
              apiService.allowMock
                ? `
              <div class="flex items-center bg-slate-800 border border-slate-700 rounded-lg p-0.5 text-[11px] font-mono">
                <button id="toggle-live-btn" 
                        class="px-2.5 py-1 rounded transition-colors focus:outline-none focus:ring-1 focus:ring-blue-400 ${isLive ? "bg-emerald-600 text-white font-bold shadow" : "text-slate-400 hover:text-slate-200"}"
                        title="Connect directly to P3 FastAPI backend">
                  Real Backend
                </button>
                <button id="toggle-mock-btn" 
                        class="px-2.5 py-1 rounded transition-colors focus:outline-none focus:ring-1 focus:ring-blue-400 ${!isLive ? "bg-blue-600 text-white font-bold shadow" : "text-slate-400 hover:text-slate-200"}"
                        title="11 Realistic Compliance Mock Fixtures (Development Only)">
                  Mock Data
                </button>
              </div>
            `
                : `
              <div class="px-2.5 py-1 rounded bg-emerald-950/80 border border-emerald-500 text-emerald-300 text-[11px] font-mono font-bold">
                PRODUCTION: REAL API
              </div>
            `
            }

            <!-- Backend Connection Status Pill -->
            <div class="hidden sm:flex items-center gap-1.5 px-2.5 py-1 bg-slate-800/80 rounded-md border border-slate-700 text-xs text-slate-300 font-mono" 
                 title="${apiService.isBackendOnline ? 'Backend Online at ' + apiService.baseUrl : 'Backend Offline'}">
              <span class="w-2 h-2 rounded-full ${apiService.isBackendOnline ? "bg-emerald-400 animate-pulse" : "bg-rose-500"}"></span>
              <span>${apiService.isBackendOnline ? "P3 API Online" : "P3 Disconnected"}</span>
            </div>

            <!-- Inspector Station Badge -->
            <div class="hidden lg:flex items-center gap-1.5 px-2.5 py-1 bg-slate-800/80 rounded-md border border-slate-700 text-xs text-slate-400 font-mono">
              <span class="w-1.5 h-1.5 rounded-full bg-blue-400"></span>
              <span>insp_delhi_01</span>
            </div>

            <!-- Mobile Navigation Menu Toggle -->
            <button type="button" 
                    id="mobile-menu-btn" 
                    class="md:hidden p-2 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    aria-expanded="false" 
                    aria-controls="mobile-nav-drawer"
                    aria-label="Toggle navigation menu">
              <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
              </svg>
            </button>

          </div>

        </div>
      </div>

      <!-- Mobile Navigation Drawer -->
      <div id="mobile-nav-drawer" 
           class="hidden md:hidden border-t border-slate-800 bg-slate-900 px-4 pt-2 pb-4 space-y-1" 
           aria-label="Mobile Navigation">
        ${navLinks
          .map((link) => {
            const isActive = activeRoute === link.route;
            const activeClass = isActive
              ? "bg-slate-800 text-white font-semibold border-l-4 border-blue-500"
              : "text-slate-300 hover:bg-slate-800 hover:text-white font-medium";
            return `
            <a href="#/${link.route}" 
               class="flex items-center gap-2.5 px-3 py-2.5 rounded-md text-sm transition-colors ${activeClass}"
               ${isActive ? 'aria-current="page"' : ""}>
              ${link.icon}
              <span>${link.label}</span>
            </a>
          `;
          })
          .join("")}

        <div class="pt-3 mt-2 border-t border-slate-800 flex items-center justify-between text-xs font-mono text-slate-400">
          <div class="flex items-center gap-1.5">
            <span class="w-2 h-2 rounded-full ${apiService.isBackendOnline ? "bg-emerald-400" : "bg-rose-500"}"></span>
            <span>${apiService.isBackendOnline ? "API Online" : "API Offline"}</span>
          </div>
          <span>Inspector: insp_delhi_01</span>
        </div>
      </div>
    </header>
  `;
}
