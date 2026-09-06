/**
 * Dashboard View (Screen 1) for SIH26034
 * Operational KPI cards, top violated compliance rules, quick fixture loader, and recent inspection queue.
 */

import { apiService } from "../services/api.js";
import { renderResultBadge, renderWorkflowBadge } from "../components/StatusBadge.js";
import { MOCK_FIXTURES } from "../services/mockFixtures.js";

export async function renderDashboardView() {
  const summary = await apiService.getDashboardSummary();
  const currentMode = apiService.getMode();

  return `
    <div class="space-y-6 animate-in fade-in duration-150">
      
      <!-- Page Header & Operational Bar -->
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-2 border-b border-slate-200">
        <div>
          <h1 class="text-2xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <span>Enforcement Compliance Dashboard</span>
            <span class="text-xs px-2.5 py-0.5 rounded-full font-mono font-medium ${currentMode === "live" ? "bg-emerald-100 text-emerald-800" : "bg-blue-100 text-blue-800"}">
              ${currentMode === "live" ? "LIVE API MODE" : "MOCK FIXTURE MODE"}
            </span>
          </h1>
          <p class="text-xs text-slate-500 mt-1">
            Monitoring packaged-commodity declarations under the Legal Metrology (Packaged Commodities) Rules, 2011.
          </p>
        </div>

        <!-- Action Buttons -->
        <div class="flex flex-wrap items-center gap-2.5">
          
          <!-- Quick Fixture Selector -->
          <div class="relative">
            <select id="quick-fixture-select" 
                    class="bg-white border border-slate-300 text-slate-700 text-xs rounded-lg px-3 py-2 font-mono hover:border-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-sm">
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
          </div>

          <a href="#/new" 
             class="inline-flex items-center gap-1.5 px-4 py-2 bg-blue-700 hover:bg-blue-800 text-white text-xs font-semibold rounded-lg shadow transition-colors">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
            <span>New Package Inspection</span>
          </a>
        </div>
      </div>

      <!-- Operational KPI Cards Grid -->
      <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3.5">
        
        <!-- Total -->
        <div class="bg-white border border-slate-200 rounded-xl p-4 shadow-sm hover:border-slate-300 transition-colors">
          <div class="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Total Scans</div>
          <div class="text-2xl font-bold font-mono text-slate-900 mt-1">${summary.total_inspections}</div>
          <div class="text-[11px] text-slate-400 mt-0.5">Recorded inspections</div>
        </div>

        <!-- Compliant -->
        <div class="bg-white border border-emerald-200 rounded-xl p-4 shadow-sm hover:border-emerald-300 transition-colors">
          <div class="text-[11px] font-semibold text-emerald-700 uppercase tracking-wider flex items-center gap-1">
            <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
            Compliant
          </div>
          <div class="text-2xl font-bold font-mono text-emerald-900 mt-1">${summary.compliant_inspections}</div>
          <div class="text-[11px] text-emerald-600 mt-0.5">Satisfies PCR 2011</div>
        </div>

        <!-- Potential Violations -->
        <div class="bg-white border border-rose-200 rounded-xl p-4 shadow-sm hover:border-rose-300 transition-colors">
          <div class="text-[11px] font-semibold text-rose-700 uppercase tracking-wider flex items-center gap-1">
            <span class="w-2 h-2 rounded-full bg-rose-500"></span>
            Violations
          </div>
          <div class="text-2xl font-bold font-mono text-rose-900 mt-1">${summary.potential_violations}</div>
          <div class="text-[11px] text-rose-600 mt-0.5">Statutory non-compliance</div>
        </div>

        <!-- Needs Manual Review -->
        <div class="bg-white border border-amber-200 rounded-xl p-4 shadow-sm hover:border-amber-300 transition-colors">
          <div class="text-[11px] font-semibold text-amber-700 uppercase tracking-wider flex items-center gap-1">
            <span class="w-2 h-2 rounded-full bg-amber-500"></span>
            Manual Review
          </div>
          <div class="text-2xl font-bold font-mono text-amber-900 mt-1">${summary.needs_manual_review}</div>
          <div class="text-[11px] text-amber-600 mt-0.5">Inspector verification</div>
        </div>

        <!-- Not Applicable -->
        <div class="bg-white border border-slate-200 rounded-xl p-4 shadow-sm hover:border-slate-300 transition-colors">
          <div class="text-[11px] font-semibold text-slate-600 uppercase tracking-wider flex items-center gap-1">
            <span class="w-2 h-2 rounded-full bg-slate-400"></span>
            Not Applicable
          </div>
          <div class="text-2xl font-bold font-mono text-slate-800 mt-1">${summary.not_applicable}</div>
          <div class="text-[11px] text-slate-500 mt-0.5">Exempt / MDR 2017</div>
        </div>

        <!-- Pipeline Failures -->
        <div class="bg-white border border-pink-200 rounded-xl p-4 shadow-sm hover:border-pink-300 transition-colors">
          <div class="text-[11px] font-semibold text-pink-700 uppercase tracking-wider flex items-center gap-1">
            <span class="w-2 h-2 rounded-full bg-pink-500"></span>
            Analysis Failed
          </div>
          <div class="text-2xl font-bold font-mono text-pink-900 mt-1">${summary.analysis_failed}</div>
          <div class="text-[11px] text-pink-600 mt-0.5">Image quality errors</div>
        </div>

      </div>

      <!-- Main Columns: Top Violated Rules & Recent Inspections -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        <!-- Left: Top Violated Rules (Operational Analytics) -->
        <div class="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-4">
          <div class="flex items-center justify-between">
            <h3 class="text-sm font-bold text-slate-900 tracking-tight">Top Flagged Rules</h3>
            <span class="text-[11px] font-mono text-slate-400">15 MVP Rules</span>
          </div>

          <div class="space-y-3">
            ${summary.top_violated_rules
              .map(
                (rule, idx) => `
              <div class="space-y-1">
                <div class="flex items-center justify-between text-xs">
                  <span class="font-mono font-bold text-slate-800">${rule.rule_id}</span>
                  <span class="font-mono text-slate-500 text-[11px]">${rule.count} flags</span>
                </div>
                <div class="text-xs text-slate-600 truncate">${rule.rule_name}</div>
                <div class="w-full bg-slate-100 rounded-full h-1.5 overflow-hidden">
                  <div class="bg-rose-500 h-1.5 rounded-full" style="width: ${Math.min(100, rule.count * 30)}%"></div>
                </div>
              </div>
            `
              )
              .join("")}
          </div>

          <div class="p-3 bg-slate-50 border border-slate-200 rounded-lg text-xs text-slate-600 space-y-1">
            <div class="font-semibold text-slate-800 flex items-center gap-1">
              <svg class="w-3.5 h-3.5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
              Inspection Notice
            </div>
            <p class="text-[11px] leading-relaxed">
              Date code overwriting and missing consumer helpline contact numbers remain the most frequent statutory infractions detected across retail inspections.
            </p>
          </div>
        </div>

        <!-- Right: Recent Inspections Table -->
        <div class="lg:col-span-2 bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-4">
          <div class="flex items-center justify-between">
            <div>
              <h3 class="text-sm font-bold text-slate-900 tracking-tight">Recent Inspection Queue</h3>
              <p class="text-xs text-slate-500">Live feed of scanned packages ready for review</p>
            </div>
            <a href="#/history" class="text-xs font-semibold text-blue-700 hover:text-blue-800">View All History &rarr;</a>
          </div>

          <div class="overflow-x-auto">
            <table class="w-full text-left text-xs border-collapse">
              <thead>
                <tr class="border-b border-slate-200 text-slate-500 font-semibold bg-slate-50/50">
                  <th class="py-2.5 px-3">Inspection ID</th>
                  <th class="py-2.5 px-3">Product / Commodity</th>
                  <th class="py-2.5 px-3">Compliance Status</th>
                  <th class="py-2.5 px-3">Workflow State</th>
                  <th class="py-2.5 px-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-100">
                ${summary.recent_inspections.slice(0, 7).map((item) => `
                  <tr class="hover:bg-slate-50 transition-colors">
                    <td class="py-3 px-3 font-mono font-medium text-slate-800">${item.id}</td>
                    <td class="py-3 px-3">
                      <div class="font-semibold text-slate-900">${escapeHtml(item.product_name || "Unspecified")}</div>
                      <div class="text-[11px] text-slate-500 font-mono">${escapeHtml(item.brand_name || "Unknown Brand")} &bull; ${escapeHtml(item.commodity_category || "Commodity")}</div>
                    </td>
                    <td class="py-3 px-3">
                      ${renderResultBadge(item.compliance_status || "PENDING", "sm")}
                    </td>
                    <td class="py-3 px-3">
                      ${renderWorkflowBadge(item.status)}
                    </td>
                    <td class="py-3 px-3 text-right">
                      <a href="#/compliance/${item.id}" 
                         class="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-slate-100 hover:bg-blue-50 text-slate-700 hover:text-blue-700 font-medium text-xs border border-slate-200 transition-colors">
                        <span>Inspect</span>
                        <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
                      </a>
                    </td>
                  </tr>
                `).join("")}
              </tbody>
            </table>
          </div>
        </div>

      </div>

    </div>
  `;
}

function escapeHtml(str) {
  return String(str || "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}
