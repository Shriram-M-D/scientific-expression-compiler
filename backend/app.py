from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import subprocess
import json
import os
import sys

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

@app.errorhandler(404)
def not_found(e):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

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
