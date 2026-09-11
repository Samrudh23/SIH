/**
 * Medical Device Confirmation Gate Component (Fix 2)
 * Strictly implements Confidence_Status_Schema.md Section 4:
 * "Mandatory human confirmation step before the terminal NOT_APPLICABLE state is reached."
 */

export function renderMedicalDeviceGateModal(inspectionId, markerText, onConfirmCallback) {
  return `
    <div id="medical-device-gate-modal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
      <div class="bg-white rounded-2xl border-2 border-teal-500 shadow-2xl max-w-lg w-full overflow-hidden animate-in fade-in duration-200">
        <!-- Header -->
        <div class="bg-teal-50 px-6 py-4 border-b border-teal-100 flex items-center gap-3">
          <div class="w-10 h-10 rounded-full bg-teal-100 border border-teal-300 flex items-center justify-center text-teal-700 flex-shrink-0">
            <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/></svg>
          </div>
          <div>
            <h3 class="text-base font-bold text-teal-950">Statutory Routing Gate — Medical Device</h3>
            <span class="text-xs font-mono text-teal-700">REQ-MVP-11 | G.S.R. 778(E) Provisos</span>
          </div>
        </div>

        <!-- Body -->
        <div class="p-6 space-y-4">
          <div class="text-sm text-slate-700 leading-relaxed">
            The OCR engine detected medical device registration markers on the packaging:
          </div>

          <div class="p-3 bg-teal-50/70 border border-teal-200 rounded-lg font-mono text-xs text-teal-900 font-semibold select-all">
            "${escapeHtml(markerText || "Mfg. Lic. No. MD-1402 (CDSCO Reg. MDR-2017)")}"
          </div>

          <div class="bg-slate-50 border border-slate-200 rounded-lg p-3.5 text-xs text-slate-600 space-y-1.5">
            <div class="font-semibold text-slate-800">Regulatory Impact of Confirmation:</div>
            <ul class="list-disc list-inside space-y-1 text-slate-600">
              <li><strong>If Confirmed (YES):</strong> Standard PCR 2011 checks are suppressed. Package is routed strictly to the <em>Medical Devices Rules, 2017</em> (result marked <code class="text-slate-800">NOT_APPLICABLE</code>).</li>
              <li><strong>If Denied (NO):</strong> Product proceeds under standard Legal Metrology (Packaged Commodities) Rules, 2011 checks.</li>
            </ul>
          </div>

          <p class="text-xs text-slate-500 italic">
            Under Legal Metrology amendments, automated bypass without human confirmation is prohibited to prevent normal commodities from evading retail packaging standards.
          </p>
        </div>

        <!-- Actions -->
        <div class="bg-slate-50 px-6 py-4 border-t border-slate-200 flex items-center justify-end gap-3">
          <button id="gate-btn-no" type="button" 
                  class="px-4 py-2 rounded-lg border border-slate-300 bg-white text-slate-700 text-xs font-semibold hover:bg-slate-100 transition-colors shadow-sm">
            No, Not a Medical Device (Apply PCR)
          </button>
          <button id="gate-btn-yes" type="button" 
                  class="px-4 py-2 rounded-lg bg-teal-700 text-white text-xs font-semibold hover:bg-teal-800 transition-colors shadow-sm flex items-center gap-1.5">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
            Yes, Confirm Medical Device (Route to MDR 2017)
          </button>
        </div>
      </div>
    </div>
  `;
}

function escapeHtml(str) {
  return String(str).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}
