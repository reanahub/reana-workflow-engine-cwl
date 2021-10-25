# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2018, 2020, 2021 CERN.
#
# REANA is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""REANA ``cwltool`` contexts."""

from cwltool.context import RuntimeContext


class REANARuntimeContext(RuntimeContext):
    """REANA runtime context."""

    def __init__(self, workflow_uuid, working_dir, publisher, pipeline, **kwargs):
        """REANA runtime context constructor."""
        self.workflow_uuid = workflow_uuid or None
        self.working_dir = working_dir or None
        self.publisher = publisher or None
        self.pipeline = pipeline or None
        super(REANARuntimeContext, self).__init__(kwargs)
