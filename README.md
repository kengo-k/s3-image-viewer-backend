# 1.事前設定

## 1-1.ディレクトリ設定

docker-compose.yml のディレクトリマウント設定で s3 にアップロードしたいファイルを配置したディレクトリを指定します

※マウント先は/opt/data から変更しないこと！

## 1-2.AWS の設定ファイルの配置

このファイルと同じ階層内に AWS の設定ファイル

- config
- credentials

を配置します。上記ファイルの内容については下記の通り

### config

```
[default]
region = ap-northeast-1
output = json
```

※本ファイルは特に変更の必要なし

### credentials

```
[default]
aws_access_key_id = AWSアクセスキーID
aws_secret_access_key = AWSシークレットアクセスキー
```

使用する AWS アカウントのキーを設定します。

※このファイルは絶対にコミットしないこと！

(上記 2 ファイルは.gitignore に登録済みです)

## 1-3.バケット名設定ファイルの修正

src/bucket-config.rc に記載されている

```
BUCKET_NAME
```

変数にバケット名を設定します

# 2.起動

## 2-1.イメージの作成

docker-compose build --no-cache

## 2-2.コンテナを起動

docker-compose up -d

## 2-3.コンテナへログイン

docker exec -it s3_uploader bash

# 3.実行

## 3-1.アップロード

src ディレクトリに移動し

```
./upload.sh
```

を実行すると/opt/data 以下にある全てのファイルを bucket-config.rc で指定した bucket に sync する。

引数を指定して

```
./upload.sh dir1
```

とした場合は/opt/data/dir1 以下にある全てのファイルを bucket-config.rc で指定した bucket 内の dir1 ディレクトリに sync する

## 3-2.ダウンロード

src ディレクトリに移動し

```
./download.sh
```

を実行すると bucket-config.rc で指定した bucket 内の全てのファイルを/opt/data ディレクトリに sync する。

引数を指定して

```
./download.sh dir1
```

とした場合は bucket-config.rc で指定した bucket 内の dir1 ディレクトリ内にある全てのファイルを/opt/data/dir1 ディレクトリに sync する
