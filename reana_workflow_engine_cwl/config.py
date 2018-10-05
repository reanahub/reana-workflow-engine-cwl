# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2017, 2018 CERN.
#
# REANA is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""REANA Workflow Controller flask configuration."""

import os

JOBCONTROLLER_HOST = os.getenv('JOB_CONTROLLER_HOST',
                               'job-controller.default.svc.cluster.local')

SHARED_VOLUME_PATH = os.getenv('SHARED_VOLUME_PATH', '/reana/default')
"""Path to the mounted REANA shared volume."""

BROKER_URL = os.getenv('RABBIT_MQ_URL',
                       'message-broker.default.svc.cluster.local')

BROKER_PORT = os.getenv('RABBIT_MQ_PORT', 5672)

BROKER_USER = os.getenv('RABBIT_MQ_USER', 'test')

BROKER_PASS = os.getenv('RABBIT_MQ_PASS', '1234')

BROKER = os.getenv('RABBIT_MQ', 'amqp://{0}:{1}@{2}//'.format(BROKER_USER,
                                                              BROKER_PASS,
                                                              BROKER_URL))


COMPONENTS_DATA = {
    'reana-job-controller': (
        'http://{address}:{port}'.format(
            address=os.getenv('JOB_CONTROLLER_SERVICE_HOST', '0.0.0.0'),
            port=os.getenv('JOB_CONTROLLER_SERVICE_PORT_HTTP', '5000')),
        'reana_job_controller.json')
}
"""REANA Job Controller address."""

