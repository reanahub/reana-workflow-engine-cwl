# This file is part of REANA.
# Copyright (C) 2017 CERN.
#
# REANA is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# REANA is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# REANA; if not, write to the Free Software Foundation, Inc., 59 Temple Place,
# Suite 330, Boston, MA 02111-1307, USA.
#
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization or
# submit itself to any jurisdiction.

FROM python:2.7

ENV TERM=xterm
RUN apt update && \
    apt install -y vim emacs-nox && \
    apt install nodejs -y && \
    pip install --upgrade pip

COPY CHANGES.rst README.rst setup.py /code/
COPY reana_workflow_engine_cwl/version.py /code/reana_workflow_engine_cwl/
WORKDIR /code
RUN pip install --no-cache-dir requirements-builder && \
    requirements-builder -e all -l pypi setup.py | pip install --no-cache-dir -r /dev/stdin && \
    pip uninstall -y requirements-builder

COPY . /code

RUN pip install git+git://github.com/reanahub/reana-workflow-commons.git@master#egg=reana-workflow-commons

# Debug off by default
ARG DEBUG=false
RUN if [ "${DEBUG}" = "true" ]; then pip install -r requirements-dev.txt; pip install -e .; else pip install .; fi;

ARG QUEUE_ENV=default
ENV QUEUE_ENV ${QUEUE_ENV}
ARG CELERY_CONCURRENCY=2
ENV CELERY_CONCURRENCY ${CELERY_CONCURRENCY}
ENV PYTHONPATH=/workdir

CMD celery -A reana_workflow_engine_cwl.celeryapp worker -l info -Q ${QUEUE_ENV} --concurrency ${CELERY_CONCURRENCY}
