#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from datetime import datetime
from functools import cache
from typing import List

import boto3
from dotenv import load_dotenv

from lib.const import JST
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
        content["Key"]: content["LastModified"].replace(tzinfo=JST)
        for content in objects["Contents"]
    }
    return file_info


def get_local_file_info(dir_path: str, suffix: str) -> TFileInfoDict:
    file_info: TFileInfoDict = {}
    for root, _, files in os.walk(top=dir_path + "/" + suffix):
        for file in files:
            file_path = os.path.join(root, file)
            stat = os.stat(file_path)
            dt = datetime.fromtimestamp(stat.st_mtime)
            file_info[file_path[len(dir_path) + 1:]] = dt.replace(tzinfo=JST)
    return file_info


def sync_local_to_s3(dir_path: str, bucket_name: str, key: str) -> None:
    local_file_info = get_local_file_info(dir_path, key)
    s3_file_info = get_s3_file_info(bucket_name, key)
    actions = create_local_to_s3_actions(src=local_file_info, dist=s3_file_info)
    apply_actions(bucket_name, dir_path, actions)

    # refetch from s3
    s3_file_info = get_s3_file_info(bucket_name, key)
    # apply s3 timestamp to local
    for local_file_path in local_file_info:
        full_path = dir_path + "/" + local_file_path
        s3_timestamp = s3_file_info[local_file_path]
        os.utime(full_path, (s3_timestamp.timestamp(), s3_timestamp.timestamp()))


def create_local_to_s3_actions(*, src: TFileInfoDict, dist: TFileInfoDict) -> List[TActionDict]:
    def create_action(path: str, is_delete: bool) -> TActionDict:
        if is_delete:
            return {"action": "delete_from_s3", "path": path}
        else:
            return {"action": "upload", "path": path}

    return __create_actions(create_action, src=src, dist=dist)


def create_s3_to_local_actions(*, src: TFileInfoDict, dist: TFileInfoDict) -> List[TActionDict]:
    def create_action(path: str, is_delete: bool) -> TActionDict:
        if is_delete:
            return {"action": "delete_from_local", "path": path}
        else:
            return {"action": "download", "path": path}

    return __create_actions(create_action, src=src, dist=dist)


def apply_actions(bucket_name: str, prefix: str, action_list: List[TActionDict]) -> None:
    client = __get_s3_client()
    for a in action_list:
        path = a["path"]
        action = a["action"]
        if action == "upload":
            key = path
            fullpath = prefix + "/" + path
            client.upload_file(fullpath, bucket_name, key)


def __create_actions(create_action: TCreateAction, *, src: TFileInfoDict, dist: TFileInfoDict) -> List[TActionDict]:
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
