/* AST Visualization using D3.js */

function showAST(astData) {
  document.getElementById("astSection").classList.remove("hidden");

  // Clear previous visualization
  const container = document.getElementById("astCanvas");
  container.innerHTML = "";

  // Set up SVG dimensions
  const width = container.clientWidth;
  const height = 500;

  const svg = d3
    .select("#astCanvas")
    .append("svg")
    .attr("width", width)
    .attr("height", height)
    .append("g")
    .attr("transform", "translate(40,20)");

  // Convert AST data to D3 hierarchy
  const root = d3.hierarchy(convertASTToHierarchy(astData));

  // Create tree layout
  const treeLayout = d3.tree().size([width - 100, height - 100]);

  treeLayout(root);

  // Add links
  svg
    .selectAll(".link")
    .data(root.links())
    .enter()
    .append("path")
    .attr("class", "link")
    .attr(
      "d",
      d3
        .linkVertical()
        .x((d) => d.x)
        .y((d) => d.y)
    )
    .style("stroke", "#6b7280")
    .style("stroke-width", 2)
    .style("fill", "none")
    .style("opacity", 0)
    .transition()
    .duration(800)
    .style("opacity", 0.6);

  // Add nodes
  const nodes = svg
    .selectAll(".node")
    .data(root.descendants())
    .enter()
    .append("g")
    .attr("class", "node")
    .attr("transform", (d) => `translate(${d.x},${d.y})`)
    .style("opacity", 0)
    .transition()
    .delay((d, i) => i * 100)
    .duration(500)
    .style("opacity", 1);

  // Add circles for nodes
  svg
    .selectAll(".node")
    .append("circle")
    .attr("r", (d) => {
      if (d.data.type === "NUMBER" || d.data.type === "VARIABLE") return 25;
      if (d.data.type === "BINARY_OP") return 30;
      return 28;
    })
    .style("fill", (d) => getNodeColor(d.data.type))
    .style("stroke", "#3b82f6")
    .style("stroke-width", 2)
    .style("cursor", "pointer")
    .on("mouseover", function (event, d) {
      d3.select(this)
        .transition()
        .duration(200)
        .attr("r", this.r.baseVal.value * 1.2)
        .style("fill", "#2563eb");
    })
    .on("mouseout", function (event, d) {
      d3.select(this)
        .transition()
        .duration(200)
        .attr("r", this.r.baseVal.value / 1.2)
        .style("fill", getNodeColor(d.data.type));
    });

  // Add text labels
  svg
    .selectAll(".node")
    .append("text")
    .attr("dy", 5)
    .attr("text-anchor", "middle")
    .style("fill", "#fff")
    .style("font-weight", "bold")
    .style("font-size", "12px")
    .style("pointer-events", "none")
    .text((d) => getNodeLabel(d.data));

  // Add type labels below nodes
  svg
    .selectAll(".node")
    .append("text")
    .attr("dy", 40)
    .attr("text-anchor", "middle")
    .style("fill", "#666")
    .style("font-size", "10px")
    .style("font-style", "italic")
    .text((d) => d.data.type);
}

// Convert AST JSON to D3 hierarchy format
function convertASTToHierarchy(node) {
  if (!node) return null;

  const result = {
    type: node.type,
    name: getNodeLabel(node),
  };

  // Add node-specific properties
  if (node.type === "NUMBER") {
    result.value = node.value;
  } else if (node.type === "VARIABLE") {
    result.name = node.name;
  } else if (node.type === "BINARY_OP") {
    result.op = node.op;
    result.children = [
      convertASTToHierarchy(node.left),
      convertASTToHierarchy(node.right),
    ].filter(Boolean);
  } else if (node.type === "UNARY_OP") {
    result.op = node.op;
    result.children = [convertASTToHierarchy(node.operand)].filter(Boolean);
  } else if (node.type === "FUNCTION_CALL") {
    result.name = node.name;
    result.children = node.arguments.map(convertASTToHierarchy).filter(Boolean);
  } else if (node.type === "DIFF_NODE") {
    result.children = [
      convertASTToHierarchy(node.expression),
      { type: "VARIABLE", name: node.variable },
      { type: "NUMBER", value: node.point },
    ].filter(Boolean);
  } else if (node.type === "INTEGRATE_NODE") {
    result.children = [
      convertASTToHierarchy(node.expression),
      { type: "VARIABLE", name: node.variable },
      { type: "NUMBER", value: node.lowerBound },
      { type: "NUMBER", value: node.upperBound },
    ].filter(Boolean);
  }

  return result;
}

// Get color for node type
function getNodeColor(type) {
  const colors = {
    NUMBER: "#3b82f6",
    VARIABLE: "#f59e0b",
    BINARY_OP: "#10b981",
    UNARY_OP: "#f97316",
    FUNCTION_CALL: "#8b5cf6",
    DIFF_NODE: "#ef4444",
    INTEGRATE_NODE: "#06b6d4",
  };
  return colors[type] || "#3b82f6";
}

// Get label text for node
function getNodeLabel(node) {
  if (!node) return "";

  if (node.type === "NUMBER") {
    return String(node.value || node.numValue || "0");
  } else if (node.type === "VARIABLE") {
    return node.name || "x";
  } else if (node.type === "BINARY_OP") {
    return node.op || "+";
  } else if (node.type === "UNARY_OP") {
    return node.op || "-";
  } else if (node.type === "FUNCTION_CALL") {
    return node.name || "f";
  } else if (node.type === "DIFF_NODE") {
    return "d/dx";
  } else if (node.type === "INTEGRATE_NODE") {
    return "∫";
  }

  return node.type || "?";
}

// Interactive AST node explorer
function exploreNode(nodeData) {
  console.log("AST Node:", nodeData);
  alert(JSON.stringify(nodeData, null, 2));
}

console.log("Visualizer.js loaded successfully");
