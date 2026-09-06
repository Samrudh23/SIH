/**
 * New Inspection View (Screen 2) for SIH26034
 * Package image upload, surface tagging (front/back/side/top), coverage checklist, and analysis creation.
 */

import { apiService } from "../services/api.js";

export function renderNewInspectionView() {
  return `
    <div class="max-w-4xl mx-auto space-y-6 animate-in fade-in duration-150">
      
      <!-- Header -->
      <div class="pb-2 border-b border-slate-200">
        <h1 class="text-2xl font-bold text-slate-900 tracking-tight">Initiate Packaged Commodity Inspection</h1>
        <p class="text-xs text-slate-500 mt-1">
          Upload container photographs across all visible surfaces to assess statutory declarations under PCR 2011.
        </p>
      </div>

      <form id="new-inspection-form" class="space-y-6">
        
        <!-- Section 1: Inspector & Product Metadata -->
        <div class="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-4">
          <h3 class="text-sm font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <span class="w-6 h-6 rounded bg-blue-100 text-blue-800 flex items-center justify-center text-xs font-mono">1</span>
            <span>Commodity & Inspection Details</span>
          </h3>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            <div>
              <label class="block font-semibold text-slate-700 mb-1">Product / Trade Name *</label>
              <input type="text" id="product_name" required placeholder="e.g. Parle-G Gold Glucose Biscuits" 
                     class="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-slate-900 focus:bg-white focus:ring-2 focus:ring-blue-500 focus:outline-none" />
            </div>

            <div>
              <label class="block font-semibold text-slate-700 mb-1">Brand Name</label>
              <input type="text" id="brand_name" placeholder="e.g. Parle" 
                     class="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-slate-900 focus:bg-white focus:ring-2 focus:ring-blue-500 focus:outline-none" />
            </div>

            <div>
              <label class="block font-semibold text-slate-700 mb-1">Commodity Classification Category</label>
              <select id="commodity_category" 
                      class="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-slate-900 focus:bg-white focus:ring-2 focus:ring-blue-500 focus:outline-none font-mono">
                <option value="General Packaged Commodity">General Packaged Commodity</option>
                <option value="Biscuits">Biscuits (Second Schedule)</option>
                <option value="Bread">Bread (Second Schedule)</option>
                <option value="Edible Oil">Edible Oil (Second Schedule)</option>
                <option value="Tea">Tea (Second Schedule)</option>
                <option value="Coffee">Coffee (Second Schedule)</option>
                <option value="Pan Masala">Pan Masala (Special GSR 881(E) Routing)</option>
                <option value="Medical Device">Medical Device (MDR 2017 Routing)</option>
                <option value="Preserved Food">Preserved Food / Jams</option>
              </select>
            </div>

            <div>
              <label class="block font-semibold text-slate-700 mb-1">Enforcement Official ID</label>
              <input type="text" id="inspector_id" value="insp_delhi_01" 
                     class="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-slate-900 font-mono focus:bg-white focus:ring-2 focus:ring-blue-500 focus:outline-none" />
            </div>
          </div>
        </div>

        <!-- Section 2: Package Surface Coverage Checklist -->
        <div class="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-4">
          <div class="flex items-center justify-between">
            <h3 class="text-sm font-bold text-slate-900 tracking-tight flex items-center gap-2">
              <span class="w-6 h-6 rounded bg-blue-100 text-blue-800 flex items-center justify-center text-xs font-mono">2</span>
              <span>Package Surface Coverage Checklist</span>
            </h3>
            <span class="text-[11px] text-slate-500 font-mono">Section 5 Coverage Model</span>
          </div>

          <p class="text-xs text-slate-600">
            Rule 6(1) compliance requires verifying declarations across multiple container faces. Mark the surfaces submitted to prevent false <code class="text-rose-600 font-mono">POTENTIAL_VIOLATION</code> flags for declarations situated on non-scanned panels.
          </p>

          <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
            <label class="flex items-center gap-2 p-3 rounded-lg border border-slate-200 bg-slate-50 cursor-pointer hover:bg-slate-100">
              <input type="checkbox" id="cov_front" checked class="rounded text-blue-600 focus:ring-blue-500 h-4 w-4" />
              <span class="font-semibold text-slate-800">Front (PDP)</span>
            </label>

            <label class="flex items-center gap-2 p-3 rounded-lg border border-slate-200 bg-slate-50 cursor-pointer hover:bg-slate-100">
              <input type="checkbox" id="cov_back" checked class="rounded text-blue-600 focus:ring-blue-500 h-4 w-4" />
              <span class="font-semibold text-slate-800">Back Panel</span>
            </label>

            <label class="flex items-center gap-2 p-3 rounded-lg border border-slate-200 bg-slate-50 cursor-pointer hover:bg-slate-100">
              <input type="checkbox" id="cov_side" class="rounded text-blue-600 focus:ring-blue-500 h-4 w-4" />
              <span class="font-semibold text-slate-800">Side Faces</span>
            </label>

            <label class="flex items-center gap-2 p-3 rounded-lg border border-slate-200 bg-slate-50 cursor-pointer hover:bg-slate-100">
              <input type="checkbox" id="cov_top" class="rounded text-blue-600 focus:ring-blue-500 h-4 w-4" />
              <span class="font-semibold text-slate-800">Top / Bottom</span>
            </label>
          </div>
        </div>

        <!-- Section 3: Package Imagery Upload -->
        <div class="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-4">
          <h3 class="text-sm font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <span class="w-6 h-6 rounded bg-blue-100 text-blue-800 flex items-center justify-center text-xs font-mono">3</span>
            <span>Upload Package Photographs</span>
          </h3>

          <!-- Dropzone -->
          <div id="drop-zone" class="border-2 border-dashed border-slate-300 rounded-xl p-8 text-center hover:border-blue-500 hover:bg-blue-50/30 transition-colors cursor-pointer">
            <input type="file" id="file-input" multiple accept="image/*" class="hidden" />
            <div class="w-12 h-12 mx-auto rounded-full bg-blue-50 text-blue-600 flex items-center justify-center mb-3">
              <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
            </div>
            <div class="text-sm font-semibold text-slate-800">Click to upload or drag & drop package photographs</div>
            <div class="text-xs text-slate-500 mt-1">JPEG, PNG, WEBP up to 10MB per surface</div>
          </div>

          <!-- Staged Images Queue -->
          <div id="staged-images-container" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
            <!-- Dynamically populated -->
          </div>
        </div>

        <!-- Submit Button -->
        <div class="flex items-center justify-end gap-3 pt-2">
          <a href="#/dashboard" class="px-4 py-2 border border-slate-300 rounded-lg text-slate-700 text-xs font-semibold hover:bg-slate-100 transition-colors">
            Cancel
          </a>
          <button type="submit" id="submit-inspection-btn" 
                  class="px-5 py-2.5 bg-blue-700 hover:bg-blue-800 text-white rounded-lg text-xs font-bold shadow flex items-center gap-2 transition-colors">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"/></svg>
            <span>Run OCR & Compliance Analysis</span>
          </button>
        </div>

      </form>

    </div>
  `;
}
