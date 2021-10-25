# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2018, 2019, 2020, 2021 CERN.
#
# REANA is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""REANA Workflow Engine CWL's ``cwltool`` wrapper."""

from __future__ import absolute_import, print_function, unicode_literals

import json
import logging
import os
import sys
from io import StringIO

import cwltool.main
import pkg_resources
from cwltool.context import LoadingContext
from reana_commons.config import REANA_LOG_FORMAT, REANA_LOG_LEVEL, REANA_WORKFLOW_UMASK

from reana_workflow_engine_cwl.__init__ import __version__
from reana_workflow_engine_cwl.config import LOGGING_MODULE
from reana_workflow_engine_cwl.context import REANARuntimeContext
from reana_workflow_engine_cwl.cwl_reana import ReanaPipeline
from reana_workflow_engine_cwl.database import SQLiteHandler

logging.basicConfig(level=REANA_LOG_LEVEL, format=REANA_LOG_FORMAT)
log = logging.getLogger(LOGGING_MODULE)
console = logging.StreamHandler()
log.addHandler(console)


def versionstring():
    """Return string with cwltool version."""
    pkg = pkg_resources.require("cwltool")
    if pkg:
        cwltool_ver = pkg[0].version
    else:
        cwltool_ver = "unknown"
    return f"{sys.argv[0]} {__version__} with cwltool {cwltool_ver}"


def main(
    publisher,
    rjc_api_client,
    workflow_uuid,
    workflow_spec,
    workflow_inputs,
    operational_options,
    working_dir,
    **kwargs,
):
    """Run main method."""
    os.chdir(working_dir)
    os.umask(REANA_WORKFLOW_UMASK)
    log.info("Dumping workflow specification and input parameter files...")
    with open("workflow.json", "w") as f:
        json.dump(workflow_spec, f)
    with open("inputs.json", "w") as f:
        json.dump(workflow_inputs, f)
    total_commands = 0
    print("workflow_spec:", workflow_spec)
    if "$graph" in workflow_spec:
        total_commands = len(workflow_spec["$graph"])
    total_jobs = {"total": total_commands - 1, "job_ids": []}
    initial_job_state = {"total": 0, "job_ids": []}
    running_jobs = initial_job_state
    finished_jobs = initial_job_state
    failed_jobs = initial_job_state
    publisher.publish_workflow_status(
        workflow_uuid,
        1,
        logs="",
        message={
            "progress": {
                "total": total_jobs,
                "running": running_jobs,
                "finished": finished_jobs,
                "failed": failed_jobs,
            }
        },
    )
    tmpdir = os.path.join(working_dir, "cwl/tmpdir")
    tmp_outdir = os.path.join(working_dir, "cwl/outdir")
    docker_stagedir = os.path.join(working_dir, "cwl/docker_stagedir")
    os.makedirs(tmpdir, exist_ok=True)
    os.makedirs(tmp_outdir, exist_ok=True)
    os.makedirs(docker_stagedir, exist_ok=True)
    args = operational_options

    log.setLevel(REANA_LOG_LEVEL)
    if REANA_LOG_LEVEL == logging.DEBUG:
        args += ["--debug"]
    elif REANA_LOG_LEVEL == logging.ERROR:
        args += ["--quiet"]

    args += [
        "--tmpdir-prefix",
        tmpdir + "/",
        "--tmp-outdir-prefix",
        tmp_outdir + "/",
        "--default-container",
        "frolvlad/alpine-bash",
        "--outdir",
        working_dir + "/" + "outputs",
        "workflow.json#main",
        "inputs.json",
    ]
    log.info("parsing arguments ...")
    parser = cwltool.main.arg_parser()
    parsed_args = parser.parse_args(args)

    if not len(args) >= 1:
        print(versionstring())
        print("CWL document required, no input file was provided")
        parser.print_usage()
        return 1

    if parsed_args.version:
        print(versionstring())
        return 0

    if parsed_args.quiet:
        log.setLevel(logging.WARN)
    if parsed_args.debug:
        log.setLevel(logging.DEBUG)

    pipeline = ReanaPipeline(rjc_api_client=rjc_api_client)
    log.info("starting the run..")
    db_log_writer = SQLiteHandler(workflow_uuid, publisher)

    f = StringIO()

    cwl_arguments = vars(parsed_args)
    runtimeContext = REANARuntimeContext(
        workflow_uuid, working_dir, publisher, pipeline, **cwl_arguments
    )
    result = cwltool.main.main(
        args=parsed_args,
        executor=pipeline.executor,
        loadingContext=LoadingContext({"construct_tool_object": pipeline.make_tool}),
        runtimeContext=runtimeContext,
        versionfunc=versionstring,
        logger_handler=db_log_writer,
        stdout=f,
        stderr=f,
    )
    logs = f.getvalue()

    return result, logs
