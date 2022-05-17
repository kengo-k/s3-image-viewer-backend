# 1.事前設定

## 1-1.ディレクトリ設定

docker-compose.yml のディレクトリマウント設定で s3 にアップロードしたいファイルを配置したディレクトリを指定します

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

※このファイルはコミットは絶対にしないこと！

(上記 2 ファイルは.gitignore に登録済みです)

# 起動手順

## イメージの作成

docker-compose build --no-cache

## コンテナを起動

docker-compose up -d

## コンテナへログイン

docker exec -it s3_uploader bash
