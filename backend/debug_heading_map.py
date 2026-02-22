from oj_problem.views import _extract_zip_safely, _normalize_statement_text, _map_heading_to_section
import tempfile, zipfile
from pathlib import Path
z='/srv/server/substring_hoj.zip'
tmp=tempfile.mkdtemp(prefix='dbg_')
with zipfile.ZipFile(z,'r') as zf:
    _extract_zip_safely(zf, Path(tmp))
md=Path(tmp)/'1411'/'problem_zh.md'
s=md.read_text(encoding='utf-8')
norm=_normalize_statement_text(s)
print('--- headings and mapping ---')
import re
for line in norm.splitlines():
    m=re.match(r'^(#{1,6})\s*(.+?)\s*$', line.strip())
    if m:
        h=m.group(2)
        print(repr(h), '->', _map_heading_to_section(h))
