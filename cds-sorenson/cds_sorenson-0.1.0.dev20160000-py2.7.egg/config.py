# -*- coding: utf-8 -*-
#
# This file is part of CERN Document Server.
# Copyright (C) 2016 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""CDS Sorenson default application configuration."""

from __future__ import absolute_import, print_function


CDS_SORENSON_USERNAME = ''
CDS_SORENSON_PASSWORD = ''
"""Username and password to access the video on file system.

Important: The username and password will be visible in the metadata on the
Sorenson server, so please use a separate account just for Sorenson!
"""

CDS_SORENSON_INPUT_FOLDER = ''
"""Input folder from where the file will be read.

For example: file://cern.ch/dfs/Users/s/switowsk/Sorenson/INPUT/
"""

CDS_SORENSON_OUTPUT_FOLDER = ''
"""Output folder where the transcoded files will be stored

For example: file://cern.ch/dfs/Users/s/switowsk/Sorenson/OUTPUT/
"""

CDS_SORENSON_SUBMIT_URL = 'http://sorenson03.cern.ch/api/jobs'
"""Sorenson endpoint for submitting a new transcoding job."""

CDS_SORENSON_DELETE_URL = 'http://sorenson03.cern.ch/api/jobs/{job_id}'
"""Sorenson endpoint for deleting a transcoding job."""

CDS_SORENSON_CURRENT_JOBS_STATUS_URL = 'http://sorenson03.cern.ch/api/jobs/status/{job_id}'
"""Sorenson endpoint for getting the status of a job waiting in the queue."""

CDS_SORENSON_ARCHIVE_JOBS_STATUS_URL = 'http://sorenson03.cern.ch/api/jobs/archive/{job_id}'
"""Sorenson endpoint for getting the status of an archived (done) job."""

CDS_SORENSON_DEFAULT_QUEUE = '00000000-0000-0000-0000-000000000000'
"""Default queue for all transcoding jobs."""

CDS_SORENSON_PRESETS = {
    'Youtube 480p': ('2c5a86db-1018-4ff8-a5ad-daebd4cb4ff4', '.mp4'),
}
"""List of presets available on Sorenson server.

Maps the names of presets (that will be used in CDS) to the preset IDs on
Sorenson server and the output file extension.
"""
