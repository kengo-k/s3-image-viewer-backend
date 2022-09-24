#!/bin/bash
#
# /app/dataディレクトリ内のファイルを
# 設定ファイルbucket-config.rcで指定したbukectにsyncする
#
# ・引数を指定しない場合は/apt/data全体をbucket直下に
# ・引数を指定した場合は/apt/data内の指定したサブディレクトリをbucketの同名ディレクトリに
# 配置する

echo ">upload s3..."
echo ">BUCKET_NAME=$1"
echo ">TARGET_DIR=$2"

BUCKET_NAME=$1
TARGET_DIR=$2
aws s3 sync --exact-timestamps --delete --exclude ".DS_Store" /app/data/$TARGET_DIR s3://$BUCKET_NAME/$TARGET_DIR
