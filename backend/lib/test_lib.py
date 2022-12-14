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

# import datetime
# import os
# import tempfile
# from pathlib import Path
#
# import lib.lib
# import pytest
#
# TMPDIR = ""
#
#
# @pytest.fixture(scope="module", autouse=True)
# def init_local_dir():
#     def mkfile(dir, name, y, m, d):
#         file_path = dir + "/" + name
#         dir_path = os.path.dirname(file_path)
#         os.makedirs(dir_path, exist_ok=True)
#         Path(file_path).touch()
#         d = datetime.datetime(y, m, d).replace(tzinfo=None).timestamp()
#         os.utime(file_path, (d, d))
#
#     global TMPDIR
#     TMPDIR = tempfile.mkdtemp()
#
#     mkfile(TMPDIR, "dir1/test1.txt", 2000, 1, 1)
#     mkfile(TMPDIR, "dir1/testA.txt", 2000, 1, 2)
#     mkfile(TMPDIR, "dir1/test3.txt", 2000, 1, 1)
#     mkfile(TMPDIR, "dir2/test2.txt", 2000, 1, 5)
#
#
# class MockClient:
#     def list_objects_v2(self, Bucket, Prefix):
#         dict = {
#             "Contents": [
#                 {
#                     "Key": "dir1/test1.txt",
#                     "LastModified": datetime.datetime(2000, 1, 1).replace(tzinfo=None),
#                 },
#                 {
#                     "Key": "dir1/test2.txt",
#                     "LastModified": datetime.datetime(2000, 1, 2).replace(tzinfo=None),
#                 },
#                 {
#                     "Key": "dir1/test3.txt",
#                     "LastModified": datetime.datetime(2000, 1, 3).replace(tzinfo=None),
#                 },
#                 {
#                     "Key": "dir2/test2.txt",
#                     "LastModified": datetime.datetime(2000, 1, 4).replace(tzinfo=None),
#                 },
#             ]
#         }
#         return dict
#
#
# def test_get_s3_file_info(mocker):
#     mocker.patch("lib.lib.__get_s3_client", return_value=MockClient())
#     s3 = lib.lib.get_s3_file_info("dummy_bucket", "dummy_prefix")
#     assert len(s3.keys()) == 4
#     table = {
#         "dir1/test1.txt": datetime.datetime(2000, 1, 1),
#         "dir1/test2.txt": datetime.datetime(2000, 1, 2),
#         "dir1/test3.txt": datetime.datetime(2000, 1, 3),
#         "dir2/test2.txt": datetime.datetime(2000, 1, 4),
#     }
#
#     for key in table:
#         assert key in s3
#         assert s3[key] == table[key]
#
#
# def test_get_local_file_info():
#     lo = lib.lib.get_local_file_info(TMPDIR + "/", "")
#     assert len(lo.keys()) == 4
#     table = {
#         "dir1/test1.txt": datetime.datetime(2000, 1, 1),
#         "dir1/testA.txt": datetime.datetime(2000, 1, 2),
#         "dir1/test3.txt": datetime.datetime(2000, 1, 1),
#         "dir2/test2.txt": datetime.datetime(2000, 1, 5),
#     }
#     for key in table:
#         assert key in lo
#         assert lo[key] == table[key]
#
#
# def test_sync_local_to_s3(mocker):
#     mocker.patch("lib.lib.__get_s3_client", return_value=MockClient())
#     src = lib.lib.get_local_file_info(TMPDIR + "/", "")
#     dist = lib.lib.get_s3_file_info("dummy_bucket", "dummy_prefix")
#
#     table = {
#         "dir2/test2.txt": {"action": "upload"},
#         "dir1/testA.txt": {"action": "upload"},
#         "dir1/test2.txt": {"action": "delete_from_s3"},
#     }
#
#     action_count = 0
#     gen = lib.lib.sync_local_to_s3(src=src, dist=dist, dry=True)
#     for action in gen:
#         action_count += 1
#         path = action["path"]
#         assert path in table
#         action["action"] == table[path]["action"]
#     assert action_count == 3
