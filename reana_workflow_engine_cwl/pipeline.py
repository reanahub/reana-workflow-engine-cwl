# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2018, 2019, 2020, 2021 CERN.
#
# REANA is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""REANA Workflow Engine CWL ``cwltool`` overriden classes."""

from __future__ import absolute_import, print_function, unicode_literals

import json
import logging
import os
import tempfile
import time
import traceback

from cwltool.errors import WorkflowException
from cwltool.mutation import MutationManager
from cwltool.process import cleanIntermediate, relocateOutputs

from reana_workflow_engine_cwl.config import LOGGING_MODULE

log = logging.getLogger(LOGGING_MODULE)


class Pipeline(object):
    """Pipeline class."""

    def __init__(self):
        """Instanciate pipeline."""
        self.threads = []

    def executor(self, tool, job_order, runtimeContext, **kwargs):  # noqa: C901
        """Executor method."""
        final_output = []
        final_status = []

        def output_callback(out, processStatus):
            final_status.append(processStatus)
            final_output.append(out)

        if not runtimeContext.basedir:
            raise WorkflowException("`runtimeContext` should contain a " "`basedir`")

        output_dirs = set()

        if runtimeContext.outdir:
            finaloutdir = os.path.abspath(runtimeContext.outdir)
        else:
            finaloutdir = None
        if runtimeContext.tmp_outdir_prefix:
            runtimeContext.outdir = tempfile.mkdtemp(
                prefix=runtimeContext.tmp_outdir_prefix
            )
        else:
            runtimeContext.outdir = tempfile.mkdtemp()

        output_dirs.add(runtimeContext.outdir)
        runtimeContext.mutation_manager = MutationManager()

        jobReqs = None
        if "cwl:requirements" in job_order:
            jobReqs = job_order["cwl:requirements"]
        elif (
            "cwl:defaults" in tool.metadata
            and "cwl:requirements" in tool.metadata["cwl:defaults"]
        ):
            jobReqs = tool.metadata["cwl:defaults"]["cwl:requirements"]
        if jobReqs:
            for req in jobReqs:
                tool.requirements.append(req)

        if not runtimeContext.default_container:
            runtimeContext.default_container = "frolvlad/alpine-bash"
        runtimeContext.tmpdir = runtimeContext.get_tmpdir()
        runtimeContext.docker_stagedir = os.path.join(
            runtimeContext.working_dir, "cwl/docker_stagedir"
        )
        runtimeContext.docker_outdir = runtimeContext.outdir
        runtimeContext.docker_tmpdir = runtimeContext.tmpdir

        jobs = tool.job(job_order, output_callback, runtimeContext)
        try:
            for runnable in jobs:
                if runnable:
                    if runtimeContext.builder:
                        runnable.builder = runtimeContext.builder
                    if runnable.outdir:
                        output_dirs.add(runnable.outdir)
                    runnable.run(runtimeContext)
                else:
                    # log.error(
                    #     "Workflow cannot make any more progress"
                    # )
                    # break
                    time.sleep(1)

        except WorkflowException as e:
            traceback.print_exc()
            raise e
        except Exception as e:
            traceback.print_exc()
            raise WorkflowException(str(e))

        # wait for all processes to finish
        self.wait()

        if final_output and final_output[0] and finaloutdir:
            final_output[0] = relocateOutputs(
                final_output[0],
                finaloutdir,
                output_dirs,
                runtimeContext.move_outputs,
                runtimeContext.make_fs_access(""),
            )

        if runtimeContext.rm_tmpdir:
            cleanIntermediate(output_dirs)

        if final_output and final_status:
            output = json.dumps(final_output[0])
            log.info(f"FinalOutput{output}FinalOutput")
            return str(final_output[0]), str(final_status[0])
        else:
            return None, "permanentFail"

    def make_exec_tool(self, spec, **kwargs):
        """Make execution tool."""
        raise Exception("Pipeline.make_exec_tool() not implemented")

    def make_tool(self, spec, **kwargs):
        """Make tool."""
        raise Exception("Pipeline.make_tool() not implemented")

    def add_thread(self, thread):
        """Add thread to self.threads."""
        self.threads.append(thread)

    def wait(self):
        """Wait."""
        while True:
            if all([not t.is_alive() for t in self.threads]):
                break
        for t in self.threads:
            t.join()
