import zipfile
from pathlib import Path
from oj_problem.models import Problem

ZIP_PATH = '/srv/server/substring_hoj.zip'
TITLE = '子串简写(编程题)'

with zipfile.ZipFile(ZIP_PATH, 'r') as zf:
    # find the markdown file inside
    candidates = [n for n in zf.namelist() if n.endswith('problem_zh.md') or n.endswith('problem.md') or n.endswith('README.md')]
    if not candidates:
        print('no md found')
    else:
        mdname = candidates[0]
        raw = zf.read(mdname).decode('utf-8')
        # split at samples heading
        import re
        parts = re.split(r'(?m)^#{1,6}\s*(?:样例|示例|sample|example)\b', raw, maxsplit=1)
        desc = parts[0].strip() if parts else raw.strip()

        # normalize: remove code fences and input/output tags
        desc = re.sub(r'```[\s\S]*?```', '', desc)
        desc = re.sub(r'<\s*input[^>]*>.*?<\s*/\s*input\s*>', '', desc, flags=re.IGNORECASE | re.DOTALL)
        desc = re.sub(r'<\s*output[^>]*>.*?<\s*/\s*output\s*>', '', desc, flags=re.IGNORECASE | re.DOTALL)
        desc = desc.strip()

        # update DB
        qs = Problem.objects.filter(title=TITLE)
        for p in qs:
            print('updating problem', p.id)
            p.description = desc
            p.save(update_fields=['description'])
        print('done')
