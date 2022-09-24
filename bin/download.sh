#!/bin/bash
#
# 設定ファイルbucket-config.rcで指定したbukectの内容をローカルにsyncする
# ※bucket内の任意のサブディレクトリを指定可能
#
# ・引数を指定しない場合はbucket内の全データを/opt/data直下に
# ・引数を指定した場合はbucket内の指定したサブディレクトリを/opt/data下の同名ディレクトリに
# 配置する
source bucket-config.rc
TARGET_DIR=$1
aws s3 sync --exact-timestamps --delete s3://$BUCKET_NAME/$TARGET_DIR /opt/data/$TARGET_DIR
