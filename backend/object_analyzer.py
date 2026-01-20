"""
Object File Analysis Module
Analyzes compiled object files (.o) using standard toolchain utilities
Provides machine-level insights for compiler education
"""

import subprocess
import re
import json
import os
from typing import Dict, List, Any, Optional


class ObjectFileAnalyzer:
    """Analyzes object files using objdump, nm, readelf, and size utilities"""
    
    def __init__(self, compiler_dir: str = "../compiler"):
        self.compiler_dir = compiler_dir
        self.object_files = {
            'O0': os.path.join(compiler_dir, 'compiler_O0.o'),
            'O2': os.path.join(compiler_dir, 'compiler_O2.o')
        }
    
    def _run_command(self, cmd: List[str]) -> tuple[str, str, int]:
        """Safely execute command and capture output"""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.stdout, result.stderr, result.returncode
        except subprocess.TimeoutExpired:
            return "", "Command timed out", -1
        except Exception as e:
            return "", str(e), -1
    
    def build_object_files(self) -> Dict[str, Any]:
        """Compile source files to object files with different optimization levels"""
        results = {'status': 'success', 'built': []}
        
        # Get all .cpp files
        cpp_files = []
        for file in os.listdir(self.compiler_dir):
            if file.endswith('.cpp') and file != 'main.cpp':
                cpp_files.append(file)  # Store just filename, not full path
        
        if not cpp_files:
            return {'status': 'error', 'message': 'No source files found'}
        
        # Build with -O0 and -O2
        for opt_level, opt_flag in [('O0', '-O0'), ('O2', '-O2')]:
            output_file = self.object_files[opt_level]
            
            # Step 1: Compile each .cpp file to .o (in compiler directory)
            object_files = []
            compile_failed = False
            
            for cpp_file in cpp_files:
                obj_file = cpp_file.replace('.cpp', '.o')
                object_files.append(obj_file)
                
                # Compile with full path
                cmd = ['g++', '-std=c++17', '-Wall', '-Wextra', opt_flag, '-c', 
                       os.path.join(self.compiler_dir, cpp_file),
                       '-o', os.path.join(self.compiler_dir, obj_file)]
                
                stdout, stderr, returncode = self._run_command(cmd)
                
                if returncode != 0:
                    results['status'] = 'error'
                    results['error'] = f'Compilation failed for {cpp_file}: {stderr}'
                    compile_failed = True
                    break
            
            if compile_failed:
                # Clean up any created .o files
                for obj_file in object_files:
                    obj_path = os.path.join(self.compiler_dir, obj_file)
                    if os.path.exists(obj_path):
                        os.remove(obj_path)
                continue
            
            # Step 2: Combine .o files into single relocatable object file using ld
            ld_cmd = ['ld', '-r', '-o', output_file] + \
                     [os.path.join(self.compiler_dir, obj) for obj in object_files]
            
            stdout, stderr, returncode = self._run_command(ld_cmd)
            
            if returncode == 0 and os.path.exists(output_file):
                results['built'].append({
                    'level': opt_level,
                    'file': output_file,
                    'size': os.path.getsize(output_file)
                })
            else:
                results['status'] = 'partial'
                results['error'] = f'Linking failed for {opt_level}: {stderr}'
            
            # Step 3: Clean up individual .o files
            for obj_file in object_files:
                obj_path = os.path.join(self.compiler_dir, obj_file)
                if os.path.exists(obj_path):
                    try:
                        os.remove(obj_path)
                    except:
                        pass  # Ignore cleanup errors
        
        return results
    
    def get_disassembly(self, opt_level: str = 'O0') -> Dict[str, Any]:
        """Extract disassembly using objdump"""
        obj_file = self.object_files.get(opt_level)
        if not obj_file or not os.path.exists(obj_file):
            return {'error': f'Object file not found: {obj_file}'}
        
        # Get disassembly with source intermixed
        cmd = ['objdump', '-d', '-C', '--no-show-raw-insn', obj_file]
        stdout, stderr, returncode = self._run_command(cmd)
        
        if returncode != 0:
            return {'error': stderr}
        
        # Parse disassembly into structured format
        functions = []
        current_function = None
        
        for line in stdout.split('\n'):
            # Match function headers like: 0000000000000000 <functionName>:
            func_match = re.match(r'^([0-9a-f]+)\s+<(.+)>:', line)
            if func_match:
                if current_function:
                    functions.append(current_function)
                current_function = {
                    'address': func_match.group(1),
                    'name': func_match.group(2),
                    'instructions': []
                }
            # Match instruction lines
            elif current_function and line.strip():
                inst_match = re.match(r'\s*([0-9a-f]+):\s+(.+)', line)
                if inst_match:
                    current_function['instructions'].append({
                        'address': inst_match.group(1),
                        'code': inst_match.group(2).strip()
                    })
        
        if current_function:
            functions.append(current_function)
        
        # Calculate instruction statistics
        total_instructions = sum(len(f['instructions']) for f in functions)
        instruction_freq = {}
        
        for func in functions:
            for inst in func['instructions']:
                mnemonic = inst['code'].split()[0] if inst['code'] else 'unknown'
                instruction_freq[mnemonic] = instruction_freq.get(mnemonic, 0) + 1
        
        return {
            'optimization': opt_level,
            'functions': functions,
            'total_functions': len(functions),
            'total_instructions': total_instructions,
            'instruction_frequency': instruction_freq
        }
    
    def get_symbol_table(self, opt_level: str = 'O0') -> Dict[str, Any]:
        """Extract symbol table using nm"""
        obj_file = self.object_files.get(opt_level)
        if not obj_file or not os.path.exists(obj_file):
            return {'error': f'Object file not found: {obj_file}'}
        
        # Get symbols with demangling
        cmd = ['nm', '-C', '--size-sort', obj_file]
        stdout, stderr, returncode = self._run_command(cmd)
        
        if returncode != 0:
            return {'error': stderr}
        
        symbols = {
            'global': [],
            'local': [],
            'undefined': [],
            'weak': []
        }
        
        for line in stdout.split('\n'):
            if not line.strip():
                continue
            
            parts = line.split()
            if len(parts) < 2:
                continue
            
            symbol_type = parts[-2] if len(parts) >= 2 else 'U'
            symbol_name = parts[-1]
            
            symbol_info = {
                'name': symbol_name,
                'type': symbol_type,
                'address': parts[0] if len(parts) >= 3 else '0'
            }
            
            # Categorize symbols
            if symbol_type in ['T', 'D', 'R', 'B']:
                symbols['global'].append(symbol_info)
            elif symbol_type in ['t', 'd', 'r', 'b']:
                symbols['local'].append(symbol_info)
            elif symbol_type == 'U':
                symbols['undefined'].append(symbol_info)
            elif symbol_type in ['W', 'w', 'V', 'v']:
                symbols['weak'].append(symbol_info)
        
        return {
            'optimization': opt_level,
            'symbols': symbols,
            'total_symbols': sum(len(v) for v in symbols.values())
        }
    
    def get_elf_sections(self, opt_level: str = 'O0') -> Dict[str, Any]:
        """Extract ELF section information using readelf"""
        obj_file = self.object_files.get(opt_level)
        if not obj_file or not os.path.exists(obj_file):
            return {'error': f'Object file not found: {obj_file}'}
        
        # Get section headers
        cmd = ['readelf', '-S', obj_file]
        stdout, stderr, returncode = self._run_command(cmd)
        
        if returncode != 0:
            return {'error': stderr}
        
        sections = []
        for line in stdout.split('\n'):
            # Parse section header lines
            # Format: [ 1] .text             PROGBITS         0000000000000000  00000040
            match = re.match(r'\s*\[\s*\d+\]\s+(\S+)\s+(\S+)\s+([0-9a-f]+)\s+([0-9a-f]+)\s+([0-9a-f]+)', line)
            if match:
                sections.append({
                    'name': match.group(1),
                    'type': match.group(2),
                    'address': match.group(3),
                    'offset': match.group(4),
                    'size': int(match.group(5), 16)
                })
        
        return {
            'optimization': opt_level,
            'sections': sections,
            'total_sections': len(sections)
        }
    
    def get_size_metrics(self, opt_level: str = 'O0') -> Dict[str, Any]:
        """Extract size metrics using size utility"""
        obj_file = self.object_files.get(opt_level)
        if not obj_file or not os.path.exists(obj_file):
            return {'error': f'Object file not found: {obj_file}'}
        
        # Get size information
        cmd = ['size', '-A', obj_file]
        stdout, stderr, returncode = self._run_command(cmd)
        
        if returncode != 0:
            # Try BSD format as fallback
            cmd = ['size', obj_file]
            stdout, stderr, returncode = self._run_command(cmd)
            if returncode != 0:
                return {'error': stderr}
        
        metrics = {
            'text': 0,
            'data': 0,
            'bss': 0,
            'rodata': 0,
            'total': 0
        }
        
        # Parse output
        for line in stdout.split('\n'):
            if '.text' in line:
                parts = line.split()
                if len(parts) >= 2:
                    metrics['text'] = int(parts[1]) if parts[1].isdigit() else 0
            elif '.data' in line:
                parts = line.split()
                if len(parts) >= 2:
                    metrics['data'] = int(parts[1]) if parts[1].isdigit() else 0
            elif '.bss' in line:
                parts = line.split()
                if len(parts) >= 2:
                    metrics['bss'] = int(parts[1]) if parts[1].isdigit() else 0
            elif '.rodata' in line:
                parts = line.split()
                if len(parts) >= 2:
                    metrics['rodata'] = int(parts[1]) if parts[1].isdigit() else 0
        
        metrics['total'] = metrics['text'] + metrics['data'] + metrics['bss'] + metrics['rodata']
        
        return {
            'optimization': opt_level,
            'metrics': metrics
        }
    
    def compare_optimizations(self) -> Dict[str, Any]:
        """Compare -O0 vs -O2 optimizations"""
        comparison = {
            'disassembly': {},
            'size': {},
            'symbols': {}
        }
        
        # Get data for both optimization levels
        o0_disasm = self.get_disassembly('O0')
        o2_disasm = self.get_disassembly('O2')
        
        o0_size = self.get_size_metrics('O0')
        o2_size = self.get_size_metrics('O2')
        
        o0_symbols = self.get_symbol_table('O0')
        o2_symbols = self.get_symbol_table('O2')
        
        # Compare instruction counts
        if 'error' not in o0_disasm and 'error' not in o2_disasm:
            comparison['disassembly'] = {
                'O0_instructions': o0_disasm['total_instructions'],
                'O2_instructions': o2_disasm['total_instructions'],
                'reduction': o0_disasm['total_instructions'] - o2_disasm['total_instructions'],
                'reduction_percent': round(
                    ((o0_disasm['total_instructions'] - o2_disasm['total_instructions']) / 
                     o0_disasm['total_instructions'] * 100) if o0_disasm['total_instructions'] > 0 else 0, 2
                )
            }
        
        # Compare sizes
        if 'error' not in o0_size and 'error' not in o2_size:
            o0_total = o0_size['metrics']['total']
            o2_total = o2_size['metrics']['total']
            comparison['size'] = {
                'O0': o0_size['metrics'],
                'O2': o2_size['metrics'],
                'reduction': o0_total - o2_total,
                'reduction_percent': round(
                    ((o0_total - o2_total) / o0_total * 100) if o0_total > 0 else 0, 2
                )
            }
        
        # Compare symbol counts
        if 'error' not in o0_symbols and 'error' not in o2_symbols:
            comparison['symbols'] = {
                'O0_total': o0_symbols['total_symbols'],
                'O2_total': o2_symbols['total_symbols']
            }
        
        return comparison
    
    def analyze_complete(self, opt_level: str = 'O0') -> Dict[str, Any]:
        """Perform complete analysis of object file"""
        return {
            'disassembly': self.get_disassembly(opt_level),
            'symbols': self.get_symbol_table(opt_level),
            'sections': self.get_elf_sections(opt_level),
            'size': self.get_size_metrics(opt_level)
        }
