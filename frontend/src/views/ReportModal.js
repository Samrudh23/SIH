/**
 * Printable Inspection Report Modal for SIH26034
 * Generates an official, printable statutory inspection certificate matching P3 report specifications.
 * Uses real backend GET /api/reports/{id} and links to GET /api/reports/{id}/html.
 */

import { apiService } from "../services/api.js";

function escapeHtml(str) {
  return String(str || "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

export async function renderReportModal(inspectionId) {
  let reportData, compliance, inspection;
  try {
    reportData = await apiService.getReportData(inspectionId);
    compliance = await apiService.getComplianceResult(inspectionId);
    inspection = await apiService.getInspection(inspectionId);
  } catch (err) {
    return `
      <div id="report-modal-backdrop" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/70 backdrop-blur-sm">
        <div class="bg-white rounded-xl p-6 max-w-md w-full text-center space-y-3 shadow-xl">
          <div class="text-rose-700 font-bold text-base">Failed to Generate Report</div>
          <p class="text-xs text-slate-600">${escapeHtml(err.message)}</p>
          <button id="close-report-modal" class="px-4 py-2 bg-slate-800 text-white text-xs font-semibold rounded-lg">Close</button>
        </div>
      </div>
    `;
  }

  const counts = compliance.summary_counts || {};
  const violations = (compliance.rule_results || []).filter((r) => r.status === "POTENTIAL_VIOLATION");
  const reviewCases = (compliance.rule_results || []).filter((r) => r.status === "NEEDS_MANUAL_REVIEW");
  const htmlUrl = apiService.getReportHtmlUrl(inspectionId);

  return `
    <div id="report-modal-backdrop" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/70 backdrop-blur-sm overflow-y-auto print:p-0 print:bg-white">
      <div class="bg-white rounded-2xl border border-slate-300 shadow-2xl max-w-4xl w-full my-8 overflow-hidden print:border-none print:shadow-none print:my-0">
        
        <!-- Modal Controls (Hidden in Print) -->
        <div class="bg-slate-900 text-white px-6 py-3 flex items-center justify-between print:hidden">
          <div class="flex items-center gap-2">
            <span class="font-bold text-xs">Official Statutory Inspection Report</span>
            <span class="text-slate-400 text-xs font-mono">(${inspection.id})</span>
          </div>
          <div class="flex items-center gap-2">
            <a href="${htmlUrl}" target="_blank" rel="noopener noreferrer" 
               class="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded text-xs font-medium transition-colors flex items-center gap-1.5">
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/></svg>
              <span>Server HTML View</span>
            </a>
            <button id="print-report-btn" class="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded text-xs font-bold transition-colors flex items-center gap-1.5 shadow-sm">
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"/></svg>
              <span>Print / Save as PDF</span>
            </button>
            <button id="close-report-modal" class="text-slate-400 hover:text-white p-1 rounded">
              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
            </button>
          </div>
        </div>

        <!-- Printable Document Body -->
        <div id="printable-report-content" class="p-8 sm:p-12 space-y-6 text-slate-900 font-serif leading-normal bg-white">
          
          <!-- Government Header -->
          <div class="text-center pb-6 border-b-2 border-slate-900 space-y-1 font-sans">
            <div class="text-xs uppercase tracking-widest font-bold text-slate-600">Government of India &bull; Ministry of Consumer Affairs, Food & Public Distribution</div>
            <div class="text-sm font-bold text-slate-800 tracking-wider">Department of Consumer Affairs &bull; Legal Metrology Division</div>
            <h1 class="text-xl font-black text-slate-900 tracking-tight pt-2 uppercase">
              Packaged Commodity Compliance Screening Certificate
            </h1>
            <div class="text-xs text-slate-500 font-mono pt-1">
              Under the Legal Metrology Act, 2009 & Legal Metrology (Packaged Commodities) Rules, 2011
            </div>
          </div>

          <!-- Metadata Record Table -->
          <div class="grid grid-cols-2 gap-4 text-xs font-sans border border-slate-300 rounded-lg p-4 bg-slate-50/50">
            <div>
              <div><strong>Inspection ID:</strong> <span class="font-mono">${inspection.id}</span></div>
              <div><strong>Date & Time of Audit:</strong> ${new Date(compliance.evaluated_at).toLocaleString()}</div>
              <div><strong>Enforcement Official:</strong> <span class="font-mono">${inspection.inspector_id}</span></div>
              <div><strong>Compliance Engine:</strong> ${compliance.engine_version}</div>
            </div>
            <div>
              <div><strong>Product / Trade Name:</strong> ${escapeHtml(inspection.product_name || "Unspecified")}</div>
              <div><strong>Brand Name:</strong> ${escapeHtml(inspection.brand_name || "Unspecified")}</div>
              <div><strong>Declared Category:</strong> ${escapeHtml(inspection.commodity_category || "General Commodity")}</div>
              <div><strong>Overall Legal Status:</strong> <span class="font-mono font-bold uppercase ${compliance.overall_status === "COMPLIANT" ? "text-emerald-700" : compliance.overall_status === "POTENTIAL_VIOLATION" ? "text-rose-700" : "text-amber-700"}">${compliance.overall_status}</span></div>
            </div>
          </div>

          <!-- Summary Matrix -->
          <div class="font-sans text-xs space-y-2">
            <h3 class="font-bold uppercase tracking-wider text-slate-800 text-xs border-b border-slate-200 pb-1">
              Statutory Evaluation Summary (15 Mandatory Checks)
            </h3>
            <div class="grid grid-cols-5 gap-2 text-center font-mono">
              <div class="p-2 border border-slate-200 rounded bg-slate-50">
                <div class="text-[10px] text-slate-500 uppercase">Compliant</div>
                <div class="font-bold text-emerald-700 text-sm">${counts.compliant || 0}</div>
              </div>
              <div class="p-2 border border-slate-200 rounded bg-slate-50">
                <div class="text-[10px] text-slate-500 uppercase">Violations</div>
                <div class="font-bold text-rose-700 text-sm">${counts.potential_violations || 0}</div>
              </div>
              <div class="p-2 border border-slate-200 rounded bg-slate-50">
                <div class="text-[10px] text-slate-500 uppercase">Manual Review</div>
                <div class="font-bold text-amber-700 text-sm">${counts.needs_manual_review || 0}</div>
              </div>
              <div class="p-2 border border-slate-200 rounded bg-slate-50">
                <div class="text-[10px] text-slate-500 uppercase">Not Applicable</div>
                <div class="font-bold text-slate-700 text-sm">${counts.not_applicable || 0}</div>
              </div>
              <div class="p-2 border border-slate-200 rounded bg-slate-50">
                <div class="text-[10px] text-slate-500 uppercase">Not Detected</div>
                <div class="font-bold text-indigo-700 text-sm">${counts.not_detected || 0}</div>
              </div>
            </div>
          </div>

          <!-- Potential Violations Section if Present -->
          ${
            violations.length > 0
              ? `
            <div class="font-sans text-xs space-y-2 pt-2">
              <h3 class="font-bold uppercase tracking-wider text-rose-800 text-xs border-b border-rose-200 pb-1">
                Identified Potential Violations (Actionable Legal Issues)
              </h3>
              <div class="space-y-2">
                ${violations
                  .map(
                    (v) => `
                  <div class="p-3 border border-rose-300 rounded bg-rose-50/50 space-y-1">
                    <div class="flex justify-between font-bold">
                      <span class="font-mono text-rose-900">${v.rule_id}: ${escapeHtml(v.rule_version?.clause || "")}</span>
                      <span class="text-rose-700 uppercase font-mono text-[10px]">POTENTIAL VIOLATION</span>
                    </div>
                    <div class="text-slate-800">${escapeHtml(v.explanation_for_inspector || v.reason)}</div>
                    <div class="text-[11px] text-slate-500 font-mono">Statutory Source: ${escapeHtml(v.rule_version?.source || "PCR 2011")} &bull; Notification: ${escapeHtml(v.rule_version?.gsr_number || "")}</div>
                  </div>
                `
                  )
                  .join("")}
              </div>
            </div>
          `
              : ""
          }

          <!-- Inspector Physical Notes -->
          ${
            inspection.notes
              ? `
            <div class="font-sans text-xs space-y-1 pt-2">
              <h3 class="font-bold uppercase tracking-wider text-slate-800 text-xs border-b border-slate-200 pb-1">
                Official Enforcement Observations
              </h3>
              <div class="p-3 bg-slate-50 border border-slate-200 rounded text-slate-800 italic">
                "${escapeHtml(inspection.notes)}"
              </div>
            </div>
          `
              : ""
          }

          <!-- Official Sign-off & Seal Block -->
          <div class="grid grid-cols-2 gap-8 pt-12 text-xs font-sans border-t border-slate-300">
            <div class="space-y-4">
              <div><strong>Inspection Facility / Station:</strong> Delhi Enforcement Directorate</div>
              <div><strong>Evidence Retention Record:</strong> <span class="font-mono text-[10px]">P3-INSP-${inspection.id}-VERIFIED</span></div>
              <div class="h-16 border border-dashed border-slate-300 rounded flex items-center justify-center text-slate-400 text-[11px]">
                [Official Regulatory Stamp / Seal Space]
              </div>
            </div>
            <div class="space-y-4 flex flex-col justify-between text-right">
              <div>
                <div class="font-mono font-bold text-slate-800">${escapeHtml(inspection.inspector_id)}</div>
                <div class="text-slate-500 text-[11px]">Authorized Legal Metrology Officer</div>
              </div>
              <div class="pt-8">
                <div class="w-48 ml-auto border-b border-slate-900"></div>
                <div class="text-[10px] text-slate-500 mt-1">Signature of Inspecting Officer</div>
              </div>
            </div>
          </div>

          <div class="text-center text-[10px] text-slate-400 font-sans pt-4 border-t border-slate-100">
            ${escapeHtml(reportData?.disclaimer || "Generated via SIH26034 Automated Screening Platform • Governed under the Legal Metrology Act, 2009")}
          </div>

        </div>

      </div>
    </div>
  `;
}
