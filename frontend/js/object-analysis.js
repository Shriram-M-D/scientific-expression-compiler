/* Object File Analysis Module */

const ANALYSIS_API = "http://localhost:5000/api/analyze";

// Global state for analysis data
let currentAnalysisData = {
  O0: null,
  O2: null,
  comparison: null,
  currentLevel: "O0",
};

// Chart instances
let instructionChart = null;
let sizeChart = null;
let comparisonInstChart = null;
let comparisonSizeChart = null;

// Build object files
async function buildObjectFiles() {
  const btn = document.getElementById("buildBtn");
  const statusDiv = document.getElementById("analysisStatus");
  const statusMsg = document.getElementById("statusMessage");

  btn.disabled = true;
  btn.textContent = "Building...";

  showAnalysisStatus("Building object files...", "info");

  try {
    const response = await fetch(`${ANALYSIS_API}/build`, {
      method: "POST",
    });

    const data = await response.json();

    if (data.success) {
      const built = data.data.built || [];
      const message =
        `Successfully built ${built.length} object file(s):\n` +
        built.map((b) => `  ${b.level}: ${b.size} bytes`).join("\n");

      showAnalysisStatus(message, "success");

      // Enable analysis buttons
      document.getElementById("analyzeO0Btn").disabled = false;
      document.getElementById("analyzeO2Btn").disabled = false;
      document.getElementById("compareBtn").disabled = false;
    } else {
      showAnalysisStatus(`Build failed: ${data.error}`, "error");
    }
  } catch (error) {
    showAnalysisStatus(`Network error: ${error.message}`, "error");
  } finally {
    btn.disabled = false;
    btn.textContent = "Build Object Files";
  }
}

// Analyze object file
async function analyzeObject(level) {
  const btn = document.getElementById(`analyze${level}Btn`);
  const originalText = btn.textContent;

  btn.disabled = true;
  btn.textContent = "Analyzing...";

  showAnalysisStatus(`Analyzing ${level} object file...`, "info");

  try {
    const response = await fetch(`${ANALYSIS_API}/object?level=${level}`);
    const data = await response.json();

    if (data.success) {
      currentAnalysisData[level] = data.data;
      currentAnalysisData.currentLevel = level;

      showAnalysisStatus(`Analysis complete for ${level}`, "success");

      // Update the active view with new data
      const activeTab = document.querySelector(".analysis-view:not(.hidden)");
      if (activeTab) {
        const tabId = activeTab.id.replace("view-", "");
        updateAnalysisView(tabId, level);
      }
    } else {
      showAnalysisStatus(`Analysis failed: ${data.error}`, "error");
    }
  } catch (error) {
    showAnalysisStatus(`Network error: ${error.message}`, "error");
  } finally {
    btn.disabled = false;
    btn.textContent = originalText;
  }
}

// Compare optimizations
async function compareOptimizations() {
  const btn = document.getElementById("compareBtn");
  btn.disabled = true;
  btn.textContent = "Comparing...";

  showAnalysisStatus("Comparing optimization levels...", "info");

  try {
    const response = await fetch(`${ANALYSIS_API}/optimization`);
    const data = await response.json();

    if (data.success) {
      currentAnalysisData.comparison = data.data;
      showAnalysisStatus("Comparison complete", "success");

      // Switch to comparison tab
      switchAnalysisTab("comparison");
      updateComparisonView(data.data);
    } else {
      showAnalysisStatus(`Comparison failed: ${data.error}`, "error");
    }
  } catch (error) {
    showAnalysisStatus(`Network error: ${error.message}`, "error");
  } finally {
    btn.disabled = false;
    btn.textContent = "Compare Optimizations";
  }
}

// Switch between analysis tabs
function switchAnalysisTab(tabName) {
  // Update tab buttons with enhanced styling
  document.querySelectorAll('[id^="tab-"]').forEach((tab) => {
    tab.style.color = "var(--text-secondary)";
    tab.style.background = "transparent";
    tab.style.borderBottom = "none";
  });

  const activeTab = document.getElementById(`tab-${tabName}`);
  if (activeTab) {
    activeTab.style.color = "var(--accent)";
    activeTab.style.background = "var(--bg-secondary)";
    activeTab.style.borderBottom = "3px solid var(--accent)";
  }

  // Update views
  document.querySelectorAll(".analysis-view").forEach((view) => {
    view.classList.add("hidden");
  });

  const activeView = document.getElementById(`view-${tabName}`);
  if (activeView) {
    activeView.classList.remove("hidden");
    updateAnalysisView(tabName, currentAnalysisData.currentLevel);
  }
}

// Update analysis view based on tab
function updateAnalysisView(tabName, level) {
  const data = currentAnalysisData[level];

  if (!data) {
    return;
  }

  switch (tabName) {
    case "disassembly":
      updateDisassemblyView(data.disassembly);
      break;
    case "symbols":
      updateSymbolsView(data.symbols);
      break;
    case "sections":
      updateSectionsView(data.sections);
      break;
    case "metrics":
      updateMetricsView(data.size);
      break;
    case "comparison":
      if (currentAnalysisData.comparison) {
        updateComparisonView(currentAnalysisData.comparison);
      }
      break;
  }
}

// Update disassembly view
function updateDisassemblyView(data) {
  if (!data || data.error) {
    return;
  }

  // Update stats
  document.getElementById("funcCount").textContent = data.total_functions || 0;
  document.getElementById("instCount").textContent =
    data.total_instructions || 0;

  // Display disassembly
  const codeDiv = document.getElementById("disassemblyCode");
  let html = "";

  (data.functions || []).forEach((func) => {
    html += `<div style="margin-bottom: 20px;">`;
    html += `<div style="color: #61afef; font-weight: bold; margin-bottom: 8px;">`;
    html += `${func.address} &lt;${func.name}&gt;:</div>`;

    (func.instructions || []).forEach((inst) => {
      html += `<div style="padding-left: 20px; font-family: monospace;">`;
      html += `<span style="color: #98c379;">${inst.address}:</span> `;
      html += `<span style="color: #abb2bf;">${escapeHtml(inst.code)}</span>`;
      html += `</div>`;
    });

    html += `</div>`;
  });

  codeDiv.innerHTML =
    html || '<p style="color: var(--text-secondary);">No disassembly data</p>';

  // Update instruction frequency chart
  updateInstructionChart(data.instruction_frequency || {});
}

// Update instruction frequency chart
function updateInstructionChart(freqData) {
  const ctx = document.getElementById("instructionChart");
  if (!ctx) return;

  // Sort by frequency and take top 15
  const sorted = Object.entries(freqData)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 15);

  const labels = sorted.map(([inst, _]) => inst);
  const values = sorted.map(([_, count]) => count);

  if (instructionChart) {
    instructionChart.destroy();
  }

  instructionChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Instruction Count",
          data: values,
          backgroundColor: "#3b82f6",
          borderColor: "#2563eb",
          borderWidth: 1,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: {
          display: false,
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            color: "#9ca3af",
          },
          grid: {
            color: "#2d3748",
          },
        },
        x: {
          ticks: {
            color: "#9ca3af",
          },
          grid: {
            color: "#2d3748",
          },
        },
      },
    },
  });
}

// Update symbols view
function updateSymbolsView(data) {
  if (!data || data.error) {
    return;
  }

  const symbols = data.symbols || {};

  // Update counts
  document.getElementById("globalCount").textContent = (
    symbols.global || []
  ).length;
  document.getElementById("localCount").textContent = (
    symbols.local || []
  ).length;

  // Display global symbols
  const globalDiv = document.getElementById("globalSymbols");
  globalDiv.innerHTML = formatSymbolList(symbols.global || []);

  // Display local symbols
  const localDiv = document.getElementById("localSymbols");
  localDiv.innerHTML = formatSymbolList(symbols.local || []);
}

// Format symbol list
function formatSymbolList(symbols) {
  if (symbols.length === 0) {
    return '<p style="color: var(--text-secondary);">No symbols</p>';
  }

  let html = "";
  symbols.forEach((sym) => {
    html += `<div style="margin-bottom: 4px;">`;
    html += `<span style="color: #98c379;">${sym.type}</span> `;
    html += `<span style="color: #61afef;">${escapeHtml(sym.name)}</span>`;
    if (sym.address && sym.address !== "0") {
      html += ` <span style="color: #5c6370;">@ ${sym.address}</span>`;
    }
    html += `</div>`;
  });

  return html;
}

// Update sections view
function updateSectionsView(data) {
  if (!data || data.error) {
    return;
  }

  const tbody = document.getElementById("sectionsBody");
  const sections = data.sections || [];

  if (sections.length === 0) {
    tbody.innerHTML =
      '<tr><td colspan="4" class="p-2" style="color: var(--text-secondary);">No sections data</td></tr>';
    return;
  }

  let html = "";
  sections.forEach((sec) => {
    html += `<tr style="border-bottom: 1px solid var(--border);">`;
    html += `<td class="p-2">${escapeHtml(sec.name)}</td>`;
    html += `<td class="p-2">${escapeHtml(sec.type)}</td>`;
    html += `<td class="p-2 font-mono text-xs">${sec.address}</td>`;
    html += `<td class="p-2">${sec.size} bytes</td>`;
    html += `</tr>`;
  });

  tbody.innerHTML = html;
}

// Update metrics view
function updateMetricsView(data) {
  if (!data || data.error) {
    return;
  }

  const metrics = data.metrics || {};

  // Update size displays
  document.getElementById("textSize").textContent = formatBytes(
    metrics.text || 0,
  );
  document.getElementById("dataSize").textContent = formatBytes(
    metrics.data || 0,
  );
  document.getElementById("bssSize").textContent = formatBytes(
    metrics.bss || 0,
  );
  document.getElementById("totalSize").textContent = formatBytes(
    metrics.total || 0,
  );

  // Update size chart
  updateSizeChart(metrics);
}

// Update size chart
function updateSizeChart(metrics) {
  const ctx = document.getElementById("sizeChart");
  if (!ctx) return;

  if (sizeChart) {
    sizeChart.destroy();
  }

  sizeChart = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: [".text", ".data", ".bss", ".rodata"],
      datasets: [
        {
          data: [
            metrics.text || 0,
            metrics.data || 0,
            metrics.bss || 0,
            metrics.rodata || 0,
          ],
          backgroundColor: ["#3b82f6", "#10b981", "#f59e0b", "#8b5cf6"],
          borderWidth: 2,
          borderColor: "#1a2035",
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: {
          position: "bottom",
          labels: {
            color: "#9ca3af",
            padding: 15,
          },
        },
      },
    },
  });
}

// Update comparison view
function updateComparisonView(data) {
  if (!data) {
    return;
  }

  // Update stats
  const disasm = data.disassembly || {};
  const size = data.size || {};

  document.getElementById("instReduction").textContent =
    `${disasm.reduction || 0} instructions`;
  document.getElementById("sizeReduction").textContent =
    `${size.reduction || 0} bytes`;
  document.getElementById("reductionPercent").textContent =
    `${disasm.reduction_percent || 0}%`;

  // Update instruction comparison chart
  updateComparisonInstChart(disasm);

  // Update size comparison chart
  updateComparisonSizeChart(size);
}

// Update comparison instruction chart
function updateComparisonInstChart(data) {
  const ctx = document.getElementById("comparisonInstChart");
  if (!ctx) return;

  if (comparisonInstChart) {
    comparisonInstChart.destroy();
  }

  comparisonInstChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: ["-O0", "-O2"],
      datasets: [
        {
          label: "Instruction Count",
          data: [data.O0_instructions || 0, data.O2_instructions || 0],
          backgroundColor: ["#ef4444", "#10b981"],
          borderWidth: 1,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: {
          display: false,
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            color: "#9ca3af",
          },
          grid: {
            color: "#2d3748",
          },
        },
        x: {
          ticks: {
            color: "#9ca3af",
          },
          grid: {
            color: "#2d3748",
          },
        },
      },
    },
  });
}

// Update comparison size chart
function updateComparisonSizeChart(data) {
  const ctx = document.getElementById("comparisonSizeChart");
  if (!ctx) return;

  if (comparisonSizeChart) {
    comparisonSizeChart.destroy();
  }

  const o0 = data.O0 || {};
  const o2 = data.O2 || {};

  comparisonSizeChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: [".text", ".data", ".bss", "Total"],
      datasets: [
        {
          label: "-O0",
          data: [o0.text || 0, o0.data || 0, o0.bss || 0, o0.total || 0],
          backgroundColor: "#ef4444",
        },
        {
          label: "-O2",
          data: [o2.text || 0, o2.data || 0, o2.bss || 0, o2.total || 0],
          backgroundColor: "#10b981",
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: {
          labels: {
            color: "#9ca3af",
          },
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            color: "#9ca3af",
          },
          grid: {
            color: "#2d3748",
          },
        },
        x: {
          ticks: {
            color: "#9ca3af",
          },
          grid: {
            color: "#2d3748",
          },
        },
      },
    },
  });
}

// Show analysis status
function showAnalysisStatus(message, type) {
  const statusDiv = document.getElementById("analysisStatus");
  const statusMsg = document.getElementById("statusMessage");

  statusDiv.classList.remove("hidden");
  statusMsg.textContent = message;

  // Color based on type
  if (type === "success") {
    statusDiv.style.borderLeft = "3px solid #10b981";
  } else if (type === "error") {
    statusDiv.style.borderLeft = "3px solid #ef4444";
  } else {
    statusDiv.style.borderLeft = "3px solid #3b82f6";
  }

  // Auto-hide after 5 seconds for success messages
  if (type === "success") {
    setTimeout(() => {
      statusDiv.classList.add("hidden");
    }, 5000);
  }
}

// Utility functions
function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

function formatBytes(bytes) {
  if (bytes === 0) return "0";
  if (bytes < 1024) return bytes;
  return bytes.toLocaleString();
}

// Initialize on page load
document.addEventListener("DOMContentLoaded", () => {
  // Set default tab
  switchAnalysisTab("disassembly");
});
