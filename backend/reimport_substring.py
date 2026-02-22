import zipfile
import tempfile
import json
import shutil
from pathlib import Path
from oj_problem.views import _extract_zip_safely, _find_problem_roots, _import_hydro_problem_root
from oj_problem.models import Problem

ZIP_PATH = '/srv/server/substring_hoj.zip'
TITLE = '子串简写(编程题)'

# Delete existing problems with same title
for p in Problem.objects.filter(title=TITLE):
    print('Deleting existing problem', p.id)
    try:
        test_case = getattr(p, 'test_case', None)
        if test_case:
            data_dir = Path('/data/judge_data/test_data') / str(test_case.test_case_id)
            if data_dir.exists():
                shutil.rmtree(data_dir, ignore_errors=True)
        p.delete()
    except Exception as e:
        print('Error deleting', e)

# Extract and import
tmp = tempfile.mkdtemp(prefix='hojreimport_')
print('tmp', tmp)
with zipfile.ZipFile(ZIP_PATH, 'r') as zf:
    _extract_zip_safely(zf, Path(tmp))

roots = _find_problem_roots(Path(tmp))
print('roots found:', roots)
for r in roots:
    try:
        res = _import_hydro_problem_root(r)
        print('imported:', res)
    except Exception as e:
        print('import failed for', r, e)

print('done')
