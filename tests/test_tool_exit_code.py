# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2026 CERN.
#
# REANA is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""REANA CWL tool exit code tests."""

import os
import re
import subprocess
import sys
import time
from unittest import mock

import pytest

from reana_workflow_engine_cwl.cwl_reana import ReanaPipelineJob
from reana_workflow_engine_cwl.main import main


def _inline(script, **tool):
    """Return a tool whose script is part of the job command."""
    arguments = [{"prefix": "-c", "valueFrom": script}]
    return {"baseCommand": "/bin/sh", "arguments": arguments, **tool}


def _program(script, **tool):
    """Return a tool that runs its script in a separate program."""
    return {"baseCommand": ["bash", "-c", script], **tool}


@pytest.fixture
def run_tool(tmp_path, monkeypatch):
    """Return a function that runs a tool and returns its job exit code.

    The function returns also the published files with their contents.
    """
    # the engine changes the working directory and the umask of the process
    monkeypatch.chdir(tmp_path)
    umask = os.umask(0o022)
    # the engine waits between its checks for new jobs
    sleep = time.sleep
    monkeypatch.setattr(time, "sleep", lambda seconds: sleep(0.01))
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    def run(tool, outputs=("out.txt",), before_job=None, before_copy=None):
        jobs, exit_codes = [], []
        create_task_msg = ReanaPipelineJob.create_task_msg

        def record_job(self, *args):
            jobs.append(self)
            return create_task_msg(self, *args)

        def submit(cmd, **kwargs):
            if before_job:
                before_job(jobs[-1])
            if before_copy:
                listing = re.compile(r"set -- \S+/\*;")
                assert len(listing.findall(cmd)) == 1
                cmd = listing.sub(lambda match: f"{match[0]} {before_copy};", cmd)
            exit_codes.append(subprocess.run(["sh", "-c", cmd]).returncode)
            return {"job_id": "job-1"}

        def check_status(job_id):
            status = "failed" if exit_codes[-1] else "finished"
            return {"job_id": job_id, "status": status}

        monkeypatch.setattr(ReanaPipelineJob, "create_task_msg", record_job)
        rjc_api_client = mock.Mock()
        rjc_api_client.submit.side_effect = submit
        rjc_api_client.check_status.side_effect = check_status
        workflow = {
            "cwlVersion": "v1.0",
            "$graph": [
                {
                    "id": "#main",
                    "class": "Workflow",
                    "inputs": [],
                    "outputs": [
                        {
                            "id": f"#main/out{i}",
                            "type": "File",
                            "outputSource": f"#main/step/out{i}",
                        }
                        for i in range(len(outputs))
                    ],
                    "steps": [
                        {
                            "id": "#main/step",
                            "run": "#tool",
                            "in": [],
                            "out": [f"#main/step/out{i}" for i in range(len(outputs))],
                        }
                    ],
                },
                {
                    "id": "#tool",
                    "class": "CommandLineTool",
                    "requirements": [
                        {"class": "DockerRequirement", "dockerPull": "busybox"},
                        *tool.pop("requirements", []),
                    ],
                    "inputs": [],
                    "outputs": [
                        {
                            "id": f"#tool/out{i}",
                            "type": "File",
                            "outputBinding": {"glob": output},
                        }
                        for i, output in enumerate(outputs)
                    ],
                    **tool,
                },
            ],
        }
        args = ("uuid", workflow, {}, [], str(workspace))
        workflow_exit_code, _ = main(mock.Mock(), rjc_api_client, *args)
        # the result of the workflow must follow the one of its job
        assert (workflow_exit_code == 0) == (exit_codes == [0])
        published = workspace / "outputs"
        files = published.iterdir() if published.exists() else []
        return exit_codes[0], {path.name: path.read_text() for path in files}

    yield run
    os.umask(umask)
    # the tool can change the permissions of its directory
    for path in workspace.glob("cwl/outdir/*"):
        path.chmod(0o700)


@pytest.mark.parametrize(
    "tool",
    [
        _program("echo a > out.txt"),
        _inline("echo a > out.txt"),
        _inline("echo a > out.txt; exit 0"),
        _inline("echo a > out.txt\n"),
        _inline("echo a > out.txt # comment"),
        _inline("cat > out.txt <<EOF\na\nEOF\n"),
        _inline("case a in a) echo a > out.txt ;; esac"),
        _inline("echo a > out.txt\n", stdout="stdout.txt"),
        _program("echo a > out.txt; exit 3", successCodes=[3]),
        _program("echo a > out.txt", successCodes=[0], permanentFailCodes=[0]),
        pytest.param(
            _program("echo a > out.txt; ln -s no-such-file link"),
            marks=pytest.mark.skipif(
                sys.platform == "darwin", reason="cp -r follows links on macOS"
            ),
        ),
    ],
)
def test_successful_tool(run_tool, tool):
    """A job must succeed and publish its output if its tool succeeds."""
    assert run_tool(tool) == (0, {"out.txt": "a\n"})


@pytest.mark.parametrize(
    "tool",
    [
        _program("true"),
        _inline("true"),
        _inline("exit 0"),
        _inline("exit 3", successCodes=[3]),
        _program("exit 3", successCodes=[3]),
        _program("touch .hidden"),
    ],
)
def test_successful_tool_without_output(run_tool, tool):
    """A job must succeed also if its tool does not write any files."""
    assert run_tool(tool, outputs=()) == (0, {})


@pytest.mark.parametrize(
    "tool, published",
    [
        (
            _inline("cat > out.txt <<EOF\na\nEOF\n", stdout="stdout.txt"),
            {"out.txt": "a\n", "stdout.txt": ""},
        ),
        (
            _inline("cat <<EOF\na\nEOF", stdout="stdout.txt"),
            {"stdout.txt": "a\n"},
        ),
        (
            _inline("echo a; echo b # comment", stdout="stdout.txt"),
            {"stdout.txt": "a\nb\n"},
        ),
        (
            _program("echo a; echo b", stdout="stdout.txt"),
            {"stdout.txt": "a\nb\n"},
        ),
        (
            _inline("echo a >&2; echo b >&2", stderr="stderr.txt"),
            {"stderr.txt": "a\nb\n"},
        ),
        (
            {
                "requirements": [{"class": "ShellCommandRequirement"}],
                "baseCommand": [],
                "arguments": [
                    {"valueFrom": "echo a 1>&2 && echo b", "shellQuote": False}
                ],
                "stdout": "stdout.txt",
                "stderr": "stderr.txt",
            },
            {"stdout.txt": "b\n", "stderr.txt": "a\n"},
        ),
    ],
)
def test_redirections(run_tool, tool, published):
    """The standard streams of the whole tool must be redirected."""
    assert run_tool(tool, outputs=tuple(published)) == (0, published)


@pytest.mark.parametrize(
    "tool, exit_code",
    [
        (_program("echo a > out.txt; exit 3"), 3),
        (_inline("echo a > out.txt; false"), 1),
        (_inline("echo a > out.txt; exit 3"), 3),
        (_inline("echo a > out.txt\nfalse\n"), 1),
        (_inline("echo a > out.txt; false # comment"), 1),
        (_inline("set -e; echo a > out.txt; false; true"), 1),
        (_inline("echo a > out.txt\nfalse\n", stdout="stdout.txt"), 1),
        (_inline("cat > out.txt <<EOF\na\nEOF\nfalse", stdout="stdout.txt"), 1),
        (_program("echo a > out.txt; false", stderr="stderr.txt"), 1),
        (
            {
                "requirements": [{"class": "ShellCommandRequirement"}],
                "baseCommand": [],
                "arguments": [
                    {"valueFrom": "echo a > out.txt && false", "shellQuote": False}
                ],
            },
            1,
        ),
        ({"baseCommand": ["no-such-command"]}, 127),
        (_program("echo a > out.txt; exit 4", successCodes=[3]), 4),
        (_program("echo a > out.txt; exit 5", temporaryFailCodes=[5]), 5),
        (_program("echo a > out.txt", permanentFailCodes=[0]), 1),
    ],
)
def test_failed_tool(run_tool, tool, exit_code):
    """A job must fail if its tool fails, also when its output is copied."""
    assert run_tool(tool)[0] == exit_code


def _prevent_copy(job):
    """Prevent copying the output of the tool to the output directory."""
    for name in ("out.txt", "*"):
        os.mkdir(os.path.join(job.outdir, name))


@pytest.mark.parametrize(
    "tool, exit_code",
    [
        (_program("echo a > out.txt"), 1),
        (_program("echo a > out.txt; exit 3"), 3),
        (_program("echo a > out.txt; exit 3", successCodes=[3]), 1),
        (_program("echo a > '*'"), 1),
        (_program("ln -s no-such-file '*'"), 1),
    ],
)
def test_failed_copy(run_tool, tool, exit_code):
    """A job must fail if the output of its tool cannot be copied."""
    assert run_tool(tool, before_job=_prevent_copy)[0] == exit_code


not_root = pytest.mark.skipif(os.geteuid() == 0, reason="root can access any directory")


@pytest.mark.parametrize(
    "script",
    [
        pytest.param("chmod 0311 .", id="not-readable", marks=not_root),
        pytest.param("chmod 0600 .", id="not-searchable", marks=not_root),
        pytest.param(
            "mv out.txt '*'; chmod 0600 .", id="not-searchable-pattern", marks=not_root
        ),
        pytest.param('rm -r "$PWD"', id="removed"),
        pytest.param(
            'd="$PWD"; cd /; rm -r "$d"; touch "$d"; chmod 0700 "$d"', id="replaced"
        ),
    ],
)
def test_inaccessible_output(run_tool, script):
    """A job must fail if it cannot know whether its tool wrote any files."""
    assert run_tool(_program(f"echo a > out.txt; {script}"))[0] == 1


def test_disappearing_file(run_tool):
    """A job must not ignore its output if a file of another job disappears."""
    tool = _program("echo a > out.txt; touch another-file")
    assert run_tool(tool, before_copy='rm "$1"')[0] == 1


def test_file_named_as_pattern(run_tool):
    """A job must copy its output also if it is named as the pattern to list it."""
    exit_code, published = run_tool(_program("echo a > '*'"), outputs=("[*]",))
    # the published name is quoted
    assert (exit_code, list(published.values())) == (0, ["a\n"])
