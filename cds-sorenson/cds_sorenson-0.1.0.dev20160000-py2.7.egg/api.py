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

"""API to use Sorenson transcoding server."""

from __future__ import absolute_import, print_function

import json
import os
import requests

from flask import current_app


class SorensonError(Exception):
    """Base class for exceptions in this module."""

    def _init_(self, error_message):
        self.error_message = error_message

    def _str_(self):
        return self.error_message


def _generate_json(input_filename, output_filename, preset_id):
    """Generate JSON that will be sent to Sorenson server.

    :param input_filename: string with the input filename.
    :param output_filename: string with the output filename.
    :param preset_id: id of the preset (taken from sorenson dashboard).
    :returns: JSON with Sorenson response.
    """
    output = {}

    input_folder = current_app.config['CDS_SORENSON_INPUT_FOLDER']
    output_folder = current_app.config['CDS_SORENSON_OUTPUT_FOLDER']
    output['Name'] = input_filename[:49]  # Name in sorenson dashboard
    output['QueueId'] = current_app.config['CDS_SORENSON_DEFAULT_QUEUE']

    source_media = {}
    source_media['FileUri'] = input_folder + input_filename
    source_media['UserName'] = current_app.config['CDS_SORENSON_USERNAME']
    source_media['Password'] = current_app.config['CDS_SORENSON_PASSWORD']

    jobInfo = {}
    jobInfo['SourceMediaList'] = [source_media]

    destination_list = {}
    destination_list['FileUri'] = output_folder + output_filename
    jobInfo['DestinationList'] = [destination_list]

    preset_id_json = {"PresetId": preset_id}
    jobInfo['CompressionPresetList'] = [preset_id_json]

    output['JobMediaInfo'] = jobInfo

    return output


def start_encoding(input_filename, preset_name):
    """Encode a video that is already in the input folder.

    :param filename: string with the filename.
    :param preset: id of the preset (taken from sorenson dashboard).
    :returns: job ID.
    """
    current_app.logger.debug("Encoding {0} with the preset {1}"
                             .format(input_filename, preset_name))

    preset_config = current_app.config['CDS_SORENSON_PRESETS'].get(preset_name)
    preset_id, extension = preset_config

    # Output file extension depends on the selected preset
    output_basename = os.path.splitext(input_filename)[0]
    output_filename = output_basename + extension

    # Build the request of the encoding job
    json_params = _generate_json(input_filename, output_filename, preset_id)

    current_app.logger.debug("Sending request to the Sorenson server")
    headers = {'Accept': 'application/json'}
    response = requests.post(current_app.config['CDS_SORENSON_SUBMIT_URL'],
                             headers=headers, json=json_params)

    data = json.loads(response.text)

    current_app.logger.debug("Response from Sorenson: {}".format(data))
    if response.status_code == requests.codes.ok:
        job_id = data.get('JobId')
        return job_id
    else:
        raise SorensonError(
            "Failed to send encoding request to the server. Received "
            "code: {0}. Make sure all parameters are set and permissions are "
            "correct".format(response.status_code)
        )


def stop_encoding(job_id):
    """Stop encoding job.

    :param job_id: string with the job ID.
    :returns: None.
    """
    # TODO: According to the docs, the job should be in "Hold", "Error" or
    # "Finished" state for this to work - check it
    delete_url = (current_app.config['CDS_SORENSON_DELETE_URL']
                             .format(job_id=job_id))
    headers = {'Accept': 'application/json'}

    response = requests.delete(delete_url, headers=headers)
    if response.status_code == requests.codes.ok:
        current_app.logger.debug("Stopped job {0}".format(job_id))
    else:
        raise SorensonError("Could not stop job: {0}".format(job_id))


def get_encoding_status(job_id):
    """Get status of a given job from the Sorenson server.

    If the job can't be found in the current queue, it's probably done, so we
    check the archival queue.

    :param job_id: string with the job ID.
    :returns: JSON with Sorenson response.
    """
    current_jobs_url = (current_app
                        .config['CDS_SORENSON_CURRENT_JOBS_STATUS_URL']
                        .format(job_id=job_id))
    archive_jobs_url = (current_app
                        .config['CDS_SORENSON_ARCHIVE_JOBS_STATUS_URL']
                        .format(job_id=job_id))

    headers = {'Accept': 'application/json'}

    current_app.logger.debug("Checking in the current jobs queue")
    response = requests.get(current_jobs_url, headers=headers)

    if response.status_code == 404:
        current_app.logger.debug("Checking in the archive jobs queue")
        response = requests.get(archive_jobs_url, headers=headers)

    if response.status_code == requests.codes.ok:
        return json.loads(response.text)
    else:
        raise SorensonError("Failed to get status for job: {0}".
                            format(response.status_code))
