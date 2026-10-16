# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2026 CERN.
#
# REANA is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""REANA CWL job tests."""

import os
import stat
import subprocess
from types import SimpleNamespace
from unittest import mock

import pytest
import shellescape
from reana_commons.errors import REANAWorkspaceError

from reana_workflow_engine_cwl.cwl_reana import ReanaPipelineJob
from reana_workflow_engine_cwl.main import main
from reana_workflow_engine_cwl.utils import share_tree_with_group, share_with_group


def test_initial_workdir_cleanup_preserves_inplace_update_symlinks(tmp_path):
    """Unlink staged inputs while preserving intentional writable symlinks."""
    uploaded_input = tmp_path / "workspace" / "gendata.C"
    uploaded_input.parent.mkdir()
    uploaded_input.write_text("uploaded input")
    writable_input = uploaded_input.parent / "writable.txt"
    writable_input.write_text("writable input")

    outdir = tmp_path / "cwl" / "outdir"
    outdir.mkdir(parents=True)
    staged_input = outdir / uploaded_input.name
    staged_input.symlink_to(uploaded_input)
    staged_writable_input = outdir / writable_input.name
    staged_writable_input.symlink_to(writable_input)

    container_outdir = "/var/lib/cwl/job"
    job = object.__new__(ReanaPipelineJob)
    job.builder = SimpleNamespace(outdir=container_outdir)
    job.generatemapper = {
        "input": SimpleNamespace(
            staged=True,
            type="File",
            resolved=str(uploaded_input),
            target=f"{container_outdir}/{uploaded_input.name}",
        ),
        "writable_input": SimpleNamespace(
            staged=True,
            type="WritableFile",
            resolved=str(writable_input),
            target=f"{container_outdir}/{writable_input.name}",
        ),
    }
    job.inplace_update = True
    job.outdir = str(outdir)

    generated_output = tmp_path / "job-output"
    generated_output.mkdir()
    (generated_output / uploaded_input.name).write_text("generated output")

    cleanup_command = job._initial_workdir_symlink_cleanup_command()
    command = (
        f"true{cleanup_command}; cp -r "
        f"{shellescape.quote(str(generated_output))}/* "
        f"{shellescape.quote(str(outdir))}"
    )
    subprocess.run(["/bin/sh", "-c", command], check=True)

    assert uploaded_input.read_text() == "uploaded input"
    assert not staged_input.is_symlink()
    assert staged_input.read_text() == "generated output"
    assert staged_writable_input.is_symlink()
    assert staged_writable_input.read_text() == "writable input"


def _mode(path):
    """Return the access permissions of a file or directory.

    The setgid bit depends on the directory where the tests run.
    """
    return stat.S_IMODE(os.lstat(path).st_mode) & 0o777


def _get_workflow(listing, docker_requirement=None):
    """Return a workflow with one step that stages the given files."""
    inputs = [
        {"id": "file", "type": "File", "location": "file.txt"},
        {"id": "directory", "type": "Directory", "location": "directory"},
    ]
    return {
        "cwlVersion": "v1.0",
        "$graph": [
            {
                "id": "#main",
                "class": "Workflow",
                "inputs": [
                    {
                        "id": f"#main/{i['id']}",
                        "type": i["type"],
                        "default": {"class": i["type"], "location": i["location"]},
                    }
                    for i in inputs
                ],
                "outputs": [],
                "steps": [
                    {
                        "id": "#main/step",
                        "run": "#tool",
                        "in": [
                            {
                                "id": f"#main/step/{i['id']}",
                                "source": f"#main/{i['id']}",
                            }
                            for i in inputs
                        ],
                        "out": [],
                    }
                ],
            },
            {
                "id": "#tool",
                "class": "CommandLineTool",
                "requirements": [
                    {
                        "class": "DockerRequirement",
                        "dockerPull": "busybox",
                        **(docker_requirement or {}),
                    },
                    {"class": "InitialWorkDirRequirement", "listing": listing},
                ],
                "baseCommand": ["sh", "script.sh"],
                "inputs": [
                    {"id": f"#tool/{i['id']}", "type": i["type"]} for i in inputs
                ],
                "outputs": [],
            },
        ],
    }


@pytest.fixture
def workspace(tmp_path, monkeypatch):
    """Create a workspace with files that only their owner can change."""
    workspace = tmp_path / "workspace"
    (workspace / "directory").mkdir(parents=True)
    for path in (workspace / "file.txt", workspace / "directory" / "file.txt"):
        path.write_text("original")
        path.chmod(0o644)
    (workspace / "directory").chmod(0o755)
    # the engine changes the working directory and the umask of the process
    monkeypatch.chdir(tmp_path)
    umask = os.umask(0o022)
    yield workspace
    os.umask(umask)


def _run_workflow(workflow, workspace, monkeypatch, check_submission):
    """Run a workflow and check its job at the time of submission."""
    jobs = []
    create_task_msg = ReanaPipelineJob.create_task_msg

    def record_job(self, *args):
        jobs.append(self)
        return create_task_msg(self, *args)

    def submit(**kwargs):
        check_submission(jobs[-1])
        return {"job_id": "job-1"}

    monkeypatch.setattr(ReanaPipelineJob, "create_task_msg", record_job)
    rjc_api_client = mock.Mock()
    rjc_api_client.submit.side_effect = submit
    rjc_api_client.check_status.return_value = {"job_id": "job-1", "status": "finished"}

    main(mock.Mock(), rjc_api_client, "uuid", workflow, {}, [], str(workspace))
    rjc_api_client.submit.assert_called_once()
    return jobs[-1]


def test_job_files_are_shared_before_submission(workspace, monkeypatch):
    """Jobs with another UID must be able to use their directories and files."""
    modes = {}

    def check_submission(job):
        modes["allocated"] = [
            _mode(path)
            for path in (job.builder.outdir, job.outdir, job.tmpdir, job.stagedir)
        ]
        for name, directory in (
            ("working", job.builder.outdir),
            ("output", job.outdir),
        ):
            modes[name] = {
                path: _mode(os.path.join(directory, path))
                for path in ("script.sh", "file.txt", "directory", "directory/file.txt")
            }

    workflow = _get_workflow(
        [
            {"entryname": "script.sh", "entry": "echo hello"},
            {"entry": "$(inputs.file)", "writable": True},
            {"entry": "$(inputs.directory)", "writable": True},
        ]
    )
    _run_workflow(workflow, workspace, monkeypatch, check_submission)

    writable_inputs = {
        "file.txt": 0o664,
        "directory": 0o775,
        "directory/file.txt": 0o664,
    }
    assert modes == {
        "allocated": [0o770] * 4,
        "working": {"script.sh": 0o440, **writable_inputs},
        # the job overwrites these files, so the literal must stay writable
        "output": {"script.sh": 0o664, **writable_inputs},
    }
    # the original files must not be changed
    assert _mode(workspace / "file.txt") == 0o644
    assert _mode(workspace / "directory") == 0o755
    assert _mode(workspace / "directory" / "file.txt") == 0o644


def test_docker_output_directory_is_not_shared(workspace, monkeypatch):
    """A directory that is not allocated for the job must not be changed."""
    directory = workspace / "declared"
    directory.mkdir(mode=0o700)
    modes = []

    def check_submission(job):
        assert job.builder.outdir == str(directory)
        modes.extend([_mode(directory), _mode(directory / "script.sh")])

    workflow = _get_workflow(
        [{"entryname": "script.sh", "entry": "echo hello"}],
        docker_requirement={"dockerOutputDirectory": str(directory)},
    )
    _run_workflow(workflow, workspace, monkeypatch, check_submission)

    assert modes == [0o700, 0o400]


def test_inplace_update_inputs_are_not_shared(tmp_path):
    """Inputs updated in place must not be changed, contrary to literals."""
    original = tmp_path / "original.txt"
    original.write_text("original")
    original.chmod(0o644)
    outdir = tmp_path / "outdir"
    outdir.mkdir()
    literal = outdir / "script.sh"
    literal.write_text("echo hello")
    literal.chmod(0o400)
    (outdir / "original.txt").symlink_to(original)

    job = object.__new__(ReanaPipelineJob)
    job.name = "job"
    job.outdir = str(outdir)
    job.builder = SimpleNamespace(outdir=str(outdir))
    job.inplace_update = True
    job.pathmapper = {}
    job.generatemapper = {
        name: SimpleNamespace(
            staged=True, type=type_, resolved=str(original), target=str(outdir / name)
        )
        for name, type_ in (
            ("script.sh", "CreateFile"),
            ("original.txt", "WritableFile"),
        )
    }

    assert list(job._get_private_copies()) == [str(literal)]
    job._share_staged_files(
        SimpleNamespace(
            working_dir=str(tmp_path),
            docker_outdir=str(outdir),
            docker_stagedir=str(outdir),
        )
    )

    assert _mode(literal) == 0o440
    assert _mode(original) == 0o644


def test_redirected_job_directories_are_not_followed(tmp_path):
    """A link above a job directory must not redirect the permission change."""
    workspace = tmp_path / "workspace"
    (workspace / "cwl").mkdir(parents=True)
    (tmp_path / "elsewhere" / "job").mkdir(parents=True)
    literal = tmp_path / "elsewhere" / "job" / "script.sh"
    literal.write_text("echo hello")
    literal.chmod(0o400)
    # the workspace is writable for the jobs, so they can replace directories
    (workspace / "cwl" / "outdir").symlink_to(tmp_path / "elsewhere")
    outdir = str(workspace / "cwl" / "outdir" / "job")

    job = object.__new__(ReanaPipelineJob)
    job.name = "job"
    job.outdir = outdir
    job.builder = SimpleNamespace(outdir=outdir)
    job.inplace_update = False
    job.pathmapper = {}
    job.generatemapper = {
        "script.sh": SimpleNamespace(
            staged=True,
            type="CreateFile",
            resolved="echo hello",
            target=f"{outdir}/script.sh",
        )
    }
    job._share_staged_files(
        SimpleNamespace(
            working_dir=str(workspace), docker_outdir=outdir, docker_stagedir=outdir
        )
    )

    assert _mode(literal) == 0o400
    with pytest.raises(REANAWorkspaceError):
        share_with_group(workspace, outdir)


def test_existing_writable_literal_is_shared(workspace, monkeypatch):
    """A literal must be shared also when it replaces a private file."""
    modes = []
    setup = ReanaPipelineJob._setup

    def create_private_file(self, *args):
        # left by a previous job, as all jobs use the same working directory
        path = os.path.join(self.builder.outdir, "config.txt")
        with open(path, "w") as f:
            f.write("previous")
        os.chmod(path, 0o600)
        setup(self, *args)

    def check_submission(job):
        path = os.path.join(job.builder.outdir, "config.txt")
        with open(path) as f:
            modes.append((f.read(), _mode(path)))

    monkeypatch.setattr(ReanaPipelineJob, "_setup", create_private_file)
    workflow = _get_workflow(
        [{"entryname": "config.txt", "entry": "literal", "writable": True}]
    )
    _run_workflow(workflow, workspace, monkeypatch, check_submission)

    assert modes == [("literal", 0o660)]


@pytest.mark.parametrize(
    "mode, shared_mode",
    [(0o400, 0o440), (0o644, 0o664), (0o700, 0o770), (0o2700, 0o2770), (0o755, 0o775)],
)
def test_share_with_group(tmp_path, mode, shared_mode):
    """The group must get the permissions of the owner, and nothing else."""
    path = tmp_path / "path"
    path.mkdir() if mode & stat.S_IXUSR else path.touch()
    path.chmod(mode)

    share_with_group(tmp_path, path)

    assert stat.S_IMODE(path.stat().st_mode) == shared_mode


def test_share_with_group_accepts_shared_files_of_other_users(tmp_path, monkeypatch):
    """Permissions that are already sufficient must not be changed."""
    (tmp_path / "file").touch()
    (tmp_path / "file").chmod(0o664)
    fchmod = mock.Mock(side_effect=PermissionError)
    monkeypatch.setattr("reana_workflow_engine_cwl.utils.os.fchmod", fchmod)

    share_with_group(tmp_path, tmp_path / "file")

    fchmod.assert_not_called()


@pytest.mark.parametrize("path", ["link", "link/file", "tree"])
def test_share_tree_with_group_does_not_follow_symlinks(tmp_path, path):
    """Neither a link nor the links in a directory must be followed."""
    target = tmp_path / "target"
    target.mkdir()
    (target / "file").touch()
    (target / "file").chmod(0o600)
    target.chmod(0o700)
    directory = tmp_path / "directory"
    (directory / "tree").mkdir(parents=True)
    for link in (directory / "link", directory / "tree" / "link"):
        link.symlink_to(target)
    (directory / "tree" / "file-link").symlink_to(target / "file")

    share_tree_with_group(directory, directory / path)

    assert _mode(target) == 0o700
    assert _mode(target / "file") == 0o600


def test_share_tree_with_group_continues_after_failures(tmp_path, monkeypatch):
    """A file that cannot be shared must not prevent sharing the others."""
    directory = tmp_path / "directory"
    directory.mkdir()
    for name in ("a", "b", "c"):
        (directory / name).touch()
        (directory / name).chmod(0o600)
    fchmod = os.fchmod
    failed = []

    def fail_for_first_file(fd, mode):
        if not failed and stat.S_ISREG(os.fstat(fd).st_mode):
            failed.append(fd)
            raise PermissionError
        fchmod(fd, mode)

    monkeypatch.setattr(
        "reana_workflow_engine_cwl.utils.os.fchmod", fail_for_first_file
    )

    share_tree_with_group(tmp_path, directory)

    modes = sorted(_mode(directory / name) for name in ("a", "b", "c"))
    assert modes == [0o600, 0o660, 0o660]
