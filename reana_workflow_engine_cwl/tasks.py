# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2017, 2018 CERN.
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

"""REANA Workflow Engine CWL tasks."""

from __future__ import absolute_import, print_function

import json
import logging

from reana_commons.publisher import Publisher

from reana_workflow_engine_cwl import main
from reana_workflow_engine_cwl.celeryapp import app

log = logging.getLogger(__name__)
outputs_dir_name = 'outputs'
known_dirs = ['inputs', 'logs', outputs_dir_name]


@app.task(name='tasks.run_cwl_workflow', ignore_result=True)
def run_cwl_workflow(workflow_uuid, workflow_workspace,
                     workflow_json=None,
                     parameters=None):
    """Run cwl workflow."""
    log.info('running workflow on context: {0}'.format(locals()))
    try:
        publisher = Publisher()
        publisher.connect()
        main.main(workflow_uuid, workflow_json,
                  parameters, workflow_workspace, publisher)
        log.info('workflow done')
        publisher.publish_workflow_status(workflow_uuid, 2)
    except Exception as e:
        log.error('workflow failed: {0}'.format(e))
        publisher.publish_workflow_status(workflow_uuid, 3, message=str(e))
    finally:
        publisher.close()
