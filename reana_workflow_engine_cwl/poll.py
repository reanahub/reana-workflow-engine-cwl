# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2017, 2018 CERN.

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

"""REANA Workflow Engine CWL polling thread."""


from __future__ import absolute_import, print_function, unicode_literals

import threading


class PollThread(threading.Thread):
    """Polling thread class."""

    def __init__(self, operation, poll_interval=5, poll_retries=10):
        """Constructor."""
        super(PollThread, self).__init__()
        self.daemon = True
        self.operation = operation
        self.id = operation['job_id']
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
