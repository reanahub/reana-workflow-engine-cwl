from __future__ import absolute_import, print_function, unicode_literals

import json
import logging
import os
import sys
from io import BytesIO

import cwltool.main
import pkg_resources
import shutil

from reana_workflow_engine_cwl.__init__ import __version__
from reana_workflow_engine_cwl.config import SHARED_VOLUME_PATH
from reana_workflow_engine_cwl.cwl_reana import ReanaPipeline
from reana_workflow_engine_cwl.database import SQLiteHandler

log = logging.getLogger("reana-workflow-engine-cwl")
log.setLevel(logging.INFO)
console = logging.StreamHandler()
log.addHandler(console)


def versionstring():
    pkg = pkg_resources.require("cwltool")
    if pkg:
        cwltool_ver = pkg[0].version
    else:
        cwltool_ver = "unknown"
    return "%s %s with cwltool %s" % (sys.argv[0], __version__, cwltool_ver)


def main(workflow_uuid, workflow_spec,
         workflow_inputs, working_dir, publisher, **kwargs):
    ORGANIZATIONS = {"default", "alice"}
    first_arg = working_dir.split("/")[0]
    if first_arg in ORGANIZATIONS:
        working_dir = working_dir.replace(first_arg, SHARED_VOLUME_PATH)
    src = os.path.join(os.path.dirname(working_dir), "code")
    inputs_dir = os.path.join(os.path.dirname(working_dir), "inputs")
    src_files = os.listdir(src)
    for file_name in src_files:
        full_file_name = os.path.join(src, file_name)
        if os.path.isfile(full_file_name):
            shutil.copy(full_file_name, inputs_dir)
    os.chdir(inputs_dir)
    log.error("dumping files...")
    with open("workflow.json", "w") as f:
        json.dump(workflow_spec, f)
    with open("inputs.json", "w") as f:
        json.dump(workflow_inputs, f)
    total_commands = 0
    print('workflow_spec:', workflow_spec)
    if '$graph' in workflow_spec:
        total_commands = len(workflow_spec['$graph'])
    planned_jobs = {"total": total_commands - 1, "job_ids": []}
    submitted_jobs = {"total": 0, "job_ids": []}
    succeeded_jobs = submitted_jobs
    failed_jobs = submitted_jobs
    publisher.publish_workflow_status(
        workflow_uuid, 1,
        logs='',
        message={
            "progress": {
                "planned": planned_jobs,
                "submitted":
                submitted_jobs,
                "succeeded":
                succeeded_jobs,
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
