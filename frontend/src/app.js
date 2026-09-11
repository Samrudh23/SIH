/**
 * Main Application Router & Event Controller for SIH26034
 * Single-Page Application client routing, accessibility coordination, and user interaction bindings.
 */

import { apiService } from "./services/api.js";
import { renderNavbar } from "./components/Navbar.js";
import { renderDashboardView } from "./views/DashboardView.js";
import { renderNewInspectionView } from "./views/NewInspectionView.js";
import { renderExtractionView } from "./views/ExtractionView.js";
import { renderComplianceView } from "./views/ComplianceView.js";
import { renderManualReviewView } from "./views/ManualReviewView.js";
import { renderHistoryView } from "./views/HistoryView.js";
import { renderRuleDetailModal } from "./components/RuleDetailModal.js";
import { renderReportModal } from "./views/ReportModal.js";

class App {
  constructor() {
    this.currentRoute = "dashboard";
    this.currentInspectionId = null;
    this.stagedFiles = [];
    this.init();
  }

  async init() {
    window.addEventListener("hashchange", () => this.handleRoute());
    window.addEventListener("api-mode-changed", () => this.render());

    // Delegate global event handlers
    document.addEventListener("click", (e) => this.handleGlobalClicks(e));
    document.addEventListener("keydown", (e) => this.handleGlobalKeydown(e));

    // Handle initial route
    await this.handleRoute();
  }

  announce(message) {
    const el = document.getElementById("aria-live-announcer");
    if (el) {
      el.textContent = "";
      setTimeout(() => {
        el.textContent = message;
      }, 50);
    }
  }

  parseHash() {
    const hash = window.location.hash.slice(2) || "dashboard";
    const parts = hash.split("/");
    return {
      route: parts[0] || "dashboard",
      id: parts[1] || null,
      subroute: parts[2] || null,
    };
  }

  async handleRoute() {
    const { route, id } = this.parseHash();
    this.currentRoute = route;
    if (id) {
      this.currentInspectionId = id;
    } else if (["extraction", "compliance", "review"].includes(route) && !this.currentInspectionId) {
      // In live mode without a specific inspection ID, redirect to dashboard or history
      window.location.hash = "#/dashboard";
      return;
    }

    await this.render();
    this.announce(`Navigated to ${route} view`);
  }

  async render() {
    const appEl = document.getElementById("app");
    if (!appEl) return;

    // Render Top Navbar
    const navHtml = renderNavbar(this.currentRoute);

    // Render View based on route
    let viewHtml = "";
    try {
      switch (this.currentRoute) {
        case "dashboard":
          viewHtml = await renderDashboardView();
          break;
        case "new":
          viewHtml = renderNewInspectionView();
          break;
        case "extraction":
          viewHtml = await renderExtractionView(this.currentInspectionId);
          break;
        case "compliance":
          viewHtml = await renderComplianceView(this.currentInspectionId);
          break;
        case "review":
          viewHtml = await renderManualReviewView(this.currentInspectionId);
          break;
        case "history":
          viewHtml = await renderHistoryView();
          break;
        default:
          viewHtml = await renderDashboardView();
      }
    } catch (err) {
      viewHtml = `
        <div class="p-8 bg-rose-50 border border-rose-200 rounded-xl text-center space-y-2">
          <div class="text-rose-800 font-bold text-base">Error Loading View</div>
          <div class="text-xs text-rose-600 font-mono">${err.message}</div>
          <a href="#/dashboard" class="inline-block mt-3 text-xs font-semibold text-blue-700 underline focus:ring-2 focus:ring-blue-500 rounded">&larr; Return to Dashboard</a>
        </div>
      `;
    }

    appEl.innerHTML = `
      ${navHtml}
      <main id="main-content" class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 flex-1 w-full" tabindex="-1">
        ${viewHtml}
      </main>
      <div id="modal-container"></div>
    `;

    this.bindViewEvents();
  }

  bindViewEvents() {
    // 1. Mobile Menu Toggle
    const mobileMenuBtn = document.getElementById("mobile-menu-btn");
    const mobileNavDrawer = document.getElementById("mobile-nav-drawer");
    if (mobileMenuBtn && mobileNavDrawer) {
      mobileMenuBtn.onclick = () => {
        const isExpanded = mobileMenuBtn.getAttribute("aria-expanded") === "true";
        mobileMenuBtn.setAttribute("aria-expanded", String(!isExpanded));
        if (isExpanded) {
          mobileNavDrawer.classList.add("hidden");
        } else {
          mobileNavDrawer.classList.remove("hidden");
        }
      };
    }

    // 2. Navbar Mode Toggles
    const mockBtn = document.getElementById("toggle-mock-btn");
    const liveBtn = document.getElementById("toggle-live-btn");
    if (mockBtn) mockBtn.onclick = () => apiService.setMode("mock");
    if (liveBtn) liveBtn.onclick = () => apiService.setMode("live");

    // 3. Quick Fixture Dropdown
    const quickSel = document.getElementById("quick-fixture-select");
    if (quickSel) {
      quickSel.onchange = (e) => {
        const selectedId = e.target.value;
        if (selectedId) {
          window.location.hash = `#/compliance/${selectedId}`;
        }
      };
    }

    // 4. New Inspection View Bindings
    this.bindNewInspectionEvents();

    // 5. Compliance View Rule Filtering
    this.bindComplianceFilterEvents();

    // 6. Manual Review View Bindings (Notes form & Medical Gate)
    this.bindManualReviewEvents();

    // 7. History Filter Bindings
    this.bindHistoryFilterEvents();
  }

  bindNewInspectionEvents() {
    const dropZone = document.getElementById("drop-zone");
    const fileInput = document.getElementById("file-input");
    const form = document.getElementById("new-inspection-form");

    if (dropZone && fileInput) {
      dropZone.onclick = () => fileInput.click();
      dropZone.onkeydown = (e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          fileInput.click();
        }
      };
      dropZone.ondragover = (e) => {
        e.preventDefault();
        dropZone.classList.add("border-blue-500", "bg-blue-50/50");
      };
      dropZone.ondragleave = () => {
        dropZone.classList.remove("border-blue-500", "bg-blue-50/50");
      };
      dropZone.ondrop = (e) => {
        e.preventDefault();
        dropZone.classList.remove("border-blue-500", "bg-blue-50/50");
        if (e.dataTransfer.files) this.handleFilesSelected(e.dataTransfer.files);
      };
      fileInput.onchange = (e) => {
        if (e.target.files) this.handleFilesSelected(e.target.files);
      };
    }

    if (form) {
      form.onsubmit = async (e) => {
        e.preventDefault();
        const submitBtn = document.getElementById("submit-inspection-btn");
        const existingAlert = document.getElementById("inspection-create-error-alert");
        if (existingAlert) existingAlert.remove();

        const updateBtn = (text) => {
          if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = `
              <svg class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path></svg>
              <span>${text}</span>
            `;
          }
        };

        try {
          updateBtn("Creating Inspection Record in P3...");

          const payload = {
            product_name: document.getElementById("product_name").value,
            brand_name: document.getElementById("brand_name").value,
            commodity_category: document.getElementById("commodity_category").value,
            inspector_id: document.getElementById("inspector_id").value || "insp_delhi_01",
            image_coverage: {
              front: document.getElementById("cov_front").checked,
              back: document.getElementById("cov_back").checked,
              side: document.getElementById("cov_side").checked,
              top: document.getElementById("cov_top").checked,
            },
          };

          const newInspection = await apiService.createInspection(payload);

          // Upload staged files with surface labels
          if (this.stagedFiles.length > 0) {
            for (let i = 0; i < this.stagedFiles.length; i++) {
              const item = this.stagedFiles[i];
              updateBtn(`Uploading Surface [${i + 1}/${this.stagedFiles.length}]: ${item.surface}...`);
              await apiService.uploadInspectionImage(newInspection.id, item.file, item.surface);
            }

            // Sync updated surface coverage based on uploaded image surfaces
            const updatedCoverage = {
              front: payload.image_coverage.front || this.stagedFiles.some((f) => f.surface === "front"),
              back: payload.image_coverage.back || this.stagedFiles.some((f) => f.surface === "back"),
              side: payload.image_coverage.side || this.stagedFiles.some((f) => f.surface === "side"),
              top: payload.image_coverage.top || this.stagedFiles.some((f) => f.surface === "top"),
            };
            try {
              await apiService.updateCoverage(newInspection.id, updatedCoverage);
            } catch (covErr) {
              console.warn("Could not sync updated coverage checklist:", covErr);
            }
          }

          // Ensure extraction payload exists for backend compliance evaluation
          updateBtn("Verifying Structured Extraction Payload...");
          let hasExtraction = false;
          try {
            await apiService.getExtraction(newInspection.id);
            hasExtraction = true;
          } catch {
            hasExtraction = false;
          }

          if (!hasExtraction) {
            updateBtn("Synthesizing P1 Extraction Observations...");
            const extractionPayload = apiService.createInitialExtractionPayload(newInspection, this.stagedFiles);
            await apiService.submitExtraction(newInspection.id, extractionPayload);
          }

          // Trigger authoritative P2 RealComplianceEngine
          updateBtn("Evaluating Legal Metrology Rules (15 checks)...");
          await apiService.analyzeInspection(newInspection.id);

          this.stagedFiles = [];
          window.location.hash = `#/compliance/${newInspection.id}`;
        } catch (err) {
          console.error("Failed to create and analyze inspection:", err);
          const errorContainer = document.createElement("div");
          errorContainer.id = "inspection-create-error-alert";
          errorContainer.className = "p-4 bg-rose-50 border border-rose-200 rounded-xl text-xs space-y-1.5 animate-in fade-in";
          errorContainer.innerHTML = `
            <div class="font-bold text-rose-900 flex items-center gap-1.5">
              <svg class="w-4 h-4 text-rose-700" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
              <span>Inspection Creation Failed (${err.status ? "HTTP " + err.status : "Network Error"})</span>
            </div>
            <div class="text-rose-800">${err.message}</div>
            ${err.actionableRemedy ? `<div class="text-slate-600 bg-white/70 p-2 rounded border border-rose-100 mt-1 font-mono">${err.actionableRemedy}</div>` : ""}
          `;
          form.insertBefore(errorContainer, form.lastElementChild);

          if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = `
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"/></svg>
              <span>Retry OCR & Compliance Analysis</span>
            `;
          }
        }
      };
    }
  }

  handleFilesSelected(files) {
    const container = document.getElementById("staged-images-container");
    if (!container) return;

    for (const file of Array.from(files)) {
      const surface = this.stagedFiles.length === 0 ? "front" : this.stagedFiles.length === 1 ? "back" : "side";
      this.stagedFiles.push({ file, surface, preview: URL.createObjectURL(file) });
    }

    this.renderStagedImages();
  }

  renderStagedImages() {
    const container = document.getElementById("staged-images-container");
    if (!container) return;

    container.innerHTML = this.stagedFiles
      .map(
        (item, idx) => `
      <div class="p-3 bg-slate-50 border border-slate-200 rounded-lg flex items-center gap-3">
        <img src="${item.preview}" alt="${item.file.name}" class="w-14 h-14 object-cover rounded border border-slate-300" />
        <div class="flex-1 min-w-0">
          <div class="text-xs font-semibold text-slate-800 truncate">${item.file.name}</div>
          <div class="text-[10px] text-slate-400 font-mono">${(item.file.size / 1024).toFixed(1)} KB</div>
          <select class="surface-picker text-[11px] mt-1 bg-white border border-slate-300 rounded px-1.5 py-0.5" data-idx="${idx}" aria-label="Select surface for ${item.file.name}">
            <option value="front" ${item.surface === "front" ? "selected" : ""}>Front (PDP)</option>
            <option value="back" ${item.surface === "back" ? "selected" : ""}>Back Panel</option>
            <option value="side" ${item.surface === "side" ? "selected" : ""}>Side Face</option>
            <option value="top" ${item.surface === "top" ? "selected" : ""}>Top / Bottom</option>
          </select>
        </div>
        <button type="button" class="remove-staged-btn text-slate-400 hover:text-rose-600 p-1" data-idx="${idx}" aria-label="Remove ${item.file.name}">&times;</button>
      </div>
    `
      )
      .join("");

    container.querySelectorAll(".surface-picker").forEach((sel) => {
      sel.onchange = (e) => {
        const idx = parseInt(e.target.dataset.idx, 10);
        this.stagedFiles[idx].surface = e.target.value;
      };
    });

    container.querySelectorAll(".remove-staged-btn").forEach((btn) => {
      btn.onclick = (e) => {
        const idx = parseInt(e.target.dataset.idx, 10);
        this.stagedFiles.splice(idx, 1);
        this.renderStagedImages();
      };
    });
  }

  bindComplianceFilterEvents() {
    const filterBtns = document.querySelectorAll(".rule-filter-btn");
    const rows = document.querySelectorAll(".rule-row");

    filterBtns.forEach((btn) => {
      btn.onclick = () => {
        filterBtns.forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        const filter = btn.dataset.filter;

        rows.forEach((row) => {
          if (filter === "ALL" || row.dataset.status === filter) {
            row.style.display = "";
          } else {
            row.style.display = "none";
          }
        });
      };
    });

    // Analyze trigger button if inspection pending
    const analyzeBtn = document.getElementById("trigger-analyze-btn");
    if (analyzeBtn) {
      analyzeBtn.onclick = async () => {
        const id = analyzeBtn.dataset.id;
        analyzeBtn.disabled = true;
        analyzeBtn.innerText = "Evaluating Compliance Rules...";
        await apiService.analyzeInspection(id);
        await this.render();
      };
    }
  }

  bindManualReviewEvents() {
    const notesForm = document.getElementById("inspector-notes-form");
    if (notesForm) {
      notesForm.onsubmit = async (e) => {
        e.preventDefault();
        const input = document.getElementById("inspector-notes-input");
        const statusMsg = document.getElementById("notes-status-msg");
        try {
          await apiService.updateNotes(this.currentInspectionId, input.value);
          if (statusMsg) {
            statusMsg.innerText = "✓ Notes saved to inspection record.";
            setTimeout(() => (statusMsg.innerText = ""), 3000);
          }
        } catch (err) {
          alert(`Failed to save notes: ${err.message}`);
        }
      };
    }

    // Medical Device Confirmation Buttons
    const medConfirmBtn = document.getElementById("trigger-med-confirm-btn");
    const medRejectBtn = document.getElementById("trigger-med-reject-btn");

    if (medConfirmBtn) {
      medConfirmBtn.onclick = async () => {
        medConfirmBtn.disabled = true;
        await apiService.confirmMedicalDevice(this.currentInspectionId, true);
        window.location.hash = `#/compliance/${this.currentInspectionId}`;
      };
    }
    if (medRejectBtn) {
      medRejectBtn.onclick = async () => {
        medRejectBtn.disabled = true;
        await apiService.confirmMedicalDevice(this.currentInspectionId, false);
        window.location.hash = `#/compliance/${this.currentInspectionId}`;
      };
    }
  }

  bindHistoryFilterEvents() {
    const form = document.getElementById("history-filter-form");
    const resetBtn = document.getElementById("reset-history-filter");

    if (form) {
      form.onsubmit = async (e) => {
        e.preventDefault();
        const query = {
          product: document.getElementById("history-search").value || undefined,
          compliance_status: document.getElementById("history-status-filter").value || undefined,
          status: document.getElementById("history-workflow-filter").value || undefined,
        };
        const appEl = document.getElementById("app");
        const viewHtml = await renderHistoryView(query);
        appEl.querySelector("main").innerHTML = viewHtml;
        this.bindViewEvents();
      };
    }

    if (resetBtn) {
      resetBtn.onclick = async () => {
        const appEl = document.getElementById("app");
        const viewHtml = await renderHistoryView();
        appEl.querySelector("main").innerHTML = viewHtml;
        this.bindViewEvents();
      };
    }
  }

  handleGlobalKeydown(e) {
    // ESC key closes any open modal or mobile drawer
    if (e.key === "Escape") {
      const modalContainer = document.getElementById("modal-container");
      if (modalContainer && modalContainer.innerHTML.trim() !== "") {
        modalContainer.innerHTML = "";
        return;
      }
      const mobileNavDrawer = document.getElementById("mobile-nav-drawer");
      const mobileMenuBtn = document.getElementById("mobile-menu-btn");
      if (mobileNavDrawer && !mobileNavDrawer.classList.contains("hidden")) {
        mobileNavDrawer.classList.add("hidden");
        if (mobileMenuBtn) mobileMenuBtn.setAttribute("aria-expanded", "false");
      }
    }
  }

  async handleGlobalClicks(e) {
    // 1. Rule Row Click -> Open Deep Detail Modal
    const ruleRow = e.target.closest(".rule-row");
    if (ruleRow) {
      const ruleId = ruleRow.dataset.ruleId;
      try {
        const compliance = await apiService.getComplianceResult(this.currentInspectionId);
        const rule = (compliance.rule_results || []).find((r) => r.rule_id === ruleId);
        if (rule) {
          const modalContainer = document.getElementById("modal-container");
          if (modalContainer) {
            modalContainer.innerHTML = renderRuleDetailModal(rule);
            const closeBtn = document.getElementById("close-rule-modal");
            const closeBtn2 = document.getElementById("close-rule-modal-btn");
            const modal = document.getElementById("rule-detail-modal");
            const closeModal = () => (modalContainer.innerHTML = "");
            if (closeBtn) closeBtn.onclick = closeModal;
            if (closeBtn2) closeBtn2.onclick = closeModal;
            if (modal) {
              modal.onclick = (event) => {
                if (event.target === modal) closeModal();
              };
            }
          }
        }
      } catch (err) {
        console.error("Error opening rule detail:", err);
      }
    }

    // 2. Open Report Modal Button
    const reportBtn = e.target.closest("#open-report-modal-btn");
    if (reportBtn) {
      if (reportBtn.disabled || reportBtn.getAttribute("data-loading") === "true") {
        return;
      }
      const id = reportBtn.dataset.id;
      const modalContainer = document.getElementById("modal-container");
      if (modalContainer) {
        reportBtn.disabled = true;
        reportBtn.setAttribute("data-loading", "true");
        reportBtn.classList.add("opacity-75", "cursor-wait");
        try {
          modalContainer.innerHTML = await renderReportModal(id);
          const closeBtn = document.getElementById("close-report-modal");
          const backdrop = document.getElementById("report-modal-backdrop");
          const printBtn = document.getElementById("print-report-btn");
          const closeModal = () => (modalContainer.innerHTML = "");
          if (closeBtn) closeBtn.onclick = closeModal;
          if (backdrop) {
            backdrop.onclick = (event) => {
              if (event.target === backdrop) closeModal();
            };
          }
          if (printBtn) {
            printBtn.onclick = () => window.print();
          }
        } finally {
          reportBtn.disabled = false;
          reportBtn.removeAttribute("data-loading");
          reportBtn.classList.remove("opacity-75", "cursor-wait");
        }
      }
    }
  }
}

// Bootstrap Application
if (document.readyState === "loading") {
  window.addEventListener("DOMContentLoaded", () => {
    window.sihApp = new App();
  });
} else {
  window.sihApp = new App();
}
