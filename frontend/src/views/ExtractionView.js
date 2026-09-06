/**
 * Extraction Review View (Screen 3) for SIH26034
 * Displays OCR/Vision extractions from P1 organized by logical declaration blocks.
 * Provides transparency into what the OCR saw before the user reviews compliance results.
 */

import { apiService } from "../services/api.js";

export async function renderExtractionView(inspectionId) {
  let inspection, extraction;
  try {
    inspection = await apiService.getInspection(inspectionId);
    extraction = await apiService.getExtraction(inspectionId);
  } catch (err) {
    return `
      <div class="p-8 text-center bg-white border border-slate-200 rounded-xl shadow-sm space-y-3">
        <div class="text-rose-600 font-bold text-base">Extraction Record Not Available</div>
        <p class="text-xs text-slate-500">${escapeHtml(err.message)}</p>
        <a href="#/compliance/${inspectionId}" class="inline-block text-xs font-semibold text-blue-600 hover:underline">&larr; Return to Compliance Results</a>
      </div>
    `;
  }

  const renderFieldRow = (label, fieldObj, extraDetails = "") => {
    if (!fieldObj) {
      return `
        <div class="flex items-start justify-between py-2 border-b border-slate-100 text-xs">
          <span class="font-medium text-slate-500">${label}:</span>
          <span class="font-mono text-rose-600 bg-rose-50 px-2 py-0.5 rounded text-[11px] font-semibold">[NOT DETECTED]</span>
        </div>
      `;
    }

    const conf = Math.round((fieldObj.confidence || 0) * 100);
    const confClass = conf >= 75 ? "text-emerald-700 bg-emerald-50" : "text-amber-700 bg-amber-50 font-bold";

    return `
      <div class="py-2.5 border-b border-slate-100 text-xs space-y-1">
        <div class="flex items-start justify-between gap-2">
          <span class="font-semibold text-slate-700">${label}:</span>
          <div class="flex items-center gap-1.5">
            ${fieldObj.location ? `<span class="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-slate-100 text-slate-600">${fieldObj.location}</span>` : ""}
            <span class="font-mono text-[11px] px-1.5 py-0.5 rounded ${confClass}">${conf}% OCR</span>
          </div>
        </div>
        <div class="font-mono text-slate-900 font-bold text-xs bg-slate-50 p-2 rounded border border-slate-200 break-words">
          ${escapeHtml(fieldObj.value !== undefined ? String(fieldObj.value) : fieldObj.raw_text)}
        </div>
        ${
          fieldObj.raw_text && fieldObj.value !== fieldObj.raw_text
            ? `
          <div class="text-[11px] text-slate-500 font-mono">Raw OCR: "${escapeHtml(fieldObj.raw_text)}"</div>
        `
            : ""
        }
        ${extraDetails}
      </div>
    `;
  };

  return `
    <div class="space-y-6 animate-in fade-in duration-150">
      
      <!-- Top Action Bar -->
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2 border-b border-slate-200">
        <div>
          <div class="flex items-center gap-2">
            <span class="font-mono text-xs px-2 py-0.5 bg-blue-100 text-blue-800 rounded font-semibold">${inspection.id}</span>
            <h1 class="text-xl font-bold text-slate-900 tracking-tight">${escapeHtml(inspection.product_name || "Inspection Extraction")}</h1>
          </div>
          <p class="text-xs text-slate-500 mt-0.5">P1 Optical Character Recognition & Structural Declarations Audit</p>
        </div>

        <div class="flex items-center gap-2">
          <a href="#/compliance/${inspectionId}" 
             class="px-3.5 py-2 rounded-lg bg-blue-700 hover:bg-blue-800 text-white text-xs font-semibold shadow transition-colors flex items-center gap-1.5">
            <span>View Rule Compliance</span>
            <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
          </a>
        </div>
      </div>

      <!-- Surface Coverage Overview Banner -->
      <div class="bg-slate-50 border border-slate-200 rounded-xl p-4 flex flex-wrap items-center justify-between gap-3 text-xs">
        <div class="flex items-center gap-2">
          <span class="font-bold text-slate-700">Submitted Surfaces:</span>
          <span class="font-mono ${inspection.image_coverage?.front ? "text-emerald-700 font-semibold" : "text-slate-400"}">Front: ${inspection.image_coverage?.front ? "✓" : "✗"}</span>
          <span class="text-slate-300">|</span>
          <span class="font-mono ${inspection.image_coverage?.back ? "text-emerald-700 font-semibold" : "text-slate-400"}">Back: ${inspection.image_coverage?.back ? "✓" : "✗"}</span>
          <span class="text-slate-300">|</span>
          <span class="font-mono ${inspection.image_coverage?.side ? "text-emerald-700 font-semibold" : "text-slate-400"}">Side: ${inspection.image_coverage?.side ? "✓" : "✗"}</span>
          <span class="text-slate-300">|</span>
          <span class="font-mono ${inspection.image_coverage?.top ? "text-emerald-700 font-semibold" : "text-slate-400"}">Top: ${inspection.image_coverage?.top ? "✓" : "✗"}</span>
        </div>
        <div class="text-[11px] text-slate-500 font-mono">
          Model: OCR-Tesseract-v2 + Regex-NLP
        </div>
      </div>

      <!-- Logical Declarations Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        
        <!-- Block 1: Commodity Identity -->
        <div class="bg-white border border-slate-200 rounded-xl p-4 shadow-sm space-y-3">
          <div class="text-xs font-bold text-slate-900 uppercase tracking-wider pb-1 border-b border-slate-100 flex items-center gap-1.5">
            <svg class="w-4 h-4 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"/></svg>
            Commodity & Classification
          </div>
          ${renderFieldRow("Generic Product Name", extraction.product_name)}
          ${renderFieldRow("Classified Category", extraction.commodity_category)}
          ${renderFieldRow("Country of Origin", extraction.country_of_origin)}
        </div>

        <!-- Block 2: Net Quantity & Measurement -->
        <div class="bg-white border border-slate-200 rounded-xl p-4 shadow-sm space-y-3">
          <div class="text-xs font-bold text-slate-900 uppercase tracking-wider pb-1 border-b border-slate-100 flex items-center gap-1.5">
            <svg class="w-4 h-4 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3"/></svg>
            Net Quantity Declarations
          </div>
          ${renderFieldRow(
            "Primary Declared Qty",
            extraction.net_quantity,
            extraction.net_quantity?.qualifiers?.length
              ? `<div class="text-[11px] text-rose-700 bg-rose-50 p-1.5 rounded border border-rose-200 font-mono mt-1">Warning: Prohibited Qualifier '${extraction.net_quantity.qualifiers.join(", ")}' detected</div>`
              : ""
          )}
          ${
            (extraction.net_quantity_observations || []).length > 1
              ? `
            <div class="p-2.5 bg-amber-50 rounded border border-amber-200 text-xs text-amber-900 font-mono">
              <span class="font-bold">Multi-Surface Observations:</span>
              ${extraction.net_quantity_observations.map((o) => `<div class="text-[11px] mt-0.5">&bull; [${o.location || "panel"}]: ${o.raw_text}</div>`).join("")}
            </div>
          `
              : ""
          }
        </div>

        <!-- Block 3: Maximum Retail Price (MRP) -->
        <div class="bg-white border border-slate-200 rounded-xl p-4 shadow-sm space-y-3">
          <div class="text-xs font-bold text-slate-900 uppercase tracking-wider pb-1 border-b border-slate-100 flex items-center gap-1.5">
            <svg class="w-4 h-4 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
            Maximum Retail Price (MRP)
          </div>
          ${renderFieldRow(
            "Declared Retail Price",
            extraction.mrp,
            extraction.mrp?.is_sticker
              ? `<div class="text-[11px] text-amber-700 bg-amber-50 p-1 rounded font-mono mt-1">Note: Individual Sticker Overlay Detected</div>`
              : ""
          )}
          ${
            (extraction.mrp_observations || []).length > 1
              ? `
            <div class="p-2.5 bg-amber-50 rounded border border-amber-200 text-xs text-amber-900 font-mono">
              <span class="font-bold">Multi-Surface Observations:</span>
              ${extraction.mrp_observations.map((o) => `<div class="text-[11px] mt-0.5">&bull; [${o.location || "panel"}]: ${o.raw_text}</div>`).join("")}
            </div>
          `
              : ""
          }
        </div>

        <!-- Block 4: Dates of Manufacture/Packing -->
        <div class="bg-white border border-slate-200 rounded-xl p-4 shadow-sm space-y-3">
          <div class="text-xs font-bold text-slate-900 uppercase tracking-wider pb-1 border-b border-slate-100 flex items-center gap-1.5">
            <svg class="w-4 h-4 text-amber-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
            Date of Packing / Manufacture
          </div>
          ${renderFieldRow("Manufacture / Packing Date", extraction.date_of_manufacture)}
          ${
            extraction.date_of_manufacture?.has_overwriting
              ? `<div class="text-[11px] text-rose-700 bg-rose-50 p-2 rounded border border-rose-200 font-mono">ALERT: Character stroke overwriting detected in date block</div>`
              : ""
          }
        </div>

        <!-- Block 5: Manufacturer & Address -->
        <div class="bg-white border border-slate-200 rounded-xl p-4 shadow-sm space-y-3">
          <div class="text-xs font-bold text-slate-900 uppercase tracking-wider pb-1 border-b border-slate-100 flex items-center gap-1.5">
            <svg class="w-4 h-4 text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/></svg>
            Manufacturer / Packer Details
          </div>
          ${renderFieldRow("Manufacturer Address", extraction.manufacturer)}
          ${extraction.packer ? renderFieldRow("Packer Address", extraction.packer) : ""}
          ${extraction.importer ? renderFieldRow("Importer Address", extraction.importer) : ""}
        </div>

        <!-- Block 6: Consumer Grievance Channel -->
        <div class="bg-white border border-slate-200 rounded-xl p-4 shadow-sm space-y-3">
          <div class="text-xs font-bold text-slate-900 uppercase tracking-wider pb-1 border-b border-slate-100 flex items-center gap-1.5">
            <svg class="w-4 h-4 text-teal-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/></svg>
            Consumer Care Contact Block
          </div>
          ${renderFieldRow("Contact Details", extraction.consumer_care)}
        </div>

      </div>

    </div>
  `;
}

function escapeHtml(str) {
  return String(str || "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}
