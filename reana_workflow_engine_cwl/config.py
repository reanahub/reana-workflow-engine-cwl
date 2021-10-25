# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2018, 2019, 2020, 2021 CERN.
#
# REANA is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""REANA Workflow Engine CWL configuration."""

import os

SHARED_VOLUME_PATH = os.getenv("SHARED_VOLUME_PATH", "/var/reana")
"""Path to the mounted REANA shared volume."""

MOUNT_CVMFS = os.getenv("REANA_MOUNT_CVMFS", "false")

LOGGING_MODULE = "reana-workflow-engine-cwl"
"""REANA Workflow Engine CWL logging module."""
