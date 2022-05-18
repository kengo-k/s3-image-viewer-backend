#!/bin/bash
#
# /opt/dataディレクトリ内のファイルを
# 設定ファイルbucket-config.rcで指定したbukectにsyncする
#
# ・引数を指定しない場合は/opt/data全体をbucket直下に
# ・引数を指定した場合は/opt/data内の指定したサブディレクトリをbucketの同名ディレクトリに
# 配置する
source bucket-config.rc
TARGET_DIR=$1
aws s3 sync --exact-timestamps --delete /opt/data/$TARGET_DIR s3://$BUCKET_NAME/$TARGET_DIR
