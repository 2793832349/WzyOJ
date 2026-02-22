import zipfile
import tempfile
import traceback
from pathlib import Path
from oj_problem.views import _extract_zip_safely, _find_problem_roots, _import_hydro_problem_root

z = '/srv/server/substring_hoj.zip'
try:
    tmp = tempfile.mkdtemp(prefix='hojtest_')
    print('tmp', tmp)
    with zipfile.ZipFile(z, 'r') as zf:
        _extract_zip_safely(zf, Path(tmp))
    roots = _find_problem_roots(Path(tmp))
    print('roots:', roots)
    for r in roots:
        try:
            res = _import_hydro_problem_root(r)
            print('imported:', res)
        except Exception:
            print('import error for', r)
            traceback.print_exc()
except Exception:
    traceback.print_exc()
