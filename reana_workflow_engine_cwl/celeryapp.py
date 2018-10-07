# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2017, 2018 CERN.
#
# REANA is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""REANA Workflow Engine CWL celery application."""

from __future__ import absolute_import

from celery import Celery

from reana_workflow_engine_cwl.config import BROKER

app = Celery('tasks',
             broker=BROKER,
             include=['reana_workflow_engine_cwl.tasks'])


app.conf.update(CELERY_ACCEPT_CONTENT=['json'],
                CELERY_TASK_SERIALIZER='json')

# ["worker", "-l", "info", "-Q", "${QUEUE_ENV}"]
if __name__ == '__main__':
    app.start()
