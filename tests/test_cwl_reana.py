# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2026 CERN.
#
# REANA is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""REANA CWL job tests."""

import stat
import subprocess
from types import SimpleNamespace

import shellescape

from reana_workflow_engine_cwl.cwl_reana import ReanaPipelineJob


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


def test_share_job_directories(tmp_path):
    """Give the workspace group access to the job directories."""
    job = object.__new__(ReanaPipelineJob)
    directories = [tmp_path / name for name in ("out", "job", "tmp", "stage")]
    for directory in directories:
        directory.mkdir(mode=0o700)
    job.outdir, builder_outdir, job.tmpdir, job.stagedir = map(str, directories)
    job.builder = SimpleNamespace(outdir=builder_outdir)

    job._share_job_directories()

    for directory in directories:
        assert stat.S_IMODE(directory.stat().st_mode) == 0o775


def test_share_job_directories_skips_missing(tmp_path):
    """Skip job directories that do not exist."""
    job = object.__new__(ReanaPipelineJob)
    job.outdir = str(tmp_path / "outdir")
    job.tmpdir = str(tmp_path / "missing")
    job.stagedir = None
    job.builder = SimpleNamespace(outdir=str(tmp_path / "missing"))
    (tmp_path / "outdir").mkdir(mode=0o700)

    job._share_job_directories()

    assert stat.S_IMODE((tmp_path / "outdir").stat().st_mode) == 0o775
