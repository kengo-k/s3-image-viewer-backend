import os
import shutil
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


def make_file(d, name):
    file_path = d + "/" + name
    dir_path = os.path.dirname(file_path)
    os.makedirs(dir_path, exist_ok=True)
    Path(file_path).touch()
    day = datetime.now().astimezone(JST).timestamp()
    os.utime(file_path, (day, day))


@pytest.fixture(scope="module", autouse=True)
def init_local_dir():

    global TMPDIR
    TMPDIR = tempfile.mkdtemp()

    make_file(TMPDIR, "dir1/test1.txt")
    make_file(TMPDIR, "dir1/test2.txt")
    make_file(TMPDIR, "dir1/subdir1/test3.txt")
    make_file(TMPDIR, "dir1/subdir1/test4.txt")
    make_file(TMPDIR, "dir1/subdir2/test5.txt")

    make_file(TMPDIR, "dir2/test1.txt")
    make_file(TMPDIR, "dir2/test2.txt")
    make_file(TMPDIR, "dir2/subdir1/test3.txt")
    make_file(TMPDIR, "dir2/subdir1/test4.txt")
    make_file(TMPDIR, "dir2/subdir2/test5.txt")


@pytest.mark.aws
def test_sync_local_to_s3():
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


@pytest.mark.aws
def test_sync_s3_from_local():
    s3_file_info = lib.get_s3_file_info(BUCKET_NAME, "dir2")
    remove_actions = lib.create_local_to_s3_actions(src={}, dist=s3_file_info)
    lib.apply_actions(BUCKET_NAME, "dir2", remove_actions)

    lib.sync_local_to_s3(TMPDIR, BUCKET_NAME, "dir2")
    local_file_info = lib.get_local_file_info(TMPDIR, "dir2")
    s3_file_info = lib.get_s3_file_info(BUCKET_NAME, "dir2")
    assert len(local_file_info) == 5
    assert len(s3_file_info) == 5

    make_file(TMPDIR, "dir2/test6.txt")
    local_file_info = lib.get_local_file_info(TMPDIR, "dir2")
    s3_file_info = lib.get_s3_file_info(BUCKET_NAME, "dir2")
    assert len(local_file_info) == 6

    actions = lib.create_s3_to_local_actions(src=s3_file_info, dist=local_file_info)
    assert len(actions) == 1
    lib.sync_s3_to_local(TMPDIR, BUCKET_NAME, "dir2")

    local_file_info = lib.get_local_file_info(TMPDIR, "dir2")
    assert len(local_file_info) == 5

    shutil.rmtree(TMPDIR + "/dir2")
    os.makedirs(TMPDIR + "/dir2")
    local_file_info = lib.get_local_file_info(TMPDIR, "dir2")
    s3_file_info = lib.get_s3_file_info(BUCKET_NAME, "dir2")
    assert len(local_file_info) == 0
    assert len(s3_file_info) == 5
    actions = lib.create_s3_to_local_actions(src=s3_file_info, dist=local_file_info)
    assert len(actions) == 5

    lib.sync_s3_to_local(TMPDIR, BUCKET_NAME, "dir2")
    s3_file_info = lib.get_s3_file_info(BUCKET_NAME, "dir2")
    local_file_info = lib.get_local_file_info(TMPDIR, "dir2")
    assert len(s3_file_info) == 5
    assert len(local_file_info) == 5

    local_file_paths = list(local_file_info.keys())
    local_file_paths.sort()

    s3_file_paths = list(s3_file_info.keys())
    s3_file_paths.sort()

    want_local_file_paths = [
        "dir2/subdir1/test3.txt",
        "dir2/subdir1/test4.txt",
        "dir2/subdir2/test5.txt",
        "dir2/test1.txt",
        "dir2/test2.txt",
    ]

    for i in range(5):
        assert local_file_paths[i] == want_local_file_paths[i]
        assert s3_file_paths[i] == want_local_file_paths[i]
        # check local and s3 timestamp is same
        assert local_file_info[local_file_paths[i]] == s3_file_info[s3_file_paths[i]]
