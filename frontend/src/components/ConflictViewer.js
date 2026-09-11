/**
 * Multi-Surface Observation Conflict Viewer for SIH26034
 * Strictly enforces legal metrology rule:
 * "Never silently choose a winning observation. Always preserve and display
 * all observations side-by-side with surface, value, confidence, and raw text."
 */

export function renderConflictViewer(conflict) {
  if (!conflict || !conflict.values_found || conflict.values_found.length < 2) {
    return "";
  }

  const fieldTitle = conflict.field === "mrp" ? "Maximum Retail Price (MRP)" : conflict.field === "net_quantity" ? "Declared Net Quantity" : conflict.field.toUpperCase();

  return `
    <div class="bg-amber-50/80 border-2 border-amber-300 rounded-xl p-5 shadow-sm space-y-4">
      <div class="flex items-start justify-between gap-3">
        <div class="flex items-center gap-2.5">
          <div class="w-9 h-9 rounded-lg bg-amber-100 border border-amber-300 flex items-center justify-center text-amber-700 flex-shrink-0">
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
          </div>
          <div>
            <h4 class="text-sm font-bold text-amber-900 tracking-tight flex items-center gap-2">
              <span>Multi-Surface Observation Discrepancy</span>
              <span class="text-xs px-2 py-0.5 rounded bg-amber-200 text-amber-800 font-mono font-semibold">${conflict.resolution}</span>
            </h4>
            <p class="text-xs text-amber-800 mt-0.5">
              Conflicting declarations detected for <strong>${fieldTitle}</strong> across submitted package faces. The system preserves all readings for human enforcement review.
            </p>
          </div>
        </div>
      </div>

      <!-- Side-by-Side Surface Comparison Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        ${conflict.values_found
          .map((item, idx) => {
            const confPct = Math.round((item.confidence || 0.9) * 100);
            return `
            <div class="bg-white border-2 border-amber-200 rounded-lg p-4 shadow-sm hover:border-amber-400 transition-colors">
              <div class="flex items-center justify-between text-xs font-semibold mb-2 pb-2 border-b border-slate-100">
                <span class="uppercase tracking-wider px-2 py-0.5 rounded bg-slate-100 text-slate-700 font-mono">
                  Surface ${idx + 1}: ${item.location ? item.location.toUpperCase() : "PANEL"}
                </span>
                <span class="text-slate-500 font-mono text-[11px]">Evidence ID: ${item.image_id || "IMG-" + (idx + 1)}</span>
              </div>

              <div class="my-3">
                <div class="text-[11px] uppercase tracking-wider text-slate-500 mb-0.5">Detected Declaration</div>
                <div class="text-xl font-bold font-mono text-slate-900 bg-amber-50/50 p-2 rounded border border-amber-100">
                  ${escapeHtml(item.value)}
                </div>
              </div>

              <div class="space-y-1.5 text-xs">
                <div class="flex justify-between text-slate-600">
                  <span>OCR Confidence:</span>
                  <span class="font-mono font-semibold text-slate-800">${confPct}%</span>
                </div>
                ${
                  item.raw_text
                    ? `
                  <div>
                    <span class="text-slate-500 text-[11px]">Exact Optical Text:</span>
                    <div class="font-mono text-[11px] text-slate-700 bg-slate-50 p-1.5 rounded border border-slate-200 mt-0.5 select-all">
                      "${escapeHtml(item.raw_text)}"
                    </div>
                  </div>
                `
                    : ""
                }
              </div>
            </div>
          `;
          })
          .join("")}
      </div>

      <div class="bg-amber-100/60 rounded-lg p-3 text-xs text-amber-900 flex items-start gap-2 border border-amber-200/60">
        <svg class="w-4 h-4 text-amber-700 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
        <span>
          <strong>Legal Metrology Standard:</strong> Packaged goods may not display differing or ambiguous retail sale prices or net weights across external surfaces. Please inspect container physically to verify if an illegal oversticker or altered packaging is present.
        </span>
      </div>
    </div>
  `;
}

function escapeHtml(str) {
  return String(str).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}
