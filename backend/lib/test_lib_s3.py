import os
import tempfile
from datetime import datetime
from pathlib import Path

import pytest
from dotenv import load_dotenv

from lib import lib
from lib.const import JST

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
        day = datetime.now().astimezone(JST).timestamp()
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
    # before sync
    before_local_file_info = lib.get_local_file_info(TMPDIR, "dir1")
    before_s3_file_info = lib.get_s3_file_info(BUCKET_NAME, "dir1")
    before_actions = lib.create_local_to_s3_actions(src=before_local_file_info, dist=before_s3_file_info)
    assert len(before_actions) == 5

    # execute sync
    lib.sync_local_to_s3(TMPDIR, BUCKET_NAME, "dir1")

    # after sync
    local_file_info = lib.get_local_file_info(TMPDIR, "dir1")
    s3_file_info = lib.get_s3_file_info(BUCKET_NAME, "dir1")
    assert len(local_file_info) == 5
    assert len(s3_file_info) == 5

    local_file_paths = list(local_file_info.keys())
    local_file_paths.sort()

    s3_file_paths = list(s3_file_info.keys())
    s3_file_paths.sort()

    want_local_file_paths = [
        "dir1/subdir1/test3.txt",
        "dir1/subdir1/test4.txt",
        "dir1/subdir2/test5.txt",
        "dir1/test1.txt",
        "dir1/test2.txt",
    ]

    for i in range(5):
        assert local_file_paths[i] == want_local_file_paths[i]
        assert s3_file_paths[i] == want_local_file_paths[i]
        # check local and s3 timestamp is same
        assert local_file_info[local_file_paths[i]] == s3_file_info[s3_file_paths[i]]

    actions = lib.create_local_to_s3_actions(src=local_file_info, dist=s3_file_info)
    assert len(actions) == 0
