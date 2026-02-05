from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import subprocess
import json
import os
import sys
import tempfile
import shutil
import re
from object_analyzer import ObjectFileAnalyzer

app = Flask(__name__, static_folder='../frontend')
CORS(app)

# Path to the compiled C++ compiler
COMPILER_PATH = os.path.join(os.path.dirname(__file__), '..', 'compiler', 'compiler.exe')
if not os.path.exists(COMPILER_PATH):
    COMPILER_PATH = os.path.join(os.path.dirname(__file__), '..', 'compiler', 'compiler')

@app.route('/')
def index():
    """Serve the main HTML page"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/js/<path:filename>')
def serve_js(filename):
    """Serve JavaScript files"""
    return send_from_directory(os.path.join(app.static_folder, 'js'), filename)

@app.route('/css/<path:filename>')
def serve_css(filename):
    """Serve CSS files"""
    return send_from_directory(os.path.join(app.static_folder, 'css'), filename)

@app.route('/api/compile', methods=['POST'])
def compile_expression():
    """
    Endpoint to compile and evaluate mathematical expressions
    
    Expected JSON input:
    {
        "expression": "sin(pi/4) + cos(pi/4)"
    }
    
    Returns:
    {
        "success": true,
        "expression": "...",
        "tokens": [...],
        "postfix": [...],
        "ast": {...},
        "intermediateCode": [...],
        "result": 1.414...,
        "calculusType": "none|differentiation|integration",
        "calculusSteps": [...]
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'expression' not in data:
            return jsonify({
                'success': False,
                'error': 'No expression provided'
            }), 400
        
        expression = data['expression'].strip()
        
        if not expression:
            return jsonify({
                'success': False,
                'error': 'Empty expression'
            }), 400
        
        # Check if compiler exists
        if not os.path.exists(COMPILER_PATH):
            return jsonify({
                'success': False,
                'error': f'Compiler not found. Please build the C++ compiler first. Looking for: {COMPILER_PATH}'
            }), 500
        
        # Run the C++ compiler
        try:
            result = subprocess.run(
                [COMPILER_PATH, expression],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Parse the JSON output from the compiler
            if result.returncode == 0:
                try:
                    output = json.loads(result.stdout)
                    return jsonify(output)
                except json.JSONDecodeError:
                    return jsonify({
                        'success': False,
                        'error': 'Invalid JSON output from compiler',
                        'stdout': result.stdout,
                        'stderr': result.stderr
                    }), 500
            else:
                # Try to parse error as JSON
                try:
                    error_output = json.loads(result.stderr)
                    return jsonify(error_output), 400
                except json.JSONDecodeError:
                    return jsonify({
                        'success': False,
                        'error': result.stderr or 'Compilation failed',
                        'stdout': result.stdout
                    }), 400
                    
        except subprocess.TimeoutExpired:
            return jsonify({
                'success': False,
                'error': 'Compilation timeout (expression took too long to evaluate)'
            }), 408
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Failed to execute compiler: {str(e)}'
            }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    compiler_exists = os.path.exists(COMPILER_PATH)
    return jsonify({
        'status': 'healthy',
        'compiler_path': COMPILER_PATH,
        'compiler_exists': compiler_exists
    })

@app.route('/api/analyze/build', methods=['POST'])
def build_object_files():
    """
    Build object files with different optimization levels
    
    Returns:
    {
        "success": true,
        "built": [
            {"level": "O0", "file": "...", "size": 12345},
            {"level": "O2", "file": "...", "size": 10234}
        ]
    }
    """
    try:
        compiler_dir = os.path.join(os.path.dirname(__file__), '..', 'compiler')
        analyzer = ObjectFileAnalyzer(compiler_dir)
        
        result = analyzer.build_object_files()
        
        if result['status'] == 'success':
            return jsonify({
                'success': True,
                'data': result
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Build failed'),
                'data': result
            }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Build error: {str(e)}'
        }), 500

@app.route('/api/analyze/object', methods=['GET'])
def analyze_object():
    """
    Perform complete object file analysis
    
    Query parameters:
    - level: O0 or O2 (default: O0)
    
    Returns complete analysis including disassembly, symbols, sections, and size
    """
    try:
        opt_level = request.args.get('level', 'O0')
        
        if opt_level not in ['O0', 'O2']:
            return jsonify({
                'success': False,
                'error': 'Invalid optimization level. Use O0 or O2'
            }), 400
        
        compiler_dir = os.path.join(os.path.dirname(__file__), '..', 'compiler')
        analyzer = ObjectFileAnalyzer(compiler_dir)
        
        # Check if object file exists
        obj_file = analyzer.object_files.get(opt_level)
        if not os.path.exists(obj_file):
            return jsonify({
                'success': False,
                'error': f'Object file not found: {obj_file}. Please build first.',
                'hint': 'Call /api/analyze/build first'
            }), 404
        
        analysis = analyzer.analyze_complete(opt_level)
        
        return jsonify({
            'success': True,
            'optimization_level': opt_level,
            'data': analysis
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Analysis error: {str(e)}'
        }), 500

@app.route('/api/analyze/optimization', methods=['GET'])
def compare_optimizations():
    """
    Compare -O0 vs -O2 optimization results
    
    Returns detailed comparison of instruction counts, binary sizes, and symbols
    """
    try:
        compiler_dir = os.path.join(os.path.dirname(__file__), '..', 'compiler')
        analyzer = ObjectFileAnalyzer(compiler_dir)
        
        # Check if both object files exist
        missing_files = []
        for level, path in analyzer.object_files.items():
            if not os.path.exists(path):
                missing_files.append(f'{level}: {path}')
        
        if missing_files:
            return jsonify({
                'success': False,
                'error': 'Object files not found',
                'missing': missing_files,
                'hint': 'Call /api/analyze/build first'
            }), 404
        
        comparison = analyzer.compare_optimizations()
        
        return jsonify({
            'success': True,
            'data': comparison
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Comparison error: {str(e)}'
        }), 500

@app.route('/api/analyze/disassembly', methods=['GET'])
def get_disassembly():
    """
    Get detailed disassembly for specific optimization level
    
    Query parameters:
    - level: O0 or O2 (default: O0)
    """
    try:
        opt_level = request.args.get('level', 'O0')
        
        if opt_level not in ['O0', 'O2']:
            return jsonify({
                'success': False,
                'error': 'Invalid optimization level. Use O0 or O2'
            }), 400
        
        compiler_dir = os.path.join(os.path.dirname(__file__), '..', 'compiler')
        analyzer = ObjectFileAnalyzer(compiler_dir)
        
        disassembly = analyzer.get_disassembly(opt_level)
        
        if 'error' in disassembly:
            return jsonify({
                'success': False,
                'error': disassembly['error']
            }), 500
        
        return jsonify({
            'success': True,
            'data': disassembly
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Disassembly error: {str(e)}'
        }), 500

def expression_to_cpp(expression):
    """
    Convert a mathematical expression to standalone C++ code
    Supports: arithmetic, factorial, nCr, nPr, differentiation, integration, trig functions
    """
    # Add necessary math functions and constants
    cpp_code = """#include <iostream>
#include <cmath>
#include <functional>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#ifndef M_E
#define M_E 2.71828182845904523536
#endif

// Factorial function
double factorial(double n) {
    if (n < 0 || n != floor(n)) return -1;
    if (n > 170) return -1;
    double result = 1.0;
    for (int i = 2; i <= (int)n; i++) {
        result *= i;
    }
    return result;
}

// nCr function
double nCr(double n, double r) {
    if (n < 0 || r < 0 || r > n) return -1;
    if (n != floor(n) || r != floor(r)) return -1;
    double n_fact = factorial(n);
    double r_fact = factorial(r);
    double nr_fact = factorial(n - r);
    return n_fact / (r_fact * nr_fact);
}

// nPr function
double nPr(double n, double r) {
    if (n < 0 || r < 0 || r > n) return -1;
    if (n != floor(n) || r != floor(r)) return -1;
    double n_fact = factorial(n);
    double nr_fact = factorial(n - r);
    return n_fact / nr_fact;
}

// Numerical differentiation using central difference method
double differentiate(std::function<double(double)> f, double x, double h = 1e-5) {
    return (f(x + h) - f(x - h)) / (2.0 * h);
}

// Numerical integration using Simpson's rule
double integrate(std::function<double(double)> f, double a, double b, int n = 1000) {
    if (n % 2 == 1) n++; // Simpson's rule requires even number of intervals
    double h = (b - a) / n;
    double sum = f(a) + f(b);
    
    for (int i = 1; i < n; i++) {
        double x = a + i * h;
        sum += (i % 2 == 0) ? 2.0 * f(x) : 4.0 * f(x);
    }
    
    return sum * h / 3.0;
}

int main() {
    double result = """
    
    # Convert expression to C++ syntax
    cpp_expr = expression
    
    # Replace constants with word boundaries (don't replace 'e' in 'integrate')
    cpp_expr = re.sub(r'\bpi\b', 'M_PI', cpp_expr)
    cpp_expr = re.sub(r'\be\b', 'M_E', cpp_expr)
    
    # Check if expression contains calculus operations
    has_calculus = 'diff(' in expression or 'integrate(' in expression
    
    # Handle differentiation: diff(expr, var, point)
    # Example: diff(x^2, x, 3) -> differentiate([](double x){ return pow(x, 2); }, 3)
    diff_pattern = r'diff\(([^,]+),\s*(\w+),\s*([^)]+)\)'
    diff_matches = re.findall(diff_pattern, cpp_expr)
    
    for expr, var, point in diff_matches:
        # Clean up the expression
        expr = expr.strip()
        # Replace variable with lambda parameter
        lambda_expr = expr.replace(var, var)  # Keep var as-is for now, will be in lambda
        # Handle power in lambda expression
        lambda_expr = lambda_expr.replace('^', '**POWER**')  # Temp marker
        while '**POWER**' in lambda_expr:
            lambda_expr = re.sub(r'(\w+|\d+\.?\d*|\([^)]+\))\s*\*\*POWER\*\*\s*(\w+|\d+\.?\d*|\([^)]+\))', 
                                r'pow(\1, \2)', lambda_expr)
        
        # Create lambda function
        lambda_code = f'[](double {var}){{ return {lambda_expr}; }}'
        replacement = f'differentiate({lambda_code}, {point})'
        
        # Replace in cpp_expr
        original = f'diff({expr}, {var}, {point})'
        cpp_expr = cpp_expr.replace(original, replacement)
    
    # Handle integration: integrate(expr, var, lower, upper)
    # Example: integrate(x^2, x, 0, 3) -> integrate([](double x){ return pow(x, 2); }, 0, 3)
    integrate_pattern = r'integrate\(([^,]+),\s*(\w+),\s*([^,]+),\s*([^)]+)\)'
    integrate_matches = re.findall(integrate_pattern, cpp_expr)
    
    for expr, var, lower, upper in integrate_matches:
        # Clean up the expression
        expr = expr.strip()
        # Handle power in lambda expression
        lambda_expr = expr.replace(var, var)
        lambda_expr = lambda_expr.replace('^', '**POWER**')
        while '**POWER**' in lambda_expr:
            lambda_expr = re.sub(r'(\w+|\d+\.?\d*|\([^)]+\))\s*\*\*POWER\*\*\s*(\w+|\d+\.?\d*|\([^)]+\))', 
                                r'pow(\1, \2)', lambda_expr)
        
        # Create lambda function
        lambda_code = f'[](double {var}){{ return {lambda_expr}; }}'
        replacement = f'integrate({lambda_code}, {lower}, {upper})'
        
        # Replace in cpp_expr
        original = f'integrate({expr}, {var}, {lower}, {upper})'
        cpp_expr = cpp_expr.replace(original, replacement)
    
    # Handle factorial (convert 5! to factorial(5))
    # Match number or parenthesized expression followed by !
    cpp_expr = re.sub(r'(\d+\.?\d*)\s*!', r'factorial(\1)', cpp_expr)
    cpp_expr = re.sub(r'\(([^)]+)\)\s*!', r'factorial(\1)', cpp_expr)
    
    # Handle power operator ^ (convert to pow function)
    # This handles x^y including nested expressions
    while '^' in cpp_expr:
        cpp_expr = re.sub(r'(\w+|\d+\.?\d*|\([^)]+\))\s*\^\s*(\w+|\d+\.?\d*|\([^)]+\))', r'pow(\1, \2)', cpp_expr)
    
    # Handle mathematical functions (already in C++ math.h)
    # These work as-is: sin, cos, tan, asin, acos, atan, log, ln->log, exp, sqrt, abs, etc.
    cpp_expr = cpp_expr.replace('ln(', 'log(')  # ln is log in C++
    cpp_expr = cpp_expr.replace('cbrt(', 'cbrt(')  # cube root is already cbrt
    
    cpp_code += cpp_expr + ";\n"
    cpp_code += "    std::cout << result << std::endl;\n"
    cpp_code += "    return 0;\n"
    cpp_code += "}\n"
    
    return cpp_code

@app.route('/api/test/cpp-gen', methods=['POST'])
def test_cpp_generation():
    """Test endpoint to verify C++ code generation"""
    try:
        data = request.get_json()
        expression = data.get('expression', '2+3')
        cpp_code = expression_to_cpp(expression)
        return jsonify({
            'success': True,
            'expression': expression,
            'cpp_code': cpp_code
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/object/analyze-expression', methods=['POST'])
def analyze_expression_optimization():
    """
    Analyze optimization for a specific mathematical expression
    
    Generates C++ code for the expression, compiles it with -O0 and -O2,
    and compares the resulting binaries
    
    Expected JSON input:
    {
        "expression": "2 + 3 * 4"
    }
    
    Returns:
    {
        "success": true,
        "expression": "2 + 3 * 4",
        "cpp_code": "...",
        "O0": {
            "size": 12345,
            "assembly_lines": 150,
            "assembly": "..."
        },
        "O2": {
            "size": 8000,
            "assembly_lines": 45,
            "assembly": "..."
        },
        "improvement": {
            "size_reduction": "35.4%",
            "instruction_reduction": "70.0%"
        }
    }
    """
    try:
        data = request.get_json()
        expression = data.get('expression', '').strip()
        
        if not expression:
            return jsonify({
                'success': False,
                'error': 'Expression is required'
            }), 400
        
        # Create temporary directory
        temp_dir = tempfile.mkdtemp(prefix='expr_analyze_')
        
        try:
            # Generate C++ code
            cpp_code = expression_to_cpp(expression)
            cpp_file = os.path.join(temp_dir, 'expr.cpp')
            
            # Debug: print generated code
            print(f"\n{'='*60}")
            print(f"Expression: {expression}")
            print(f"{'='*60}")
            print(f"Generated C++ Code:")
            print(cpp_code)
            print(f"{'='*60}\n")
            
            with open(cpp_file, 'w') as f:
                f.write(cpp_code)
            
            # Compile with -O0
            o0_exe = os.path.join(temp_dir, 'expr_O0.exe')
            o0_compile = subprocess.run(
                ['g++', '-std=c++11', '-O0', '-o', o0_exe, cpp_file],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if o0_compile.returncode != 0:
                return jsonify({
                    'success': False,
                    'error': 'Compilation failed (O0)',
                    'details': o0_compile.stderr,
                    'stdout': o0_compile.stdout,
                    'cpp_code': cpp_code
                }), 500
            
            # Compile with -O2
            o2_exe = os.path.join(temp_dir, 'expr_O2.exe')
            o2_compile = subprocess.run(
                ['g++', '-std=c++11', '-O2', '-o', o2_exe, cpp_file],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if o2_compile.returncode != 0:
                return jsonify({
                    'success': False,
                    'error': 'Compilation failed (O2)',
                    'details': o2_compile.stderr,
                    'stdout': o2_compile.stdout,
                    'cpp_code': cpp_code
                }), 500
            
            # Get file sizes
            o0_size = os.path.getsize(o0_exe)
            o2_size = os.path.getsize(o2_exe)
            
            # Disassemble both
            o0_asm = subprocess.run(
                ['objdump', '-d', o0_exe],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            o2_asm = subprocess.run(
                ['objdump', '-d', o2_exe],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Extract main function assembly
            def extract_main_function(asm_text):
                lines = asm_text.split('\n')
                main_lines = []
                in_main = False
                
                for line in lines:
                    if '<main>:' in line or '<_main>:' in line:
                        in_main = True
                        main_lines.append(line)
                    elif in_main:
                        if line.strip() and not line.startswith(' '):
                            # New function started
                            break
                        main_lines.append(line)
                
                return '\n'.join(main_lines)
            
            o0_main = extract_main_function(o0_asm.stdout)
            o2_main = extract_main_function(o2_asm.stdout)
            
            # Count instructions (lines with opcodes)
            def count_instructions(asm_text):
                return len([line for line in asm_text.split('\n') 
                           if ':' in line and any(op in line.lower() for op in 
                           ['mov', 'add', 'sub', 'mul', 'div', 'call', 'ret', 'jmp', 'cmp', 'push', 'pop', 'imul', 'lea'])])
            
            o0_instructions = count_instructions(o0_main)
            o2_instructions = count_instructions(o2_main)
            
            # Calculate improvements
            size_reduction = ((o0_size - o2_size) / o0_size * 100) if o0_size > 0 else 0
            instr_reduction = ((o0_instructions - o2_instructions) / o0_instructions * 100) if o0_instructions > 0 else 0
            
            return jsonify({
                'success': True,
                'expression': expression,
                'cpp_code': cpp_code,
                'O0': {
                    'size': o0_size,
                    'assembly_lines': o0_instructions,
                    'assembly': o0_main,
                    'full_assembly': o0_asm.stdout
                },
                'O2': {
                    'size': o2_size,
                    'assembly_lines': o2_instructions,
                    'assembly': o2_main,
                    'full_assembly': o2_asm.stdout
                },
                'improvement': {
                    'size_reduction_bytes': o0_size - o2_size,
                    'size_reduction_percent': round(size_reduction, 2),
                    'instruction_reduction': o2_instructions - o0_instructions,
                    'instruction_reduction_percent': round(instr_reduction, 2)
                }
            })
        
        finally:
            # Cleanup temporary directory
            try:
                shutil.rmtree(temp_dir)
            except:
                pass
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Analysis error: {str(e)}'
        }), 500

@app.errorhandler(404)
def not_found(e):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.route('/api/analyze/pnc', methods=['POST'])
def analyze_pnc():
    """
    Endpoint for Probability and Combinatorics analysis
    
    Expected JSON input:
    {
        "expression": "nCr(10,3)" or "nCr(5,2)/nCr(10,2)"
    }
    
    Returns:
    {
        "success": true,
        "expression": "nCr(10,3)",
        "ast": {...},
        "intermediateCode": [...],
        "result": 120,
        "steps": [
            {"step": "Calculate n!", "value": 3628800},
            {"step": "Calculate r!", "value": 6},
            ...
        ],
        "isProbability": false,
        "probabilityValid": null
    }
    """
    try:
        data = request.get_json()
        expression = data.get('expression', '').strip()
        
        if not expression:
            return jsonify({
                'success': False,
                'error': 'No expression provided'
            }), 400
        
        # Call the C++ compiler
        process = subprocess.Popen(
            [COMPILER_PATH],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate(input=expression)
        
        if process.returncode != 0:
            return jsonify({
                'success': False,
                'error': stderr or 'Compilation failed'
            }), 400
        
        # Parse the JSON output from compiler
        compiler_output = json.loads(stdout)
        
        if not compiler_output.get('success'):
            return jsonify({
                'success': False,
                'error': compiler_output.get('error', 'Compilation failed')
            }), 400
        
        # Extract PnC-specific information
        result = compiler_output.get('result', 0)
        intermediate_code = compiler_output.get('intermediateCode', [])
        
        # Generate step-by-step evaluation
        steps = generate_pnc_steps(intermediate_code, expression)
        
        # Check if expression is a probability (contains division)
        is_probability = '/' in expression
        probability_valid = None
        
        if is_probability:
            # Validate probability is in [0, 1]
            probability_valid = 0 <= result <= 1
            if not probability_valid:
                steps.append({
                    'step': '⚠️ Warning: Result outside [0,1] range',
                    'value': result,
                    'warning': True
                })
        
        return jsonify({
            'success': True,
            'expression': expression,
            'ast': compiler_output.get('ast', {}),
            'intermediateCode': intermediate_code,
            'tokens': compiler_output.get('tokens', []),
            'postfix': compiler_output.get('postfix', []),
            'result': result,
            'steps': steps,
            'isProbability': is_probability,
            'probabilityValid': probability_valid
        })
        
    except json.JSONDecodeError:
        return jsonify({
            'success': False,
            'error': 'Invalid compiler output'
        }), 500
    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False,
            'error': 'Compilation timeout'
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def generate_pnc_steps(intermediate_code, expression):
    """
    Generate human-readable evaluation steps from intermediate code
    """
    steps = []
    temp_values = {}
    
    for line in intermediate_code:
        parts = line.split(' = ')
        if len(parts) != 2:
            continue
        
        temp_var = parts[0]
        operation = parts[1]
        
        # Parse constants
        try:
            value = float(operation)
            temp_values[temp_var] = value
            continue
        except ValueError:
            pass
        
        # Parse factorial operations
        if operation.startswith('fact '):
            operand = operation.replace('fact ', '')
            if operand in temp_values:
                n = int(temp_values[operand])
                result = 1
                for i in range(2, n + 1):
                    result *= i
                temp_values[temp_var] = result
                steps.append({
                    'step': f'Calculate {n}!',
                    'formula': f'{n}! = ' + ' × '.join(str(i) for i in range(1, min(n+1, 6))) + ('...' if n > 5 else ''),
                    'value': result
                })
        
        # Parse arithmetic operations
        elif ' - ' in operation:
            left, right = operation.split(' - ')
            if left in temp_values and right in temp_values:
                result = temp_values[left] - temp_values[right]
                temp_values[temp_var] = result
                steps.append({
                    'step': f'Subtract: {int(temp_values[left])} - {int(temp_values[right])}',
                    'value': result
                })
        
        elif ' * ' in operation:
            left, right = operation.split(' * ')
            if left in temp_values and right in temp_values:
                result = temp_values[left] * temp_values[right]
                temp_values[temp_var] = result
                steps.append({
                    'step': f'Multiply: {temp_values[left]} × {temp_values[right]}',
                    'value': result
                })
        
        elif ' / ' in operation:
            left, right = operation.split(' / ')
            if left in temp_values and right in temp_values:
                result = temp_values[left] / temp_values[right]
                temp_values[temp_var] = result
                steps.append({
                    'step': f'Divide: {temp_values[left]} ÷ {temp_values[right]}',
                    'value': result
                })
    
    return steps

@app.errorhandler(500)
def internal_error(e):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    print("=" * 60)
    print("Scientific Expression Compiler - Backend Server")
    print("=" * 60)
    print(f"Compiler path: {COMPILER_PATH}")
    print(f"Compiler exists: {os.path.exists(COMPILER_PATH)}")
    print(f"Static folder: {app.static_folder}")
    print("=" * 60)
    
    if not os.path.exists(COMPILER_PATH):
        print("\n⚠️  WARNING: C++ compiler not found!")
        print("Please build the compiler first:")
        print("  cd compiler")
        print("  make")
        print("=" * 60)
    
    print("\nStarting server on http://localhost:5000")
    print("Press Ctrl+C to stop\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
