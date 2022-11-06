#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import os
import pathlib

import boto3
from dotenv import load_dotenv

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
BUCKET_NAME = os.getenv("BUCKET_NAME")

client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)

objects = client.list_objects_v2(Bucket=BUCKET_NAME, Prefix="R4-2022")
file_info_list = [
    {"path": content["Key"], "last_modified": content["LastModified"]}
    for content in objects["Contents"]
]

local_file_dict = {}
for root, dirs, files in os.walk(top="../images"):
    for file in files:
        file_path = os.path.join(root, file)
        stat = os.stat(file_path)
        dt = datetime.datetime.fromtimestamp(stat.st_mtime)
        local_file_dict[file_path] = dt

for f in file_info_list:
    path = f["path"]
    last_modified = f["last_modified"]
    nestedDir = os.path.dirname(path)
    pathlib.Path("../images/" + nestedDir).mkdir(parents=True, exist_ok=True)
    client.download_file(BUCKET_NAME, path, "../images/" + path)
