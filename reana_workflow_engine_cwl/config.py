# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2017 CERN.
#
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

"""REANA Workflow Controller flask configuration."""

import os

BROKER = os.getenv("RABBIT_MQ", "amqp://test:1234@message-broker.default.svc.cluster.local//")
# BROKER = os.getenv("RABBIT_MQ", "amqp://reana:reana@localhost:5672/reanahost")
JOBCONTROLLER_HOST = os.getenv("JOB_CONTROLLER_HOST", 'job-controller.default.svc.cluster.local')

INPUTS_DIRECTORY_RELATIVE_PATH = 'inputs'
"""Represents the relative path to the inputs directory (populated by RWC)"""

SHARED_VOLUME = os.getenv('SHARED_VOLUME', '/reana/default')
"""Path to the mounted REANA shared volume."""

REANA_DB_FILE = './reana.db'
"""REANA SQLite db file."""

SQLALCHEMY_DATABASE_URI = \
    'sqlite:///{SHARED_VOLUME}/{REANA_DB_FILE}'.format(
        SHARED_VOLUME=SHARED_VOLUME,
        REANA_DB_FILE=REANA_DB_FILE)
"""SQL database URI."""
