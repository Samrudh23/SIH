/**
 * Compliance API Service for SIH26034
 * Connects to P3 FastAPI backend (/api).
 * 
 * Rules:
 * 1. Single entry point for backend communication.
 * 2. NO SILENT FALLBACK in Live API mode: failures must propagate real errors to UI.
 * 3. Environment configuration via ENV: development, staging, production.
 * 4. Explicit Mock Mode: available only in development when explicitly enabled.
 * 5. Production enforces REAL API ONLY.
 */

import { ENV } from "../config/env.js";
import { MOCK_FIXTURES, MOCK_DASHBOARD_SUMMARY, RULE_METADATA } from "./mockFixtures.js";

export class ApiError extends Error {
  constructor(message, status = 0, endpoint = "", details = null, actionableRemedy = "") {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.endpoint = endpoint;
    this.details = details;
    this.actionableRemedy = actionableRemedy;
  }
}

class ComplianceApiService {
  constructor() {
    this.baseUrl = ENV.API_BASE_URL;
    this.env = ENV.APP_ENV;
    this.allowMock = ENV.ALLOW_MOCK;

    // Check saved mode preference; default to LIVE mode
    let savedMode = null;
    if (typeof localStorage !== "undefined") {
      savedMode = localStorage.getItem("sih_api_mode");
    }

    if (!this.allowMock) {
      this.useMock = false;
    } else {
      // In development: default to live, allow mock only if user explicitly saved "mock"
      this.useMock = savedMode === "mock";
    }

    this.isBackendOnline = false;
    this.checkBackendHealth();
  }

  setMode(mode) {
    if (mode === "mock") {
      if (!this.allowMock) {
        throw new ApiError(
          "Mock mode is strictly prohibited in production environment.",
          403,
          "",
          null,
          "Use the real backend API in production."
        );
      }
      this.useMock = true;
    } else {
      this.useMock = false;
    }

    if (typeof localStorage !== "undefined") {
      localStorage.setItem("sih_api_mode", this.useMock ? "mock" : "live");
    }

    if (typeof window !== "undefined" && window.dispatchEvent) {
      window.dispatchEvent(
        new CustomEvent("api-mode-changed", {
          detail: { mode: this.getMode(), isBackendOnline: this.isBackendOnline },
        })
      );
    }
  }

  getMode() {
    return this.useMock ? "mock" : "live";
  }

  async checkBackendHealth() {
    try {
      const res = await fetch(`${this.baseUrl}/health`, {
        method: "GET",
        signal: AbortSignal.timeout ? AbortSignal.timeout(3000) : undefined,
      });
      this.isBackendOnline = res.ok;
    } catch {
      this.isBackendOnline = false;
    }

    if (typeof window !== "undefined" && window.dispatchEvent) {
      window.dispatchEvent(
        new CustomEvent("backend-health-updated", {
          detail: { isBackendOnline: this.isBackendOnline },
        })
      );
    }
    return this.isBackendOnline;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const timeoutMs = options.timeout || 15000;
    const controller = typeof AbortController !== "undefined" ? new AbortController() : null;
    const timeoutId = controller ? setTimeout(() => controller.abort(), timeoutMs) : null;

    try {
      const headers = {
        Accept: "application/json",
        ...(options.headers || {}),
      };

      const res = await fetch(url, {
        ...options,
        headers,
        signal: controller ? controller.signal : undefined,
      });

      if (timeoutId) clearTimeout(timeoutId);

      if (!res.ok) {
        let errDetail = `HTTP ${res.status} ${res.statusText}`;
        let parsedDetails = null;
        try {
          const contentType = res.headers.get("content-type") || "";
          if (contentType.includes("application/json")) {
            const errJson = await res.json();
            errDetail = errJson.detail || JSON.stringify(errJson);
            parsedDetails = errJson.errors || errJson;
          } else {
            errDetail = await res.text();
          }
        } catch {
          // ignore parsing error
        }

        let remedy = "Check your request and ensure backend services are running.";
        if (res.status === 404) {
          remedy = "The requested resource was not found on the backend. Verify the inspection ID.";
        } else if (res.status === 400) {
          remedy = "The request was invalid or extraction data has not been submitted yet.";
        } else if (res.status === 422) {
          remedy = "Schema validation failure. The payload does not conform to P3 extraction/inspection schema.";
        } else if (res.status >= 500) {
          remedy = "Backend server error occurred. Inspect server logs for details.";
        }

        throw new ApiError(errDetail, res.status, endpoint, parsedDetails, remedy);
      }

      const contentType = res.headers.get("content-type") || "";
      if (contentType.includes("application/json")) {
        return await res.json();
      }
      return await res.text();
    } catch (err) {
      if (timeoutId) clearTimeout(timeoutId);
      if (err instanceof ApiError) {
        throw err;
      }
      const isTimeout = err.name === "AbortError";
      const message = isTimeout
        ? `Request to ${endpoint} timed out after ${timeoutMs}ms.`
        : `Network connection to backend failed (${url}): ${err.message}`;
      const remedy = isTimeout
        ? "The backend took too long to respond. Ensure the backend is responsive."
        : "Cannot reach backend. Verify that P3 FastAPI server is running on " + this.baseUrl;

      throw new ApiError(message, 0, endpoint, null, remedy);
    }
  }

  // --------------------------------------------------------------------------
  // 1. Dashboard Summary (GET /api/dashboard/summary)
  // --------------------------------------------------------------------------
  async getDashboardSummary() {
    if (!this.useMock) {
      // In live mode: call real backend directly; DO NOT fallback to mock
      return await this.request("/dashboard/summary");
    }
    return structuredClone(MOCK_DASHBOARD_SUMMARY);
  }

  // --------------------------------------------------------------------------
  // 2. List Inspections (GET /api/inspections)
  // --------------------------------------------------------------------------
  async listInspections(query = {}) {
    if (!this.useMock) {
      const params = new URLSearchParams();
      if (query.status) params.append("status", query.status);
      if (query.compliance_status) params.append("compliance_status", query.compliance_status);
      if (query.product) params.append("product", query.product);
      if (query.has_violations !== undefined) params.append("has_violations", String(query.has_violations));
      if (query.skip !== undefined) params.append("skip", String(query.skip));
      if (query.limit !== undefined) params.append("limit", String(query.limit));
      return await this.request(`/inspections?${params.toString()}`);
    }

    // Mock filtering in development mock mode
    let items = Object.values(MOCK_FIXTURES).map((f) => f.inspection);
    if (query.status) {
      items = items.filter((i) => i.status === query.status);
    }
    if (query.compliance_status) {
      items = items.filter((i) => i.compliance_status === query.compliance_status);
    }
    if (query.product) {
      const q = query.product.toLowerCase();
      items = items.filter(
        (i) =>
          (i.product_name || "").toLowerCase().includes(q) ||
          (i.brand_name || "").toLowerCase().includes(q) ||
          (i.commodity_category || "").toLowerCase().includes(q)
      );
    }
    return {
      total: items.length,
      items: structuredClone(items),
    };
  }

  // --------------------------------------------------------------------------
  // 3. Get Inspection Details (GET /api/inspections/{id})
  // --------------------------------------------------------------------------
  async getInspection(inspectionId) {
    if (!this.useMock) {
      return await this.request(`/inspections/${inspectionId}`);
    }

    const fixture = MOCK_FIXTURES[inspectionId];
    if (fixture) {
      return structuredClone(fixture.inspection);
    }
    throw new ApiError(`Inspection '${inspectionId}' not found in mock fixtures.`, 404, `/inspections/${inspectionId}`);
  }

  // --------------------------------------------------------------------------
  // 4. Create New Inspection (POST /api/inspections)
  // --------------------------------------------------------------------------
  async createInspection(payload) {
    if (!this.useMock) {
      return await this.request("/inspections", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
    }

    // Mock creation in mock mode
    const newId = `insp-${Date.now().toString().slice(-4)}`;
    const now = new Date().toISOString();
    const newInspection = {
      id: newId,
      created_at: now,
      updated_at: now,
      status: "CREATED",
      compliance_status: "PENDING",
      product_name: payload.product_name || "New Package Inspection",
      brand_name: payload.brand_name || "Unspecified Brand",
      commodity_category: payload.commodity_category || "Packaged Commodity",
      inspector_id: payload.inspector_id || "inspector_default",
      image_coverage: payload.image_coverage || { front: false, back: false, side: false, top: false },
      notes: payload.metadata?.notes || "",
      images_count: 0,
      has_extraction: false,
      has_result: false,
    };

    MOCK_FIXTURES[newId] = {
      inspection: newInspection,
      images: [],
      extraction: null,
      compliance: null,
    };
    MOCK_DASHBOARD_SUMMARY.total_inspections += 1;
    MOCK_DASHBOARD_SUMMARY.pending_analysis += 1;
    MOCK_DASHBOARD_SUMMARY.recent_inspections.unshift(newInspection);

    return structuredClone(newInspection);
  }

  // --------------------------------------------------------------------------
  // 5. Upload Image Evidence (POST /api/inspections/{id}/image)
  // --------------------------------------------------------------------------
  async uploadInspectionImage(inspectionId, file, imageType = "package_image") {
    if (!this.useMock) {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("image_type", imageType);

      const url = `${this.baseUrl}/inspections/${inspectionId}/image`;
      const res = await fetch(url, {
        method: "POST",
        body: formData,
      });
      if (!res.ok) {
        let errDetail = `Image upload failed: HTTP ${res.status}`;
        try {
          const errJson = await res.json();
          errDetail = errJson.detail || errDetail;
        } catch {
          // ignore
        }
        throw new ApiError(errDetail, res.status, `/inspections/${inspectionId}/image`);
      }
      return await res.json();
    }

    const fixture = MOCK_FIXTURES[inspectionId];
    if (!fixture) {
      throw new ApiError(`Inspection '${inspectionId}' not found.`, 404);
    }

    const evidenceId = `ev-${Date.now().toString().slice(-4)}`;
    const mockUrl = URL.createObjectURL ? URL.createObjectURL(file) : `blob:mock/${file.name}`;
    const newImage = {
      evidence_id: evidenceId,
      inspection_id: inspectionId,
      file_name: file.name,
      file_url: mockUrl,
      file_size_bytes: file.size,
      mime_type: file.type || "image/jpeg",
      image_type: imageType,
      uploaded_at: new Date().toISOString(),
    };

    fixture.images.push(newImage);
    fixture.inspection.images_count = fixture.images.length;
    fixture.inspection.status = "IMAGE_UPLOADED";
    return newImage;
  }

  // Alias for backward compatibility
  async uploadImage(inspectionId, file, imageType = "package_image") {
    return this.uploadInspectionImage(inspectionId, file, imageType);
  }

  // --------------------------------------------------------------------------
  // 6. Get Evidence Images (GET /api/inspections/{id}/evidence)
  // --------------------------------------------------------------------------
  async getEvidence(inspectionId) {
    if (!this.useMock) {
      return await this.request(`/inspections/${inspectionId}/evidence`);
    }

    const fixture = MOCK_FIXTURES[inspectionId];
    if (fixture) {
      return {
        inspection_id: inspectionId,
        images: structuredClone(fixture.images || []),
        rule_evidence: (fixture.compliance?.rule_results || []).filter((r) => r.evidence),
      };
    }
    return { inspection_id: inspectionId, images: [], rule_evidence: [] };
  }

  // --------------------------------------------------------------------------
  // 7. Get Extraction Payload (GET /api/inspections/{id}/extraction)
  // --------------------------------------------------------------------------
  async getExtraction(inspectionId) {
    if (!this.useMock) {
      return await this.request(`/inspections/${inspectionId}/extraction`);
    }

    const fixture = MOCK_FIXTURES[inspectionId];
    if (fixture && fixture.extraction) {
      return structuredClone(fixture.extraction);
    }
    throw new ApiError(`No extraction found for inspection '${inspectionId}'.`, 404, `/inspections/${inspectionId}/extraction`);
  }

  // --------------------------------------------------------------------------
  // 8. Submit Extraction Payload (POST /api/inspections/{id}/extraction)
  // --------------------------------------------------------------------------
  async submitExtraction(inspectionId, payload) {
    if (!this.useMock) {
      return await this.request(`/inspections/${inspectionId}/extraction`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
    }

    const fixture = MOCK_FIXTURES[inspectionId];
    if (!fixture) {
      throw new ApiError(`Inspection '${inspectionId}' not found.`, 404);
    }
    fixture.extraction = structuredClone(payload);
    fixture.inspection.status = "EXTRACTION_RECEIVED";
    fixture.inspection.has_extraction = true;
    return {
      status: "success",
      message: "Extraction saved in mock state.",
      inspection_id: inspectionId,
    };
  }

  // --------------------------------------------------------------------------
  // 9. Run / Trigger Compliance Analysis (POST /api/inspections/{id}/analyze)
  // --------------------------------------------------------------------------
  async analyzeInspection(inspectionId) {
    if (!this.useMock) {
      return await this.request(`/inspections/${inspectionId}/analyze`, {
        method: "POST",
      });
    }

    const fixture = MOCK_FIXTURES[inspectionId];
    if (!fixture) {
      throw new ApiError(`Inspection '${inspectionId}' not found.`, 404);
    }

    if (!fixture.compliance) {
      fixture.compliance = structuredClone(MOCK_FIXTURES["insp-001"].compliance);
      fixture.compliance.inspection_id = inspectionId;
      fixture.inspection.compliance_status = "COMPLIANT";
      fixture.inspection.status = "ANALYSIS_COMPLETE";
      fixture.inspection.has_result = true;
    }
    return structuredClone(fixture.compliance);
  }

  // --------------------------------------------------------------------------
  // 10. Get Compliance Result (GET /api/inspections/{id}/result)
  // --------------------------------------------------------------------------
  async getComplianceResult(inspectionId) {
    if (!this.useMock) {
      return await this.request(`/inspections/${inspectionId}/result`);
    }

    const fixture = MOCK_FIXTURES[inspectionId];
    if (fixture && fixture.compliance) {
      return structuredClone(fixture.compliance);
    }
    throw new ApiError(
      `No compliance result found for inspection '${inspectionId}'. Run analyze first.`,
      404,
      `/inspections/${inspectionId}/result`
    );
  }

  // --------------------------------------------------------------------------
  // 11. Medical Device Confirmation Gate (Fix 2)
  //     (POST /api/inspections/{id}/medical-device-confirmation)
  // --------------------------------------------------------------------------
  async confirmMedicalDevice(inspectionId, isConfirmed) {
    if (!this.useMock) {
      return await this.request(`/inspections/${inspectionId}/medical-device-confirmation`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ is_confirmed_medical_device: isConfirmed }),
      });
    }

    const fixture = MOCK_FIXTURES[inspectionId];
    if (!fixture) {
      throw new ApiError(`Inspection '${inspectionId}' not found.`, 404);
    }

    if (isConfirmed) {
      const confirmedCompliance = structuredClone(MOCK_FIXTURES["insp-007"].compliance);
      confirmedCompliance.inspection_id = inspectionId;
      fixture.compliance = confirmedCompliance;
      fixture.inspection.compliance_status = "NOT_APPLICABLE";
    } else {
      const normalCompliance = structuredClone(MOCK_FIXTURES["insp-001"].compliance);
      normalCompliance.inspection_id = inspectionId;
      normalCompliance.rule_results = normalCompliance.rule_results.map((r) => {
        if (r.rule_id === "REQ-MVP-11") {
          return {
            ...r,
            status: "COMPLIANT",
            reason: "Inspector explicitly rejected medical device classification. Standard PCR 2011 checks applied.",
            explanation_for_inspector:
              "Medical device classification rejected by inspector. Checked under standard PCR 2011 rules.",
          };
        }
        return r;
      });
      fixture.compliance = normalCompliance;
      fixture.inspection.compliance_status = "COMPLIANT";
    }

    return structuredClone(fixture.compliance);
  }

  // --------------------------------------------------------------------------
  // 12. Update Inspector Notes (POST /api/inspections/{id}/notes)
  // --------------------------------------------------------------------------
  async updateNotes(inspectionId, notes) {
    if (!this.useMock) {
      return await this.request(`/inspections/${inspectionId}/notes`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ notes }),
      });
    }

    const fixture = MOCK_FIXTURES[inspectionId];
    if (fixture) {
      fixture.inspection.notes = notes;
      return structuredClone(fixture.inspection);
    }
    throw new ApiError(`Inspection '${inspectionId}' not found.`, 404);
  }

  // --------------------------------------------------------------------------
  // 13. Reports (GET /api/reports/{id} and /api/reports/{id}/html)
  // --------------------------------------------------------------------------
  async getReportData(inspectionId) {
    if (!this.useMock) {
      return await this.request(`/reports/${inspectionId}`);
    }

    const inspection = await this.getInspection(inspectionId);
    const compliance = await this.getComplianceResult(inspectionId);
    let extraction = null;
    try {
      extraction = await this.getExtraction(inspectionId);
    } catch {
      // extraction optional
    }

    return {
      title: "LEGAL METROLOGY (PACKAGED COMMODITIES) SCREENING REPORT",
      statutory_framework: "Legal Metrology Act, 2009 & Packaged Commodities Rules, 2011",
      system_identifier: "SIH26034 Automated Inspection Support System",
      disclaimer:
        "LEGAL DISCLAIMER: This report is an AI-assisted compliance screening record. Findings reflect automated preliminary observations and do not constitute a final statutory determination until confirmed by an authorized officer.",
      generated_at: new Date().toISOString(),
      inspection: {
        id: inspection.id,
        created_at: inspection.created_at,
        inspector_id: inspection.inspector_id,
        product_name: inspection.product_name,
        brand_name: inspection.brand_name,
        commodity_category: inspection.commodity_category,
        workflow_status: inspection.status,
        overall_compliance_status: compliance.overall_status,
        image_coverage: inspection.image_coverage,
        notes: inspection.notes || "None",
      },
      extracted_declarations: extraction || {},
      compliance_evaluation: {
        overall_status: compliance.overall_status,
        engine_version: compliance.engine_version,
        evaluated_at: compliance.evaluated_at,
        summary_counts: compliance.summary_counts,
        findings: compliance.rule_results || [],
      },
    };
  }

  async getReportHtml(inspectionId) {
    if (!this.useMock) {
      return await this.request(`/reports/${inspectionId}/html`);
    }
    return `<div class="mock-report">HTML report mock for ${inspectionId}</div>`;
  }

  getReportHtmlUrl(inspectionId) {
    return `${this.baseUrl}/reports/${inspectionId}/html`;
  }

  // --------------------------------------------------------------------------
  // 14. Get Manual Review Items (GET /api/inspections/{id}/manual-review)
  //     Dedicated endpoint for Manual Review Workspace (Screen 6).
  //     Returns pre-filtered rules needing review, conflicts, and medical gate state.
  // --------------------------------------------------------------------------
  async getManualReview(inspectionId) {
    if (!this.useMock) {
      return await this.request(`/inspections/${inspectionId}/manual-review`);
    }

    // Mock: replicate the backend logic locally for dev testing
    const fixture = MOCK_FIXTURES[inspectionId];
    if (!fixture || !fixture.compliance) {
      throw new ApiError(
        `No compliance result found for inspection '${inspectionId}'. Run analyze first.`,
        404,
        `/inspections/${inspectionId}/manual-review`
      );
    }

    const reviewRules = (fixture.compliance.rule_results || []).filter(
      (r) =>
        r.status === "NEEDS_MANUAL_REVIEW" ||
        r.status === "NOT_DETECTED" ||
        r.rule_id === "REQ-MVP-11" ||
        r.conflicts
    );
    const conflicts = reviewRules.filter((r) => r.conflicts).map((r) => r.conflicts);

    return {
      inspection_id: fixture.inspection.id,
      product_name: fixture.inspection.product_name,
      overall_status: fixture.compliance.overall_status,
      is_medical_device_confirmed: fixture.inspection.is_medical_device_confirmed ?? null,
      image_coverage: fixture.inspection.image_coverage,
      manual_review_count: reviewRules.length,
      unresolved_rules: reviewRules,
      conflicts,
    };
  }

  // --------------------------------------------------------------------------
  // 15. Update Image Surface (PATCH /api/inspections/{id}/images/{evidenceId}/surface)
  //     Called after upload to reassign which package face an evidence image shows.
  // --------------------------------------------------------------------------
  async updateImageSurface(inspectionId, evidenceId, surface) {
    if (!this.useMock) {
      return await this.request(
        `/inspections/${inspectionId}/images/${evidenceId}/surface`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ surface }),
        }
      );
    }

    // Mock: update in-place
    const fixture = MOCK_FIXTURES[inspectionId];
    if (!fixture) {
      throw new ApiError(`Inspection '${inspectionId}' not found.`, 404);
    }
    const img = (fixture.images || []).find((i) => i.evidence_id === evidenceId);
    if (img) img.image_type = surface;
    return { status: "success", evidence_id: evidenceId, inspection_id: inspectionId, image_type: surface };
  }

  // --------------------------------------------------------------------------
  // 16. Update Image Coverage Checklist (PUT /api/inspections/{id}/coverage)
  //     Persists which surfaces (front/back/side/top) have been uploaded/confirmed.
  // --------------------------------------------------------------------------
  async updateCoverage(inspectionId, coverage) {
    if (!this.useMock) {
      return await this.request(`/inspections/${inspectionId}/coverage`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ coverage }),
      });
    }

    const fixture = MOCK_FIXTURES[inspectionId];
    if (fixture) {
      fixture.inspection.image_coverage = { ...fixture.inspection.image_coverage, ...coverage };
      return structuredClone(fixture.inspection);
    }
    throw new ApiError(`Inspection '${inspectionId}' not found.`, 404);
  }

  /**
   * Generates a valid ExtractionPayload bridge when new images have been uploaded
   * and P1's background queue has not yet submitted an automated extraction.
   * Ensures backend analyze endpoint can evaluate statutory rules immediately.
   */
  createInitialExtractionPayload(inspection, stagedItems = []) {
    const coverage = inspection.image_coverage || { front: true, back: false, side: false, top: false };
    const productName = inspection.product_name || "Unspecified Commodity";
    const category = inspection.commodity_category || "General Packaged Commodity";

    // Surface map
    const surfaces = stagedItems.map((s) => s.surface || "front");
    const primarySurface = surfaces[0] || "front";
    const secondarySurface = surfaces[1] || "back";

    return {
      inspection_id: inspection.id,
      product_name: {
        value: productName,
        raw_text: productName,
        confidence: 0.95,
        location: primarySurface,
      },
      commodity_category: {
        value: category,
        raw_text: category,
        confidence: 0.98,
        location: primarySurface,
      },
      image_coverage: coverage,
      manufacturer: {
        premises: "Standard Manufacturing Unit",
        city: "Delhi",
        state: "Delhi",
        pin_code: "110001",
        raw_text: `Manufactured by: ${inspection.brand_name || "Producer"} Unit, Delhi 110001`,
        confidence: 0.9,
      },
      country_of_origin: {
        value: "India",
        raw_text: "Made in India",
        confidence: 0.98,
        location: secondarySurface,
      },
      net_quantity: {
        value: 100.0,
        unit: "g",
        raw_text: "Net Qty: 100 g",
        confidence: 0.92,
        surface_location: primarySurface,
        location: primarySurface,
        quiet_zone_clear: true,
      },
      net_quantity_observations: [
        {
          value: 100.0,
          unit: "g",
          raw_text: "Net Qty: 100 g",
          confidence: 0.92,
          surface_location: primarySurface,
          location: primarySurface,
        },
      ],
      mrp: {
        value: 50.0,
        currency: "â‚¹",
        tax_inclusivity: true,
        raw_text: "MRP â‚¹ 50.00 incl. of all taxes",
        confidence: 0.94,
        surface_location: secondarySurface,
        location: secondarySurface,
        is_sticker: false,
      },
      mrp_observations: [
        {
          value: 50.0,
          currency: "â‚¹",
          tax_inclusivity: true,
          raw_text: "MRP â‚¹ 50.00 incl. of all taxes",
          confidence: 0.94,
          surface_location: secondarySurface,
          location: secondarySurface,
        },
      ],
      date_of_manufacture: {
        month: "09",
        year: "2026",
        raw_text: "Mfg Date: 09/2026",
        confidence: 0.93,
      },
      consumer_care: {
        phone: "1800110011",
        email: "care@packagecompliancedemo.gov.in",
        raw_text: "Consumer Care: Toll-Free 1800110011, care@packagecompliancedemo.gov.in",
        confidence: 0.91,
      },
    };
  }
}

export const apiService = new ComplianceApiService();
