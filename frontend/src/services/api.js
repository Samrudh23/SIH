/**
 * Compliance API Service for SIH26034
 * Connects to P3 FastAPI backend (/api) with automatic mock fixture fallback.
 * Allows instant live/mock mode switching for seamless demo & offline inspection.
 */

import { MOCK_FIXTURES, MOCK_DASHBOARD_SUMMARY, RULE_METADATA } from "./mockFixtures.js";

class ComplianceApiService {
  constructor() {
    this.baseUrl = (typeof window !== "undefined" && window.API_BASE_URL) || "http://127.0.0.1:8000/api";
    // Check localStorage for saved mode preference
    const savedMode = typeof localStorage !== "undefined" ? localStorage.getItem("sih_api_mode") : null;
    this.useMock = savedMode ? savedMode === "mock" : true; // Default to mock for self-contained evaluation
    this.isBackendOnline = false;
    this.checkBackendHealth();
  }

  setMode(mode) {
    this.useMock = mode === "mock";
    if (typeof localStorage !== "undefined") {
      localStorage.setItem("sih_api_mode", mode);
    }
    if (typeof window !== "undefined" && window.dispatchEvent) {
      window.dispatchEvent(new CustomEvent("api-mode-changed", { detail: { mode: this.useMock ? "mock" : "live" } }));
    }
  }

  getMode() {
    return this.useMock ? "mock" : "live";
  }

  async checkBackendHealth() {
    try {
      const res = await fetch(`${this.baseUrl}/health`, { method: "GET", signal: AbortSignal.timeout(2000) });
      this.isBackendOnline = res.ok;
    } catch {
      this.isBackendOnline = false;
    }
    return this.isBackendOnline;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    try {
      const res = await fetch(url, {
        headers: {
          Accept: "application/json",
          ...(options.headers || {}),
        },
        ...options,
      });

      if (!res.ok) {
        let errDetail = `HTTP ${res.status} ${res.statusText}`;
        try {
          const errJson = await res.json();
          errDetail = errJson.detail || JSON.stringify(errJson);
        } catch {
          // ignore
        }
        throw new Error(errDetail);
      }

      return await res.json();
    } catch (err) {
      console.warn(`[ComplianceApiService] Network request to ${url} failed:`, err.message);
      throw err;
    }
  }

  // 1. Dashboard Summary
  async getDashboardSummary() {
    if (!this.useMock) {
      try {
        return await this.request("/dashboard/summary");
      } catch (err) {
        console.warn("Live backend failed, falling back to mock fixtures:", err);
      }
    }
    return structuredClone(MOCK_DASHBOARD_SUMMARY);
  }

  // 2. List Inspections
  async listInspections(query = {}) {
    if (!this.useMock) {
      try {
        const params = new URLSearchParams();
        if (query.status) params.append("status", query.status);
        if (query.compliance_status) params.append("compliance_status", query.compliance_status);
        if (query.product) params.append("product", query.product);
        if (query.has_violations !== undefined) params.append("has_violations", String(query.has_violations));
        return await this.request(`/inspections?${params.toString()}`);
      } catch (err) {
        console.warn("Live backend failed, falling back to mock fixtures:", err);
      }
    }

    // Mock filtering
    let items = Object.values(MOCK_FIXTURES).map((f) => f.inspection);
    if (query.status) {
      items = items.filter((i) => i.status === query.status);
    }
    if (query.compliance_status) {
      items = items.filter((i) => i.compliance_status === query.compliance_status);
    }
    if (query.product) {
      const q = query.product.toLowerCase();
      items = items.filter((i) => (i.product_name || "").toLowerCase().includes(q) || (i.brand_name || "").toLowerCase().includes(q));
    }
    return {
      total: items.length,
      items: structuredClone(items),
    };
  }

  // 3. Get Inspection Details
  async getInspection(inspectionId) {
    if (!this.useMock) {
      try {
        return await this.request(`/inspections/${inspectionId}`);
      } catch (err) {
        console.warn("Live backend failed, checking mock fixtures:", err);
      }
    }

    const fixture = MOCK_FIXTURES[inspectionId];
    if (fixture) {
      return structuredClone(fixture.inspection);
    }
    throw new Error(`Inspection '${inspectionId}' not found.`);
  }

  // 4. Create New Inspection
  async createInspection(payload) {
    if (!this.useMock) {
      try {
        return await this.request("/inspections", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
      } catch (err) {
        console.warn("Live backend failed, using mock creation:", err);
      }
    }

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

  // 5. Upload Image Evidence
  async uploadImage(inspectionId, file, imageType = "package_image") {
    if (!this.useMock) {
      try {
        const formData = new FormData();
        formData.append("file", file);
        formData.append("image_type", imageType);

        const res = await fetch(`${this.baseUrl}/inspections/${inspectionId}/image`, {
          method: "POST",
          body: formData,
        });
        if (!res.ok) throw new Error(await res.text());
        return await res.json();
      } catch (err) {
        console.warn("Live upload failed, storing in mock state:", err);
      }
    }

    const fixture = MOCK_FIXTURES[inspectionId];
    if (!fixture) throw new Error(`Inspection '${inspectionId}' not found.`);

    const evidenceId = `ev-${Date.now().toString().slice(-4)}`;
    const mockUrl = URL.createObjectURL(file);
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

  // 6. Get Evidence Images
  async getEvidence(inspectionId) {
    if (!this.useMock) {
      try {
        return await this.request(`/inspections/${inspectionId}/evidence`);
      } catch (err) {
        console.warn("Live evidence retrieval failed, checking mock:", err);
      }
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

  // 7. Get Extraction Payload
  async getExtraction(inspectionId) {
    if (!this.useMock) {
      try {
        return await this.request(`/inspections/${inspectionId}/extraction`);
      } catch (err) {
        console.warn("Live extraction retrieval failed, checking mock:", err);
      }
    }

    const fixture = MOCK_FIXTURES[inspectionId];
    if (fixture && fixture.extraction) {
      return structuredClone(fixture.extraction);
    }
    throw new Error(`No extraction found for inspection '${inspectionId}'.`);
  }

  // 8. Run / Trigger Compliance Analysis
  async analyzeInspection(inspectionId) {
    if (!this.useMock) {
      try {
        return await this.request(`/inspections/${inspectionId}/analyze`, {
          method: "POST",
        });
      } catch (err) {
        console.warn("Live analysis failed, checking mock:", err);
      }
    }

    const fixture = MOCK_FIXTURES[inspectionId];
    if (!fixture) throw new Error(`Inspection '${inspectionId}' not found.`);

    if (!fixture.compliance) {
      // Generate default compliant response if newly created
      fixture.compliance = structuredClone(MOCK_FIXTURES["insp-001"].compliance);
      fixture.compliance.inspection_id = inspectionId;
      fixture.inspection.compliance_status = "COMPLIANT";
      fixture.inspection.status = "ANALYSIS_COMPLETE";
      fixture.inspection.has_result = true;
    }
    return structuredClone(fixture.compliance);
  }

  // 9. Get Compliance Result
  async getComplianceResult(inspectionId) {
    if (!this.useMock) {
      try {
        return await this.request(`/inspections/${inspectionId}/result`);
      } catch (err) {
        console.warn("Live result retrieval failed, checking mock:", err);
      }
    }

    const fixture = MOCK_FIXTURES[inspectionId];
    if (fixture && fixture.compliance) {
      return structuredClone(fixture.compliance);
    }
    throw new Error(`No compliance result found for inspection '${inspectionId}'.`);
  }

  // 10. Medical Device Confirmation Gate (Fix 2)
  async confirmMedicalDevice(inspectionId, isConfirmed) {
    if (!this.useMock) {
      try {
        return await this.request(`/inspections/${inspectionId}/medical-device-confirmation`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ is_confirmed_medical_device: isConfirmed }),
        });
      } catch (err) {
        console.warn("Live medical confirmation failed, using mock state:", err);
      }
    }

    const fixture = MOCK_FIXTURES[inspectionId];
    if (!fixture) throw new Error(`Inspection '${inspectionId}' not found.`);

    if (isConfirmed) {
      // Suppress PCR rules to NOT_APPLICABLE
      const confirmedCompliance = structuredClone(MOCK_FIXTURES["insp-007"].compliance);
      confirmedCompliance.inspection_id = inspectionId;
      fixture.compliance = confirmedCompliance;
      fixture.inspection.compliance_status = "NOT_APPLICABLE";
    } else {
      // Revert to standard PCR compliance check
      const normalCompliance = structuredClone(MOCK_FIXTURES["insp-001"].compliance);
      normalCompliance.inspection_id = inspectionId;
      normalCompliance.rule_results = normalCompliance.rule_results.map((r) => {
        if (r.rule_id === "REQ-MVP-11") {
          return {
            ...r,
            status: "COMPLIANT",
            reason: "Inspector explicitly rejected medical device classification. Standard PCR 2011 checks applied.",
            explanation_for_inspector: "Medical device classification rejected by inspector. Checked under standard PCR 2011 rules.",
          };
        }
        return r;
      });
      fixture.compliance = normalCompliance;
      fixture.inspection.compliance_status = "COMPLIANT";
    }

    return structuredClone(fixture.compliance);
  }

  // 11. Update Inspector Notes
  async updateNotes(inspectionId, notes) {
    if (!this.useMock) {
      try {
        return await this.request(`/inspections/${inspectionId}/notes`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ notes }),
        });
      } catch (err) {
        console.warn("Live note update failed, updating mock:", err);
      }
    }

    const fixture = MOCK_FIXTURES[inspectionId];
    if (fixture) {
      fixture.inspection.notes = notes;
      return structuredClone(fixture.inspection);
    }
    throw new Error(`Inspection '${inspectionId}' not found.`);
  }

  // 12. Get Printable Report URL
  getReportHtmlUrl(inspectionId) {
    return `${this.baseUrl}/reports/${inspectionId}/html`;
  }
}

export const apiService = new ComplianceApiService();
