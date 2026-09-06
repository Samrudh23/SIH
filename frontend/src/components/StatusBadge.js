/**
 * Accessible Status & Result State Badges for SIH26034
 * Enforces text + icon + visual styling so status is never communicated by color alone.
 */

export const RESULT_STATE_CONFIG = {
  COMPLIANT: {
    label: "COMPLIANT",
    bgClass: "badge-compliant",
    icon: `<svg class="w-3.5 h-3.5 mr-1 inline" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/></svg>`,
    description: "Statutory requirement satisfied with sufficient evidence.",
    ariaLabel: "Status: Compliant",
  },
  POTENTIAL_VIOLATION: {
    label: "POTENTIAL VIOLATION",
    bgClass: "badge-violation",
    icon: `<svg class="w-3.5 h-3.5 mr-1 inline" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>`,
    description: "Evidence indicates statutory requirement is likely violated.",
    ariaLabel: "Status: Potential Violation",
  },
  NEEDS_MANUAL_REVIEW: {
    label: "NEEDS MANUAL REVIEW",
    bgClass: "badge-review",
    icon: `<svg class="w-3.5 h-3.5 mr-1 inline" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>`,
    description: "Ambiguity, conflict, low OCR confidence, or physical verification required.",
    ariaLabel: "Status: Needs Manual Review",
  },
  NOT_APPLICABLE: {
    label: "NOT APPLICABLE",
    bgClass: "badge-na",
    icon: `<svg class="w-3.5 h-3.5 mr-1 inline" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636"/></svg>`,
    description: "Statutory exemption or regulatory routing confirmed.",
    ariaLabel: "Status: Not Applicable",
  },
  NOT_DETECTED: {
    label: "NOT DETECTED",
    bgClass: "badge-not-detected",
    icon: `<svg class="w-3.5 h-3.5 mr-1 inline" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>`,
    description: "Expected declaration was not identified on visible panels.",
    ariaLabel: "Status: Not Detected",
  },
  ANALYSIS_FAILED: {
    label: "ANALYSIS FAILED",
    bgClass: "badge-failed",
    icon: `<svg class="w-3.5 h-3.5 mr-1 inline" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>`,
    description: "Technical vision pipeline failed. No legal determination made.",
    ariaLabel: "Status: Analysis Failed",
  },
};

export function renderResultBadge(state, size = "md") {
  const config = RESULT_STATE_CONFIG[state] || {
    label: state || "UNKNOWN",
    bgClass: "badge-na",
    icon: "",
    ariaLabel: `Status: ${state}`,
  };

  const sizeClasses = size === "sm" ? "text-xs px-2 py-0.5" : size === "lg" ? "text-sm px-3.5 py-1.5 font-semibold" : "text-xs px-2.5 py-1 font-medium";

  return `
    <span class="inline-flex items-center rounded-md font-mono tracking-wide ${config.bgClass} ${sizeClasses}" 
          title="${config.description || config.label}" 
          aria-label="${config.ariaLabel}">
      ${config.icon}
      <span>${config.label}</span>
    </span>
  `;
}

export function renderWorkflowBadge(status) {
  const map = {
    CREATED: { label: "CREATED", class: "bg-slate-100 text-slate-700 border-slate-300" },
    IMAGE_UPLOADED: { label: "IMAGES UPLOADED", class: "bg-blue-50 text-blue-700 border-blue-200" },
    EXTRACTION_RECEIVED: { label: "OCR EXTRACTED", class: "bg-indigo-50 text-indigo-700 border-indigo-200" },
    ANALYSIS_COMPLETE: { label: "ANALYZED", class: "bg-emerald-50 text-emerald-700 border-emerald-200" },
    REPORT_GENERATED: { label: "REPORT READY", class: "bg-purple-50 text-purple-700 border-purple-200" },
    FAILED: { label: "FAILED", class: "bg-rose-50 text-rose-700 border-rose-200" },
  };
  const c = map[status] || { label: status, class: "bg-slate-100 text-slate-700 border-slate-300" };
  return `<span class="inline-flex items-center text-xs font-mono font-medium px-2 py-0.5 rounded border ${c.class}">${c.label}</span>`;
}
