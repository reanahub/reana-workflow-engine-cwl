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

"""REANA Workflow Engine CWL pipeline."""

from __future__ import absolute_import, print_function, unicode_literals

import logging
import os
import tempfile
import time
import traceback

from cwltool.errors import WorkflowException
from cwltool.job import JobBase
from cwltool.mutation import MutationManager
from cwltool.process import cleanIntermediate, relocateOutputs

log = logging.getLogger("tes-backend")


class Pipeline(object):
    """Pipeline class."""

    def __init__(self):
        """Constructor."""
        self.threads = []

    def executor(self, tool, job_order, **kwargs):
        """Executor method."""
        final_output = []
        final_status = []

        def output_callback(out, processStatus):
            final_status.append(processStatus)
            final_output.append(out)

        if "basedir" not in kwargs:
            raise WorkflowException("Must provide 'basedir' in kwargs")

        output_dirs = set()

        if kwargs.get("outdir"):
            finaloutdir = os.path.abspath(kwargs.get("outdir"))
        else:
            finaloutdir = None
        if kwargs.get("tmp_outdir_prefix"):
            kwargs["outdir"] = tempfile.mkdtemp(
                prefix=kwargs["tmp_outdir_prefix"]
            )
        else:
            kwargs["outdir"] = tempfile.mkdtemp()

        output_dirs.add(kwargs["outdir"])
        kwargs["mutation_manager"] = MutationManager()

        jobReqs = None
        if "cwl:requirements" in job_order:
            jobReqs = job_order["cwl:requirements"]
        elif ("cwl:defaults" in tool.metadata and
              "cwl:requirements" in tool.metadata["cwl:defaults"]):
            jobReqs = tool.metadata["cwl:defaults"]["cwl:requirements"]
        if jobReqs:
            for req in jobReqs:
                tool.requirements.append(req)

        if kwargs.get("default_container"):
            tool.requirements.insert(0, {
                "class": "DockerRequirement",
                "dockerPull": kwargs["default_container"]
            })
        else:
            kwargs['default_container'] = 'frolvlad/alpine-bash'
        kwargs['docker_outdir'] = os.path.join(
            self.working_dir, "cwl/docker_outdir")
        kwargs['docker_tmpdir'] = os.path.join(
            self.working_dir, "cwl/docker_tmpdir")
        kwargs["docker_stagedir"] = os.path.join(
            self.working_dir, "cwl/docker_stagedir")

        jobs = tool.job(job_order, output_callback, **kwargs)
        try:
            for runnable in jobs:
                if runnable:
                    builder = kwargs.get("builder", None)
                    if builder is not None:
                        runnable.builder = builder
                    if runnable.outdir:
                        output_dirs.add(runnable.outdir)
                    runnable.run(**kwargs)
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
                final_output[0], finaloutdir,
                output_dirs, kwargs.get("move_outputs"),
                kwargs["make_fs_access"](""))

        if kwargs.get("rm_tmpdir"):
            cleanIntermediate(output_dirs)

        if final_output and final_status:
            return (final_output[0], final_status[0])
        else:
            return (None, "permanentFail")

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


class PipelineJob(JobBase):
    """Pipeline Job class."""

    def __init__(self, spec, pipeline):
        """Constructor."""
        super(JobBase, self).__init__()
        self.spec = spec
        self.pipeline = pipeline
        self.running = False

    def find_docker_requirement(self):
        """Find docker from pipeline."""
        default = "python:2.7"
        container = default
        if self.pipeline.kwargs["default_container"]:
            container = self.pipeline.kwargs["default_container"]

        reqs = self.spec.get("requirements", []) + self.spec.get("hints", [])
        for i in reqs:
            if i.get("class", "NA") == "DockerRequirement":
                container = i.get(
                    "dockerPull",
                    i.get("dockerImageId", default)
                )
        return container

    def run(self, pull_image=True, rm_container=True, rm_tmpdir=True,
            move_outputs="move", **kwargs):
        """Run pipeline job."""
        raise Exception("PipelineJob.run() not implemented")
