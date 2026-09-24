#!/usr/bin/env python3
"""
Script to clean the CodefyExcelAnalyzer_V11.3.1.py file of Git conflict markers
"""

import re

def clean_file(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    cleaned_lines = []
    skip_block = False
    
    for line in lines:
        # Check for Git conflict markers
        if line.strip().startswith('<<<<<<<') or line.strip().startswith('=======') or line.strip().startswith('>>>>>>>'):
            skip_block = True
            continue
        elif line.strip() == '```' or line.strip().startswith('```python'):
            # Skip markdown code block delimiters
            continue
        elif skip_block and (line.strip().startswith('if __name__') or 'MAIN' in line or line.strip().startswith('# â•')):
            # End skipping when we reach main section
            skip_block = False
        
        if not skip_block:
            cleaned_lines.append(line)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(cleaned_lines)
    
    print(f"Cleaned file saved to: {output_path}")

if __name__ == "__main__":
    input_file = "Statics/PY/CodefyExcelAnalyzer_V11.3.1.py"
    output_file = "Statics/PY/CodefyExcelAnalyzer_V11.3.1.py.clean"
    clean_file(input_file, output_file)