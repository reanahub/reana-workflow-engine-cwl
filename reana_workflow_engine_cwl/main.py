# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2017, 2018 CERN.
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

"""REANA Workflow Engine CWL main."""

from __future__ import absolute_import, print_function, unicode_literals

import json
import logging
import os
import shutil
import sys
from io import BytesIO

import cwltool.main
import pkg_resources

from reana_workflow_engine_cwl.__init__ import __version__
from reana_workflow_engine_cwl.config import SHARED_VOLUME_PATH
from reana_workflow_engine_cwl.cwl_reana import ReanaPipeline
from reana_workflow_engine_cwl.database import SQLiteHandler

log = logging.getLogger("reana-workflow-engine-cwl")
log.setLevel(logging.INFO)
console = logging.StreamHandler()
log.addHandler(console)


def versionstring():
    """Return string with cwltool version."""
    pkg = pkg_resources.require("cwltool")
    if pkg:
        cwltool_ver = pkg[0].version
    else:
        cwltool_ver = "unknown"
    return "%s %s with cwltool %s" % (sys.argv[0], __version__, cwltool_ver)


def main(workflow_uuid, workflow_spec,
         workflow_inputs, working_dir, publisher, **kwargs):
    """Run main method."""
    working_dir = os.path.join(SHARED_VOLUME_PATH, working_dir)
    os.chdir(working_dir)
    log.error("Dumping workflow specification and input parameter files...")
    with open("workflow.json", "w") as f:
        json.dump(workflow_spec, f)
    with open("inputs.json", "w") as f:
        json.dump(workflow_inputs, f)
    total_commands = 0
    print('workflow_spec:', workflow_spec)
    if '$graph' in workflow_spec:
        total_commands = len(workflow_spec['$graph'])
    total_jobs = {"total": total_commands - 1, "job_ids": []}
    initial_job_state = {"total": 0, "job_ids": []}
    running_jobs = initial_job_state
    finished_jobs = initial_job_state
    failed_jobs = initial_job_state
    publisher.publish_workflow_status(
        workflow_uuid, 1,
        logs='',
        message={
            "progress": {
                "total": total_jobs,
                "running": running_jobs,
                "finisned": finished_jobs,
                "failed": failed_jobs
            }})
    tmpdir = os.path.join(working_dir, "cwl/tmpdir")
    tmp_outdir = os.path.join(working_dir, "cwl/outdir")
    os.makedirs(tmpdir)
    os.makedirs(tmp_outdir)
    args = ["--debug",
            "--tmpdir-prefix", tmpdir + "/",
            "--tmp-outdir-prefix", tmp_outdir + "/",
            "--default-container", "frolvlad/alpine-bash",
            "--outdir", os.path.join(os.path.dirname(working_dir), "outputs"),
            "workflow.json#main", "inputs.json"]
    log.error("parsing arguments ...")
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

    pipeline = ReanaPipeline(workflow_uuid, working_dir, publisher,
                             vars(parsed_args))
    log.error("starting the run..")
    db_log_writer = SQLiteHandler(workflow_uuid, publisher)

    f = BytesIO()
    result = cwltool.main.main(
        args=parsed_args,
        executor=pipeline.executor,
        makeTool=pipeline.make_tool,
        versionfunc=versionstring,
        logger_handler=db_log_writer,
        stdout=f
    )
    publisher.publish_workflow_status(workflow_uuid, 2,
                                      f.getvalue().decode("utf-8"))
    return result
