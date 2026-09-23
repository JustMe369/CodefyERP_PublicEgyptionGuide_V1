import re
import os

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

sections = ['login', 'bulk-import', 'relationships', 'assignments', 'pricing', 'readiness']
for sec_id in sections:
    pattern = r'(<section id="' + sec_id + r'"[\s\S]*?</section>\s*)'
    match = re.search(pattern, content)
    if match:
        section_html = match.group(1).strip()
        with open(f'sections/{sec_id}.html', 'w', encoding='utf-8') as f:
            f.write(section_html)
        print(f'Created sections/{sec_id}.html ({len(section_html)} bytes)')
    else:
        print(f'WARNING: Could not find section {sec_id}')
