#!/bin/bash
#
# /opt/dataディレクトリ内のファイルを
# 設定ファイルbucket-config.rcで指定したbukectにsyncする
#
# ・引数を指定しないしない場合はbucket直下に
# ・引数を指定した場合はbucket内のサブディレクトリに
# 配置する
source bucket-config.rc
TARGET_DIR=$1
aws s3 sync --exact-timestamps --delete /opt/data s3://$BUCKET_NAME/$TARGET_DIR
