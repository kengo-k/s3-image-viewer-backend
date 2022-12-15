import datetime
import os
import tempfile
from pathlib import Path
from typing import Callable, List

import pytest

from lib import lib
from lib.types import TFileInfoDict

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


class MockClient:
    def list_objects_v2(self, Bucket, Prefix):
        dict = {
            "Contents": [
                {
                    "Key": "dir1/test1.txt",
                    "LastModified": datetime.datetime(2000, 1, 1).replace(tzinfo=None),
                },
                {
                    "Key": "dir1/test2.txt",
                    "LastModified": datetime.datetime(2000, 1, 2).replace(tzinfo=None),
                },
                {
                    "Key": "dir1/test3.txt",
                    "LastModified": datetime.datetime(2000, 1, 3).replace(tzinfo=None),
                },
                {
                    "Key": "dir2/test2.txt",
                    "LastModified": datetime.datetime(2000, 1, 4).replace(tzinfo=None),
                },
            ]
        }
        return dict


def test_get_local_file_info():
    class Arg:
        root: str

        def __init__(self, root: str):
            self.root = root

    class TestParam:
        arg: Arg
        predicates: List[Callable[[TFileInfoDict], bool]]

        def __init__(self, arg: Arg, *predicates: Callable[[TFileInfoDict], bool]):
            self.arg = arg
            self.predicates = predicates

    def is_len(expected_len: int) -> Callable[[TFileInfoDict], None]:
        def f(file_info: TFileInfoDict):
            assert len(file_info) == expected_len

        return f

    ts: List[TestParam] = [
        TestParam(Arg(TMPDIR + "/dir1/"), is_len(5))
    ]

    for t in ts:
        got = lib.get_local_file_info(t.arg.root)
        for pred in t.predicates:
            pred(got)


def test_get_s3_file_info(mocker):
    mocker.patch("lib.lib.__get_s3_client", return_value=MockClient())
    s3 = lib.get_s3_file_info("dummy_bucket", "dummy_prefix")
    assert len(s3.keys()) == 4
    table = {
        "dir1/test1.txt": datetime.datetime(2000, 1, 1),
        "dir1/test2.txt": datetime.datetime(2000, 1, 2),
        "dir1/test3.txt": datetime.datetime(2000, 1, 3),
        "dir2/test2.txt": datetime.datetime(2000, 1, 4),
    }

    for key in table:
        assert key in s3
        assert s3[key] == table[key]


def test_sync_local_to_s3():
    src: TFileInfoDict = {
        "newfile.txt": datetime.datetime(2000, 1, 1),
        "upload.txt": datetime.datetime(2001, 1, 1),
        "no_upload.txt": datetime.datetime(2000, 1, 1),
    }
    dist: TFileInfoDict = {
        "upload.txt": datetime.datetime(2000, 1, 1),
        "no_upload.txt": datetime.datetime(2000, 1, 1),
        "delete.txt": datetime.datetime(2000, 1, 1)
    }
    actions = lib.sync_local_to_s3(src=src, dist=dist)
    assert len(actions) == 3
    want = {
        "newfile.txt": "upload",
        "upload.txt": "upload",
        "delete.txt": "delete_from_s3"
    }
    for a in actions:
        assert a["action"] == want[a["path"]]


def test_sync_s3_to_local():
    src: TFileInfoDict = {
        "newfile.txt": datetime.datetime(2000, 1, 1),
        "download.txt": datetime.datetime(2001, 1, 1),
        "no_download.txt": datetime.datetime(2000, 1, 1),
    }
    dist: TFileInfoDict = {
        "download.txt": datetime.datetime(2000, 1, 1),
        "no_download.txt": datetime.datetime(2000, 1, 1),
        "delete.txt": datetime.datetime(2000, 1, 1)
    }
    actions = lib.sync_s3_to_local(src=src, dist=dist)
    assert len(actions) == 3
    want = {
        "newfile.txt": "download",
        "download.txt": "download",
        "delete.txt": "delete_from_local"
    }
    for a in actions:
        assert a["action"] == want[a["path"]]
