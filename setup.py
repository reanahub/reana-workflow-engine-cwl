# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2017, 2018, 2019 CERN.
#
# REANA is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""REANA-Workflow-Engine-CWL."""

from __future__ import absolute_import, print_function

import os
import re

from setuptools import find_packages, setup

readme = open('README.rst').read()
history = open('CHANGES.rst').read()

tests_require = [
    'pytest-reana>=0.6.0.dev20190705,<0.7.0',
]

extras_require = {
    'docs': [
        'Sphinx>=1.4.4,<1.6',
        'sphinx-rtd-theme>=0.1.9'
    ],
    'tests': tests_require,
}

extras_require['all'] = []
for key, reqs in extras_require.items():
    if ':' == key[0]:
        continue
    extras_require['all'].extend(reqs)

setup_requires = [
    'pytest-runner>=2.7',
]

install_requires = [
    'cwltool==1.0.20190815141648',
    'schema-salad==4.5.20190815125611',
    'click>=7',
    'enum34>=1.1.6',
    'SQLAlchemy>=1.3.7',
    'SQLAlchemy-Utils>=0.34.2',
    'reana-commons>=0.6.0.dev20190823,<0.7.0',
]

packages = find_packages()


# Get the version string. Cannot be done with import!
with open(os.path.join('reana_workflow_engine_cwl', 'version.py'), 'rt') as f:
    version = re.search(
        '__version__\s*=\s*"(?P<version>.*)"\n',
        f.read()
    ).group('version')

setup(
    name='reana-workflow-engine-cwl',
    version=version,
    description=__doc__,
    long_description=readme + '\n\n' + history,
    author='REANA',
    author_email='info@reana.io',
    url='https://github.com/reanahub/reana-workflow-engine-cwl',
    packages=['reana_workflow_engine_cwl'],
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'run-cwl-workflow='
            'reana_workflow_engine_cwl.tasks:run_cwl_workflow',
        ]
    },
    extras_require=extras_require,
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
