/**
 * Evidence Viewer Component for SIH26034
 * Connects compliance findings directly to package imagery:
 * - Interactive bounding box coordinates overlay
 * - REQ-MVP-14 Quiet Zone simulator (1H vertical, 2H horizontal clearance)
 * - Raw OCR text preservation alongside normalized interpretation
 */

export function renderEvidenceCard(evidence, options = {}) {
  if (!evidence) {
    return `
      <div class="bg-slate-50 border border-dashed border-slate-300 rounded-lg p-4 text-center text-sm text-slate-500">
        <svg class="w-8 h-8 mx-auto mb-1.5 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
        <span>No specific visual bounding box recorded for this declaration.</span>
      </div>
    `;
  }

  const { isQuietZoneSimulated, numeralHeight = 35 } = options;
  const bbox = evidence.bounding_box || { x: 80, y: 150, w: 200, h: 45 };

  // Calculate Rule 8(1) quiet zone box: 1H top/bottom, 2H left/right
  const qz = {
    x: Math.max(0, bbox.x - 2 * numeralHeight),
    y: Math.max(0, bbox.y - 1 * numeralHeight),
    w: bbox.w + 4 * numeralHeight,
    h: bbox.h + 2 * numeralHeight,
  };

  return `
    <div class="bg-white border border-slate-200 rounded-lg overflow-hidden shadow-sm">
      <div class="bg-slate-50 px-3.5 py-2 border-b border-slate-200 flex items-center justify-between text-xs">
        <span class="font-semibold text-slate-700 flex items-center gap-1.5">
          <svg class="w-4 h-4 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></svg>
          Optical Evidence & Spatial Coordinates
        </span>
        <span class="font-mono text-slate-500 text-[11px]">
          [x:${Math.round(bbox.x)}, y:${Math.round(bbox.y)}, w:${Math.round(bbox.w)}, h:${Math.round(bbox.h)}]
        </span>
      </div>

      <!-- Evidence Canvas Preview -->
      <div class="p-3 bg-slate-900 flex flex-col items-center justify-center relative overflow-hidden min-h-[220px]">
        <svg viewBox="0 0 500 280" class="w-full max-w-[480px] h-auto border border-slate-700 rounded shadow-inner bg-slate-950">
          <!-- Package Container Mock Background -->
          <rect width="500" height="280" fill="#0f172a" />
          <rect x="20" y="20" width="460" height="240" rx="6" fill="#1e293b" stroke="#334155" stroke-width="2" />
          
          <!-- Package graphic hints -->
          <line x1="40" y1="50" x2="200" y2="50" stroke="#475569" stroke-width="3" stroke-linecap="round" />
          <line x1="40" y1="65" x2="160" y2="65" stroke="#334155" stroke-width="2" stroke-linecap="round" />

          ${
            isQuietZoneSimulated
              ? `
            <!-- Rule 8(1) Simulated Quiet Zone Area (1H Top/Bottom, 2H Left/Right) -->
            <rect x="${qz.x}" y="${qz.y}" width="${qz.w}" height="${qz.h}" 
                  fill="#f59e0b" fill-opacity="0.15" stroke="#f59e0b" stroke-width="1.5" stroke-dasharray="4 3"/>
            <text x="${qz.x + 8}" y="${qz.y + 14}" fill="#fbbf24" font-family="monospace" font-size="10" font-weight="bold">
              Rule 8(1) Quiet Zone (1H Vert / 2H Horiz)
            </text>
          `
              : ""
          }

          <!-- Bounding Box around text block -->
          <rect x="${bbox.x}" y="${bbox.y}" width="${bbox.w}" height="${bbox.h}" 
                fill="#3b82f6" fill-opacity="0.25" stroke="#60a5fa" stroke-width="2" rx="3"/>
          <circle cx="${bbox.x}" cy="${bbox.y}" r="3.5" fill="#3b82f6" />
          
          <!-- Bounding Box Label -->
          <text x="${bbox.x + 8}" y="${bbox.y + bbox.h / 2 + 4}" fill="#ffffff" font-family="monospace" font-size="12" font-weight="600">
            ${escapeHtml(evidence.raw_ocr_text || "Identified Text Block")}
          </text>
        </svg>

        ${
          isQuietZoneSimulated
            ? `
          <div class="mt-2 text-amber-300 text-xs flex items-center gap-1.5 font-mono">
            <span class="w-2 h-2 rounded-full bg-amber-400 animate-pulse"></span>
            Rule 8(1) Overlay Active: 1H (${numeralHeight}px) Vertical & 2H (${2 * numeralHeight}px) Horizontal Clearance
          </div>
        `
            : ""
        }
      </div>

      <!-- Raw OCR Segment Readout -->
      <div class="p-3 bg-slate-50 border-t border-slate-200">
        <div class="text-[11px] uppercase tracking-wider font-semibold text-slate-500 mb-1">
          Preserved Optical Character String (Unmodified)
        </div>
        <div class="font-mono text-xs text-slate-800 bg-white border border-slate-200 rounded p-2 select-all">
          "${escapeHtml(evidence.raw_ocr_text || "N/A")}"
        </div>
      </div>
    </div>
  `;
}

function escapeHtml(str) {
  return String(str).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}
