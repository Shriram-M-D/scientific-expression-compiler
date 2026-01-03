# Interactive Scientific Expression Compiler with Numerical Calculus and Visualization Dashboard

A complete compiler-style system that processes mathematical expressions through lexical analysis, parsing, AST construction, semantic validation, intermediate code generation, numerical evaluation, and calculus — all visualized through an interactive animated dashboard.

---

## 🚀 Features

- **Full Compiler Pipeline**: Lexer → Parser → AST → Semantic Analysis → Intermediate Code → Evaluation
- **Numerical Calculus**: Differentiation (central finite difference) and Integration (Trapezoidal/Simpson's Rule)
- **Scientific Functions**: sin, cos, tan, asin, acos, atan, log, ln, exp, sqrt, cbrt, abs, factorial
- **Interactive Visualization**: Real-time animated visualization of all compiler stages
- **Mathematical Rendering**: Beautiful LaTeX-style rendering with MathJax
- **Function Plotting**: Graph functions with tangent lines and area under curve

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
│   └── requirements.txt
│
├── frontend/               # Interactive Dashboard
│   ├── index.html
│   ├── js/
│   │   ├── app.js
│   │   └── visualizer.js
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

### 2️⃣ Set Up Python Backend

```bash
cd backend
pip install -r requirements.txt
```

### 3️⃣ Run the Application

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
