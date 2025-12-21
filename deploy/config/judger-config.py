from pathlib import Path
import pwd
import grp
import os

PARALLEL_TESTS = int(os.getenv('PARALLEL_TESTS', 2))
PARALLEL_USERS = int(os.getenv('PARALLEL_USERS', 1))

BASE_DIR = Path('/judger').resolve()
DEBUG = False

RUN_USER_UID = pwd.getpwnam('code').pw_uid
RUN_GROUP_GID = grp.getgrnam('code').gr_gid

COMPILER_USER_UID = pwd.getpwnam('compiler').pw_uid
COMPILER_GROUP_GID = grp.getgrnam('compiler').gr_gid

SPJ_USER_UID = pwd.getpwnam('spj').pw_uid
SPJ_GROUP_GID = grp.getgrnam('spj').gr_gid

TEST_CASE_DIR = Path(os.getenv('TEST_CASE_DIR', '/srv/test_data')).resolve()
SPJ_DIR = Path(os.getenv('SPJ_DIR', '/srv/spj')).resolve()