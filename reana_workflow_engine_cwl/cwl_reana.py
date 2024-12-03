# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2018, 2019, 2020, 2021, 2022 CERN.
#
# REANA is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""REANA Workflow Engine CWL reana pipeline."""

from __future__ import absolute_import, print_function, unicode_literals

import logging
import os
import pipes
import re
import shutil
import tempfile
import time
from pprint import pformat

import shellescape
from cwltool.command_line_tool import CommandLineTool
from cwltool.errors import WorkflowException
from cwltool.job import (
    JobBase,
    needs_shell_quoting_re,
    relink_initialworkdir,
    stage_files,
)
from cwltool.utils import ensure_writable
from cwltool.workflow import default_make_tool
from reana_commons.api_client import JobControllerAPIClient as rjc_api_client
from reana_commons.config import REANA_WORKFLOW_UMASK

from reana_workflow_engine_cwl.config import LOGGING_MODULE, MOUNT_CVMFS
from reana_workflow_engine_cwl.pipeline import Pipeline
from reana_workflow_engine_cwl.poll import PollThread

from .config import WORKFLOW_KERBEROS

log = logging.getLogger(LOGGING_MODULE)


class ReanaPipeline(Pipeline):
    """REANA Pipeline class."""

    def __init__(self, **kwargs):
        """Instanciate reana pipeline."""
        super(ReanaPipeline, self).__init__()
        self.service = kwargs.get(
            "rjc_api_client", rjc_api_client("reana-job-controller")
        )
        if kwargs.get("basedir") is not None:
            self.basedir = kwargs.get("basedir")
        else:
            self.basedir = os.getcwd()

    def make_exec_tool(self, spec, loadingContext):
        """Make execution tool."""
        return ReanaPipelineTool(spec, loadingContext)

    def make_tool(self, spec, loadingContext):
        """Make tool."""
        if "class" in spec and spec["class"] == "CommandLineTool":
            return self.make_exec_tool(spec, loadingContext)
        else:
            return default_make_tool(spec, loadingContext)


class ReanaPipelineTool(CommandLineTool):
    """REANA Pipeline Tool class."""

    def __init__(self, spec, loadingContext):
        """REANA tool adapted to support REANA jobs submission."""
        super(ReanaPipelineTool, self).__init__(spec, loadingContext)

    def make_job_runner(self, runtimeContext):
        """REANA make job runner."""
        dockerReq, _ = self.get_requirement("DockerRequirement")
        if not dockerReq and runtimeContext.use_container:
            if runtimeContext.find_default_container:
                default_container = runtimeContext.find_default_container(self)
                if default_container:
                    self.requirements.insert(
                        0,
                        {"class": "DockerRequirement", "dockerPull": default_container},
                    )

        return ReanaPipelineJob


class ReanaPipelineJob(JobBase):
    """REANA Pipeline Job."""

    def __init__(
        self, builder, joborder, make_path_mapper, requirements, hints, jobname
    ):
        """Instanciate REANA pipeline job."""
        super(ReanaPipelineJob, self).__init__(
            builder, joborder, make_path_mapper, requirements, hints, jobname
        )

        self.builder = builder
        self.joborder = joborder
        self.make_path_mapper = make_path_mapper
        self.requirements = requirements
        self.hints = hints
        self.jobname = jobname

        self.outputs = None
        self.volumes = []
        self.task_name_map = {}

    def add_volumes(self, pathmapper):
        """Customize add volumes for REANA system."""
        host_outdir = self.outdir
        container_outdir = self.builder.outdir
        for src, vol in pathmapper.items():
            if not vol.staged:
                continue
            if vol.target.startswith(container_outdir + "/"):
                host_outdir_tgt = os.path.join(
                    host_outdir, vol.target[len(container_outdir) + 1 :]
                )
            else:
                host_outdir_tgt = None
            if vol.type in ("File", "Directory"):
                if not vol.resolved.startswith("_:"):
                    resolved = vol.resolved
                    if not os.path.exists(resolved):
                        resolved = (
                            "/".join(vol.resolved.split("/")[:-1])
                            + "/"
                            + vol.target.split("/")[-1]
                        )
                    self.volumes.append((resolved, vol.target))
            elif vol.type == "WritableFile":
                if self.inplace_update:
                    self.volumes.append((vol.resolved, vol.target))
                else:
                    shutil.copy(vol.resolved, host_outdir_tgt)
                    ensure_writable(host_outdir_tgt)
            if vol.type == "WritableDirectory":
                if vol.resolved.startswith("_:"):
                    if not os.path.exists(vol.target):
                        os.makedirs(vol.target)
                else:
                    if self.inplace_update:
                        pass
                    else:
                        shutil.copytree(vol.resolved, host_outdir_tgt)
                        ensure_writable(host_outdir_tgt)
            elif vol.type == "CreateFile":
                if host_outdir_tgt:
                    with open(host_outdir_tgt, "wb") as f:
                        f.write(vol.resolved.encode("utf-8"))
                else:
                    fd, createtmp = tempfile.mkstemp(dir=self.tmpdir)
                    with os.fdopen(fd, "wb") as f:
                        f.write(vol.resolved.encode("utf-8"))

    def create_task_msg(self, working_dir, workflow_uuid):  # noqa: C901
        """Create job message spec to be sent to REANA-Job-Controller."""
        job_name = self.name
        docker_req, _ = self.get_requirement("DockerRequirement")
        container = str(docker_req["dockerPull"])
        umask_cmd = f"umask {REANA_WORKFLOW_UMASK};"
        requirements_command_line = umask_cmd
        for var in self.environment:
            requirements_command_line += f"export {var}" f'="{self.environment[var]}";'

        if self.volumes:
            for filepair in self.volumes:
                if os.path.isdir(filepair[0]):
                    requirements_command_line += (
                        f"cp -a {filepair[0]} "
                        f"{'/'.join(filepair[1].split('/')[:-1])} ;"
                    )
                else:
                    requirements_command_line += f"cp -a {filepair[0]} {filepair[1]} ;"

        mounted_outdir = self.outdir
        scr, _ = self.get_requirement("ShellCommandRequirement")

        shebang_lines = {"/bin/bash", "/bin/sh"}
        if scr or self.command_line[0] in shebang_lines:

            def shouldquote(x):
                return False

            self.command_line = self.command_line[2:]
        else:
            shouldquote = needs_shell_quoting_re.search
        shellQuote = True
        for b in self.builder.bindings:
            if "shellQuote" in b:
                shellQuote = b.get("shellQuote")
                break

        command_line = " ".join(
            [
                shellescape.quote(arg) if shouldquote(arg) else arg
                for arg in self.command_line
            ]
        )
        command_line = command_line.replace("/bin/sh -c ", "")
        command_line = re.sub(
            "/var/lib/cwl/.*?/",
            "/".join(working_dir.split("/")[:-1]) + "/workspace/",
            command_line,
        )
        command_line = re.sub("/tmp/.*?/.*?/", working_dir + "/", command_line)
        if self.stdin:
            path = self.stdin.split("/")
            if os.path.isabs(self.stdin):
                command_line += f" < {self.stdin}"
            else:
                if len(path) > 1:
                    parent_dir = "/".join(mounted_outdir.split("/")[:-1])
                    command_line += f" < {os.path.join(parent_dir, path[-1])}"
                else:
                    command_line += f" < {os.path.join(mounted_outdir, path)}"
        if self.stdout:
            if os.path.isabs(self.stdout):
                command_line += f" > {self.stdout}"
            else:
                _cmd = os.path.join(self.environment["HOME"], self.stdout)
                command_line += f" > {_cmd}"
        if self.stderr:
            if os.path.isabs(self.stderr):
                stderr = self.stderr
            else:
                stderr = os.path.join(mounted_outdir, self.stderr)
            command_line += " 2> " + stderr
            if scr and not shellQuote:
                command_line = command_line.replace("&2", stderr)

        wf_space_cmd = (
            f"mkdir -p {self.environment['HOME']} "
            f"&& cd {self.environment['HOME']} "
            f"&& {command_line}"
        )
        wf_space_cmd = requirements_command_line + wf_space_cmd

        docker_output_dir = None
        docker_req, _ = self.get_requirement("DockerRequirement")
        if docker_req:
            docker_output_dir = docker_req.get("dockerOutputDirectory", None)
        if docker_output_dir:
            wf_space_cmd = (
                f"mkdir -p {docker_output_dir} && {wf_space_cmd}"
                f" ; cp -r {docker_output_dir} {mounted_outdir}"
            )
        wf_space_cmd += f"; cp -r {self.environment['HOME']}/* " f"{mounted_outdir}"
        wrapped_cmd = f"/bin/sh -c {pipes.quote(wf_space_cmd)} "
        compute_backend = self._get_hint("compute_backend")

        kerberos = self._get_hint("kerberos")
        if kerberos is None:
            kerberos = WORKFLOW_KERBEROS

        unpacked_img = self._get_hint("unpacked_img")
        voms_proxy = self._get_hint("voms_proxy")
        rucio = self._get_hint("rucio")
        htcondor_max_runtime = self._get_hint("htcondor_max_runtime")
        htcondor_accounting_group = self._get_hint("htcondor_accounting_group")
        slurm_partition = self._get_hint("slurm_partition")
        slurm_time = self._get_hint("slurm_time")
        kubernetes_uid = self._get_hint("kubernetes_uid")
        kubernetes_memory_limit = self._get_hint("kubernetes_memory_limit")
        kubernetes_job_timeout = self._get_hint("kubernetes_job_timeout")
        c4p_cpu_cores = self._get_hint("c4p_cpu_cores")
        c4p_memory_limit = self._get_hint("c4p_memory_limit")
        c4p_additional_requirements = self._get_hint("c4p_additional_requirements")
        create_body = {
            "image": container,
            "cmd": wrapped_cmd,
            "prettified_cmd": wrapped_cmd,
            "workflow_workspace": working_dir,
            "job_name": job_name,
            "cvmfs_mounts": MOUNT_CVMFS,
            "workflow_uuid": workflow_uuid,
            "compute_backend": compute_backend,
            "kerberos": kerberos,
            "unpacked_img": unpacked_img,
            "voms_proxy": voms_proxy,
            "rucio": rucio,
            "htcondor_max_runtime": htcondor_max_runtime,
            "htcondor_accounting_group": htcondor_accounting_group,
            "kubernetes_uid": kubernetes_uid,
            "kubernetes_memory_limit": kubernetes_memory_limit,
            "kubernetes_job_timeout": kubernetes_job_timeout,
            "slurm_partition": slurm_partition,
            "slurm_time": slurm_time,
            "c4p_cpu_cores": c4p_cpu_cores,
            "c4p_memory_limit": c4p_memory_limit,
            "c4p_additional_requirements": c4p_additional_requirements,
        }

        return create_body

    def _required_env(self):
        """Variables required by the CWL spec."""
        return {
            "TMPDIR": self.tmpdir,
            "HOME": self.builder.outdir,
        }

    def _get_hint(self, hint_name):
        """Return specific hint if specified."""
        if self.hints:
            for hint in self.hints:
                if hint_name in hint:
                    return hint.get(hint_name)
        return None

    def run(self, runtimeContext):  # noqa: C901
        """Run a job."""
        self._setup(runtimeContext)

        env = self.environment
        if not os.path.exists(self.tmpdir):
            os.makedirs(self.tmpdir)
        vars_to_preserve = runtimeContext.preserve_environment
        if runtimeContext.preserve_entire_environment:
            vars_to_preserve = os.environ
        if vars_to_preserve is not None:
            for key, value in os.environ.items():
                if key in vars_to_preserve and key not in env:
                    env[key] = value
        env["HOME"] = self.builder.outdir
        env["TMPDIR"] = self.tmpdir
        if "PATH" not in env:
            env["PATH"] = os.environ["PATH"]
        if "SYSTEMROOT" not in env and "SYSTEMROOT" in os.environ:
            env["SYSTEMROOT"] = os.environ["SYSTEMROOT"]

        try:
            stage_files(self.pathmapper, ignore_writable=True, symlink=False)
            if getattr(self, "generatemapper", ""):
                stage_files(
                    self.generatemapper,
                    ignore_writable=self.inplace_update,
                    symlink=False,
                )
                relink_initialworkdir(
                    self.generatemapper,
                    self.outdir,
                    self.builder.outdir,
                    inplace_update=self.inplace_update,
                )
        except OSError:
            # cwltool/process.py, line 239, in stage_files
            # shutil.copytree(p.resolved, p.target)
            pass
        self.add_volumes(self.pathmapper)
        if getattr(self, "generatemapper", ""):
            self.add_volumes(self.generatemapper)

        # useful for debugging
        log.debug(f"[job {self.name}] self.__dict__ in run() ---------------")
        log.debug(pformat(self.__dict__))

        task = self.create_task_msg(
            runtimeContext.working_dir, runtimeContext.workflow_uuid
        )

        log.info(f"[job {self.name}] CREATED TASK MSG----------------------")
        log.info(pformat(task))

        try:
            # task_id = job_id received from job-controller
            task_id = runtimeContext.pipeline.service.submit(**task)
            task_id = str(task_id["job_id"])
            running_jobs = {"total": 1, "job_ids": [task_id]}
            runtimeContext.publisher.publish_workflow_status(
                runtimeContext.workflow_uuid,
                1,
                message={
                    "progress": {
                        "running": running_jobs,
                    }
                },
            )
            log.info(f"[job {self.name}] SUBMITTED TASK --------------------")
            log.info(f"[job {self.name}] task id: {task_id} ")
            self.task_name_map[self.name] = task_id
            operation = runtimeContext.pipeline.service.check_status(task_id)
        except Exception as e:
            log.error(
                f"[job {self.name}] " f"Failed to submit task to job controller:\n{e}"
            )
            raise WorkflowException(e)

        def callback(rcode):
            try:
                outputs = self.collect_outputs(self.outdir, rcode=rcode)
                cleaned_outputs = {}
                for k, v in outputs.items():
                    if isinstance(k, bytes):
                        k = k.decode("utf8")
                    if isinstance(v, bytes):
                        v = v.decode("utf8")
                    cleaned_outputs[k] = v
                self.outputs = cleaned_outputs
                status = "success" if rcode == 0 else "permanentFail"
                self.output_callback(self.outputs, status)
            except WorkflowException as e:
                log.error(f"[job {self.name}] workflow job error:\n{e}")
                self.output_callback({}, "permanentFail")
            except Exception as e:
                log.error(f"[job {self.name}] job error:\n{e}")
                self.output_callback({}, "permanentFail")
            finally:
                if self.outputs is not None:
                    log.info(f"[job {self.name}] OUTPUTS ------------------")
                self.cleanup(runtimeContext.rm_tmpdir)

        poll = ReanaPipelinePoll(
            workflow_uuid=runtimeContext.workflow_uuid,
            task_id=self.task_name_map.get(self.name),
            jobname=self.name,
            service=runtimeContext.pipeline.service,
            operation=operation,
            callback=callback,
            publisher=runtimeContext.publisher,
        )

        runtimeContext.pipeline.add_thread(poll)
        poll.start()

    def cleanup(self, rm_tmpdir):
        """Clean up procedure."""
        log.debug(f"[job {self.name}] STARTING CLEAN UP ------------------")
        if self.stagedir and os.path.exists(self.stagedir):
            log.debug(
                f"[job {self.name}] "
                f"Removing input staging directory {self.stagedir}"
            )
            shutil.rmtree(self.stagedir, True)

        if rm_tmpdir:
            log.debug(
                f"[job {self.name}] " f"Removing temporary directory {self.tmpdir}"
            )
            shutil.rmtree(self.tmpdir, True)


class ReanaPipelinePoll(PollThread):
    """REANA Pipeline Poll class."""

    def __init__(
        self, workflow_uuid, task_id, jobname, service, operation, callback, publisher
    ):
        """Instanciate REANA pipeline poll."""
        super(ReanaPipelinePoll, self).__init__(operation)
        self.workflow_uuid = workflow_uuid
        self.task_id = task_id
        self.name = jobname
        self.service = service
        self.callback = callback
        self.publisher = publisher
        self.rcode = None

    def run(self):
        """Start polling."""
        while not self.is_done(self.operation):
            time.sleep(self.poll_interval)
            # slow down polling over time till it hits a max
            # if self.poll_interval < 30:
            #     self.poll_interval += 1
            log.debug(f"[job {self.name}] POLLING {format(self.id)}")
            try:
                self.operation = self.poll()
            except Exception as e:
                log.error(f"[job {self.name}] POLLING ERROR {e}")
                if self.poll_retries > 0:
                    self.poll_retries -= 1
                    continue
                else:
                    log.error(f"[job {self.name}] " f"MAX POLLING RETRIES EXCEEDED")
                    break

        self.complete(self.operation)

    def poll(self):
        """Poll procedure."""
        return self.service.check_status(self.id)

    def is_done(self, operation):
        """Check if operation is done."""
        terminal_states = ["finished", "failed", "stopped"]
        if operation["status"] in terminal_states:
            log.info(
                f"[job {self.name}] FINAL JOB STATE: "
                f"{operation['status']} ------------------"
            )
            if operation["status"] == "finished":
                self.rcode = 0
                # here we could publish that the job with id: self.task_id
                # finished or failed.
                self.publisher.publish_workflow_status(
                    self.workflow_uuid,
                    1,
                    logs="",
                    message={
                        "progress": {
                            "finished": {"total": 1, "job_ids": [self.task_id]},
                        }
                    },
                )
                log.error(f"[job {self.name}] task id: {self.id}")
            else:
                self.rcode = 1
                self.publisher.publish_workflow_status(
                    self.workflow_uuid,
                    1,
                    logs="",
                    message={
                        "progress": {
                            "failed": {"total": 1, "job_ids": [self.task_id]},
                        }
                    },
                )
            return True
        return False

    def complete(self, operation):
        """Complete."""
        self.callback(self.rcode)
