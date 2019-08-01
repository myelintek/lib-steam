FROM ubuntu:18.04

ENV SHELL /bin/bash
ENV DEBIAN_FRONTEND noninteractive
ENV HOME /workspace
ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

RUN sed -i 's/archive.ubuntu.com/tw.archive.ubuntu.com/g' /etc/apt/sources.list && \
    apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    python3 \
    python3-pip \
    python3-setuptools \
    vim \
    wget \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN pip3 install wheel \
                 pytest \
                 pexpect

COPY . /build/
# build & install mlsteam_cli
RUN cd /build && \
    python3 setup.py bdist_wheel && \
    pip3 install dist/mlsteam-*

COPY tests /workspace/tests
COPY example /workspace/example
WORKDIR /workspace
