# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2017, 2018, 2019, 2020, 2021, 2022, 2024, 2025 CERN.
#
# REANA is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""REANA-Workflow-Engine-CWL."""

from __future__ import absolute_import, print_function

import os
import re

from setuptools import find_packages, setup

readme = open("README.md").read()
history = open("CHANGELOG.md").read()

extras_require = {
    "debug": [
        "wdb",
        "ipdb",
        "Flask-DebugToolbar",
    ],
    "docs": ["myst-parser", "Sphinx>=1.4.4", "sphinx-rtd-theme>=0.1.9", "Jinja2<3.1"],
    "tests": [
        "pytest-reana>=0.95.0a2,<0.96.0",
    ],
}

extras_require["all"] = []
for key, reqs in extras_require.items():
    if ":" == key[0]:
        continue
    extras_require["all"].extend(reqs)

install_requires = [
    "reana-commons[cwl]>=0.95.0a7,<0.96.0",
]

packages = find_packages()


# Get the version string. Cannot be done with import!
with open(os.path.join("reana_workflow_engine_cwl", "version.py"), "rt") as f:
    version = re.search(r'__version__\s*=\s*"(?P<version>.*)"\n', f.read()).group(
        "version"
    )

setup(
    name="reana-workflow-engine-cwl",
    version=version,
    description=__doc__,
    long_description=readme + "\n\n" + history,
    long_description_content_type="text/markdown",
    author="REANA",
    author_email="info@reana.io",
    url="https://github.com/reanahub/reana-workflow-engine-cwl",
    packages=["reana_workflow_engine_cwl"],
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "run-cwl-workflow=" "reana_workflow_engine_cwl.tasks:run_cwl_workflow",
        ]
    },
    python_requires=">=3.8",
    extras_require=extras_require,
    install_requires=install_requires,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
