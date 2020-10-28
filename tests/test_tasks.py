# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2020 CERN.
#
# REANA is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""REANA-Workflow-Engine-CWL tasks tests."""


def test_parse_str_to_int():
    """Test parse_str_to_int"""
    from reana_workflow_engine_cwl.tasks import parse_str_to_int

    assert parse_str_to_int({"sleeptime": "'2'"}) == {"sleeptime": 2}
    assert parse_str_to_int({"sleeptime": "2"}) == {"sleeptime": 2}
    assert parse_str_to_int({"sleeptime": "two"}) == {"sleeptime": "two"}
    assert parse_str_to_int({"helloworld": {"class": "File"}}) == {
        "helloworld": {"class": "File"}
    }
