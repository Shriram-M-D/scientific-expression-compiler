from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import subprocess
import json
import os
import sys
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
