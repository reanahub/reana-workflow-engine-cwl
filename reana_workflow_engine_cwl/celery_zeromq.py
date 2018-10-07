# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2017, 2018 CERN.
#
# REANA is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""ZeroMQ utilities."""

import logging

import zmq
from celery import signals

ZMQ_SOCKET_LINGER = 100
context = zmq.Context()
context.linger = ZMQ_SOCKET_LINGER

log = logging.getLogger(__name__)


def reset_zmq_context(**kwargs):
    """Reset ZeroMQ context."""
    log.debug("Resetting ZMQ Context")
    reset_context()


signals.worker_process_init.connect(reset_zmq_context)


def get_context():
    """Get context."""
    global context
    if context.closed:
        context = zmq.Context()
        context.linger = ZMQ_SOCKET_LINGER
    return context


def reset_context():
    """Reset context."""
    global context
    context.term()
    context = zmq.Context()
    context.linger = ZMQ_SOCKET_LINGER
