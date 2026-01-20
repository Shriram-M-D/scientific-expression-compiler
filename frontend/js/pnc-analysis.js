/* Probability & Combinatorics Analysis Module */

const PNC_API = "http://localhost:5000/api/analyze/pnc";

// Set example expression
function setPnCExample(expression) {
  document.getElementById("pncInput").value = expression;
}

// Main analysis function
async function analyzePnC() {
  const input = document.getElementById("pncInput").value.trim();

  if (!input) {
    alert("Please enter a PnC expression");
    return;
  }

  try {
    const response = await fetch(PNC_API, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ expression: input }),
    });

    const data = await response.json();

    if (!data.success) {
      alert("Error: " + (data.error || "Analysis failed"));
      return;
    }

    displayPnCResults(data);
  } catch (error) {
    console.error("PnC Analysis Error:", error);
    alert("Failed to analyze expression: " + error.message);
  }
}

// Display results
function displayPnCResults(data) {
  const resultsDiv = document.getElementById("pncResults");
  resultsDiv.classList.remove("hidden");

  // Update summary
  document.getElementById("pncExpression").textContent = data.expression;
  document.getElementById("pncResult").textContent = formatNumber(data.result);

  const isProbability = data.isProbability;
  document.getElementById("pncType").textContent = isProbability
    ? "Probability"
    : "Combinatorics";

  // Display AST
  displayAST(data.ast, data.expression);

  // Display intermediate code
  displayIntermediateCode(data.intermediateCode);

  // Display evaluation steps
  displayEvaluationSteps(data.steps);

  // Display probability validation
  if (isProbability) {
    displayProbabilityValidation(data.result, data.probabilityValid);
  } else {
    document.getElementById("pncProbabilityCheck").classList.add("hidden");
  }
}

// Format number for display
function formatNumber(num) {
  if (num === Math.floor(num)) {
    return num.toLocaleString();
  }
  return num.toFixed(6);
}

// Display AST
function displayAST(ast, expression) {
  const astDisplay = document
    .getElementById("pncAstDisplay")
    .querySelector("pre");

  // Generate AST visualization
  let astText = "";

  if (expression.includes("nCr")) {
    astText = generateCombinationAST(expression);
  } else if (expression.includes("nPr")) {
    astText = generatePermutationAST(expression);
  } else if (expression.includes("!")) {
    astText = generateFactorialAST(expression);
  } else {
    astText = JSON.stringify(ast, null, 2);
  }

  astDisplay.textContent = astText;
}

// Generate visual AST for combinations
function generateCombinationAST(expr) {
  if (expr.includes("/")) {
    // Probability expression
    return `        Division (/)
       /           \\
     nCr            nCr
    /   \\          /   \\
   n₁    r₁       n₂    r₂
   
Probability = P(favorable) / P(total)`;
  } else {
    // Simple nCr
    const match = expr.match(/nCr\((\d+),(\d+)\)/);
    if (match) {
      const n = match[1];
      const r = match[2];
      return `        nCr
       /   \\
      ${n}     ${r}
      
Formula: ${n}! / (${r}! × (${n}-${r})!)`;
    }
  }
  return expr;
}

// Generate visual AST for permutations
function generatePermutationAST(expr) {
  if (expr.includes("/")) {
    return `        Division (/)
       /           \\
     nPr            nPr
    /   \\          /   \\
   n₁    r₁       n₂    r₂
   
Probability = P(favorable) / P(total)`;
  } else {
    const match = expr.match(/nPr\((\d+),(\d+)\)/);
    if (match) {
      const n = match[1];
      const r = match[2];
      return `        nPr
       /   \\
      ${n}     ${r}
      
Formula: ${n}! / (${n}-${r})!`;
    }
  }
  return expr;
}

// Generate visual AST for factorial
function generateFactorialAST(expr) {
  const match = expr.match(/(\d+)!/);
  if (match) {
    const n = match[1];
    return `    Factorial (!)
        |
        ${n}
        
Formula: ${n}! = 1 × 2 × 3 × ... × ${n}`;
  }
  return expr;
}

// Display intermediate code
function displayIntermediateCode(code) {
  const codeDisplay = document
    .getElementById("pncIntermediateCode")
    .querySelector("pre");

  let formatted = "";
  code.forEach((line, idx) => {
    const color = line.includes("fact")
      ? "#3b82f6"
      : line.includes("/")
        ? "#10b981"
        : line.includes("*")
          ? "#f59e0b"
          : line.includes("-")
            ? "#ef4444"
            : "#6b7280";

    formatted += `<span style="color: ${color};">${line}</span>\n`;
  });

  codeDisplay.innerHTML = formatted;
}

// Display evaluation steps
function displayEvaluationSteps(steps) {
  const stepsContainer = document.getElementById("pncSteps");
  stepsContainer.innerHTML = "";

  steps.forEach((step, idx) => {
    const stepDiv = document.createElement("div");
    stepDiv.className = "p-4 rounded-lg";
    stepDiv.style.cssText =
      "background: var(--bg-primary); border-left: 3px solid var(--accent);";

    const isWarning = step.warning || false;
    if (isWarning) {
      stepDiv.style.borderColor = "#ef4444";
    }

    let content = `
      <div class="flex items-start gap-3">
        <div class="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold" 
             style="background: ${isWarning ? "#ef4444" : "var(--accent)"}; color: white;">
          ${idx + 1}
        </div>
        <div class="flex-1">
          <p class="font-semibold mb-1" style="color: var(--text-primary);">
            ${step.step}
          </p>
    `;

    if (step.formula) {
      content += `
          <p class="text-sm mb-2" style="color: var(--text-secondary); font-family: monospace;">
            ${step.formula}
          </p>
      `;
    }

    content += `
          <p class="text-lg font-bold" style="color: ${isWarning ? "#ef4444" : "#10b981"};">
            = ${formatNumber(step.value)}
          </p>
        </div>
      </div>
    `;

    stepDiv.innerHTML = content;
    stepsContainer.appendChild(stepDiv);
  });
}

// Display probability validation
function displayProbabilityValidation(result, isValid) {
  const checkDiv = document.getElementById("pncProbabilityCheck");
  const messageP = document.getElementById("pncProbabilityMessage");

  checkDiv.classList.remove("hidden");

  if (isValid) {
    checkDiv.style.borderColor = "#10b981";
    messageP.innerHTML = `
      <span style="color: #10b981; font-weight: bold;">✓ Valid Probability</span><br>
      Result ${result.toFixed(6)} is within the valid range [0, 1]
    `;
  } else {
    checkDiv.style.borderColor = "#ef4444";
    messageP.innerHTML = `
      <span style="color: #ef4444; font-weight: bold;">⚠ Invalid Probability</span><br>
      Result ${result.toFixed(6)} is outside the valid range [0, 1]<br>
      <small>This may indicate an error in the expression or represent a non-probability ratio.</small>
    `;
  }
}

// Keyboard shortcut
document.addEventListener("DOMContentLoaded", () => {
  const pncInput = document.getElementById("pncInput");
  if (pncInput) {
    pncInput.addEventListener("keypress", (e) => {
      if (e.key === "Enter") {
        analyzePnC();
      }
    });
  }
});
