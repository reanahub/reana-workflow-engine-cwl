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

import json
import logging

import requests

from reana_workflow_engine_cwl.config import JOBCONTROLLER_HOST

log = logging.getLogger('yadage.cap.submit')


class ReanaJobControllerHTTPClient:

    def submit(self, experiment, image, cmd, workflow_workspace):
        job_spec = {
            'experiment': experiment,
            'docker_img': image,
            'cmd': cmd,
            'max_restart_count': 0,
            'env_vars': {},
            'workflow_workspace': workflow_workspace
        }

        log.info('submitting %s', json.dumps(job_spec, indent=4, sort_keys=True))

        response = requests.post(
            'http://{host}/{resource}'.format(
                host=JOBCONTROLLER_HOST,
                resource='jobs'
            ),
            json=job_spec,
            headers={'content-type': 'application/json'}
        )

        job_id = str(response.json()['job_id'])
        return job_id

    def check_status(self, job_id):
        response = requests.get(
            'http://{host}/{resource}/{id}'.format(
                host=JOBCONTROLLER_HOST,
                resource='jobs',
                id=job_id
            ),
            headers={'cache-control': 'no-cache'}
        )

        job_info = response.json()
        return job_info

    def get_logs(self, job_id):
        response = requests.get(
            'http://{host}/{resource}/{id}/logs'.format(
                host=JOBCONTROLLER_HOST,
                resource='jobs',
                id=job_id
            ),
            headers={'cache-control': 'no-cache'}
        )

        return response.text
