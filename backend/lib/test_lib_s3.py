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
    def make_file(d, name):
        file_path = d + "/" + name
        dir_path = os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok=True)
        Path(file_path).touch()
        day = datetime.datetime.now().timestamp()
        os.utime(file_path, (day, day))

    global TMPDIR
    TMPDIR = tempfile.mkdtemp()

    make_file(TMPDIR, "dir1/test1.txt")
    make_file(TMPDIR, "dir1/test2.txt")
    make_file(TMPDIR, "dir1/subdir1/test3.txt")
    make_file(TMPDIR, "dir1/subdir1/test4.txt")
    make_file(TMPDIR, "dir1/subdir2/test5.txt")


@pytest.mark.aws
def test_upload_s3_from_local():
    local_file_info = lib.get_local_file_info(TMPDIR, "dir1")
    assert len(local_file_info) == 5

    local_file_paths = list(local_file_info.keys())
    local_file_paths.sort()
    want_local_file_paths = [
        "dir1/subdir1/test3.txt",
        "dir1/subdir1/test4.txt",
        "dir1/subdir2/test5.txt",
        "dir1/test1.txt",
        "dir1/test2.txt",
    ]
    for i in range(5):
        assert local_file_paths[i] == want_local_file_paths[i]

    action_list = lib.create_local_to_s3_actions(src=local_file_info, dist={})
    assert len(action_list) == 5

    lib.apply_actions(BUCKET_NAME, TMPDIR + "/", action_list)
    s3_file_info = lib.get_s3_file_info(BUCKET_NAME, "dir1")
    assert len(s3_file_info) == 5

    s3_file_paths = list(s3_file_info.keys())
    s3_file_paths.sort()
    for i in range(5):
        assert local_file_paths[i] == want_local_file_paths[i]

    print(s3_file_info)
