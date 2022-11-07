import datetime

import lib.lib


class MockClient:
    def list_objects_v2(self, Bucket, Prefix):
        dict = {
            "Contents": [
                {
                    "Key": "dir1/test1.txt",
                    "LastModified": datetime.datetime(2000, 1, 1),
                },
                {
                    "Key": "dir1/test2.txt",
                    "LastModified": datetime.datetime(2000, 1, 2),
                },
                {
                    "Key": "dir2/test1.txt",
                    "LastModified": datetime.datetime(2010, 12, 31),
                },
            ]
        }
        return dict


def test_get_s3_file_info(mocker):
    mocker.patch("lib.lib.__get_s3_client", return_value=MockClient())
    s3 = lib.lib.get_s3_file_info("dummy_bucket", "dummy_prefix")
    assert len(s3.keys()) == 3
    table = {
        "dir1/test1.txt": datetime.datetime(2000, 1, 1),
        "dir1/test2.txt": datetime.datetime(2000, 1, 2),
        "dir2/test1.txt": datetime.datetime(2010, 12, 31),
    }

    for key in table:
        assert key in s3
        assert s3[key] == table[key]
