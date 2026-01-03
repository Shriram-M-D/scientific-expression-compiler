/* Main Application Logic */

const API_BASE_URL = "http://localhost:5000";

// Set example expression
function setExample(expr) {
  document.getElementById("expressionInput").value = expr;
}

// Main compilation function
async function compileExpression() {
  const input = document.getElementById("expressionInput").value.trim();

  if (!input) {
    showError("Please enter an expression");
    return;
  }

  // Hide all sections
  hideAllSections();

  try {
    const response = await fetch(`${API_BASE_URL}/api/compile`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ expression: input }),
    });

    const data = await response.json();

    if (data.success) {
      displayResults(data);
    } else {
      showError(data.error || "Compilation failed");
    }
  } catch (error) {
    showError(
      `Network error: ${error.message}. Make sure the backend server is running.`
    );
  }
}

// Display all compilation results
function displayResults(data) {
  // Show result
  document.getElementById("resultSection").classList.remove("hidden");
  const resultDiv = document.getElementById("resultValue");
  resultDiv.innerHTML = `\\(${formatNumber(data.result)}\\)`;

  // Render MathJax
  if (window.MathJax) {
    MathJax.typesetPromise([resultDiv]).catch((err) => console.log(err));
  }

  // Show tokens
  if (data.tokens) {
    showTokens(data.tokens);
  }

  // Show postfix
  if (data.postfix) {
    showPostfix(data.postfix);
  }

  // Show AST
  if (data.ast) {
    showAST(data.ast);
  }

  // Show intermediate code
  if (data.intermediateCode) {
    showIntermediateCode(data.intermediateCode);
  }

  // Show calculus visualization if applicable
  if (data.calculusType !== "none" && data.calculusSteps) {
    showCalculusVisualization(data);
  }
}

// Show tokens with color coding
function showTokens(tokens) {
  document.getElementById("tokensSection").classList.remove("hidden");
  const container = document.getElementById("tokensDisplay");
  container.innerHTML = "";

  const colorMap = {
    NUMBER: "",
    PLUS: "",
    MINUS: "",
    MULTIPLY: "",
    DIVIDE: "",
    POWER: "",
    MODULO: "",
    FACTORIAL: "",
    LPAREN: "",
    RPAREN: "",
    COMMA: "",
    FUNCTION: "",
    CONSTANT: "",
    VARIABLE: "",
    END: "",
  };

  tokens.forEach((token, index) => {
    const badge = document.createElement("span");
    badge.className = `token-badge ${colorMap[token.type] || ""}`;
    badge.style.animationDelay = `${index * 0.05}s`;
    badge.innerHTML = `<strong>${escapeHtml(
      token.value
    )}</strong> <small style="opacity: 0.6;">${token.type}</small>`;
    container.appendChild(badge);
  });
}

// Show postfix notation
function showPostfix(postfix) {
  document.getElementById("postfixSection").classList.remove("hidden");
  const container = document.getElementById("postfixDisplay");
  container.innerHTML = "";

  postfix.forEach((item, index) => {
    const badge = document.createElement("span");
    badge.className = "token-badge";
    badge.style.animationDelay = `${index * 0.05}s`;
    badge.textContent = item;
    container.appendChild(badge);
  });
}

// Show intermediate code
function showIntermediateCode(code) {
  document.getElementById("intermediateSection").classList.remove("hidden");
  const container = document.getElementById("intermediateCode");
  container.innerHTML = code
    .map(
      (line, i) =>
        `<div style="animation-delay: ${i * 0.1}s" class="fadeIn">${
          i + 1
        }. ${escapeHtml(line)}</div>`
    )
    .join("");
}

// Show calculus visualization
function showCalculusVisualization(data) {
  document.getElementById("calculusSection").classList.remove("hidden");

  // Show steps
  const stepsContainer = document.getElementById("calculusSteps");
  stepsContainer.innerHTML = data.calculusSteps
    .map(
      (step, i) =>
        `<div style="animation-delay: ${i * 0.05}s" class="fadeIn">${escapeHtml(
          step.description
        )}</div>`
    )
    .join("");

  // Create chart
  createCalculusChart(data);
}

// Create calculus chart using Chart.js
function createCalculusChart(data) {
  const canvas = document.getElementById("calculusChart");
  const ctx = canvas.getContext("2d");

  // Destroy existing chart if any
  if (window.calculusChartInstance) {
    window.calculusChartInstance.destroy();
  }

  const steps = data.calculusSteps;

  // For differentiation, show the actual function being differentiated
  // For integration, show the function being integrated with area fill
  if (data.calculusType === "differentiation") {
    // Extract the function being differentiated and the point
    const point = steps[Math.floor(steps.length / 2)].x; // center point

    // Generate function values around the differentiation point
    const xValues = [];
    const yValues = [];
    const range = 4; // Show function in range [point-2, point+2]
    const numPoints = 100;

    for (let i = 0; i < numPoints; i++) {
      const x = point - range / 2 + (i / numPoints) * range;
      xValues.push(x);
      // Find corresponding y value from steps or interpolate
      const closestStep = steps.reduce((prev, curr) =>
        Math.abs(curr.x - x) < Math.abs(prev.x - x) ? curr : prev
      );
      yValues.push(closestStep.fx);
    }

    window.calculusChartInstance = new Chart(ctx, {
      type: "line",
      data: {
        labels: xValues.map((x) => x.toFixed(2)),
        datasets: [
          {
            label: "f(x)",
            data: yValues,
            borderColor: "#3b82f6",
            backgroundColor: "rgba(59, 130, 246, 0.1)",
            borderWidth: 2,
            fill: false,
            tension: 0.4,
            pointRadius: 0,
          },
          {
            label: `f'(${point}) = ${data.result.toFixed(4)}`,
            data: [{ x: point, y: steps[Math.floor(steps.length / 2)].fx }],
            borderColor: "#ef4444",
            backgroundColor: "#ef4444",
            pointRadius: 6,
            pointHoverRadius: 8,
            showLine: false,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
          legend: {
            display: true,
            labels: {
              color: getComputedStyle(document.body).getPropertyValue(
                "--text-primary"
              ),
              font: { size: 12 },
            },
          },
          title: {
            display: true,
            text: "Function and Differentiation Point",
            color: getComputedStyle(document.body).getPropertyValue(
              "--text-primary"
            ),
            font: { size: 14 },
          },
        },
        scales: {
          x: {
            type: "linear",
            ticks: {
              color: getComputedStyle(document.body).getPropertyValue(
                "--text-secondary"
              ),
              font: { size: 10 },
            },
            grid: {
              color: getComputedStyle(document.body).getPropertyValue(
                "--border"
              ),
            },
          },
          y: {
            ticks: {
              color: getComputedStyle(document.body).getPropertyValue(
                "--text-secondary"
              ),
              font: { size: 10 },
            },
            grid: {
              color: getComputedStyle(document.body).getPropertyValue(
                "--border"
              ),
            },
          },
        },
      },
    });
  } else {
    // Integration: show function with area fill
    const labels = steps.map((s) => s.x.toFixed(3));
    const values = steps.map((s) => s.fx);

    window.calculusChartInstance = new Chart(ctx, {
      type: "line",
      data: {
        labels: labels,
        datasets: [
          {
            label: "f(x)",
            data: values,
            borderColor: "#3b82f6",
            backgroundColor: "rgba(59, 130, 246, 0.2)",
            borderWidth: 2,
            fill: true,
            tension: 0.4,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
          legend: {
            display: true,
            labels: {
              color: getComputedStyle(document.body).getPropertyValue(
                "--text-primary"
              ),
              font: { size: 12 },
            },
          },
          title: {
            display: true,
            text: `Integration Area = ${data.result.toFixed(6)}`,
            color: getComputedStyle(document.body).getPropertyValue(
              "--text-primary"
            ),
            font: { size: 14 },
          },
        },
        scales: {
          x: {
            ticks: {
              color: getComputedStyle(document.body).getPropertyValue(
                "--text-secondary"
              ),
              font: { size: 10 },
            },
            grid: {
              color: getComputedStyle(document.body).getPropertyValue(
                "--border"
              ),
            },
          },
          y: {
            ticks: {
              color: getComputedStyle(document.body).getPropertyValue(
                "--text-secondary"
              ),
              font: { size: 10 },
            },
            grid: {
              color: getComputedStyle(document.body).getPropertyValue(
                "--border"
              ),
            },
          },
        },
      },
    });
  }
}

// Show error message
function showError(message) {
  hideAllSections();
  document.getElementById("errorSection").classList.remove("hidden");
  document.getElementById("errorMessage").textContent = message;
}

// Hide all result sections
function hideAllSections() {
  document.getElementById("resultSection").classList.add("hidden");
  document.getElementById("tokensSection").classList.add("hidden");
  document.getElementById("postfixSection").classList.add("hidden");
  document.getElementById("astSection").classList.add("hidden");
  document.getElementById("intermediateSection").classList.add("hidden");
  document.getElementById("calculusSection").classList.add("hidden");
  document.getElementById("errorSection").classList.add("hidden");
}

// Utility functions
function formatNumber(num) {
  if (Math.abs(num) < 0.0001 || Math.abs(num) > 1000000) {
    return num.toExponential(6);
  }
  return num.toFixed(6).replace(/\.?0+$/, "");
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

// Add fade-in animation style
const style = document.createElement("style");
style.textContent = `
    .fadeIn {
        animation: fadeIn 0.5s ease-in;
    }
`;
document.head.appendChild(style);

console.log("App.js loaded successfully");
