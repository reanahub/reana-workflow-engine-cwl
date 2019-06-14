# This file is part of REANA.
# Copyright (C) 2017, 2018, 2019 CERN.
#
# REANA is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

FROM python:2.7-slim

ENV TERM=xterm
RUN apt update && \
    apt install -y \
      gcc \
      nodejs \
      vim-tiny && \
    pip install --upgrade pip

COPY CHANGES.rst README.rst setup.py /code/
COPY reana_workflow_engine_cwl/version.py /code/reana_workflow_engine_cwl/
WORKDIR /code
RUN pip install requirements-builder && \
    requirements-builder -e all -l pypi setup.py | pip install -r /dev/stdin && \
    pip uninstall -y requirements-builder

COPY . /code

# Debug off by default
ARG DEBUG=false
RUN if [ "${DEBUG}" = "true" ]; then pip install -r requirements-dev.txt; pip install -e .; else pip install .; fi;

# Building with locally-checked-out shared modules?
RUN if test -e modules/reana-commons; then pip install modules/reana-commons --upgrade; fi

ARG QUEUE_ENV=default
ENV QUEUE_ENV ${QUEUE_ENV}
ARG CELERY_CONCURRENCY=2
ENV CELERY_CONCURRENCY ${CELERY_CONCURRENCY}
ENV PYTHONPATH=/workdir

CMD celery -A reana_workflow_engine_cwl.celeryapp worker -l info -Q ${QUEUE_ENV} --concurrency ${CELERY_CONCURRENCY} -Ofair
