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
from reana_commons.utils import check_connection_to_job_controller

from reana_workflow_engine_cwl import main
from reana_workflow_engine_cwl.config import LOGGING_MODULE

log = logging.getLogger(LOGGING_MODULE)

rcode_to_workflow_status_mapping = {0: 2, 1: 3}


def load_json(ctx, param, value):
    """Load json from click option."""
    value = value[1:]
    return json.loads(base64.standard_b64decode(value).decode())


def rcode_to_workflow_status(response_code):
    """Map the cwl tool exit code to a workflow status."""
    return rcode_to_workflow_status_mapping[response_code]


def parse_str_to_int(workflow_parameters):
    """Parse integers stored as strings to integers.

    >>> parse_str_to_int({'sleeptime': "'2'"})
    {'sleeptime': 2}
    >>> parse_str_to_int({'sleeptime': '2'})
    {'sleeptime': 2}
    >>> parse_str_to_int({'sleeptime': 'two'})
    {'sleeptime': 'two'}
    >>> parse_str_to_int({'helloworld': {'class': 'File'}})
    {'helloworld': {'class': 'File', 'location': 'code/helloworld.py'}}
    """
    for (key, val) in workflow_parameters.items():
        try:
            if isinstance(val, str) and val[0] == "'":
                # The actual value of the int as str could be stored as:
                # '\'val\'', since ' is an escape character.
                workflow_parameters[key] = int(val[1:-1])
            else:
                workflow_parameters[key] = int(val)
        except (ValueError, TypeError, KeyError):
            # Skip values and types which cannot be casted to integer.
            pass
    return workflow_parameters


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
    workflow_parameters = parse_str_to_int(workflow_parameters)
    log.info(f'running workflow on context: {locals()}')
    try:
        check_connection_to_job_controller()
        publisher = WorkflowStatusPublisher()
        rcode = main.main(workflow_uuid, workflow_json, workflow_parameters,
                          operational_options, workflow_workspace, publisher)
        log.info('workflow done')

        publisher.publish_workflow_status(workflow_uuid,
                                          rcode_to_workflow_status(rcode))

    except Exception as e:
        log.error(f'workflow failed: {e}')
        publisher.publish_workflow_status(workflow_uuid, 3, message=str(e))
    finally:
        if publisher:
            publisher.close()
        else:
            log.error(f'Workflow {workflow_uuid} failed but status '
                      'could not be published.')
