FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive
COPY config /tmp/config
COPY credentials /tmp/credentials
RUN \
  apt-get update \
    && apt-get -y install awscli \
    && mkdir ~/.aws \
    && mv /tmp/config ~/.aws \
    && mv /tmp/credentials ~/.aws
