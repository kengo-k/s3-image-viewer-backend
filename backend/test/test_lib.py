import datetime
import os
import tempfile
from pathlib import Path

import lib.lib
import pytest

TMPDIR = ""


@pytest.fixture(scope="module", autouse=True)
def init_local_dir():
    def mkfile(dir, name, y, m, d):
        file_path = dir + "/" + name
        dir_path = os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok=True)
        Path(file_path).touch()
        d = datetime.datetime(y, m, d).replace(tzinfo=None).timestamp()
        os.utime(file_path, (d, d))

    global TMPDIR
    TMPDIR = tempfile.mkdtemp()

    mkfile(TMPDIR, "dir1/test1.txt", 2000, 1, 1)
    mkfile(TMPDIR, "dir1/testA.txt", 2000, 1, 2)
    mkfile(TMPDIR, "dir1/test3.txt", 2000, 1, 1)
    mkfile(TMPDIR, "dir2/test2.txt", 2000, 1, 5)


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


def test_get_s3_file_info(mocker):
    mocker.patch("lib.lib.__get_s3_client", return_value=MockClient())
    s3 = lib.lib.get_s3_file_info("dummy_bucket", "dummy_prefix")
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


def test_get_local_file_info():
    lo = lib.lib.get_local_file_info(TMPDIR + "/", "")
    assert len(lo.keys()) == 4
    table = {
        "dir1/test1.txt": datetime.datetime(2000, 1, 1),
        "dir1/testA.txt": datetime.datetime(2000, 1, 2),
        "dir1/test3.txt": datetime.datetime(2000, 1, 1),
        "dir2/test2.txt": datetime.datetime(2000, 1, 5),
    }
    for key in table:
        assert key in lo
        assert lo[key] == table[key]


def test_get_download_list(mocker):
    mocker.patch("lib.lib.__get_s3_client", return_value=MockClient())
    s3 = lib.lib.get_s3_file_info("dummy_bucket", "dummy_prefix")
    lo = lib.lib.get_local_file_info(TMPDIR + "/", "")
    d = lib.lib.get_download_list(lo=lo, s3=s3)
    assert len(d) == 2
    table = ["dir1/test2.txt", "dir1/test3.txt"]
    for t in table:
        assert t in d


def test_get_upload_list(mocker):
    mocker.patch("lib.lib.__get_s3_client", return_value=MockClient())
    s3 = lib.lib.get_s3_file_info("dummy_bucket", "dummy_prefix")
    lo = lib.lib.get_local_file_info(TMPDIR + "/", "")
    u = lib.lib.get_upload_list(lo=lo, s3=s3)
    assert len(u) == 2
    table = ["dir1/testA.txt", "dir2/test2.txt"]
    for t in table:
        assert t in u
