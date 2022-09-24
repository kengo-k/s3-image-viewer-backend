#!/bin/bash
# デバッグ用

docker run \
  -it \
  --rm \
  -v ${HOME}/Documents/tax:/app/data \
  -v ${PWD}/../../settings:/root/.aws \
  tool-s3-sync:v1.0.0
