#!/bin/bash
#
# 設定ファイルbucket-config.rcで指定したbukectの内容をローカルにsyncする
# ※bucket内の任意のサブディレクトリを指定可能
#
# ・1番目の引数: ダウンロード先のディレクトリのパス
# ・2番目の引数: bucketのサブディレクトリ
# を指定する。
#
# 2番目の引数を指定しない場合はbucket内のデータを全てsyncする
# ※引数を指定する順番に注意
source bucket-config.rc
TO_DIR=$1
FROM_DIR=$2
aws s3 sync --exact-timestamps --delete s3://$BUCKET_NAME/$FROM_DIR $TO_DIR
