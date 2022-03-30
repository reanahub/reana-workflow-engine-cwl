# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2018, 2019, 2020, 2021 CERN.
#
# REANA is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Rest API endpoint for workflow management."""

from __future__ import absolute_import

import logging
import time


class SQLiteHandler(logging.StreamHandler):
    """
    Logging handler for SQLite.

    Based on Vinay Sajip's DBHandler class
    (http://www.red-dove.com/python_logging.html)

    This version sacrifices performance for thread-safety:
    Instead of using a persistent cursor, we open/close
    connections for each entry.

    AFAIK this is necessary in multi-threaded applications,
    because SQLite doesn't allow access to objects across threads.
    """

    def __init__(self, workflow_uuid, publisher, stream=None):
        """
        Initialize the handler.

        If stream is not specified, sys.stderr is used.
        """
        logging.StreamHandler.__init__(self, stream)
        self.workflow_uuid = workflow_uuid
        self.publisher = publisher

    def formatDBTime(self, record):
        """Format DB time."""
        record.dbtime = time.strftime(
            "%Y-%m-%d %H:%M:%S", time.localtime(record.created)
        )

    def emit(self, record):
        """
        Emit a record.

        If a formatter is specified, it is used to format the record.
        The record is then written to the stream with a trailing newline.  If
        exception information is present, it is formatted using
        traceback.print_exception and appended to the stream.  If the stream
        has an 'encoding' attribute, it is used to determine how to do the
        output to the stream.
        """
        try:
            logs = self.format(record)
            stream = self.stream
            fs = "%s\n"

            try:
                if getattr(stream, "encoding", None):
                    ufs = "%s\n"
                    try:
                        stream.write(ufs % logs)
                        self.publisher.publish_workflow_status(
                            self.workflow_uuid, 1, logs
                        )

                    except UnicodeEncodeError:
                        # Printing to terminals sometimes fails.
                        # For example,
                        # with an encoding of 'cp1251', the above write
                        # will work if written to a stream opened or
                        # wrapped by the codecs module, but fail when
                        # writing to a terminal even when the codepage
                        # is set to cp1251. An extra encoding step seems
                        # to be needed.
                        stream.write((ufs % logs).encode(stream.encoding))
                        self.publisher.publish_workflow_status(
                            self.workflow_uuid, 1, logs
                        )

                else:
                    stream.write(fs % logs)
                    self.publisher.publish_workflow_status(self.workflow_uuid, 1, logs)

            except UnicodeError:
                stream.write(fs % logs.encode("UTF-8"))
                self.publisher.publish_workflow_status(
                    self.workflow_uuid, 1, logs.encode("UTF-8")
                )

            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            self.handleError(record)
