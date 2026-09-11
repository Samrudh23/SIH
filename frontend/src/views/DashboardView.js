/**
 * Enforcement Dashboard View (Screen 1) for SIH26034
 * Restructured as an action-oriented regulatory inspection workstation.
 * Prioritizes: "What requires the inspector's attention?" over generic analytics.
 * Benchmarked against Refero enterprise data tables, compact metrics, and audit queues.
 */

import { apiService } from "../services/api.js";
import { renderResultBadge, renderWorkflowBadge } from "../components/StatusBadge.js";

function escapeHtml(str) {
  return String(str || "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

export async function renderDashboardView() {
  let summary;
  const currentMode = apiService.getMode();

  try {
    summary = await apiService.getDashboardSummary();
  } catch (err) {
    return `
      <div class="space-y-6">
        <div class="p-6 bg-rose-50 border border-rose-200 rounded-xl max-w-2xl mx-auto space-y-4 shadow-sm text-center">
          <div class="w-12 h-12 mx-auto rounded-full bg-rose-100 text-rose-700 flex items-center justify-center font-bold">
            <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
            </svg>
          </div>
          <div>
            <h2 class="text-base font-bold text-rose-900">Backend API Offline or Unreachable</h2>
            <p class="text-xs text-rose-700 mt-1">${escapeHtml(err.message)}</p>
          </div>
          ${
            err.actionableRemedy
              ? `<div class="text-xs text-slate-700 bg-white p-3 rounded-lg border border-rose-200 font-mono text-left space-y-1">
                  <div class="font-bold text-slate-800">Actionable Remedy:</div>
                  <div>${escapeHtml(err.actionableRemedy)}</div>
                  <div class="text-[11px] text-slate-500 mt-1">Command to start backend: <code>python -m uvicorn app.main:app --port 8000</code></div>
                </div>`
              : ""
          }
          <div class="flex items-center justify-center gap-3 pt-2">
            <button onclick="window.location.reload()" 
                    class="px-4 py-2 bg-blue-700 text-white rounded-lg text-xs font-bold hover:bg-blue-800 shadow-sm transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500">
              Retry Connection
            </button>
            ${
              apiService.allowMock
                ? `<button onclick="apiService.setMode('mock'); window.location.reload();" 
                           class="px-4 py-2 border border-slate-300 bg-white text-slate-700 rounded-lg text-xs font-semibold hover:bg-slate-50 shadow-sm transition-colors focus:outline-none focus:ring-2 focus:ring-slate-400">
                     Switch to Mock Mode (Dev Only)
                   </button>`
                : ""
            }
          </div>
        </div>
      </div>
    `;
  }

  const attentionCount = (summary.needs_manual_review || 0) + (summary.potential_violations || 0);
  const recentList = summary.recent_inspections || [];

  return `
    <div class="space-y-6">
      
      <!-- Screen Header & Top Action Bar -->
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-3 border-b border-slate-200">
        <div>
          <div class="flex items-center gap-2 mb-1">
            <span class="text-xs font-mono font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-700 border border-slate-200">
              STATION: DELHI-01
            </span>
            <span class="text-xs px-2 py-0.5 rounded font-mono font-medium ${
              currentMode === "live" ? "bg-emerald-100 text-emerald-800" : "bg-blue-100 text-blue-800"
            }">
              ${currentMode === "live" ? "LIVE P3 API" : "LOCAL FIXTURES"}
            </span>
          </div>
          <h1 class="text-xl font-bold text-slate-900 tracking-tight">
            Inspection Screening Workstation
          </h1>
          <p class="text-xs text-slate-500 mt-0.5">
            Packaged commodity statutory declarations screening under Legal Metrology (Packaged Commodities) Rules, 2011.
          </p>
        </div>

        <!-- Action Controls -->
        <div class="flex flex-wrap items-center gap-2.5">
          ${
            currentMode === "mock"
              ? `<!-- Quick Scenario Selector (Dev/Mock Mode Only) -->
            <div class="relative">
              <label for="quick-fixture-select" class="sr-only">Jump to test scenario</label>
              <select id="quick-fixture-select" 
                      class="bg-white border border-slate-300 text-slate-700 text-xs rounded-lg px-3 py-2 font-mono hover:border-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-sm"
                      aria-label="Jump to realistic test scenario">
                <option value="">⚡ Jump to Test Scenario...</option>
                <option value="insp-001">1. Fully Compliant (Parle-G 100g)</option>
                <option value="insp-002">2. Potential Violation (Berry Jam)</option>
                <option value="insp-003">3. Low OCR Confidence (Masala Chai)</option>
                <option value="insp-004">4. Conflicting MRP (Basmati Rice)</option>
                <option value="insp-005">5. Conflicting Net Qty (Cashews)</option>
                <option value="insp-006">6. Medical Device Pending Gate</option>
                <option value="insp-007">7. Confirmed Medical Device</option>
                <option value="insp-008">8. Incomplete Surface Coverage</option>
                <option value="insp-009">9. Technical Analysis Failed</option>
                <option value="insp-010">10. Small Pack Exemption (0.5g)</option>
                <option value="insp-011">11. Pan Masala Special Router</option>
              </select>
            </div>`
              : `<a href="#/history" 
                    class="inline-flex items-center gap-1.5 px-3 py-2 border border-slate-300 bg-white hover:bg-slate-50 text-slate-700 text-xs font-semibold rounded-lg shadow-sm transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500">
                  <svg class="w-4 h-4 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                  <span>Inspection Archive</span>
                </a>`
          }

          <a href="#/new" 
             class="inline-flex items-center gap-1.5 px-4 py-2 bg-blue-700 hover:bg-blue-800 text-white text-xs font-bold rounded-lg shadow transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
            <span>New Package Inspection</span>
          </a>
        </div>
      </div>

      <!-- Priority Inspector Attention Banner (If issues pending) -->
      ${
        attentionCount > 0
          ? `
        <div class="bg-amber-50 border border-amber-200 rounded-xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-sm">
          <div class="flex items-start sm:items-center gap-3">
            <div class="w-8 h-8 rounded-lg bg-amber-100 border border-amber-300 flex items-center justify-center text-amber-800 flex-shrink-0 mt-0.5 sm:mt-0">
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
              </svg>
            </div>
            <div>
              <h2 class="text-xs font-bold text-amber-950 uppercase tracking-wide">
                Items Requiring Inspector Verification (${attentionCount})
              </h2>
              <p class="text-xs text-amber-800 mt-0.5">
                ${summary.needs_manual_review} package(s) have unresolved conflicts or low OCR certainty; ${summary.potential_violations} have flagged statutory non-compliance.
              </p>
            </div>
          </div>
          <div class="flex items-center gap-2 flex-shrink-0">
            <a href="#/history" 
               class="px-3 py-1.5 bg-amber-800 hover:bg-amber-900 text-white text-xs font-bold rounded-lg shadow-sm transition-colors focus:outline-none focus:ring-2 focus:ring-amber-500">
              Review Flagged Queue &rarr;
            </a>
          </div>
        </div>
      `
          : ""
      }

      <!-- Operational Status Overview (Restrained Refero Metric Strip) -->
      <section aria-label="Operational Status Overview">
        <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2.5">
          
          <!-- Total -->
          <div class="bg-white border border-slate-200 rounded-lg p-3 shadow-sm hover:border-slate-300 transition-colors">
            <div class="text-[10px] font-semibold text-slate-500 uppercase tracking-wider">Total Scans</div>
            <div class="text-xl font-bold font-mono text-slate-900 mt-0.5">${summary.total_inspections}</div>
            <div class="text-[10px] text-slate-400 font-mono">audited packages</div>
          </div>

          <!-- Compliant -->
          <div class="bg-white border border-emerald-200 rounded-lg p-3 shadow-sm hover:border-emerald-300 transition-colors">
            <div class="text-[10px] font-semibold text-emerald-700 uppercase tracking-wider flex items-center gap-1">
              <span class="w-1.5 h-1.5 rounded-full bg-emerald-500" aria-hidden="true"></span>
              Compliant
            </div>
            <div class="text-xl font-bold font-mono text-emerald-900 mt-0.5">${summary.compliant_inspections}</div>
            <div class="text-[10px] text-emerald-600 font-mono">satisfies PCR 2011</div>
          </div>

          <!-- Potential Violations -->
          <div class="bg-white border border-rose-200 rounded-lg p-3 shadow-sm hover:border-rose-300 transition-colors">
            <div class="text-[10px] font-semibold text-rose-700 uppercase tracking-wider flex items-center gap-1">
              <span class="w-1.5 h-1.5 rounded-full bg-rose-500" aria-hidden="true"></span>
              Violations
            </div>
            <div class="text-xl font-bold font-mono text-rose-900 mt-0.5">${summary.potential_violations}</div>
            <div class="text-[10px] text-rose-600 font-mono">statutory breach</div>
          </div>

          <!-- Needs Manual Review -->
          <div class="bg-white border border-amber-200 rounded-lg p-3 shadow-sm hover:border-amber-300 transition-colors">
            <div class="text-[10px] font-semibold text-amber-700 uppercase tracking-wider flex items-center gap-1">
              <span class="w-1.5 h-1.5 rounded-full bg-amber-500" aria-hidden="true"></span>
              Manual Review
            </div>
            <div class="text-xl font-bold font-mono text-amber-900 mt-0.5">${summary.needs_manual_review}</div>
            <div class="text-[10px] text-amber-600 font-mono">conflicts & ambiguity</div>
          </div>

          <!-- Not Applicable -->
          <div class="bg-white border border-slate-200 rounded-lg p-3 shadow-sm hover:border-slate-300 transition-colors">
            <div class="text-[10px] font-semibold text-slate-600 uppercase tracking-wider flex items-center gap-1">
              <span class="w-1.5 h-1.5 rounded-full bg-slate-400" aria-hidden="true"></span>
              Not Applicable
            </div>
            <div class="text-xl font-bold font-mono text-slate-800 mt-0.5">${summary.not_applicable}</div>
            <div class="text-[10px] text-slate-500 font-mono">exempt / MDR 2017</div>
          </div>

          <!-- Pipeline Failures -->
          <div class="bg-white border border-pink-200 rounded-lg p-3 shadow-sm hover:border-pink-300 transition-colors">
            <div class="text-[10px] font-semibold text-pink-700 uppercase tracking-wider flex items-center gap-1">
              <span class="w-1.5 h-1.5 rounded-full bg-pink-500" aria-hidden="true"></span>
              Failed Vision
            </div>
            <div class="text-xl font-bold font-mono text-pink-900 mt-0.5">${summary.analysis_failed || 0}</div>
            <div class="text-[10px] text-pink-600 font-mono">technical image error</div>
          </div>

        </div>
      </section>

      <!-- Main Workstation Layout: Priority Inspection Queue & Infraction Analysis -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        <!-- Left 2 Cols: Recent Inspection Queue (Primary Workstation Task Table) -->
        <div class="lg:col-span-2 bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-3">
          <div class="flex items-center justify-between pb-2 border-b border-slate-100">
            <div>
              <h2 class="text-sm font-bold text-slate-900 tracking-tight">Recent Inspection Queue</h2>
              <p class="text-xs text-slate-500">Active inspections ready for statutory evaluation or review sign-off</p>
            </div>
            <a href="#/history" class="text-xs font-bold text-blue-700 hover:text-blue-800 focus:outline-none focus:underline">
              Full Archive &rarr;
            </a>
          </div>

          <!-- Desktop Table View -->
          <div class="hidden sm:block overflow-x-auto">
            <table class="w-full text-left text-xs border-collapse" aria-label="Recent Inspections">
              <thead>
                <tr class="border-b border-slate-200 text-slate-500 font-semibold bg-slate-50/50">
                  <th class="py-2.5 px-3">ID</th>
                  <th class="py-2.5 px-3">Commodity / Product</th>
                  <th class="py-2.5 px-3">Screening Status</th>
                  <th class="py-2.5 px-3">Workflow State</th>
                  <th class="py-2.5 px-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-100">
                ${recentList.slice(0, 8).map((item) => {
                  const isReview = item.compliance_status === "NEEDS_MANUAL_REVIEW";
                  return `
                  <tr class="hover:bg-slate-50/80 transition-colors ${isReview ? "bg-amber-50/30" : ""}">
                    <td class="py-3 px-3 font-mono font-bold text-slate-800">
                      ${escapeHtml(item.id)}
                    </td>
                    <td class="py-3 px-3">
                      <div class="font-bold text-slate-900">${escapeHtml(item.product_name || "Unspecified")}</div>
                      <div class="text-[11px] text-slate-500 font-mono">
                        ${escapeHtml(item.brand_name || "Generic")} &bull; ${escapeHtml(item.commodity_category || "General")}
                      </div>
                    </td>
                    <td class="py-3 px-3">
                      ${renderResultBadge(item.compliance_status || "PENDING", "sm")}
                    </td>
                    <td class="py-3 px-3">
                      ${renderWorkflowBadge(item.status)}
                    </td>
                    <td class="py-3 px-3 text-right">
                      ${
                        isReview
                          ? `<a href="#/review/${item.id}" 
                                class="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-amber-100 hover:bg-amber-200 text-amber-900 font-bold text-xs border border-amber-300 transition-colors focus:outline-none focus:ring-2 focus:ring-amber-500">
                               <span>Review</span>
                               <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
                             </a>`
                          : `<a href="#/compliance/${item.id}" 
                                class="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-slate-100 hover:bg-blue-50 text-slate-700 hover:text-blue-700 font-medium text-xs border border-slate-200 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500">
                               <span>Inspect</span>
                               <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
                             </a>`
                      }
                    </td>
                  </tr>
                `;
                }).join("")}
              </tbody>
            </table>
          </div>

          <!-- Mobile Card-Stack Fallback (< 640px) -->
          <div class="sm:hidden space-y-2.5">
            ${recentList.slice(0, 6).map((item) => `
              <div class="p-3 rounded-lg border border-slate-200 bg-slate-50/50 space-y-2">
                <div class="flex items-center justify-between">
                  <span class="font-mono text-xs font-bold text-slate-800">${escapeHtml(item.id)}</span>
                  ${renderResultBadge(item.compliance_status || "PENDING", "sm")}
                </div>
                <div>
                  <div class="text-xs font-bold text-slate-900">${escapeHtml(item.product_name || "Unspecified")}</div>
                  <div class="text-[11px] text-slate-500 font-mono">${escapeHtml(item.brand_name || "")} &bull; ${escapeHtml(item.commodity_category || "")}</div>
                </div>
                <div class="flex items-center justify-between pt-1 border-t border-slate-100">
                  ${renderWorkflowBadge(item.status)}
                  <a href="#/compliance/${item.id}" class="text-xs font-bold text-blue-700 hover:underline">
                    Inspect &rarr;
                  </a>
                </div>
              </div>
            `).join("")}
          </div>

        </div>

        <!-- Right Col: Top Flagged Infractions (Refero Audit Distribution) -->
        <div class="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-4">
          <div class="flex items-center justify-between pb-2 border-b border-slate-100">
            <div>
              <h2 class="text-sm font-bold text-slate-900 tracking-tight">Top Flagged Infractions</h2>
              <p class="text-xs text-slate-500">Statutory clauses most frequently violated</p>
            </div>
            <span class="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-100 text-slate-600">PCR 2011</span>
          </div>

          <div class="space-y-3">
            ${summary.top_violated_rules.map((rule) => `
              <div class="space-y-1">
                <div class="flex items-center justify-between text-xs">
                  <span class="font-mono font-bold text-slate-800">${escapeHtml(rule.rule_id)}</span>
                  <span class="font-mono text-rose-700 text-[11px] font-semibold">${rule.count} infractions</span>
                </div>
                <div class="text-xs text-slate-600 truncate">${escapeHtml(rule.rule_name)}</div>
                <div class="w-full bg-slate-100 rounded-full h-1.5 overflow-hidden">
                  <div class="bg-rose-600 h-1.5 rounded-full" style="width: ${Math.min(100, rule.count * 30)}%"></div>
                </div>
              </div>
            `).join("")}
          </div>

          <div class="p-3 bg-slate-50 border border-slate-200 rounded-lg text-xs text-slate-600 space-y-1">
            <div class="font-semibold text-slate-800 flex items-center gap-1.5">
              <svg class="w-3.5 h-3.5 text-blue-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
              <span>Statutory Reminder</span>
            </div>
            <p class="text-[11px] leading-relaxed text-slate-600">
              Violations under Rule 6(1) (mandatory declarations) and Rule 6(2) (consumer care details) mandate official documentation prior to report generation.
            </p>
          </div>
        </div>

      </div>

    </div>
  `;
}
