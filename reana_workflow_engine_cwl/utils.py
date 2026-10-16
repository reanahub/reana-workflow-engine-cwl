# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2026 CERN.
#
# REANA is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""REANA Workflow Engine CWL utilities."""

import logging
import os
import stat

from reana_commons import workspace
from reana_commons.errors import REANAWorkspaceError

from reana_workflow_engine_cwl.config import LOGGING_MODULE

log = logging.getLogger(LOGGING_MODULE)


def share_with_group(workflow_workspace, path):
    """Give the group of a file or directory the same permissions as its owner.

    The jobs share the group with the workflow engine, but not always the UID.
    Other permissions are kept.

    :param workflow_workspace: Path to the workspace of the workflow.
    :param path: Path to share, inside the workspace.
    :raises REANAWorkspaceError: If the path is not in the workspace or if it
        contains symbolic links.
    """
    fd = workspace.open_fd(workflow_workspace, _relative(workflow_workspace, path))
    try:
        mode = stat.S_IMODE(os.fstat(fd).st_mode)
        shared_mode = mode | (mode & stat.S_IRWXU) >> 3
        if mode != shared_mode:
            os.fchmod(fd, shared_mode)
    finally:
        os.close(fd)


def share_tree_with_group(workflow_workspace, path):
    """Share a file, or a directory and all its contents, with the group.

    Symbolic links are skipped. The jobs of a workflow use the same working
    directory, so some files can belong to a job with another UID, and only that
    job can share them.

    :param workflow_workspace: Path to the workspace of the workflow.
    :param path: Path to share, inside the workspace.
    """

    def share(path):
        try:
            share_with_group(workflow_workspace, path)
        except REANAWorkspaceError as e:
            log.debug(f"Not sharing {path} with the group: {e}")
        except OSError as e:
            log.warning(f"Cannot share {path} with the group: {e}")

    share(path)
    relative_path = _relative(workflow_workspace, path)
    if workspace.is_directory(workflow_workspace, relative_path):
        try:
            for entry in workspace.walk(workflow_workspace, relative_path):
                share(os.path.join(workflow_workspace, entry))
        except OSError as e:
            log.warning(f"Cannot list {path}: {e}")


def _relative(workflow_workspace, path):
    """Return the path relative to the workspace, without resolving links."""
    return os.path.relpath(path, workflow_workspace)
