# System Architecture

## Overview

The Scientific Expression Compiler is a multi-tier system consisting of three main components:

1. **C++ Compiler Engine** - Core compilation and evaluation
2. **Python Flask Backend** - API layer
3. **JavaScript Frontend** - Interactive visualization dashboard

---

## Component Architecture

### 1. C++ Compiler Engine

#### Lexer (lexer.h/cpp)

- **Purpose**: Tokenization of input expressions
- **Functionality**:
  - Character-by-character scanning
  - Token classification (numbers, operators, functions, variables)
  - Constant recognition (pi, e)
  - Function keyword identification
- **Output**: Vector of Token objects

#### Parser (parser.h/cpp)

- **Purpose**: Syntax analysis and postfix conversion
- **Algorithm**: Shunting Yard Algorithm (Dijkstra)
- **Functionality**:
  - Infix to postfix conversion
  - Operator precedence handling
  - Associativity management
  - Parentheses matching
- **Output**: Postfix token stream

#### AST Builder (ast.h/cpp)

- **Purpose**: Abstract Syntax Tree construction
- **Node Types**:
  - NumberNode: Numeric literals
  - VariableNode: Variable references
  - BinaryOpNode: Binary operations (+, -, \*, /, ^, %)
  - UnaryOpNode: Unary operations (-, !)
  - FunctionCallNode: Function invocations
  - DiffNode: Differentiation operations
  - IntegrateNode: Integration operations
- **Output**: Hierarchical AST structure

#### Evaluator (evaluator.h/cpp)

- **Purpose**: Expression evaluation and intermediate code generation
- **Functionality**:
  - Tree traversal and evaluation
  - Three-address code generation
  - Variable binding
  - Function execution
  - Domain validation
- **Output**: Numeric result + intermediate code

#### Calculus Engine (calculus.h/cpp)

- **Purpose**: Numerical calculus operations
- **Methods**:
  - **Differentiation**: Central finite difference
    ```
    f'(x) ≈ [f(x+h) - f(x-h)] / (2h)
    where h = 0.0001
    ```
  - **Integration**: Trapezoidal Rule (default)
    ```
    ∫f(x)dx ≈ (h/2)[f(a) + 2Σf(xi) + f(b)]
    ```
  - **Integration**: Simpson's Rule (optional)
    ```
    ∫f(x)dx ≈ (h/3)[f(a) + 4Σf(odd) + 2Σf(even) + f(b)]
    ```
- **Output**: Numeric result + computation steps

#### Main Driver (main.cpp)

- **Purpose**: CLI interface and JSON output generation
- **Functionality**:
  - Command-line argument parsing
  - Pipeline orchestration
  - JSON serialization
  - Error handling
- **Output**: Structured JSON response

---

### 2. Python Flask Backend (app.py)

#### API Endpoints

**POST /api/compile**

- Input: `{ "expression": "sin(pi/2)" }`
- Process:
  1. Validate input
  2. Execute C++ compiler via subprocess
  3. Parse JSON output
  4. Return result to frontend
- Output: Complete compilation result in JSON

**GET /api/health**

- Purpose: Health check and compiler status
- Output: Server and compiler status

**GET /**

- Purpose: Serve frontend application
- Output: index.html

#### Features

- CORS enabled for frontend communication
- Subprocess timeout protection (10s)
- Comprehensive error handling
- Static file serving

---

### 3. JavaScript Frontend

#### index.html

- **Layout**: Responsive dashboard with Tailwind CSS
- **Sections**:
  - Expression input with quick examples
  - Result display with MathJax rendering
  - Compiler pipeline diagram (Mermaid.js)
  - Token stream visualization
  - Postfix notation display
  - AST visualization (D3.js)
  - Intermediate code display
  - Calculus visualization (Chart.js)

#### app.js

- **Main Application Logic**:
  - API communication
  - Result processing
  - Section visibility management
  - Error handling
  - MathJax integration

#### visualizer.js

- **D3.js AST Visualization**:
  - Hierarchical tree layout
  - Interactive node exploration
  - Animated transitions
  - Color-coded node types
  - Hover effects

#### Chart.js Integration

- Function plotting for calculus
- Area under curve visualization
- Tangent line rendering
- Interactive data points

---

## Data Flow

```
User Input (Frontend)
    ↓
POST /api/compile (Flask)
    ↓
Execute compiler.exe (Subprocess)
    ↓
C++ Compiler Pipeline:
    1. Lexer → Tokens
    2. Parser → Postfix + AST
    3. Evaluator → Intermediate Code
    4. Calculus (if needed) → Steps
    5. Evaluation → Result
    ↓
JSON Output
    ↓
Flask API Response
    ↓
Frontend Visualization
```

---

## Technology Stack Summary

| Layer          | Technology        | Purpose                          |
| -------------- | ----------------- | -------------------------------- |
| Compiler       | C++17             | Performance-critical compilation |
| API            | Python 3.8+ Flask | REST API layer                   |
| Frontend       | HTML5             | Structure                        |
| Styling        | Tailwind CSS      | Responsive design                |
| Math Rendering | MathJax           | LaTeX-style equations            |
| AST Viz        | D3.js v7          | Tree visualization               |
| Plots          | Chart.js          | Function graphs                  |
| Diagrams       | Mermaid.js        | Flow charts                      |

---

## Design Patterns

### Compiler Engine (C++)

- **Visitor Pattern**: AST traversal
- **Factory Pattern**: Token creation
- **Strategy Pattern**: Calculus methods
- **Composite Pattern**: AST structure

### Backend (Python)

- **MVC Pattern**: Route handling
- **Facade Pattern**: Compiler interface
- **Dependency Injection**: Configuration

### Frontend (JavaScript)

- **Module Pattern**: Code organization
- **Observer Pattern**: Event handling
- **MVC Pattern**: Data flow

---

## Performance Considerations

### C++ Optimizations

- O2 optimization level
- Minimal memory allocations
- Efficient string handling
- Smart pointer usage

### Numerical Precision

- Step size: h = 0.0001 for calculus
- Integration steps: 1000 (configurable)
- Double precision floating point

### Frontend Performance

- Lazy rendering of visualizations
- Debounced animations
- Efficient DOM manipulation
- CDN-hosted libraries

---

## Security

### Input Validation

- Expression length limits
- Character whitelist
- Timeout protection (10s)

### Subprocess Safety

- Isolated execution
- No shell injection
- Timeout enforcement

### CORS

- Controlled cross-origin access
- Development mode configuration

---

## Extensibility

### Adding New Functions

1. Update `lexer.cpp` function map
2. Implement in `evaluator.cpp`
3. Update frontend documentation

### Adding New Operators

1. Define token type in `lexer.h`
2. Add parsing logic in `parser.cpp`
3. Implement evaluation in `evaluator.cpp`

### Adding New Calculus Methods

1. Implement in `calculus.cpp`
2. Add method selector in main
3. Update frontend visualization

---

## Error Handling

### Compilation Errors

- Lexical errors: Invalid characters
- Syntax errors: Mismatched parentheses
- Semantic errors: Domain violations
- Runtime errors: Division by zero

### Error Propagation

```
C++ Exception
    ↓
JSON Error Object
    ↓
Flask Error Response
    ↓
Frontend Error Display
```

---

## Testing Strategy

### Unit Tests (Suggested)

- Lexer token generation
- Parser postfix conversion
- AST construction
- Evaluation correctness
- Calculus accuracy

### Integration Tests

- End-to-end compilation
- API endpoint responses
- Frontend rendering

### Test Cases

- See TEST_CASES.md for comprehensive suite

---

## Deployment

### Development

```bash
./start.bat  # Windows
./start.sh   # Linux/Mac
```

### Production (Suggested)

- Build C++ with release flags
- Use Gunicorn for Flask
- Nginx reverse proxy
- Static asset optimization

---

## Future Enhancements

1. **Symbolic Differentiation**
2. **Indefinite Integrals**
3. **Multi-variable Functions**
4. **3D Plotting**
5. **Code Optimization Passes**
6. **WebAssembly Compilation**
7. **Real-time Collaboration**
8. **Expression History**
9. **Custom Function Definitions**
10. **Mobile Responsive Enhancements**
