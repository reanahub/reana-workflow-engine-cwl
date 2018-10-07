# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2017, 2018 CERN.
#
# REANA is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""REANA Workflow Engine CWL tasks."""

from __future__ import absolute_import, print_function

import json
import logging

from reana_commons.publisher import Publisher

from reana_workflow_engine_cwl import main
from reana_workflow_engine_cwl.celeryapp import app

log = logging.getLogger(__name__)
outputs_dir_name = 'outputs'
known_dirs = ['inputs', 'logs', outputs_dir_name]


@app.task(name='tasks.run_cwl_workflow', ignore_result=True)
def run_cwl_workflow(workflow_uuid, workflow_workspace,
                     workflow_json=None,
                     parameters=None):
    """Run cwl workflow."""
    log.info('running workflow on context: {0}'.format(locals()))
    try:
        publisher = Publisher()
        publisher.connect()
        main.main(workflow_uuid, workflow_json,
                  parameters, workflow_workspace, publisher)
        log.info('workflow done')
        publisher.publish_workflow_status(workflow_uuid, 2)
    except Exception as e:
        log.error('workflow failed: {0}'.format(e))
        publisher.publish_workflow_status(workflow_uuid, 3, message=str(e))
    finally:
        publisher.close()
