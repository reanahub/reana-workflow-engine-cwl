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
from cwltool.draft2tool import CommandLineTool
from cwltool.errors import WorkflowException
from cwltool.job import relink_initialworkdir, needs_shell_quoting_re
from cwltool.job import stageFiles
from cwltool.pathmapper import ensure_writable
from cwltool.utils import get_feature
from cwltool.workflow import defaultMakeTool

from reana_workflow_engine_cwl.httpclient import ReanaJobControllerHTTPClient \
    as HttpClient
from reana_workflow_engine_cwl.pipeline import Pipeline, PipelineJob
from reana_workflow_engine_cwl.poll import PollThread

log = logging.getLogger("cwl-backend")


class ReanaPipeline(Pipeline):

    def __init__(self, workflow_uuid, working_dir, publisher, kwargs):
        super(ReanaPipeline, self).__init__()
        self.workflow_uuid = workflow_uuid
        self.kwargs = kwargs
        self.service = HttpClient()
        if kwargs.get("basedir") is not None:
            self.basedir = kwargs.get("basedir")
        else:
            self.basedir = os.getcwd()
        self.working_dir = working_dir
        self.publisher = publisher

    def make_exec_tool(self, spec, **kwargs):
        return ReanaPipelineTool(self.workflow_uuid, spec, self,
                                 working_dir=self.working_dir,
                                 publisher=self.publisher,
                                 **kwargs)

    def make_tool(self, spec, **kwargs):
        if "class" in spec and spec["class"] == "CommandLineTool":
            return self.make_exec_tool(spec, **kwargs)
        else:
            return defaultMakeTool(spec, **kwargs)


class ReanaPipelineTool(CommandLineTool):

    def __init__(self, workflow_uuid, spec, pipeline,
                 working_dir, publisher, **kwargs):
        super(ReanaPipelineTool, self).__init__(spec, **kwargs)
        self.workflow_uuid = workflow_uuid
        self.spec = spec
        self.pipeline = pipeline
        self.working_dir = working_dir
        self.publisher = publisher

    def makeJobRunner(self, use_container=True, **kwargs):
        dockerReq, _ = self.get_requirement("DockerRequirement")
        if not dockerReq and use_container:
            if self.find_default_container:
                default_container = self.find_default_container(self)
                if default_container:
                    self.requirements.insert(0, {
                        "class": "DockerRequirement",
                        "dockerPull": default_container
                    })

        return ReanaPipelineJob(self.workflow_uuid, self.spec,
                                self.pipeline, self.working_dir,
                                self.publisher)


class ReanaPipelineJob(PipelineJob):

    def __init__(self, workflow_uuid, spec, pipeline, working_dir, publisher):
        super(ReanaPipelineJob, self).__init__(spec, pipeline)
        self.workflow_uuid = workflow_uuid
        self.outputs = None
        self.working_dir = working_dir
        self.inplace_update = False
        self.volumes = []
        self.task_name_map = {}
        self.publisher = publisher

    def add_volumes(self, pathmapper):

        host_outdir = self.outdir
        container_outdir = self.builder.outdir
        for src, vol in pathmapper.items():
            if not vol.staged:
                continue
            if vol.target.startswith(container_outdir + "/"):
                host_outdir_tgt = os.path.join(
                    host_outdir, vol.target[len(container_outdir) + 1:])
            else:
                host_outdir_tgt = None
            if vol.type in ("File", "Directory"):
                if not vol.resolved.startswith("_:"):
                    resolved = vol.resolved
                    if not os.path.exists(resolved):
                        resolved = "/".join(
                            vol.resolved.split("/")[:-1]) + "/" + \
                            vol.target.split("/")[-1]
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
                        os.makedirs(vol.target, mode=0o0755)
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

    def create_task_msg(self):
        prettified_cmd = self.command_line[2]
        job_name = self.name
        container = self.find_docker_requirement()
        requirements_command_line = ""
        for var in self.environment:
            requirements_command_line += "export {0}=\"{1}\";".format(
                var, self.environment[var])

        if self.volumes:
            for filepair in self.volumes:
                if os.path.isdir(filepair[0]):
                    requirements_command_line += "cp -a {0} {1} ;".format(
                        filepair[0], "/".join(filepair[1].split("/")[:-1]))
                else:
                    requirements_command_line += "cp -a {0} {1} ;".format(
                        filepair[0], filepair[1])

        mounted_outdir = self.outdir
        scr, _ = get_feature(self, "ShellCommandRequirement")

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

        command_line = " ".join([shellescape.quote(arg) if shouldquote(arg)
                                 else arg for arg in
                                 self.command_line])
        command_line = command_line.replace('/bin/sh -c ', '')
        command_line = re.sub(
            "/var/lib/cwl/.*?/", "/".join(self.working_dir.split("/")[:-1]) +
            "/workspace/", command_line)
        command_line = re.sub(
            "/tmp/.*?/.*?/", self.working_dir + "/", command_line)
        if self.stdin:
            path = self.stdin.split("/")
            if os.path.isabs(self.stdin):
                command_line = command_line + " < {0}".format(self.stdin)
            else:
                if len(path) > 1:
                    parent_dir = "/".join(mounted_outdir.split("/")[:-1])
                    command_line = command_line + \
                        " < {0}".format(os.path.join(parent_dir, path[-1]))
                else:
                    command_line = command_line + \
                        " < {0}".format(os.path.join(mounted_outdir, path))
        if self.stdout:
            if os.path.isabs(self.stdout):
                command_line = command_line + " > {0}".format(self.stdout)
            else:
                command_line = command_line + \
                    " > {0}".format(os.path.join(
                        self.environment["HOME"], self.stdout))
        if self.stderr:
            if os.path.isabs(self.stderr):
                stderr = self.stderr
            else:
                stderr = os.path.join(mounted_outdir, self.stderr)
            command_line += " 2> " + stderr
            if scr and not shellQuote:
                command_line = command_line.replace("&2", stderr)

        wf_space_cmd = "mkdir -p {0} && cd {0} && ".format(
            self.environment["HOME"]) + command_line
        wf_space_cmd = requirements_command_line + wf_space_cmd

        docker_output_dir = None
        docker_req, _ = get_feature(self, "DockerRequirement")
        if docker_req:
            docker_output_dir = docker_req.get("dockerOutputDirectory", None)
        if docker_output_dir:
            wf_space_cmd = "mkdir -p {0} && {1} ; cp -r {0} {2}".format(
                docker_output_dir, wf_space_cmd, mounted_outdir)
        wf_space_cmd += "; cp -r {0}/* {1}".format(
            self.environment['HOME'], mounted_outdir)
        wrapped_cmd = "/bin/sh -c {} ".format(pipes.quote(wf_space_cmd))

        create_body = {
            "experiment": "default",
            "image": container,
            "cmd": wrapped_cmd,
            "workflow_workspace": self.working_dir,
            "prettified_cmd": prettified_cmd,
            "job_name": job_name
        }

        return create_body

    def run(self, pull_image=True, rm_container=True, rm_tmpdir=True,
            move_outputs="move", **kwargs):

        self._setup(kwargs)

        env = self.environment
        if not os.path.exists(self.tmpdir):
            os.makedirs(self.tmpdir)
        vars_to_preserve = kwargs.get("preserve_environment")
        if kwargs.get("preserve_entire_environment"):
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
            stageFiles(self.pathmapper, ignoreWritable=True, symLink=False)
            if getattr(self, "generatemapper", ""):
                stageFiles(self.generatemapper,
                           ignoreWritable=self.inplace_update, symLink=False)
                relink_initialworkdir(self.generatemapper,
                                      self.outdir,
                                      self.builder.outdir,
                                      inplace_update=self.inplace_update)
        except OSError:
            # cwltool/process.py, line 239, in stageFiles
            # shutil.copytree(p.resolved, p.target)
            pass
        self.add_volumes(self.pathmapper)
        if getattr(self, "generatemapper", ""):
            self.add_volumes(self.generatemapper)

        # useful for debugging
        log.debug(
            "[job %s] self.__dict__ in run() ----------------------" %
            (self.name)
        )
        log.debug(pformat(self.__dict__))

        task = self.create_task_msg()

        log.info(
            "[job %s] CREATED TASK MSG----------------------" %
            (self.name)
        )
        log.info(pformat(task))

        try:
            # task_id = job_id received from job-controller
            task_id = self.pipeline.service.submit(**task)
            submitted_jobs = {"total": 1, "job_ids": [task_id]}
            self.publisher.publish_workflow_status(
                self.workflow_uuid, 1,
                message={
                    "progress": {
                        "submitted":
                        submitted_jobs,
                    }})
            log.info(
                "[job %s] SUBMITTED TASK ----------------------" %
                (self.name)
            )
            log.info("[job %s] task id: %s " % (self.name, task_id))
            self.task_name_map[self.name] = task_id
            operation = self.pipeline.service.check_status(task_id)
        except Exception as e:
            log.error(
                "[job %s] Failed to submit task to job controller:\n%s" %
                (self.name, e)
            )
            return WorkflowException(e)

        def callback():
            try:
                outputs = self.collect_outputs(self.outdir)
                cleaned_outputs = {}
                for k, v in outputs.items():
                    if isinstance(k, bytes):
                        k = k.decode("utf8")
                    if isinstance(v, bytes):
                        v = v.decode("utf8")
                    cleaned_outputs[k] = v
                self.outputs = cleaned_outputs
                self.output_callback(self.outputs, "success")
            except WorkflowException as e:
                log.error("[job %s] job error:\n%s" % (self.name, e))
                self.output_callback({}, "permanentFail")
            except Exception as e:
                log.error("[job %s] job error:\n%s" % (self.name, e))
                self.output_callback({}, "permanentFail")
            finally:
                if self.outputs is not None:
                    log.info(
                        "[job %s] OUTPUTS ------------------" %
                        (self.name)
                    )
                    log.info(pformat(self.outputs))
                self.cleanup(rm_tmpdir)

        poll = ReanaPipelinePoll(
            workflow_uuid=self.workflow_uuid,
            task_id=self.task_name_map.get(self.name),
            jobname=self.name,
            service=self.pipeline.service,
            operation=operation,
            callback=callback,
            publisher=self.publisher
        )

        self.pipeline.add_thread(poll)
        poll.start()

    def cleanup(self, rm_tmpdir):
        log.debug(
            "[job %s] STARTING CLEAN UP ------------------" %
            (self.name)
        )
        if self.stagedir and os.path.exists(self.stagedir):
            log.debug(
                "[job %s] Removing input staging directory %s" %
                (self.name, self.stagedir)
            )
            shutil.rmtree(self.stagedir, True)

        if rm_tmpdir:
            log.debug(
                "[job %s] Removing temporary directory %s" %
                (self.name, self.tmpdir)
            )
            shutil.rmtree(self.tmpdir, True)


class ReanaPipelinePoll(PollThread):

    def __init__(self, workflow_uuid, task_id, jobname,
                 service, operation, callback, publisher):
        super(ReanaPipelinePoll, self).__init__(operation)
        self.workflow_uuid = workflow_uuid
        self.task_id = task_id
        self.name = jobname
        self.service = service
        self.callback = callback
        self.publisher = publisher

    def run(self):
        while not self.is_done(self.operation):
            time.sleep(self.poll_interval)
            # slow down polling over time till it hits a max
            # if self.poll_interval < 30:
            #     self.poll_interval += 1
            log.debug(
                "[job %s] POLLING %s" %
                (self.name, pformat(self.id))
            )
            try:
                self.operation = self.poll()
            except Exception as e:
                log.error("[job %s] POLLING ERROR %s" % (self.name, e))
                if self.poll_retries > 0:
                    self.poll_retries -= 1
                    continue
                else:
                    log.error("[job %s] MAX POLLING RETRIES EXCEEDED" %
                              (self.name))
                    break

        self.complete(self.operation)

    def poll(self):
        return self.service.check_status(self.id)

    def is_done(self, operation):
        terminal_states = ["succeeded", "failed"]
        if operation['status'] in terminal_states:
            log.info(
                "[job %s] FINAL JOB STATE: %s ------------------" %
                (self.name, operation['status'])
            )
            if operation['status'] != "failed":
                # here we could publish that the job with id: self.task_id
                # succeeded or failed.
                self.publisher.publish_workflow_status(
                    self.workflow_uuid, 1, logs='',
                    message={
                        'progress': {
                            'succeeded':
                            {'total': 1, 'job_ids': [
                                self.task_id]},
                        }})
                log.error(
                    "[job %s] task id: %s" % (self.name, self.id)
                )
                log.error(
                    "[job %s] logs: %s" %
                    (
                        self.name,
                        self.service.get_logs(self.id)
                    )

                )
            else:
                self.publisher.publish_workflow_status(
                    self.workflow_uuid, 1, logs='',
                    message={
                        'progress': {
                            'failed':
                            {'total': 1, 'job_ids': [
                                self.task_id]},
                        }})
            return True
        return False

    def complete(self, operation):
        self.callback()
