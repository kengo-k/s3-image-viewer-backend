#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

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
    {"key": content["Key"], "last_modified": content["LastModified"]}
    for content in objects["Contents"]
]
for info in file_info_list:
    print(info["key"], info["last_modified"])
