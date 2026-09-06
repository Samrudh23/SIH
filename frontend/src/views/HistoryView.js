/**
 * Inspection History & Audit Archive View (Screen 7) for SIH26034
 * Search, filter, inspect past examinations, and identify unresolved manual review cases.
 */

import { apiService } from "../services/api.js";
import { renderResultBadge, renderWorkflowBadge } from "../components/StatusBadge.js";

export async function renderHistoryView(initialQuery = {}) {
  const result = await apiService.listInspections(initialQuery);
  const items = result.items || [];

  return `
    <div class="space-y-6 animate-in fade-in duration-150">
      
      <!-- Top Title & Search Header -->
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-2 border-b border-slate-200">
        <div>
          <h1 class="text-2xl font-bold text-slate-900 tracking-tight">Inspection History & Audit Archive</h1>
          <p class="text-xs text-slate-500 mt-1">Searchable repository of scanned packaged commodities and enforcement outcomes.</p>
        </div>

        <div class="flex items-center gap-2">
          <a href="#/new" class="px-4 py-2 bg-blue-700 hover:bg-blue-800 text-white rounded-lg text-xs font-bold shadow transition-colors flex items-center gap-1.5">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
            <span>New Inspection</span>
          </a>
        </div>
      </div>

      <!-- Search & Filter Controls -->
      <div class="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
        <form id="history-filter-form" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 text-xs">
          
          <!-- Search input -->
          <div>
            <label class="block font-semibold text-slate-700 mb-1">Search Product / Brand</label>
            <input type="text" id="history-search" placeholder="Filter by keyword..." 
                   class="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-slate-900 focus:bg-white focus:ring-2 focus:ring-blue-500 focus:outline-none" />
          </div>

          <!-- Compliance Status Filter -->
          <div>
            <label class="block font-semibold text-slate-700 mb-1">Compliance Status</label>
            <select id="history-status-filter" 
                    class="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-slate-900 focus:bg-white focus:ring-2 focus:ring-blue-500 focus:outline-none font-mono">
              <option value="">All Compliance States</option>
              <option value="COMPLIANT">Compliant Only</option>
              <option value="POTENTIAL_VIOLATION">Potential Violations Only</option>
              <option value="NEEDS_MANUAL_REVIEW">Needs Manual Review Only</option>
              <option value="NOT_APPLICABLE">Not Applicable / Exempt Only</option>
              <option value="ANALYSIS_FAILED">Analysis Failed Only</option>
            </select>
          </div>

          <!-- Workflow Status Filter -->
          <div>
            <label class="block font-semibold text-slate-700 mb-1">Workflow Lifecycle State</label>
            <select id="history-workflow-filter" 
                    class="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-slate-900 focus:bg-white focus:ring-2 focus:ring-blue-500 focus:outline-none font-mono">
              <option value="">All Workflow States</option>
              <option value="CREATED">Created</option>
              <option value="IMAGE_UPLOADED">Images Uploaded</option>
              <option value="ANALYSIS_COMPLETE">Analysis Complete</option>
              <option value="REPORT_GENERATED">Report Generated</option>
              <option value="FAILED">Failed</option>
            </select>
          </div>

          <!-- Actions -->
          <div class="flex items-end gap-2">
            <button type="submit" 
                    class="w-full px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-lg font-semibold shadow-sm transition-colors">
              Filter Archive
            </button>
            <button type="button" id="reset-history-filter" 
                    class="px-3 py-2 border border-slate-300 rounded-lg text-slate-600 hover:bg-slate-100 font-semibold transition-colors">
              Reset
            </button>
          </div>

        </form>
      </div>

      <!-- History Table -->
      <div class="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm">
        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs border-collapse">
            <thead>
              <tr class="border-b border-slate-200 bg-slate-50/50 text-slate-500 font-semibold">
                <th class="py-3 px-4 w-32">Inspection ID</th>
                <th class="py-3 px-4">Commodity Description</th>
                <th class="py-3 px-4 w-44">Compliance Status</th>
                <th class="py-3 px-4 w-36">Workflow State</th>
                <th class="py-3 px-4 w-36">Surfaces Covered</th>
                <th class="py-3 px-4 w-32">Inspector</th>
                <th class="py-3 px-4 w-28 text-right">Actions</th>
              </tr>
            </thead>
            <tbody id="history-table-body" class="divide-y divide-slate-100">
              ${
                items.length === 0
                  ? `
                <tr>
                  <td colspan="7" class="py-8 text-center text-slate-400 font-mono">
                    No inspections match the selected filters.
                  </td>
                </tr>
              `
                  : items
                      .map((item) => {
                        const cov = item.image_coverage || {};
                        const covText = [cov.front && "Front", cov.back && "Back", cov.side && "Side", cov.top && "Top"].filter(Boolean).join(", ") || "None";
                        const isReviewNeeded = item.compliance_status === "NEEDS_MANUAL_REVIEW";
                        return `
                  <tr class="hover:bg-slate-50 transition-colors ${isReviewNeeded ? "bg-amber-50/30" : ""}">
                    <td class="py-3.5 px-4 font-mono font-bold text-slate-900">
                      ${item.id}
                      ${isReviewNeeded ? `<div class="text-[10px] text-amber-700 font-semibold">Review Pending</div>` : ""}
                    </td>
                    <td class="py-3.5 px-4">
                      <div class="font-bold text-slate-900">${escapeHtml(item.product_name || "Unspecified")}</div>
                      <div class="text-[11px] text-slate-500 font-mono">
                        ${escapeHtml(item.brand_name || "Generic")} &bull; ${escapeHtml(item.commodity_category || "General")}
                      </div>
                    </td>
                    <td class="py-3.5 px-4">
                      ${renderResultBadge(item.compliance_status || "PENDING", "sm")}
                    </td>
                    <td class="py-3.5 px-4">
                      ${renderWorkflowBadge(item.status)}
                    </td>
                    <td class="py-3.5 px-4 font-mono text-[11px] text-slate-600">
                      ${covText} (${item.images_count || 1} imgs)
                    </td>
                    <td class="py-3.5 px-4 font-mono text-[11px] text-slate-500">
                      ${item.inspector_id || "inspector"}
                    </td>
                    <td class="py-3.5 px-4 text-right">
                      <div class="flex items-center justify-end gap-1.5">
                        <a href="#/compliance/${item.id}" 
                           class="px-2.5 py-1 rounded bg-slate-100 hover:bg-blue-50 text-slate-700 hover:text-blue-700 font-semibold text-[11px] border border-slate-200 transition-colors"
                           title="Inspect full 15 compliance checks">
                          Inspect
                        </a>
                        ${
                          isReviewNeeded
                            ? `
                          <a href="#/review/${item.id}" 
                             class="px-2 py-1 rounded bg-amber-100 hover:bg-amber-200 text-amber-900 font-bold text-[11px] border border-amber-300 transition-colors"
                             title="Review multi-surface conflicts or low OCR certainty">
                            Review
                          </a>
                        `
                            : ""
                        }
                      </div>
                    </td>
                  </tr>
                `;
                      })
                      .join("")
              }
            </tbody>
          </table>
        </div>
      </div>

    </div>
  `;
}

function escapeHtml(str) {
  return String(str || "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}
