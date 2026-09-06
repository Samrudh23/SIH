/**
 * Dual Confidence Meter Component for SIH26034
 * Enforces the strict rule from Confidence_Status_Schema.md Section 2:
 * "Two confidence numbers, kept permanently separate — never combined into one score."
 * "Never phrase either number as '% legally compliant'."
 */

export function renderConfidenceMeter(detectionConfidence, applicabilityConfidence, compact = false) {
  const detVal = Math.round((detectionConfidence || 0) * 100);
  const appVal = Math.round((applicabilityConfidence || 0) * 100);

  const getBarColor = (score) => {
    if (score >= 85) return "bg-emerald-600";
    if (score >= 70) return "bg-amber-500";
    return "bg-rose-600";
  };

  if (compact) {
    return `
      <div class="flex flex-col gap-1 text-xs font-mono">
        <div class="flex items-center justify-between gap-2" title="Detection Confidence: confidence in OCR/CV text characters read">
          <span class="text-slate-500 text-[11px]">OCR Read:</span>
          <span class="font-medium ${detVal >= 75 ? "text-slate-700" : "text-amber-600 font-bold"}">${detVal}%</span>
        </div>
        <div class="flex items-center justify-between gap-2" title="Applicability Confidence: confidence that this statutory rule applies to this commodity">
          <span class="text-slate-500 text-[11px]">Rule Match:</span>
          <span class="font-medium text-slate-700">${appVal}%</span>
        </div>
      </div>
    `;
  }

  return `
    <div class="bg-slate-50 border border-slate-200 rounded-lg p-3 space-y-2.5">
      <div class="text-xs font-semibold text-slate-700 uppercase tracking-wider flex items-center justify-between">
        <span>Confidence Assessment</span>
        <span class="text-[10px] text-slate-400 font-normal">Separate OCR & Applicability Signals</span>
      </div>

      <!-- Detection Confidence -->
      <div>
        <div class="flex justify-between items-center text-xs mb-1">
          <span class="font-medium text-slate-700 flex items-center gap-1">
            <span>OCR Detection Confidence</span>
            <span class="text-slate-400 cursor-help" title="Confidence of the optical character recognition model regarding what text was printed on the container.">&#9432;</span>
          </span>
          <span class="font-mono font-bold text-xs ${detVal >= 75 ? "text-slate-800" : "text-amber-700"}">${detVal}%</span>
        </div>
        <div class="w-full bg-slate-200 rounded-full h-1.5 overflow-hidden">
          <div class="${getBarColor(detVal)} h-1.5 rounded-full transition-all duration-300" style="width: ${detVal}%"></div>
        </div>
        <div class="text-[10px] text-slate-500 mt-0.5">
          ${detVal >= 75 ? "High-clarity text capture" : "Low OCR certainty — manual verification recommended"}
        </div>
      </div>

      <!-- Applicability Confidence -->
      <div>
        <div class="flex justify-between items-center text-xs mb-1">
          <span class="font-medium text-slate-700 flex items-center gap-1">
            <span>Rule Applicability Confidence</span>
            <span class="text-slate-400 cursor-help" title="Confidence that this statutory rule or exemption threshold legally applies to this product category.">&#9432;</span>
          </span>
          <span class="font-mono font-bold text-xs text-slate-800">${appVal}%</span>
        </div>
        <div class="w-full bg-slate-200 rounded-full h-1.5 overflow-hidden">
          <div class="${getBarColor(appVal)} h-1.5 rounded-full transition-all duration-300" style="width: ${appVal}%"></div>
        </div>
        <div class="text-[10px] text-slate-500 mt-0.5">
          ${appVal === 100 ? "Definite commodity category match" : "Potential sector exemption threshold"}
        </div>
      </div>
    </div>
  `;
}
