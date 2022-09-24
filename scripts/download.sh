#!/bin/bash
#
# 設定ファイルbucket-config.rcで指定したbukectの内容をローカルにsyncする
# ※bucket内の任意のサブディレクトリを指定可能
#
# ・引数を指定しない場合はbucket内の全データを/app/data直下に
# ・引数を指定した場合はbucket内の指定したサブディレクトリを/app/data下の同名ディレクトリに
# 配置する

#TARGET_DIR=$1
#aws s3 sync --exact-timestamps --delete s3://$BUCKET_NAME/$TARGET_DIR /opt/data/$TARGET_DIR

echo ">download s3..."
echo "BUCKET_NAME=$1"
echo "TARGET_DIR=$2"

BUCKET_NAME=$1
TARGET_DIR=$2
aws s3 sync --exact-timestamps --delete s3://$BUCKET_NAME/$TARGET_DIR /app/data/$TARGET_DIR
