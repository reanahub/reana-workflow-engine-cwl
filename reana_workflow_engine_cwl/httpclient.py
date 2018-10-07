# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2017, 2018 CERN.
#
# REANA is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""REANA Workflow Engine CWL http client of REANA Job Controller."""

import json
import logging

import requests

from reana_workflow_engine_cwl.config import JOBCONTROLLER_HOST

log = logging.getLogger('yadage.cap.submit')


class ReanaJobControllerHTTPClient:
    """REANA-Job-Controller http client class."""

    def submit(self, experiment, image, cmd, workflow_workspace,
               prettified_cmd, job_name):
        """Submit a new job."""
        job_spec = {
            'experiment': experiment,
            'docker_img': image,
            'cmd': cmd,
            'max_restart_count': 0,
            'env_vars': {},
            'workflow_workspace': workflow_workspace,
            'prettified_cmd': prettified_cmd,
            'job_name': job_name
        }

        log.info('submitting %s', json.dumps(job_spec, indent=4,
                                             sort_keys=True))

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
        """Check status of a job."""
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
        """Get logs of a job."""
        response = requests.get(
            'http://{host}/{resource}/{id}/logs'.format(
                host=JOBCONTROLLER_HOST,
                resource='jobs',
                id=job_id
            ),
            headers={'cache-control': 'no-cache'}
        )

        return response.text
