#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
import os
from functools import cache
from typing import List

import boto3
from dotenv import load_dotenv

from lib.types import TActionDict, TCreateAction, TFileInfoDict

load_dotenv()

DATA_DIR = os.getenv("DATA_DIR")
BUCKET_NAME = os.getenv("BUCKET_NAME")


@cache
def __get_s3_client():
    client = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )
    return client


def get_s3_file_info(bucket_name: str, prefix: str) -> TFileInfoDict:
    client = __get_s3_client()
    objects = client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    if "Contents" not in objects:
        return {}
    file_info: TFileInfoDict = {
        content["Key"]: content["LastModified"].replace(tzinfo=None)
        for content in objects["Contents"]
    }
    return file_info


def get_local_file_info(prefix: str) -> TFileInfoDict:
    file_info: TFileInfoDict = {}
    for root, _, files in os.walk(top=prefix):
        for file in files:
            file_path = os.path.join(root, file)
            stat = os.stat(file_path)
            dt = datetime.datetime.fromtimestamp(stat.st_mtime)
            file_info[file_path[len(prefix):]] = dt.replace(tzinfo=None)
    return file_info


def sync_date(*, lo, s3):
    """
    localを基準に回しlocalの更新時刻をs3に更新時刻に合わせる
    """
    for lopath in lo:
        s3time = s3[lopath]
        os.utime(DATA_DIR + lopath, (s3time.timestamp(), s3time.timestamp()))


def sync_local_to_s3(*, src: TFileInfoDict, dist: TFileInfoDict, dry=True):
    def create_action(path: str, is_delete: bool) -> TActionDict:
        if is_delete:
            return {"action": "delete_from_s3", "path": path}
        else:
            return {"action": "upload", "path": path}

    return __sync(create_action, src=src, dist=dist)


def sync_s3_to_local(*, src: TFileInfoDict, dist: TFileInfoDict, dry=True):
    def create_action(path: str, is_delete: bool) -> TActionDict:
        if is_delete:
            return {"action": "delete_from_local", "path": path}
        else:
            return {"action": "download", "path": path}

    return __sync(create_action, src=src, dist=dist)


def apply_actions(bucket_name: str, action_list: List[TActionDict]) -> None:
    client = __get_s3_client()
    for a in action_list:
        path = a["path"]
        action = a["action"]
        if action == "upload":
            print("path:" + path)
            # client.upload_file(path, bucket_name, )


def __sync(create_action: TCreateAction, *, src: TFileInfoDict, dist: TFileInfoDict) -> List[TActionDict]:
    """
    同期元(src)を基準として同期先(dist)へ同期を実行する
    - 1.同期先のファイルが同期元に存在しない場合同期先からファイルを削除する
    - 2.同期元のファイルが同期先に存在しない場合は新規追加として同期先へ送信する
    - 3.同期元のファイルが同期先にも存在する場合は同期元の更新時刻のほうが新しい場合のみ同期先へ送信する
    dry=Trueの場合は同期は実行せずに対象のリストを返す
    """

    actions: List[TActionDict] = []
    for dist_path in dist:
        if dist_path not in src:
            # pattern 1
            action = create_action(dist_path, True)
            actions.append(action)

    for src_path in src:
        if src_path not in dist:
            # pattern 2
            action = create_action(src_path, False)
            actions.append(action)
        else:
            src_date = src[src_path]
            dist_date = dist[src_path]
            if src_date > dist_date:
                # pattern 3
                action = create_action(src_path, False)
                actions.append(action)

    return actions
