import datetime
import os
import tempfile
from pathlib import Path

import pytest
from dotenv import load_dotenv

from lib import lib

load_dotenv()

DATA_DIR = os.getenv("DATA_DIR")
BUCKET_NAME = os.getenv("BUCKET_NAME")

TMPDIR = ""


@pytest.fixture(scope="module", autouse=True)
def init_local_dir():
    def make_file(d, name, year, month, day):
        file_path = d + "/" + name
        dir_path = os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok=True)
        Path(file_path).touch()
        day = datetime.datetime(year, month, day).replace(tzinfo=None).timestamp()
        os.utime(file_path, (day, day))

    global TMPDIR
    TMPDIR = tempfile.mkdtemp()

    make_file(TMPDIR, "dir1/test1.txt", 2000, 1, 1)
    make_file(TMPDIR, "dir1/test2.txt", 2000, 1, 1)
    make_file(TMPDIR, "dir1/subdir1/test3.txt", 2000, 1, 1)
    make_file(TMPDIR, "dir1/subdir1/test4.txt", 2000, 1, 1)
    make_file(TMPDIR, "dir1/subdir2/test5.txt", 2000, 1, 1)


def test_get_s3_file_info():
    s3_file_info = lib.get_s3_file_info(BUCKET_NAME, "")
    local_file_info = lib.get_local_file_info(TMPDIR + "/dir1/")
    action_list = lib.sync_local_to_s3(src=local_file_info, dist=s3_file_info)
    assert 5 == len(action_list)
    lib.apply_actions(BUCKET_NAME, TMPDIR + "/", action_list)
