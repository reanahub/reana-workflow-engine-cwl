# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2017, 2018 CERN.
#
# REANA is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""REANA Workflow Engine CWL tasks."""

from __future__ import absolute_import, print_function

import base64
import json
import logging

import click
from reana_commons.publisher import WorkflowStatusPublisher
from reana_workflow_engine_cwl import main
from reana_workflow_engine_cwl.config import LOGGING_MODULE


log = logging.getLogger(LOGGING_MODULE)


def load_json(ctx, param, value):
    """Callback function for click option"""
    value = value[1:]
    return json.loads(base64.standard_b64decode(value).decode())


@click.command()
@click.option('--workflow-uuid',
              required=True,
              help='UUID of workflow to be run.')
@click.option('--workflow-workspace',
              required=True,
              help='Name of workspace in which workflow should run.')
@click.option('--workflow-json',
              help='JSON representation of workflow object to be run.',
              callback=load_json)
@click.option('--workflow-parameters',
              help='JSON representation of parameters received by'
                   ' the workflow.',
              callback=load_json)
@click.option('--operational-options',
              help='Options to be passed to the workflow engine'
                   ' (i.e. caching).',
              callback=load_json)
def run_cwl_workflow(workflow_uuid, workflow_workspace,
                     workflow_json=None,
                     workflow_parameters=None,
                     operational_options={}):
    """Run cwl workflow."""
    log.info('running workflow on context: {0}'.format(locals()))
    try:
        publisher = WorkflowStatusPublisher()
        main.main(workflow_uuid, workflow_json, workflow_parameters,
                  operational_options, workflow_workspace, publisher)
        log.info('workflow done')
        publisher.publish_workflow_status(workflow_uuid, 2)
    except Exception as e:
        log.error('workflow failed: {0}'.format(e))
        publisher.publish_workflow_status(workflow_uuid, 3, message=str(e))
    finally:
        if publisher:
            publisher.close()
        else:
            log.error('Workflow {workflow_uuid} failed but status '
                      'could not be published.'.format(
                          workflow_uuid=workflow_uuid))
