FROM ubuntu:14.04
MAINTAINER Zach Mullen <zach.mullen@kitware.com>

RUN mkdir /test
COPY test.sh /test/test.sh
COPY test.py /test/test.py

RUN apt-get update && apt-get install -qy software-properties-common python-software-properties && \
  apt-get update && apt-get install -qy \
    build-essential \
    libffi-dev \
    libpython-dev

ENTRYPOINT ["python", "/test/test.py"]
