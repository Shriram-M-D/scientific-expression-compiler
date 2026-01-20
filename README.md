# Interactive Scientific Expression Compiler with Numerical Calculus and Visualization Dashboard

A complete compiler-style system that processes mathematical expressions through lexical analysis, parsing, AST construction, semantic validation, intermediate code generation, numerical evaluation, and calculus — all visualized through an interactive animated dashboard.

---

## 🚀 Features

- **Full Compiler Pipeline**: Lexer → Parser → AST → Semantic Analysis → Intermediate Code → Evaluation
- **Numerical Calculus**: Differentiation (central finite difference) and Integration (Trapezoidal/Simpson's Rule)
- **Probability & Combinatorics**: Factorial (!), Combinations (nCr), Permutations (nPr) as compiled language features
- **Scientific Functions**: sin, cos, tan, asin, acos, atan, log, ln, exp, sqrt, cbrt, abs, factorial
- **Interactive Visualization**: Real-time animated visualization of all compiler stages
- **Mathematical Rendering**: Beautiful LaTeX-style rendering with MathJax
- **Function Plotting**: Graph functions with tangent lines and area under curve
- **🔍 Object File Analysis**: Machine-level insights with disassembly, symbol tables, and optimization comparisons

---

## 🎓 What is Object File Analysis?

**Object files (.o)** are the intermediate compilation artifacts containing machine code before final linking. They bridge the gap between high-level source code and executable binaries.

### Why Object File Analysis Matters in Compilers:

1. **Educational Value**: Understand how high-level constructs translate to machine instructions
2. **Optimization Insights**: Compare -O0 (no optimization) vs -O2 (optimized) to see compiler transformations
3. **Performance Analysis**: Identify instruction patterns, code size, and memory footprint
4. **Debugging Aid**: Examine symbol tables and function boundaries
5. **Compiler Verification**: Ensure code generation produces expected machine code

### What We Extract:

- **Disassembly**: Human-readable assembly from .text section
- **Symbol Tables**: Global, local, and weak symbols (mangled/demangled)
- **ELF Sections**: .text (code), .data (initialized data), .bss (uninitialized), .rodata (constants)
- **Size Metrics**: Memory footprint breakdown by section
- **Optimization Impact**: Quantitative comparison of compiler optimization effects

---

## 📁 Project Structure

```
expression-compiler/
├── compiler/               # C++ Compiler Engine
│   ├── lexer.h
│   ├── lexer.cpp          # Tokenization
│   ├── parser.h
│   ├── parser.cpp         # Shunting Yard Algorithm
│   ├── ast.h
│   ├── ast.cpp            # AST Construction
│   ├── calculus.h
│   ├── calculus.cpp       # Numerical Calculus
│   ├── evaluator.h
│   ├── evaluator.cpp      # Expression Evaluation
│   ├── main.cpp           # Compiler Driver
│   └── Makefile           # Build Script
│
├── backend/                # Python Flask API
│   ├── app.py
│   ├── object_analyzer.py # Object file analysis module
│   └── requirements.txt
│
├── frontend/               # Interactive Dashboard
│   ├── index.html
│   ├── js/
│   │   ├── app.js
│   │   ├── visualizer.js
│   │   └── object-analysis.js  # Object analysis UI
│   └── css/
│       └── style.css
│
└── README.md
```

---

## 🛠️ Prerequisites

### Required Software:

- **C++ Compiler**: g++ (MinGW on Windows) with C++17 support
- **Python**: 3.8 or higher
- **pip**: Python package manager

---

## 📦 Installation

### 1️⃣ Build the C++ Compiler

```bash
cd compiler
make
```

This will create `compiler.exe` (Windows) or `compiler` (Linux/Mac).

### 2️⃣ Build Object Files for Analysis (Optional)

```bash
cd compiler
make analyze-objects
```

This creates `compiler_O0.o` and `compiler_O2.o` for machine-level analysis.

### 2️⃣ Set Up Python Backend

```bash
cd backend
pip install -r requirements.txt
```

**Note**: Object file analysis requires standard GNU binutils (objdump, nm, readelf, size).

- On **Linux/WSL**: Pre-installed with build-essential
- On **Windows**: Install via MinGW or use WSL for full functionality

### 4️⃣ Run the Application

Start the Flask server:

```bash
cd backend
python app.py
```

The application will be available at: **http://localhost:5000**

---

## 🎯 Usage

### Supported Syntax

#### Operators:

```
+  -  *  /  %  ^  !
```

#### Functions:

```
sin(x)  cos(x)  tan(x)
asin(x) acos(x) atan(x)
log(x)  ln(x)   exp(x)
sqrt(x) cbrt(x) abs(x)
nCr(n,r)  # Combinations
nPr(n,r)  # Permutations
```

#### Constants:

```
pi    # 3.14159...
e     # 2.71828...
```

#### Numerical Calculus:

**Differentiation:**

```
diff(sin(x) + x^2, x, 1)
```

**Integration:**

```
integrate(x^2 + sin(x), x, 0, 3)
```

### Example Expressions:

```
sin(pi/4) + cos(pi/4)
2^10 - sqrt(144)
log(e^5)
diff(x^3, x, 2)
integrate(x^2, x, 0, 10)
abs(-5!) + cbrt(27)
5!                      # Factorial: 120
nCr(10,3)              # Combinations: 120
nPr(10,3)              # Permutations: 720
nCr(5,2)/nCr(10,2)     # Probability: 0.222222
```

---

## 🎯 Probability & Combinatorics (PnC)

### Mathematical Foundations

#### Factorial (!)

**Definition:**

```
n! = n × (n-1) × (n-2) × ... × 2 × 1
```

**Constraints:**

- n must be a non-negative integer
- n ≤ 170 (overflow protection)

**Examples:**

```
5! = 120
10! = 3628800
0! = 1
```

#### Combinations - nCr(n,r)

**Definition:**

```
nCr(n,r) = n! / (r! × (n-r)!)
```

**Meaning:** Number of ways to choose r items from n items (order doesn't matter)

**Constraints:**

- n ≥ r ≥ 0
- Both n and r must be integers

**Examples:**

```
nCr(10,3) = 120        # Choose 3 from 10
nCr(52,5) = 2598960    # Poker hands from deck
nCr(5,5) = 1           # Only 1 way to choose all
```

#### Permutations - nPr(n,r)

**Definition:**

```
nPr(n,r) = n! / (n-r)!
```

**Meaning:** Number of ways to arrange r items from n items (order matters)

**Constraints:**

- n ≥ r ≥ 0
- Both n and r must be integers

**Examples:**

```
nPr(10,3) = 720        # Arrange 3 from 10
nPr(5,5) = 120         # All permutations of 5 items
nPr(10,1) = 10         # Just choosing one
```

#### Probability Expressions

**Form:**

```
P(event) = favorable_outcomes / total_outcomes
```

**Examples:**

```
nCr(5,2)/nCr(10,2)     # Probability of selecting 2 specific items
nPr(6,3)/nPr(10,3)     # Probability of specific arrangement
```

**Validation:**

- Result must be in range [0, 1]
- Compiler warns if probability is invalid

### Compiler Integration

PnC constructs are **first-class language features**, not calculator shortcuts:

1. **Lexical Analysis**: Recognize `!`, `nCr`, `nPr` as tokens
2. **Syntax Analysis**: Parse as postfix operator (!) or function calls (nCr, nPr)
3. **AST**: Explicit nodes (FactorialNode, NCrNode, NPrNode)
4. **Semantic Validation**:
   - Enforce n ≥ r ≥ 0
   - Integer-only arguments
   - Overflow checks
5. **Intermediate Code**: Lower to factorial-based three-address code
6. **Evaluation**: Safe integer arithmetic → float division

### Intermediate Code Generation

**Example: nCr(10,3)**

```
t0 = 10
t1 = 3
t2 = fact t0          # 10!
t3 = fact t1          # 3!
t4 = t0 - t1          # 10 - 3 = 7
t5 = fact t4          # 7!
t6 = t3 * t5          # 3! × 7!
t7 = t2 / t6          # 10! / (3! × 7!) = 120
```

**Example: nPr(10,3)**

```
t0 = 10
t1 = 3
t2 = fact t0          # 10!
t3 = t0 - t1          # 7
t4 = fact t3          # 7!
t5 = t2 / t4          # 10! / 7! = 720
```

### Error Cases

**Semantic Errors:**

```
nCr(5, 10)            # Error: r > n
nCr(-5, 2)            # Error: negative n
nCr(5.5, 2)           # Error: non-integer
nCr(200, 2)           # Error: factorial overflow
```

**Probability Warnings:**

```
nCr(10,3) / nCr(5,2)  # Result > 1 → Warning: invalid probability
```

---

## 🏗️ Architecture

### Compiler Pipeline:

1. **Lexical Analysis**: Tokenize input into operators, numbers, functions, variables
2. **Syntax Analysis**: Parse using Shunting Yard algorithm
3. **AST Construction**: Build abstract syntax tree
4. **Semantic Analysis**: Validate domain constraints (sqrt(-x), log(0), etc.)
5. **Intermediate Code**: Generate three-address code
6. **Evaluation**: Compute numerical result

### Numerical Calculus:

- **Differentiation**: Central finite difference method

  ```
  f'(x) ≈ [f(x+h) - f(x-h)] / (2h)
  ```

- **Integration**: Trapezoidal Rule (default) and Simpson's Rule
  ```
  ∫f(x)dx ≈ (h/2)[f(a) + 2Σf(xi) + f(b)]
  ```

---

## 🎨 Dashboard Features

### Visualizations:

- **Token Stream**: Color-coded token display
- **Parsing Animation**: Step-by-step Shunting Yard visualization
- **AST Graph**: Interactive, zoomable tree using D3.js
- **Compiler Flow**: Mermaid.js pipeline diagrams
- **Function Plots**: Chart.js graphs with calculus overlays
- **Mathematical Rendering**: MathJax for beautiful expressions

### Interactive Elements:

- Live expression input
- Step-size control for calculus
- Integration method toggle (Trapezoidal/Simpson's)
- Collapsible visualization panels
- Smooth animations and transitions

---

## 🧪 Testing

Try these test cases:

```
# Basic arithmetic
2 + 3 * 4
(5 + 3) * 2

# Scientific functions
sin(pi/2)
log(100) / log(10)

# Factorial
5! / 3!

# Derivatives
diff(x^2, x, 3)
diff(sin(x), x, 0)

# Integrals
integrate(1, x, 0, 5)
integrate(x, x, 0, 10)
integrate(x^2, x, 0, 3)
```

### Object File Analysis:

Navigate to the **"🔍 Machine-Level Object File Analysis"** section at the bottom of the dashboard.

#### Steps:

1. **Build Object Files**: Click "Build Object Files" to compile with -O0 and -O2
2. **Analyze**: Click "Analyze -O0" or "Analyze -O2" to examine specific optimization level
3. **Compare**: Click "Compare Optimizations" to see side-by-side differences

#### Views:

- **Disassembly**: Assembly instructions grouped by function with syntax highlighting
- **Symbol Table**: Global/local symbols with addresses
- **ELF Sections**: Section breakdown (.text, .data, .bss, .rodata)
- **Size Metrics**: Memory footprint visualization
- **Optimization Comparison**: Charts showing instruction count and size reduction

---

## 🔧 Troubleshooting

### C++ Compilation Issues:

- Ensure g++ is installed and in PATH
- On Windows, install MinGW or use WSL
- Check C++17 support: `g++ --version`

### Python Issues:

- Verify Python version: `python --version`
- Install dependencies: `pip install flask flask-cors`

### Port Already in Use:

- Change port in `backend/app.py` (default: 5000)

### Object File Analysis Not Working:

- **Missing tools**: Install GNU binutils (objdump, nm, readelf, size)
  - Linux: `sudo apt-get install binutils`
  - WSL: Same as Linux
  - Windows: Use WSL or install MinGW-w64 with binutils
- **Object files not found**: Run `make analyze-objects` in compiler directory first
- **Build errors**: Ensure g++ is properly configured and source files compile successfully

---

## 📚 Technical Details

### Algorithms:

- **Parsing**: Shunting Yard Algorithm (Dijkstra)
- **Differentiation**: Central Finite Difference
- **Integration**: Trapezoidal Rule & Simpson's Rule

### Design Patterns:

- **Visitor Pattern**: AST traversal
- **Factory Pattern**: Token creation
- **Strategy Pattern**: Calculus methods

### Performance:

- **Precision**: Step size h = 0.0001 for calculus
- **Integration Steps**: 1000 (adjustable)
- **JSON Output**: Structured response for all stages

### Object File Analysis:

- **Tools Used**: objdump (disassembly), nm (symbols), readelf (ELF), size (metrics)
- **Optimization Levels**: -O0 (baseline), -O2 (production-grade optimization)
- **Supported Formats**: ELF object files (.o)
- **Analysis Modes**: Static analysis only (no execution or emulation)

---

## 👨‍💻 Developer Notes

### Adding New Functions:

1. Add token type in `lexer.h`
2. Implement in `lexer.cpp` tokenization
3. Add AST node in `ast.cpp`
4. Implement evaluation in `evaluator.cpp`
5. Update frontend documentation

### Extending Calculus:

- Modify step size in `calculus.cpp`
- Add new methods (Simpson's, Romberg, etc.)
- Update JSON output format

### Object File Analysis API:

#### Build Object Files:

```bash
POST /api/analyze/build
```

#### Analyze Object File:

```bash
GET /api/analyze/object?level=O0  # or O2
```

#### Compare Optimizations:

```bash
GET /api/analyze/optimization
```

#### Get Disassembly:

```bash
GET /api/analyze/disassembly?level=O0
```

---

## 📄 License

This project is created for educational purposes.

---

## 🙏 Acknowledgments

- Dijkstra's Shunting Yard Algorithm
- Numerical Analysis techniques
- D3.js, Chart.js, Mermaid.js communities
- MathJax for mathematical typesetting

---

**Built with ❤️ using C++, Python, and JavaScript**
