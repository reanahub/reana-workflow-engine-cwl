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

import logging
import os
from glob import glob

import zmq

from reana_workflow_engine_cwl import celery_zeromq
from reana_workflow_engine_cwl.celeryapp import app
from reana_workflow_engine_cwl import main
from reana_workflow_engine_cwl.database import load_session
from reana_workflow_engine_cwl.models import Workflow, WorkflowStatus

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
    db_session = load_session()

    # if workflow_json:
        # When `cwl` is launched using an already validated workflow file.
        # workflow_kwargs = dict(workflow_json=workflow_json)
    # analysis_directory = os.path.join(
    #     os.getenv('SHARED_VOLUME', '/data'),
    #     '00000000-0000-0000-0000-000000000000',  # FIXME parameter from RWC
    #     'analyses',
    #     workflow_uuid)
    #
    # analysis_workspace = os.path.join(analysis_directory, 'workspace')
    #
    # if not os.path.exists(analysis_workspace):
    #     os.makedirs(analysis_workspace)

    log.info('running workflow on context: {0}'.format(locals()))
    Workflow.update_workflow_status(
        db_session,
        workflow_uuid,
        WorkflowStatus.running, log)
    try:
        main.main(workflow_json, parameters, workflow_workspace)
        Workflow.update_workflow_status(
            db_session,
            workflow_uuid,
            WorkflowStatus.finished, log)
        log.info('workflow done')
    except Exception as e:
        log.error('workflow failed: {0}'.format(e))
        Workflow.update_workflow_status(
            db_session,
            workflow_uuid,
            WorkflowStatus.failed,
            log,
            message=str(e))
