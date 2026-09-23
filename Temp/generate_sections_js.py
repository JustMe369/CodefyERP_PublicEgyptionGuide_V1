import os
import re
import json

sections_dir = 'sections'
output_file = 'sections-content.js'

section_ids = ['login', 'bulk-import', 'relationships', 'assignments', 'pricing', 'readiness']

with open(output_file, 'w', encoding='utf-8') as f:
    f.write('// Auto-generated: Section content as JavaScript strings\n')
    f.write('// Loaded via <script src> to support file:// protocol\n\n')
    f.write('var SECTION_CONTENT = {\n')

    for i, sec_id in enumerate(section_ids):
        filepath = os.path.join(sections_dir, f'{sec_id}.html')
        with open(filepath, 'r', encoding='utf-8') as sf:
            content = sf.read()

        # Escape backticks and ${ in template literal
        escaped = content.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')

        # Use quoted property name (handles hyphens etc.)
        key = json.dumps(sec_id)
        comma = ',' if i < len(section_ids) - 1 else ''
        f.write(f'    {key}: `{escaped}`{comma}\n')

    f.write('};\n')

print(f'Created {output_file}')
