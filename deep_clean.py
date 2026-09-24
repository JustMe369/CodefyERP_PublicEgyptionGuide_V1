#!/usr/bin/env python3
"""
Deep cleaning script for CodefyExcelAnalyzer_V11.3.1.py file
Removes all Git conflict markers, markdown syntax, and other problematic content
"""

import re

def deep_clean_file(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Remove Git conflict markers and their content
    content = re.sub(r'<<<<<<< HEAD.*?=======.*?>>>>>>>.*?(\n|$)', '', content, flags=re.DOTALL)
    
    # Remove markdown code block delimiters
    content = re.sub(r'^```\s*(python)?\s*$', '', content, flags=re.MULTILINE)
    
    # Remove file path comments that shouldn't be in the code
    content = re.sub(r'^CodefyERP_Public_Egyption_version.*?\.py\s*$', '', content, flags=re.MULTILINE)
    
    # Remove any remaining Git-related lines
    content = re.sub(r'^>>>>>>>.*$', '', content, flags=re.MULTILINE)
    content = re.sub(r'^<<<<<<<.*$', '', content, flags=re.MULTILINE)
    content = re.sub(r'^=======.*$', '', content, flags=re.MULTILINE)
    
    # Clean up multiple consecutive empty lines
    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Deep cleaned file saved to: {output_path}")
    
    # Count lines to verify it's reasonable
    lines = content.split('\n')
    print(f"File has {len(lines)} lines after cleaning")

if __name__ == "__main__":
    input_file = "Statics/PY/CodefyExcelAnalyzer_V11.3.1.py"
    output_file = "Statics/PY/CodefyExcelAnalyzer_V11.3.1.py.deep_cleaned"
    deep_clean_file(input_file, output_file)