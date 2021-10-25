# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2018, 2019, 2020, 2021 CERN.

# REANA is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""REANA Workflow Engine CWL's RJC jobs status polling class."""


from __future__ import absolute_import, print_function, unicode_literals

import threading


class PollThread(threading.Thread):
    """Polling thread class."""

    def __init__(self, operation, poll_interval=5, poll_retries=10):
        """Instanciate poll thread."""
        super(PollThread, self).__init__()
        self.daemon = True
        self.operation = operation
        self.id = operation["job_id"]
        self.poll_interval = poll_interval
        self.poll_retries = poll_retries

    def poll(self):
        """Poll."""
        raise Exception("PollThread.poll() not implemented")

    def is_done(self, operation):
        """Check if operation is done."""
        raise Exception("PollThread.is_done(operation) not implemented")

    def complete(self, operation):
        """Check if operation is complete."""
        raise Exception("PollThread.complete(operation) not implemented")

    def run(self):
        """Run polling thread."""
        raise Exception("PollThread.run() not implemented")
