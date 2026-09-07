/**
 * 5-Stage Inspection Workflow Stepper for SIH26034
 * Enforces the statutory inspection mental model:
 * 01 Evidence -> 02 Extraction -> 03 Compliance -> 04 Review -> 05 Inspection Report
 *
 * Rules:
 * - Distinguishes: completed stages, current stage, available future stages, unavailable/locked future stages.
 * - Never blindly clickable: a stage is only actionable when underlying inspection state permits.
 * - Prioritizes inspector attention with contextual badges (e.g., unresolved review count).
 */

export function renderWorkflowStepper(options = {}) {
  const {
    inspectionId = null,
    currentStage = "evidence", // "evidence" | "extraction" | "compliance" | "review" | "report"
    inspection = null,
    compliance = null,
  } = options;

  // Determine stage availability and completion based on actual application state
  const hasInspection = Boolean(inspectionId);
  const isAnalyzed = Boolean(
    compliance?.overall_status ||
    inspection?.status === "ANALYSIS_COMPLETE" ||
    inspection?.status === "REPORT_GENERATED"
  );
  const reviewCount = compliance?.summary_counts?.needs_manual_review || 0;

  const stages = [
    {
      key: "evidence",
      number: "01",
      name: "Evidence",
      description: "Container & Surfaces",
      route: hasInspection ? `#/new` : "#/new",
      isCurrent: currentStage === "evidence",
      isCompleted: hasInspection,
      isActionable: true,
      tooltip: hasInspection ? "Inspect container photos & coverage" : "Upload container evidence",
    },
    {
      key: "extraction",
      number: "02",
      name: "Extraction",
      description: "P1 Optical Audit",
      route: hasInspection ? `#/extraction/${inspectionId}` : null,
      isCurrent: currentStage === "extraction",
      isCompleted: isAnalyzed,
      isActionable: hasInspection,
      tooltip: hasInspection ? "Review OCR readings across 6 blocks" : "Locked: Complete evidence upload first",
    },
    {
      key: "compliance",
      number: "03",
      name: "Compliance",
      description: "15 Rule Screening",
      route: hasInspection ? `#/compliance/${inspectionId}` : null,
      isCurrent: currentStage === "compliance",
      isCompleted: isAnalyzed,
      isActionable: hasInspection,
      tooltip: hasInspection ? "Inspect 15-rule compliance screening" : "Locked: Complete evidence upload first",
    },
    {
      key: "review",
      number: "04",
      name: "Review",
      description: "Conflicts & Gates",
      route: hasInspection && isAnalyzed ? `#/review/${inspectionId}` : null,
      isCurrent: currentStage === "review",
      isCompleted: isAnalyzed && reviewCount === 0,
      isActionable: hasInspection && isAnalyzed,
      attentionCount: reviewCount,
      tooltip: isAnalyzed
        ? reviewCount > 0
          ? `${reviewCount} items require inspector attention`
          : "Manual review items resolved"
        : "Locked: Run compliance analysis first",
    },
    {
      key: "report",
      number: "05",
      name: "Inspection Report",
      description: "Findings & Export",
      isReportTrigger: true,
      inspectionId: inspectionId,
      isCurrent: currentStage === "report",
      isCompleted: inspection?.status === "REPORT_GENERATED",
      isActionable: hasInspection && isAnalyzed,
      tooltip: isAnalyzed ? "Generate & print inspection report" : "Locked: Run compliance analysis first",
    },
  ];

  return `
    <nav aria-label="Inspection Workflow Progression" class="bg-white border border-slate-200 rounded-xl p-2.5 shadow-sm mb-6">
      <div class="flex items-center justify-between gap-1 sm:gap-2 overflow-x-auto">
        ${stages
          .map((s, idx) => {
            let statusClasses = "";
            let badgeClasses = "";
            let numberContent = s.number;

            if (s.isCurrent) {
              // Current active stage
              statusClasses = "border-blue-600 bg-blue-50/70 text-slate-900 shadow-sm";
              badgeClasses = "bg-blue-600 text-white font-bold";
            } else if (s.isCompleted) {
              // Completed prior stage
              statusClasses = "border-slate-200 bg-slate-50/50 hover:bg-slate-100/70 text-slate-800 cursor-pointer";
              badgeClasses = "bg-emerald-600 text-white";
              numberContent = `
                <svg class="w-3.5 h-3.5 inline" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
                </svg>
              `;
            } else if (s.isActionable) {
              // Available future stage
              statusClasses = "border-slate-200 bg-white hover:bg-slate-50 text-slate-700 cursor-pointer";
              badgeClasses = "bg-slate-200 text-slate-700 font-semibold";
            } else {
              // Locked future stage
              statusClasses = "border-slate-100 bg-slate-50/40 text-slate-400 cursor-not-allowed opacity-60";
              badgeClasses = "bg-slate-100 text-slate-400";
            }

            const currentAttr = s.isCurrent ? 'aria-current="step"' : "";
            const disabledAttr = !s.isActionable ? 'aria-disabled="true" tabindex="-1"' : 'tabindex="0"';

            // Attention badge (e.g., review items count)
            const attentionPill =
              s.attentionCount && s.attentionCount > 0
                ? `<span class="ml-1.5 px-1.5 py-0.2 text-[10px] font-mono font-bold rounded-full bg-amber-200 text-amber-900 border border-amber-300" title="${s.attentionCount} items require inspector verification">${s.attentionCount}</span>`
                : "";

            // Render tag: button for report modal trigger, anchor for actionable links, div for locked
            if (s.isReportTrigger && s.isActionable) {
              return `
                <button type="button" 
                        id="open-report-modal-btn" 
                        data-id="${s.inspectionId}"
                        ${currentAttr}
                        class="stepper-stage flex-1 min-w-[130px] p-2 sm:p-2.5 rounded-lg border text-left flex items-center gap-2.5 transition-all focus:outline-none ${statusClasses}"
                        title="${s.tooltip}">
                  <span class="w-6 h-6 rounded-md flex items-center justify-center text-xs font-mono flex-shrink-0 ${badgeClasses}">
                    ${numberContent}
                  </span>
                  <div class="min-w-0">
                    <div class="text-xs font-bold tracking-tight truncate flex items-center">
                      <span>${s.name}</span>
                      ${attentionPill}
                    </div>
                    <div class="text-[10px] text-slate-500 truncate hidden sm:block">${s.description}</div>
                  </div>
                </button>
              `;
            }

            if (s.isActionable && s.route) {
              return `
                <a href="${s.route}" 
                   ${currentAttr}
                   ${disabledAttr}
                   class="stepper-stage flex-1 min-w-[130px] p-2 sm:p-2.5 rounded-lg border text-left flex items-center gap-2.5 transition-all no-underline focus:outline-none ${statusClasses}"
                   title="${s.tooltip}">
                  <span class="w-6 h-6 rounded-md flex items-center justify-center text-xs font-mono flex-shrink-0 ${badgeClasses}">
                    ${numberContent}
                  </span>
                  <div class="min-w-0">
                    <div class="text-xs font-bold tracking-tight truncate flex items-center">
                      <span>${s.name}</span>
                      ${attentionPill}
                    </div>
                    <div class="text-[10px] text-slate-500 truncate hidden sm:block">${s.description}</div>
                  </div>
                </a>
              `;
            }

            return `
              <div ${currentAttr}
                   ${disabledAttr}
                   class="stepper-stage flex-1 min-w-[130px] p-2 sm:p-2.5 rounded-lg border text-left flex items-center gap-2.5 transition-all select-none ${statusClasses}"
                   title="${s.tooltip}">
                <span class="w-6 h-6 rounded-md flex items-center justify-center text-xs font-mono flex-shrink-0 ${badgeClasses}">
                  ${numberContent}
                </span>
                <div class="min-w-0">
                  <div class="text-xs font-semibold tracking-tight truncate flex items-center text-slate-400">
                    <span>${s.name}</span>
                    <svg class="w-3 h-3 ml-1 text-slate-300 inline" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/></svg>
                  </div>
                  <div class="text-[10px] text-slate-400 truncate hidden sm:block">${s.description}</div>
                </div>
              </div>
            `;
          })
          .join(`
            <div class="hidden md:flex items-center text-slate-300 flex-shrink-0" aria-hidden="true">
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7" />
              </svg>
            </div>
          `)}
      </div>
    </nav>
  `;
}
