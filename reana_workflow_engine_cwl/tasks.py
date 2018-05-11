# -*- coding: utf-8 -*-
#
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

from __future__ import absolute_import, print_function

import json
import logging

import pika
from reana_workflow_engine_cwl import main
from reana_workflow_engine_cwl.celeryapp import app
from reana_workflow_engine_cwl.config import (BROKER_PASS, BROKER_PORT,
                                              BROKER_URL, BROKER_USER)
from reana_workflow_engine_cwl.utils import publish_workflow_status

log = logging.getLogger(__name__)
outputs_dir_name = 'outputs'
known_dirs = ['inputs', 'logs', outputs_dir_name]


@app.task(name='tasks.run_cwl_workflow', ignore_result=True)
def run_cwl_workflow(workflow_uuid, workflow_workspace,
                     workflow_json=None,
                     parameters=None):
    # log.info('getting socket..')
    #
    # zmqctx = celery_zeromq.get_context()
    # socket = zmqctx.socket(zmq.PUB)
    # socket.connect(os.environ['ZMQ_PROXY_CONNECT'])
    #
    # log.info('running recast workflow on context: {ctx}'.format(ctx=ctx))

    log.info('running workflow on context: {0}'.format(locals()))
    try:
        main.main(workflow_uuid, workflow_json,
                  parameters, workflow_workspace)
        log.info('workflow done')
        publish_workflow_status(workflow_uuid, 2)
    except Exception as e:
        log.error('workflow failed: {0}'.format(e))
        publish_workflow_status(workflow_uuid, 3, message=str(e))
