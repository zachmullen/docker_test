FROM ubuntu:14.04
MAINTAINER Zach Mullen <zach.mullen@kitware.com>

RUN mkdir /test
COPY test.sh /test/test.sh

ENTRYPOINT ["bash", "/test/test.sh"]
