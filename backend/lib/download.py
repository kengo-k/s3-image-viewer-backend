#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import os
import pathlib

import boto3
from dotenv import load_dotenv

load_dotenv()

BUCKET_NAME = os.getenv("BUCKET_NAME")
client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
)


def get_s3_file_info(bucket_name, prefix):
    objects = client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    dict = {
        content["Key"]: content["LastModified"].replace(tzinfo=None)
        for content in objects["Contents"]
    }
    return dict


def get_local_file_info(prefix, dir):
    dict = {}
    for root, dirs, files in os.walk(top=prefix + dir):
        for file in files:
            file_path = os.path.join(root, file)
            stat = os.stat(file_path)
            dt = datetime.datetime.fromtimestamp(stat.st_mtime)
            dict[file_path[len(prefix) :]] = dt.replace(tzinfo=None)
    return dict


def get_download_list(local_file_info, s3_file_info):
    """
    s3を基準に回し
    - s3に存在するがlocalに存在しない
    - s3にもlocalにも存在するがs3のほうが更新時刻が新しい
    ファイルの一覧をダウンロード対象のファイルと判断する
    """
    dlist = []
    for s3path in s3_file_info:
        if s3path not in local_file_info:
            dlist.append(s3path)
        s3date = s3_file_info[s3path]
        lodate = local_file_info[s3path]
        if s3date > lodate:
            dlist.append(s3path)
    return dlist


def get_upload_list(local_file_info, s3_file_info):
    """
    localを基準に回し
    - localに存在するがs3に存在しない
    - localにもs3にも存在するがlocalのほうが更新時刻が新しい
    ファイルの一覧をアップロード対象のファイルと判断する
    """
    pass


s3 = get_s3_file_info(BUCKET_NAME, "R4-2022/04")
lo = get_local_file_info("../images/", "R4-2022/04")

dl = get_download_list(lo, s3)
