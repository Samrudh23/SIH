/**
 * Dedicated Manual Review & Conflict Resolution Workspace (Screen 6) for SIH26034
 * Dedicated enforcement workflow for:
 * - Multi-surface MRP & Net Quantity conflicts (Side-by-side comparison, never auto-resolves)
 * - Low OCR confidence declarations
 * - Medical device routing confirmation gate (Fix 2)
 * - Insufficient package surface coverage
 * - Assistive visual aids (REQ-MVP-14, REQ-MVP-15)
 * - Inspector determination & notes recording (POST /api/inspections/{id}/notes)
 */

import { apiService } from "../services/api.js";
import { renderResultBadge } from "../components/StatusBadge.js";
import { renderConfidenceMeter } from "../components/ConfidenceMeter.js";
import { renderConflictViewer } from "../components/ConflictViewer.js";
import { renderEvidenceCard } from "../components/EvidenceViewer.js";

export async function renderManualReviewView(inspectionId) {
  let compliance, inspection;
  try {
    compliance = await apiService.getComplianceResult(inspectionId);
    inspection = await apiService.getInspection(inspectionId);
  } catch (err) {
    return `
      <div class="p-8 bg-white border border-slate-200 rounded-xl text-center space-y-3">
        <div class="text-rose-600 font-bold">Inspection Result Unavailable</div>
        <p class="text-xs text-slate-500">${escapeHtml(err.message)}</p>
        <a href="#/compliance/${inspectionId}" class="text-xs font-semibold text-blue-600 hover:underline">&larr; Return to Compliance Overview</a>
      </div>
    `;
  }

  // Filter items needing human review or manual confirmation
  const reviewItems = (compliance.rule_results || []).filter(
    (r) => r.status === "NEEDS_MANUAL_REVIEW" || r.status === "NOT_DETECTED" || r.conflicts || r.rule_id === "REQ-MVP-11"
  );

  return `
    <div class="space-y-6 animate-in fade-in duration-150">
      
      <!-- Top Header -->
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2 border-b border-slate-200">
        <div>
          <div class="flex items-center gap-2">
            <span class="font-mono text-xs px-2.5 py-0.5 rounded-full bg-amber-100 text-amber-900 font-bold border border-amber-300">
              MANUAL REVIEW WORKSPACE
            </span>
            <span class="font-mono text-xs text-slate-500">${inspection.id}</span>
          </div>
          <h1 class="text-xl font-bold text-slate-900 tracking-tight mt-1">
            Enforcement Review & Conflict Resolution: ${escapeHtml(inspection.product_name || "Inspection")}
          </h1>
          <p class="text-xs text-slate-500 mt-0.5">
            Resolve multi-surface conflicts, verify low-confidence OCR text, and execute regulatory classification gates.
          </p>
        </div>

        <div class="flex items-center gap-2">
          <a href="#/compliance/${inspectionId}" 
             class="px-3.5 py-2 rounded-lg border border-slate-300 bg-white hover:bg-slate-50 text-slate-700 text-xs font-semibold shadow-sm transition-colors">
            &larr; Back to All 15 Rules
          </a>
        </div>
      </div>

      <!-- Governing Principles Notice -->
      <div class="bg-amber-50/70 border border-amber-200 rounded-xl p-4 text-xs text-amber-900 space-y-1.5 shadow-sm">
        <div class="font-bold flex items-center gap-2">
          <svg class="w-4 h-4 text-amber-700" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
          Legal Metrology Audit Requirements (Confidence_Status_Schema.md)
        </div>
        <ul class="list-disc list-inside space-y-0.5 text-amber-800 text-[11px]">
          <li><strong>Zero Silent Overrides:</strong> When differing prices or net weights exist across container panels, both readings must be presented to the inspector.</li>
          <li><strong>Visual-Aid Rules (REQ-MVP-14, 15):</strong> Camera distortion limits automated pass/fail determinations. Visual clearance box & contrast ratio require human eye verification.</li>
          <li><strong>Regulatory Gate (REQ-MVP-11):</strong> Medical device routing requires explicit officer confirmation before PCR 2011 checks are suppressed.</li>
        </ul>
      </div>

      <!-- Active Review Items List -->
      <div class="space-y-5">
        ${
          reviewItems.length === 0
            ? `
          <div class="bg-white border border-slate-200 rounded-2xl p-10 text-center space-y-2">
            <div class="w-12 h-12 mx-auto rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center">
              <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
            </div>
            <h3 class="text-sm font-bold text-slate-900">No Unresolved Review Cases</h3>
            <p class="text-xs text-slate-500">All mandatory checks have high-confidence determinations or confirmed exemptions.</p>
          </div>
        `
            : reviewItems
                .map((item) => {
                  const isQuietZone = item.rule_id === "REQ-MVP-14";
                  const isMedicalGate = item.rule_id === "REQ-MVP-11";
                  return `
            <div class="bg-white border-2 ${item.conflicts ? "border-amber-400" : "border-slate-200"} rounded-2xl p-5 shadow-sm space-y-4">
              
              <!-- Rule Title & Status Bar -->
              <div class="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-100">
                <div class="flex items-center gap-3">
                  <span class="font-mono text-xs font-bold px-2 py-0.5 rounded bg-slate-100 text-slate-800 border border-slate-300">
                    ${item.rule_id}
                  </span>
                  <div>
                    <h3 class="text-sm font-bold text-slate-900">${item.rule_version?.clause || "Statutory Check"}</h3>
                    <div class="text-[11px] text-slate-500 font-mono">${item.rule_version?.source || "PCR 2011"} &bull; ${item.rule_version?.gsr_number || ""}</div>
                  </div>
                </div>

                <div class="flex items-center gap-2">
                  ${renderResultBadge(item.status, "sm")}
                </div>
              </div>

              <!-- Explanation for Official -->
              <div class="bg-blue-50/50 border border-blue-200 rounded-lg p-3 text-xs text-slate-800">
                <strong>Why Review is Required:</strong> ${escapeHtml(item.explanation_for_inspector || item.reason)}
              </div>

              <!-- Surface Conflict Display if Applicable -->
              ${item.conflicts ? renderConflictViewer(item.conflicts) : ""}

              <!-- Medical Device Confirmation Action if Applicable -->
              ${
                isMedicalGate
                  ? `
                <div class="bg-teal-50 border border-teal-300 rounded-xl p-4 space-y-3">
                  <div class="flex items-center justify-between">
                    <div>
                      <h4 class="text-xs font-bold text-teal-950 uppercase tracking-wider">Fix 2 Confirmation Gate Action</h4>
                      <p class="text-xs text-teal-800">Confirm whether this product is certified under Medical Devices Rules, 2017.</p>
                    </div>
                    <span class="text-xs font-mono px-2 py-0.5 rounded bg-teal-200 text-teal-900 font-semibold">Action Required</span>
                  </div>

                  <div class="flex items-center gap-2.5 pt-1">
                    <button id="trigger-med-confirm-btn" data-id="${inspectionId}" data-confirm="true" 
                            class="px-4 py-2 bg-teal-700 hover:bg-teal-800 text-white rounded-lg text-xs font-bold shadow-sm transition-colors flex items-center gap-1.5">
                      <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                      <span>Confirm as Medical Device (Route to MDR 2017)</span>
                    </button>
                    <button id="trigger-med-reject-btn" data-id="${inspectionId}" data-confirm="false" 
                            class="px-4 py-2 bg-white hover:bg-slate-100 border border-slate-300 text-slate-700 rounded-lg text-xs font-semibold transition-colors">
                      <span>Reject Classification (Apply Standard PCR)</span>
                    </button>
                  </div>
                </div>
              `
                  : ""
              }

              <!-- Visual Evidence Preview -->
              <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
                <div>
                  <h4 class="text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2">Optical Evidence</h4>
                  ${renderEvidenceCard(item.evidence, { isQuietZoneSimulated: isQuietZone })}
                </div>

                <div>
                  <h4 class="text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2">Confidence Telemetry</h4>
                  ${renderConfidenceMeter(item.detection_confidence, item.applicability_confidence)}
                  
                  <div class="mt-3 p-3 bg-slate-50 rounded-lg border border-slate-200 text-xs text-slate-600 font-mono space-y-1">
                    <div><strong>Detected Value:</strong> ${escapeHtml(item.detected_value || "N/A")}</div>
                    <div><strong>Normalized Value:</strong> ${escapeHtml(item.normalized_value || "N/A")}</div>
                  </div>
                </div>
              </div>

            </div>
          `;
                })
                .join("")
        }
      </div>

      <!-- Section: Inspector Physical Findings & Determination Notes -->
      <div class="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-4">
        <h3 class="text-sm font-bold text-slate-900 tracking-tight flex items-center gap-2">
          <svg class="w-4 h-4 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/></svg>
          <span>Official Inspector Determination & Measurement Notes</span>
        </h3>

        <p class="text-xs text-slate-500">
          Record tactile inspection observations, physical caliper measurements (e.g. font numeral height, quiet zone margins), retail sample seizure details, or resolution reasoning.
        </p>

        <form id="inspector-notes-form" class="space-y-3">
          <textarea id="inspector-notes-input" rows="4" 
                    placeholder="Enter official enforcement observations, physical caliper readings, or resolution notes..." 
                    class="w-full bg-slate-50 border border-slate-300 rounded-xl p-3.5 text-xs text-slate-900 focus:bg-white focus:ring-2 focus:ring-blue-500 focus:outline-none font-sans leading-relaxed">${escapeHtml(inspection.notes || "")}</textarea>
          
          <div class="flex items-center justify-between">
            <span id="notes-status-msg" class="text-xs text-emerald-600 font-semibold"></span>
            <button type="submit" id="save-notes-btn" 
                    class="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white text-xs font-bold rounded-lg shadow-sm transition-colors">
              Save Determination Notes
            </button>
          </div>
        </form>
      </div>

    </div>
  `;
}

function escapeHtml(str) {
  return String(str || "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}
