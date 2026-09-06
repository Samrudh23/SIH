/**
 * Rule Detail Deep-Dive Modal for SIH26034
 * Renders complete statutory citation, evidence preview, and inspector action.
 */

import { renderResultBadge } from "./StatusBadge.js";
import { renderConfidenceMeter } from "./ConfidenceMeter.js";
import { renderEvidenceCard } from "./EvidenceViewer.js";
import { renderConflictViewer } from "./ConflictViewer.js";

export function renderRuleDetailModal(ruleResult) {
  if (!ruleResult) return "";

  const meta = ruleResult.rule_version || {
    source: "01_Packaged_Commodities_Rules_2011.pdf",
    clause: "Principal Rules",
    gsr_number: "G.S.R. 202(E)",
    verification_status: "VERIFIED",
    last_verified: "2026-09-05",
  };

  const isQuietZone = ruleResult.rule_id === "REQ-MVP-14";
  const isContrast = ruleResult.rule_id === "REQ-MVP-15";
  const isVisualAid = isQuietZone || isContrast;

  return `
    <div id="rule-detail-modal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm overflow-y-auto">
      <div class="bg-white rounded-2xl border border-slate-300 shadow-2xl max-w-2xl w-full my-8 overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        
        <!-- Header -->
        <div class="bg-slate-900 text-white px-6 py-4 flex items-center justify-between">
          <div class="flex items-center gap-3">
            <span class="font-mono text-xs font-bold px-2.5 py-1 rounded bg-blue-500/20 text-blue-300 border border-blue-400/30">
              ${ruleResult.rule_id}
            </span>
            <div>
              <h3 class="text-base font-bold tracking-tight text-white">${meta.clause || "Compliance Rule"}</h3>
              <p class="text-xs text-slate-400">${meta.source}</p>
            </div>
          </div>
          <button id="close-rule-modal" class="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition-colors">
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </div>

        <!-- Scrollable Content -->
        <div class="p-6 space-y-5 max-h-[75vh] overflow-y-auto">
          
          <!-- Status Banner -->
          <div class="flex flex-wrap items-center justify-between gap-3 p-3.5 bg-slate-50 border border-slate-200 rounded-xl">
            <div class="flex items-center gap-2">
              <span class="text-xs font-semibold text-slate-500 uppercase tracking-wider">Evaluation Result:</span>
              ${renderResultBadge(ruleResult.status, "lg")}
            </div>
            <div class="text-xs font-mono text-slate-600 bg-white px-2.5 py-1 rounded border border-slate-200">
              ${meta.gsr_number}
            </div>
          </div>

          ${
            isVisualAid
              ? `
            <div class="bg-indigo-50 border border-indigo-200 rounded-xl p-3.5 text-xs text-indigo-950 flex items-start gap-2.5">
              <svg class="w-5 h-5 text-indigo-600 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
              <div>
                <strong>Assistive Visual Aid Only:</strong> Per Confidence_Status_Schema Section 9, this rule is strictly restricted to <code class="bg-indigo-100 px-1 py-0.5 rounded text-indigo-900 font-mono">NEEDS_MANUAL_REVIEW</code> or <code class="bg-indigo-100 px-1 py-0.5 rounded text-indigo-900 font-mono">NOT_DETECTED</code>. It never issues automated Pass or Violation determinations.
              </div>
            </div>
          `
              : ""
          }

          <!-- Explanation for Inspector -->
          <div class="space-y-1.5">
            <h4 class="text-xs font-bold text-slate-900 uppercase tracking-wider">Official Explanation for Inspector</h4>
            <div class="text-sm text-slate-800 bg-blue-50/50 border border-blue-200/70 rounded-lg p-3.5 leading-relaxed font-sans">
              ${escapeHtml(ruleResult.explanation_for_inspector || ruleResult.reason)}
            </div>
          </div>

          <!-- Detected vs Expected Comparison -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div class="bg-slate-50 p-3.5 rounded-lg border border-slate-200">
              <div class="text-[11px] font-semibold text-slate-500 uppercase tracking-wider mb-1">Detected Observation</div>
              <div class="font-mono text-xs font-bold text-slate-900 break-words">
                ${escapeHtml(ruleResult.detected_value || "NONE DETECTED")}
              </div>
              ${
                ruleResult.normalized_value
                  ? `
                <div class="text-[11px] text-slate-500 font-mono mt-1 pt-1 border-t border-slate-200">
                  Normalized: ${escapeHtml(ruleResult.normalized_value)}
                </div>
              `
                  : ""
              }
            </div>

            <div class="bg-slate-50 p-3.5 rounded-lg border border-slate-200">
              <div class="text-[11px] font-semibold text-slate-500 uppercase tracking-wider mb-1">Statutory Clause Citation</div>
              <div class="text-xs text-slate-800 font-medium">
                ${meta.clause}
              </div>
              <div class="text-[11px] text-emerald-700 font-mono mt-1 font-semibold flex items-center gap-1">
                <svg class="w-3.5 h-3.5 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                ${meta.verification_status} (${meta.last_verified})
              </div>
            </div>
          </div>

          <!-- Multi-Surface Conflict if Present -->
          ${ruleResult.conflicts ? renderConflictViewer(ruleResult.conflicts) : ""}

          <!-- Confidence Breakdown -->
          ${renderConfidenceMeter(ruleResult.detection_confidence, ruleResult.applicability_confidence)}

          <!-- Visual Evidence Viewer -->
          <div class="space-y-1.5">
            <h4 class="text-xs font-bold text-slate-900 uppercase tracking-wider">Optical Evidence Record</h4>
            ${renderEvidenceCard(ruleResult.evidence, { isQuietZoneSimulated: isQuietZone })}
          </div>

          <!-- Technical Reason -->
          <div class="text-xs text-slate-600 bg-slate-100 p-3 rounded-lg border border-slate-200 font-mono">
            <span class="font-bold text-slate-700">Engine Audit Log:</span> ${escapeHtml(ruleResult.reason)}
          </div>
        </div>

        <!-- Footer -->
        <div class="bg-slate-50 px-6 py-3.5 border-t border-slate-200 flex items-center justify-between">
          <div class="text-[11px] text-slate-500 font-mono">
            Enforcement Audit Trail Preserved
          </div>
          <button id="close-rule-modal-btn" class="px-4 py-2 bg-slate-800 text-white rounded-lg text-xs font-semibold hover:bg-slate-900 transition-colors shadow-sm">
            Close Inspector View
          </button>
        </div>
      </div>
    </div>
  `;
}

function escapeHtml(str) {
  return String(str).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}
