# 🚀 Quick Start Guide

Welcome to the **Scientific Expression Compiler**! This guide will help you get started quickly.

---

## ⚡ Super Quick Start (Windows)

1. **Double-click** `start.bat`
2. **Wait** for compilation and server startup
3. **Open browser** to http://localhost:5000
4. **Done!** Start entering expressions

---

## 📋 Prerequisites

### Required Software

✅ **C++ Compiler** (g++)

- Windows: Install [MinGW-w64](https://www.mingw-w64.org/)
- Mac: Install Xcode Command Line Tools: `xcode-select --install`
- Linux: `sudo apt-get install g++`

✅ **Python 3.8+**

- Download from [python.org](https://www.python.org/downloads/)
- Make sure to check "Add Python to PATH" during installation

✅ **pip** (Python package manager)

- Usually comes with Python
- Verify: `pip --version`

---

## 🛠️ Installation Steps

### Method 1: Automated (Recommended)

**Windows:**

```batch
start.bat
```

**Linux/Mac:**

```bash
chmod +x start.sh
./start.sh
```

### Method 2: Manual

**Step 1: Build C++ Compiler**

```bash
cd compiler
make
cd ..
```

**Step 2: Install Python Dependencies**

```bash
cd backend
pip install -r requirements.txt
cd ..
```

**Step 3: Run Flask Server**

```bash
cd backend
python app.py
```

**Step 4: Open Browser**
Navigate to: http://localhost:5000

---

## 🎮 Using the Application

### Basic Expressions

Try these in the input box:

```
2 + 3 * 4
sin(pi/2)
sqrt(144)
5!
2^10
```

### Advanced Calculus

**Differentiation:**

```
diff(x^2, x, 3)
diff(sin(x), x, 0)
```

**Integration:**

```
integrate(x^2, x, 0, 3)
integrate(sin(x), x, 0, pi)
```

---

## 📊 Understanding the Dashboard

### 1️⃣ **Token Stream**

- Shows how your expression is broken into tokens
- Color-coded by token type:
  - 🔵 Blue = Numbers
  - 🟢 Green = Operators
  - 🟣 Purple = Functions
  - 🟡 Yellow = Variables

### 2️⃣ **Postfix Notation**

- Reverse Polish Notation (RPN)
- Shows the Shunting Yard algorithm output
- No parentheses needed!

### 3️⃣ **Abstract Syntax Tree (AST)**

- Interactive tree visualization
- Hover over nodes to see details
- Shows expression structure

### 4️⃣ **Intermediate Code**

- Three-address code representation
- Similar to assembly language
- Shows compilation steps

### 5️⃣ **Calculus Visualization**

- Function plots with Chart.js
- Area under curve for integrals
- Tangent lines for derivatives
- Step-by-step calculations

---

## 🎯 Supported Features

### Operators

| Operator | Description    | Example |
| -------- | -------------- | ------- |
| +        | Addition       | 2 + 3   |
| -        | Subtraction    | 5 - 2   |
| \*       | Multiplication | 4 \* 7  |
| /        | Division       | 10 / 2  |
| %        | Modulo         | 10 % 3  |
| ^        | Power          | 2 ^ 10  |
| !        | Factorial      | 5!      |

### Functions

| Function | Description    | Example   |
| -------- | -------------- | --------- |
| sin(x)   | Sine           | sin(pi/4) |
| cos(x)   | Cosine         | cos(0)    |
| tan(x)   | Tangent        | tan(pi/4) |
| asin(x)  | Arc sine       | asin(0.5) |
| acos(x)  | Arc cosine     | acos(1)   |
| atan(x)  | Arc tangent    | atan(1)   |
| log(x)   | Log base 10    | log(100)  |
| ln(x)    | Natural log    | ln(e)     |
| exp(x)   | e^x            | exp(2)    |
| sqrt(x)  | Square root    | sqrt(16)  |
| cbrt(x)  | Cube root      | cbrt(27)  |
| abs(x)   | Absolute value | abs(-5)   |

### Constants

| Constant | Value      |
| -------- | ---------- |
| pi       | 3.14159... |
| e        | 2.71828... |

### Calculus

| Operation  | Syntax                     | Example                 |
| ---------- | -------------------------- | ----------------------- |
| Derivative | diff(expr, var, point)     | diff(x^2, x, 3)         |
| Integral   | integrate(expr, var, a, b) | integrate(x^2, x, 0, 5) |

---

## 🔧 Troubleshooting

### Problem: "Compiler not found"

**Solution:**

1. Make sure you've built the C++ compiler: `cd compiler && make`
2. Check that `compiler.exe` or `compiler` exists in the `compiler/` directory

### Problem: "Python module not found"

**Solution:**

```bash
cd backend
pip install flask flask-cors
```

### Problem: "Port 5000 already in use"

**Solution:**

- Change port in `backend/app.py` (line: `app.run(port=5000)`)
- Or kill the process using port 5000

### Problem: "g++ not found"

**Solution:**

- **Windows**: Install MinGW-w64
- **Mac**: Run `xcode-select --install`
- **Linux**: Run `sudo apt-get install g++`

### Problem: Blank page in browser

**Solution:**

1. Check browser console for errors (F12)
2. Make sure server is running
3. Try clearing browser cache
4. Check firewall settings

---

## 📝 Example Session

```
Input: sin(pi/4) + cos(pi/4)

Result: 1.414214

Tokens: sin ( pi / 4 ) + cos ( pi / 4 )
Postfix: pi 4 / sin pi 4 / cos +
AST: [Interactive tree visualization]
Intermediate Code:
  1. t0 = pi
  2. t1 = 4
  3. t2 = t0 / t1
  4. t3 = sin(t2)
  5. t4 = pi
  6. t5 = 4
  7. t6 = t4 / t5
  8. t7 = cos(t6)
  9. t8 = t3 + t7
```

---

## 🎓 Learning Resources

### Understanding Compiler Stages

1. **Lexical Analysis**: Breaking input into tokens
2. **Syntax Analysis**: Checking grammar and structure
3. **AST Construction**: Building tree representation
4. **Semantic Analysis**: Checking meaning and validity
5. **Intermediate Code**: Generating low-level instructions
6. **Evaluation**: Computing the final result

### Shunting Yard Algorithm

- Converts infix notation to postfix (RPN)
- Uses operator precedence
- Handles parentheses and associativity
- Invented by Edsger Dijkstra

### Numerical Methods

**Central Finite Difference (Differentiation):**

```
f'(x) ≈ [f(x+h) - f(x-h)] / (2h)
```

**Trapezoidal Rule (Integration):**

```
∫f(x)dx ≈ (h/2)[f(a) + 2Σf(xi) + f(b)]
```

---

## 🚀 Advanced Usage

### Running Tests

Test the compiler directly:

```bash
cd compiler
./compiler "sin(pi/2)"
```

### API Testing

Using curl:

```bash
curl -X POST http://localhost:5000/api/compile \
  -H "Content-Type: application/json" \
  -d '{"expression":"2+2"}'
```

### Custom Modifications

**Add a new function:**

1. Edit `compiler/lexer.cpp` - add to functions map
2. Edit `compiler/evaluator.cpp` - implement evaluation
3. Rebuild: `cd compiler && make`

---

## 📚 Additional Documentation

- **README.md** - Project overview and installation
- **ARCHITECTURE.md** - Detailed system architecture
- **TEST_CASES.md** - Comprehensive test cases

---

## 💡 Tips & Tricks

1. **Use Quick Examples**: Click the example buttons for instant testing
2. **Parentheses**: Use them to control evaluation order
3. **Precision**: Results are displayed with 6 decimal places
4. **Variables**: Use single letters (x, y, z) in calculus operations
5. **Constants**: Use `pi` and `e` instead of numbers for better accuracy

---

## 🐛 Known Limitations

- **Symbolic calculus**: Not supported (numerical only)
- **Indefinite integrals**: Not supported (definite only)
- **Multi-variable**: Single variable only
- **Complex numbers**: Not supported
- **Matrix operations**: Not supported

---

## 🤝 Contributing

Want to improve the project?

1. Add new mathematical functions
2. Implement symbolic differentiation
3. Add more visualization options
4. Improve error messages
5. Add unit tests

---

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section
2. Review error messages in the browser console
3. Check the Flask server console output
4. Verify all prerequisites are installed

---

## 🎉 Have Fun!

Start exploring mathematical expressions and watch the compiler work its magic! 🔬✨

Happy coding! 🚀
