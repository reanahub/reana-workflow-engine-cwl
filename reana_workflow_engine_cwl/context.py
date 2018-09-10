# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2018 CERN.
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

"""REANA ``cwltool`` contexts."""

from cwltool.context import RuntimeContext


class REANARuntimeContext(RuntimeContext):
    """REANA runtime context."""

    def __init__(self, workflow_uuid, working_dir, publisher, pipeline,
                 **kwargs):
        """REANA runtime context constructor."""
        self.workflow_uuid = workflow_uuid or None
        self.working_dir = working_dir or None
        self.publisher = publisher or None
        self.pipeline = pipeline or None
        super(REANARuntimeContext, self).__init__(kwargs)
