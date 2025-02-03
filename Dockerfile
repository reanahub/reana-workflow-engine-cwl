# This file is part of REANA.
# Copyright (C) 2018, 2019, 2020, 2021, 2022, 2023, 2024 CERN.
#
# REANA is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

# Use Ubuntu LTS base image
FROM docker.io/library/ubuntu:24.04

# Use default answers in installation commands
ENV DEBIAN_FRONTEND=noninteractive

# Allow pip to install packages in the system site-packages dir
ENV PIP_BREAK_SYSTEM_PACKAGES=true

# Prepare list of Python dependencies
COPY requirements.txt /code/

# Install all system and Python dependencies in one go
# hadolint ignore=DL3008,DL3013
RUN apt-get update -y && \
    apt-get install --no-install-recommends -y \
      gcc \
      nodejs \
      python3.12 \
      python3.12-dev \
      python3-pip \
      vim-tiny && \
    pip install --no-cache-dir --upgrade setuptools && \
    pip install --no-cache-dir -r /code/requirements.txt && \
    apt-get remove -y \
      gcc \
      python3.12-dev && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy cluster component source code
WORKDIR /code
COPY . /code

# Are we debugging?
ARG DEBUG=0
RUN if [ "${DEBUG}" -gt 0 ]; then pip install --no-cache-dir -e ".[debug]"; else pip install --no-cache-dir .; fi;

# Are we building with locally-checked-out shared modules?
# hadolint ignore=DL3013
RUN if test -e modules/reana-commons; then \
      if [ "${DEBUG}" -gt 0 ]; then \
        pip install --no-cache-dir -e "modules/reana-commons[cwl]" --upgrade; \
      else \
        pip install --no-cache-dir "modules/reana-commons[cwl]" --upgrade; \
      fi \
    fi

# Check for any broken Python dependencies
RUN pip check

# Set useful environment variables
ENV PYTHONPATH=/workdir \
    TERM=xterm

# Set image labels
LABEL org.opencontainers.image.authors="team@reanahub.io"
LABEL org.opencontainers.image.created="2024-03-04"
LABEL org.opencontainers.image.description="REANA reproducible analysis platform - CWL workflow engine component"
LABEL org.opencontainers.image.documentation="https://reana-workflow-engine-cwl.readthedocs.io/"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.source="https://github.com/reanahub/reana-workflow-engine-cwl"
LABEL org.opencontainers.image.title="reana-workflow-engine-cwl"
LABEL org.opencontainers.image.url="https://github.com/reanahub/reana-workflow-engine-cwl"
LABEL org.opencontainers.image.vendor="reanahub"
# x-release-please-start-version
LABEL org.opencontainers.image.version="0.95.0-alpha.2"
# x-release-please-end
