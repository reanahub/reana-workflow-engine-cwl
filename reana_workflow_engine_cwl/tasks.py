# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2017, 2018 CERN.
#
# REANA is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""REANA Workflow Engine CWL tasks."""

from __future__ import absolute_import, print_function

import logging

from reana_commons.workflow_engine import create_workflow_engine_command

from reana_workflow_engine_cwl import main
from reana_workflow_engine_cwl.config import LOGGING_MODULE

log = logging.getLogger(LOGGING_MODULE)


def rcode_to_workflow_status(response_code):
    """Map the cwl tool exit code to a workflow status."""
    rcode_to_workflow_status_mapping = {0: 2, 1: 3}
    return rcode_to_workflow_status_mapping[response_code]


def parse_str_to_int(workflow_parameters):
    """Parse integers stored as strings to integers."""
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


def run_cwl_workflow_engine_adapter(
    publisher,
    rjc_api_client,
    workflow_uuid=None,
    workflow_workspace=None,
    workflow_json=None,
    workflow_parameters=None,
    operational_options={},
    **kwargs,
):
    """Run cwl workflow."""
    workflow_parameters = parse_str_to_int(workflow_parameters)
    log.info(f"running workflow on context: {locals()}")
    rcode = main.main(
        publisher,
        rjc_api_client,
        workflow_uuid,
        workflow_json,
        workflow_parameters,
        operational_options,
        workflow_workspace,
    )
    log.info("workflow done")

    publisher.publish_workflow_status(workflow_uuid, rcode_to_workflow_status(rcode))


run_cwl_workflow = create_workflow_engine_command(
    run_cwl_workflow_engine_adapter, engine_type="cwl"
)
