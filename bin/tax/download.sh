#!/bin/bash
source bucket-config.rc

docker run \
  -it \
  --rm \
  -v ${HOME}/Documents/tax:/app/data \
  -v ${PWD}/../../settings:/root/.aws \
  tool-s3-sync:v1.0.0 \
  download.sh $BUCKET_NAME $1
