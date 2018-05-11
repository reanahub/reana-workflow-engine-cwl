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

"""Rest API endpoint for workflow management."""

from __future__ import absolute_import

import logging
import time
from logging import StreamHandler

from reana_workflow_engine_cwl.utils import publish_workflow_status


class SQLiteHandler(StreamHandler):
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

    def __init__(self, workflow_uuid, stream=None):
        """
        Initialize the handler.

        If stream is not specified, sys.stderr is used.
        """
        StreamHandler.__init__(self, stream)
        self.workflow_uuid = workflow_uuid

    def formatDBTime(self, record):
        record.dbtime = time.strftime(
            "%Y-%m-%d %H:%M:%S", time.localtime(record.created))

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
            if not logging._unicode:  # if no unicode support...
                stream.write(fs % logs)
                publish_workflow_status(self.workflow_uuid, 1, logs)
            else:
                try:
                    if (isinstance(logs, unicode) and
                            getattr(stream, 'encoding', None)):
                        ufs = u'%s\n'
                        try:
                            stream.write(ufs % logs)
                            publish_workflow_status(self.workflow_uuid,
                                                    1,
                                                    logs)

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
                            publish_workflow_status(
                                self.workflow_uuid, 1, logs)

                    else:
                        stream.write(fs % logs)
                        publish_workflow_status(
                            self.workflow_uuid, 1, logs)

                except UnicodeError:
                    stream.write(fs % logs.encode("UTF-8"))
                    publish_workflow_status(
                        self.workflow_uuid, 1, logs.encode("UTF-8"))
            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            self.handleError(record)
