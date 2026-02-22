import tempfile, zipfile, os
from pathlib import Path
from oj_problem.views import _extract_zip_safely, _normalize_statement_text, _extract_markdown_sections
z='/srv/server/substring_hoj.zip'
tmp=tempfile.mkdtemp(prefix='debug_')
print('tmp',tmp)
with zipfile.ZipFile(z,'r') as zf:
    _extract_zip_safely(zf, Path(tmp))
md=Path(tmp)/'1411'/'problem_zh.md'
s=md.read_text(encoding='utf-8')
print('\n'.join(s.splitlines()[:60]))
norm=_normalize_statement_text(s)
print('\n--- normalized ---\n')
print('\n'.join(norm.splitlines()[:60]))
sect=_extract_markdown_sections(norm)
print('\n--- sections ---\n')
import pprint
pprint.pprint(sect)
