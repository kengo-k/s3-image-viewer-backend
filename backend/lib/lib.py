#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
import os
from functools import cache
from typing import Callable, Literal, TypedDict

import boto3
from dotenv import load_dotenv

ActionKey = Literal["upload", "download", "delete_from_s3", "delete_from_local"]
Action = TypedDict("ActionDictType", {"action": ActionKey, "path": str})
FileInfo = dict[str, datetime.datetime]
CreateAction = Callable[[str, bool], Action]

load_dotenv()

DATA_DIR = os.getenv("DATA_DIR")
BUCKET_NAME = os.getenv("BUCKET_NAME")


@cache
def __get_s3_client():
    print("create client")
    client = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )
    return client


def get_s3_file_info(bucket_name: str, prefix: str) -> FileInfo:
    client = __get_s3_client()
    objects = client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    dict = {
        content["Key"]: content["LastModified"].replace(tzinfo=None)
        for content in objects["Contents"]
    }
    return dict


def get_local_file_info(prefix: str, dir: str) -> FileInfo:
    dict = {}
    for root, _, files in os.walk(top=prefix + dir):
        for file in files:
            file_path = os.path.join(root, file)
            stat = os.stat(file_path)
            dt = datetime.datetime.fromtimestamp(stat.st_mtime)
            dict[file_path[len(prefix) :]] = dt.replace(tzinfo=None)
    return dict


def sync_date(*, lo, s3):
    """
    localを基準に回しlocalの更新時刻をs3に更新時刻に合わせる
    """
    for lopath in lo:
        s3time = s3[lopath]
        os.utime(DATA_DIR + lopath, (s3time.timestamp(), s3time.timestamp()))


def sync_local_to_s3(*, src: FileInfo, dist: FileInfo, dry=True):
    def create_action(path: str, is_delete: bool) -> Action:
        if is_delete:
            return {"action": "delete_from_s3", "path": path}
        else:
            return {"action": "upload", "path": path}

    return __sync(create_action, src=src, dist=dist, dry=dry)


def sync_s3_to_local(*, src: FileInfo, dist: FileInfo, dry=True):
    def create_action(path: str, is_delete: bool) -> Action:
        if is_delete:
            return {"action": "delete_from_local", "path": path}
        else:
            return {"action": "download", "path": path}

    return __sync(create_action, src=src, dist=dist, dry=dry)


def __sync(create_action: CreateAction, *, src: FileInfo, dist: FileInfo, dry=True):
    """
    同期元(src)を基準として同期先(dist)へ同期を実行する
    - 1.同期先のファイルが同期元に存在しない場合同期先からファイルを削除する
    - 2.同期元のファイルが同期先に存在しない場合は新規追加として同期先へ送信する
    - 3.同期元のファイルが同期先にも存在する場合は同期元の更新時刻のほうが新しい場合のみ同期先へ送信する
    dry=Trueの場合は同期は実行せずに対象のリストを返す
    """

    def run_action(action: Action):
        a = action["action"]
        if a == "upload":
            pass
        elif a == "download":
            pass
        elif a == "delete_from_local":
            pass
        elif a == "delete_from_s3":
            pass

    for distpath in dist:
        if distpath not in src:
            # pattern 1
            action = create_action(distpath, True)
            yield action
            if not dry:
                run_action(action)
    for srcpath in src:
        if srcpath not in dist:
            # pattern 2
            action = create_action(srcpath, False)
            yield action
            if not dry:
                run_action(action)
        else:
            src_date = src[srcpath]
            dist_date = dist[srcpath]
            if src_date > dist_date:
                # pattern 3
                action = create_action(srcpath, False)
                yield action
                if not dry:
                    run_action(action)
