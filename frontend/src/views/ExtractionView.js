/**
 * Extraction Review View (Screen 3) for SIH26034
 * Displays OCR/Vision extractions from P1 organized by logical declaration blocks.
 * Provides full transparency into what OCR observed across all surfaces.
 */

import { apiService } from "../services/api.js";

function escapeHtml(str) {
  return String(str || "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

function renderFieldRow(label, fieldObj, extraDetails = "") {
  if (!fieldObj || (fieldObj.value === undefined && !fieldObj.raw_text)) {
    return `
      <div class="py-2 border-b border-slate-100 text-xs">
        <div class="flex items-center justify-between">
          <span class="font-medium text-slate-500">${escapeHtml(label)}:</span>
          <span class="font-mono text-slate-400 bg-slate-100 px-2 py-0.5 rounded text-[10px] uppercase font-semibold">NOT DETECTED</span>
        </div>
      </div>
    `;
  }

  const conf = fieldObj.confidence !== undefined ? Math.round(fieldObj.confidence * 100) : null;
  const confClass = conf !== null && conf >= 75 ? "text-emerald-700 bg-emerald-50" : "text-amber-700 bg-amber-50 font-bold";
  const loc = fieldObj.surface_location || fieldObj.location;

  return `
    <div class="py-2.5 border-b border-slate-100 text-xs space-y-1">
      <div class="flex items-start justify-between gap-2">
        <span class="font-semibold text-slate-700">${escapeHtml(label)}:</span>
        <div class="flex items-center gap-1.5 flex-wrap justify-end">
          ${loc ? `<span class="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-slate-100 text-slate-600">${escapeHtml(loc)}</span>` : ""}
          ${conf !== null ? `<span class="font-mono text-[10px] px-1.5 py-0.5 rounded ${confClass}">OCR Conf: ${conf}%</span>` : ""}
        </div>
      </div>
      <div class="font-mono text-slate-900 font-bold text-xs bg-slate-50 p-2 rounded border border-slate-200 break-words">
        ${escapeHtml(fieldObj.value !== undefined && fieldObj.value !== null ? String(fieldObj.value) : fieldObj.raw_text)}
      </div>
      ${
        fieldObj.raw_text && String(fieldObj.value) !== fieldObj.raw_text
          ? `<div class="text-[11px] text-slate-500 font-mono">Raw OCR: "${escapeHtml(fieldObj.raw_text)}"</div>`
          : ""
      }
      ${
        fieldObj.bounding_box
          ? `<div class="text-[10px] text-slate-400 font-mono">BBox: [x:${Math.round(fieldObj.bounding_box.x)}, y:${Math.round(fieldObj.bounding_box.y)}, w:${Math.round(fieldObj.bounding_box.w)}, h:${Math.round(fieldObj.bounding_box.h)}]</div>`
          : ""
      }
      ${extraDetails}
    </div>
  `;
}

export async function renderExtractionView(inspectionId) {
  let inspection, extraction, evidence;
  try {
    inspection = await apiService.getInspection(inspectionId);
    extraction = await apiService.getExtraction(inspectionId);
    try {
      evidence = await apiService.getEvidence(inspectionId);
    } catch {
      evidence = { images: [], rule_evidence: [] };
    }
  } catch (err) {
    return `
      <div class="p-8 text-center bg-white border border-slate-200 rounded-xl shadow-sm space-y-3 max-w-xl mx-auto">
        <div class="w-12 h-12 mx-auto rounded-full bg-rose-100 text-rose-700 flex items-center justify-center font-bold">!</div>
        <div class="text-rose-800 font-bold text-base">Extraction Data Unavailable</div>
        <p class="text-xs text-slate-600">${escapeHtml(err.message)}</p>
        ${err.actionableRemedy ? `<div class="text-xs text-slate-500 bg-slate-50 p-2.5 rounded border border-slate-200">${escapeHtml(err.actionableRemedy)}</div>` : ""}
        <div class="pt-2">
          <a href="#/compliance/${inspectionId}" class="inline-block text-xs font-semibold text-blue-700 hover:underline">&larr; Return to Compliance Results</a>
        </div>
      </div>
    `;
  }

  const cov = inspection.image_coverage || {};
  const images = evidence?.images || [];

  return `
    <div class="space-y-6 animate-in fade-in duration-150">
      
      <!-- Top Action Bar -->
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2 border-b border-slate-200">
        <div>
          <div class="flex items-center gap-2">
            <span class="font-mono text-xs px-2.5 py-0.5 bg-blue-100 text-blue-800 rounded font-semibold">${inspection.id}</span>
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
        <div class="flex items-center gap-2 flex-wrap">
          <span class="font-bold text-slate-700">Submitted Package Surfaces:</span>
          <span class="font-mono px-2 py-0.5 rounded ${cov.front ? "bg-emerald-100 text-emerald-800 font-semibold" : "bg-slate-200 text-slate-500"}">
            Front: ${cov.front ? "✓ Present" : "✗ Missing"}
          </span>
          <span class="font-mono px-2 py-0.5 rounded ${cov.back ? "bg-emerald-100 text-emerald-800 font-semibold" : "bg-slate-200 text-slate-500"}">
            Back: ${cov.back ? "✓ Present" : "✗ Missing"}
          </span>
          <span class="font-mono px-2 py-0.5 rounded ${cov.side ? "bg-emerald-100 text-emerald-800 font-semibold" : "bg-slate-200 text-slate-500"}">
            Side: ${cov.side ? "✓ Present" : "✗ Missing"}
          </span>
          <span class="font-mono px-2 py-0.5 rounded ${cov.top ? "bg-emerald-100 text-emerald-800 font-semibold" : "bg-slate-200 text-slate-500"}">
            Top: ${cov.top ? "✓ Present" : "✗ Missing"}
          </span>
        </div>
        <div class="text-[11px] text-slate-500 font-mono">
          Uploaded Images: ${images.length}
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
          ${
            extraction.medical_device_markers
              ? renderFieldRow("CDSCO / Medical Device Marker", extraction.medical_device_markers)
              : ""
          }
        </div>

        <!-- Block 2: Net Quantity & Measurement -->
        <div class="bg-white border border-slate-200 rounded-xl p-4 shadow-sm space-y-3">
          <div class="text-xs font-bold text-slate-900 uppercase tracking-wider pb-1 border-b border-slate-100 flex items-center gap-1.5">
            <svg class="w-4 h-4 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3"/></svg>
            Net Quantity Declarations
          </div>
          ${renderFieldRow(
            "Primary Net Quantity",
            extraction.net_quantity,
            `
              ${extraction.net_quantity?.unit ? `<div class="text-[11px] text-slate-600 font-mono">Declared Unit: <strong>${escapeHtml(extraction.net_quantity.unit)}</strong></div>` : ""}
              ${
                extraction.net_quantity?.qualifiers?.length
                  ? `<div class="text-[11px] text-rose-700 bg-rose-50 p-1.5 rounded border border-rose-200 font-mono mt-1">Warning: Prohibited Qualifier '${escapeHtml(extraction.net_quantity.qualifiers.join(", "))}' detected</div>`
                  : ""
              }
              ${
                extraction.net_quantity?.quiet_zone_clear !== undefined
                  ? `<div class="text-[11px] font-mono text-slate-600">Quiet Zone Clear (Visual Aid): ${extraction.net_quantity.quiet_zone_clear ? "Yes" : "Obstructed / Low Clearance"}</div>`
                  : ""
              }
            `
          )}
          ${
            (extraction.net_quantity_observations || []).length > 0
              ? `
            <div class="p-2.5 bg-slate-50 rounded border border-slate-200 text-xs space-y-1.5">
              <span class="font-bold text-slate-700">All Net Quantity Observations (${extraction.net_quantity_observations.length}):</span>
              ${extraction.net_quantity_observations
                .map(
                  (o, idx) => `
                <div class="p-1.5 bg-white rounded border border-slate-200 font-mono text-[11px]">
                  <div class="flex justify-between text-slate-600">
                    <span class="font-semibold">[${escapeHtml(o.surface_location || o.location || "panel")}]:</span>
                    <span>${o.value !== undefined ? o.value + " " + (o.unit || "") : ""}</span>
                  </div>
                  <div class="text-slate-800 break-words mt-0.5">"${escapeHtml(o.raw_text)}"</div>
                  <div class="text-[10px] text-slate-400">OCR Conf: ${Math.round((o.confidence || 0) * 100)}%</div>
                </div>
              `
                )
                .join("")}
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
            "Primary Retail Price",
            extraction.mrp,
            `
              ${
                extraction.mrp?.tax_inclusivity !== undefined
                  ? `<div class="text-[11px] font-mono ${extraction.mrp.tax_inclusivity ? "text-emerald-700" : "text-rose-700 font-bold"}">Tax Inclusivity Wording: ${extraction.mrp.tax_inclusivity ? "Detected (Inclusive of all taxes)" : "NOT DETECTED"}</div>`
                  : ""
              }
              ${
                extraction.mrp?.is_sticker
                  ? `<div class="text-[11px] text-amber-700 bg-amber-50 p-1 rounded font-mono mt-1">Sticker Overlay Detected (Individual Sticker)</div>`
                  : ""
              }
            `
          )}
          ${
            (extraction.mrp_observations || []).length > 0
              ? `
            <div class="p-2.5 bg-slate-50 rounded border border-slate-200 text-xs space-y-1.5">
              <span class="font-bold text-slate-700">All MRP Observations (${extraction.mrp_observations.length}):</span>
              ${extraction.mrp_observations
                .map(
                  (o, idx) => `
                <div class="p-1.5 bg-white rounded border border-slate-200 font-mono text-[11px]">
                  <div class="flex justify-between text-slate-600">
                    <span class="font-semibold">[${escapeHtml(o.surface_location || o.location || "panel")}]:</span>
                    <span>${o.currency || "₹"} ${o.value !== undefined ? o.value : ""}</span>
                  </div>
                  <div class="text-slate-800 break-words mt-0.5">"${escapeHtml(o.raw_text)}"</div>
                  <div class="flex justify-between text-[10px] text-slate-400 mt-0.5">
                    <span>Tax Inc: ${o.tax_inclusivity ? "Yes" : "No"}</span>
                    <span>OCR Conf: ${Math.round((o.confidence || 0) * 100)}%</span>
                  </div>
                </div>
              `
                )
                .join("")}
            </div>
          `
              : ""
          }
        </div>

        <!-- Block 4: Dates of Packing / Manufacture / Expiry -->
        <div class="bg-white border border-slate-200 rounded-xl p-4 shadow-sm space-y-3">
          <div class="text-xs font-bold text-slate-900 uppercase tracking-wider pb-1 border-b border-slate-100 flex items-center gap-1.5">
            <svg class="w-4 h-4 text-amber-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
            Dates of Packing & Manufacture
          </div>
          ${renderFieldRow(
            "Packing / Manufacture Date",
            extraction.date_of_manufacture,
            `
              ${extraction.date_of_manufacture?.month && extraction.date_of_manufacture?.year ? `<div class="text-[11px] text-slate-600 font-mono">Parsed: Month: ${escapeHtml(extraction.date_of_manufacture.month)}, Year: ${escapeHtml(extraction.date_of_manufacture.year)}</div>` : ""}
              ${extraction.date_of_manufacture?.is_rubber_stamped ? `<div class="text-[11px] text-amber-700 bg-amber-50 p-1 rounded font-mono mt-1">Rubber Stamped Marking</div>` : ""}
              ${extraction.date_of_manufacture?.has_overwriting ? `<div class="text-[11px] text-rose-700 bg-rose-50 p-1.5 rounded border border-rose-200 font-mono mt-1 font-bold">ALERT: Character stroke overwriting detected</div>` : ""}
            `
          )}
        </div>

        <!-- Block 5: Manufacturer / Packer / Importer -->
        <div class="bg-white border border-slate-200 rounded-xl p-4 shadow-sm space-y-3">
          <div class="text-xs font-bold text-slate-900 uppercase tracking-wider pb-1 border-b border-slate-100 flex items-center gap-1.5">
            <svg class="w-4 h-4 text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/></svg>
            Manufacturer / Packer / Importer
          </div>
          ${renderFieldRow("Manufacturer Address", extraction.manufacturer)}
          ${extraction.packer ? renderFieldRow("Packer Address", extraction.packer) : ""}
          ${
            extraction.importer
              ? renderFieldRow(
                  "Importer Address",
                  extraction.importer,
                  extraction.is_importer_on_pdp !== undefined
                    ? `<div class="text-[11px] font-mono text-slate-600 mt-1">Importer on PDP: ${extraction.is_importer_on_pdp ? "Yes" : "No"}</div>`
                    : ""
                )
              : ""
          }
        </div>

        <!-- Block 6: Consumer Grievance Channel -->
        <div class="bg-white border border-slate-200 rounded-xl p-4 shadow-sm space-y-3">
          <div class="text-xs font-bold text-slate-900 uppercase tracking-wider pb-1 border-b border-slate-100 flex items-center gap-1.5">
            <svg class="w-4 h-4 text-teal-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/></svg>
            Consumer Care Contact Block
          </div>
          ${renderFieldRow(
            "Consumer Grievance Details",
            extraction.consumer_care,
            `
              ${extraction.consumer_care?.phone ? `<div class="text-[11px] font-mono text-slate-700">Telephone / Toll-Free: <strong>${escapeHtml(extraction.consumer_care.phone)}</strong></div>` : ""}
              ${extraction.consumer_care?.email ? `<div class="text-[11px] font-mono text-slate-700">Email: <strong>${escapeHtml(extraction.consumer_care.email)}</strong></div>` : ""}
              ${extraction.consumer_care?.address ? `<div class="text-[11px] font-mono text-slate-700">Postal Address: ${escapeHtml(extraction.consumer_care.address)}</div>` : ""}
            `
          )}
        </div>

      </div>

      <!-- Uploaded Images & Evidence Gallery -->
      ${
        images.length > 0
          ? `
        <div class="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-3">
          <h3 class="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-1.5">
            <svg class="w-4 h-4 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
            Package Image Evidence (${images.length} Surfaces)
          </h3>
          <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
            ${images
              .map(
                (img) => `
              <div class="border border-slate-200 rounded-lg overflow-hidden bg-slate-50">
                <img src="${img.url || (apiService.baseUrl + '/images/' + (img.file_name || ''))}" alt="${escapeHtml(img.image_type || "Surface")}" class="w-full h-36 object-contain bg-slate-900" onerror="this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><rect fill=%22%231e293b%22 width=%22100%22 height=%22100%22/><text fill=%22%2394a3b8%22 x=%2250%22 y=%2255%22 font-size=%2210%22 text-anchor=%22middle%22>${escapeHtml(img.image_type || "Image")}</text></svg>'" />
                <div class="p-2 text-[11px] font-mono">
                  <div class="font-bold text-slate-800 uppercase">${escapeHtml(img.image_type || "package_image")}</div>
                  <div class="text-slate-500 truncate">${escapeHtml(img.file_name)}</div>
                </div>
              </div>
            `
              )
              .join("")}
          </div>
        </div>
      `
          : ""
      }

    </div>
  `;
}
