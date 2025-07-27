#!/usr/bin/env python3
"""
Script to check Python files for indentation errors and fix them.
"""

import ast
import os
import sys
import traceback
from pathlib import Path

def check_file_for_syntax_errors(file_path):
    """
    Check a Python file for syntax errors including indentation issues.
    
    Args:
        file_path (str): Path to the Python file
        
    Returns:
        tuple: (has_error, error_message)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Try to parse the file with AST
        ast.parse(content, filename=file_path)
        return False, ""
    except IndentationError as e:
        return True, f"IndentationError: {str(e)}"
    except SyntaxError as e:
        return True, f"SyntaxError: {str(e)}"
    except Exception as e:
        return True, f"Error: {str(e)}"

def fix_indentation_in_file(file_path):
    """
    Attempt to fix indentation issues in a Python file.
    
    Args:
        file_path (str): Path to the Python file
        
    Returns:
        bool: True if file was modified, False otherwise
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        modified = False
        fixed_lines = []
        
        for i, line in enumerate(lines):
            # Check for mixed tabs and spaces
            if '\t' in line and ' ' in line[:line.find('\t')]:
                # Replace tabs with 4 spaces
                line = line.replace('\t', '    ')
                modified = True
            fixed_lines.append(line)
        
        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(fixed_lines)
            return True
        return False
    except Exception as e:
        print(f"Error fixing {file_path}: {str(e)}")
        return False

def check_and_fix_directory(directory):
    """
    Check all Python files in a directory for indentation errors.
    
    Args:
        directory (str): Directory path to check
        
    Returns:
        dict: Summary of findings
    """
    summary = {
        'total_files': 0,
        'files_with_errors': [],
        'files_fixed': [],
        'errors': []
    }
    
    # Find all Python files
    python_files = list(Path(directory).rglob("*.py"))
    
    for file_path in python_files:
        summary['total_files'] += 1
        has_error, error_msg = check_file_for_syntax_errors(file_path)
        
        if has_error:
            print(f"ERROR in {file_path}: {error_msg}")
            summary['files_with_errors'].append((str(file_path), error_msg))
            
            # Try to fix indentation
            if fix_indentation_in_file(file_path):
                print(f"FIXED indentation in {file_path}")
                summary['files_fixed'].append(str(file_path))
                
                # Verify the fix
                has_error_after_fix, error_msg_after_fix = check_file_for_syntax_errors(file_path)
                if has_error_after_fix:
                    summary['errors'].append(f"Still has error after fix in {file_path}: {error_msg_after_fix}")
                else:
                    print(f"VERIFIED fix in {file_path}")
        else:
            print(f"OK: {file_path}")
            
    return summary

def main():
    """Main function to check indentation in all Python files."""
    project_root = Path(__file__).parent
    
    print(f"Checking Python files for indentation errors in: {project_root}")
    print("=" * 60)
    
    summary = check_and_fix_directory(project_root)
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total Python files checked: {summary['total_files']}")
    print(f"Files with errors: {len(summary['files_with_errors'])}")
    print(f"Files fixed: {len(summary['files_fixed'])}")
    
    if summary['files_with_errors']:
        print("\nFiles with errors:")
        for file_path, error in summary['files_with_errors']:
            print(f"  - {file_path}: {error}")
            
    if summary['files_fixed']:
        print("\nFiles fixed:")
        for file_path in summary['files_fixed']:
            print(f"  - {file_path}")
            
    if summary['errors']:
        print("\nErrors that remain after fixing:")
        for error in summary['errors']:
            print(f"  - {error}")
            
    # Return exit code 1 if there were any errors
    if summary['files_with_errors']:
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
