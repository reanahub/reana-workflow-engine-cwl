# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2018, 2019, 2020, 2021 CERN.
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
    log.info(f"running workflow on context: {locals()}")
    rcode, logs = main.main(
        publisher,
        rjc_api_client,
        workflow_uuid,
        workflow_json,
        workflow_parameters,
        operational_options,
        workflow_workspace,
    )
    log.info("workflow done")

    publisher.publish_workflow_status(
        workflow_uuid, rcode_to_workflow_status(rcode), logs
    )


run_cwl_workflow = create_workflow_engine_command(
    run_cwl_workflow_engine_adapter, engine_type="cwl"
)
