#!/usr/bin/python
#
# runDocker.py - Functions to run and interact with the docker container.
#
# Copyright 2017 Clinc2Clound Team
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY
# WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import docker
import tarfile
import tempfile
import os

client = docker.from_env()

CONTAINER_NAME = "ilent2/clinic2cloud"

INPUT_TARGET = "/home/neuro/"
OUTPUT_FILENAME = "output.mnc"
OUTPUT_TARGET = "/home/neuro/" + OUTPUT_FILENAME

def startDocker(dataSet):
    """ Start a new docker instance and copy the data into the container.

    @param dataSet      The folder name that container the input DICOM.
    @return container   Reference to the created docker container.
    """

    # Check for updates to the docker image
    client.images.pull(CONTAINER_NAME)

    container = client.api.create_container(CONTAINER_NAME)

    with docker.utils.tar(dataSet) as tar:
        client.api.put_archive(container, INPUT_TARGET, tar)

    client.api.start(container)

    return container

def waitUntilDone(container):
    """ Blocks until the docker container has processed the files.

    @param container    The container object returned by startDocker.
    @return jobStatus   Returns 0 if docker ran successfully.
    """

    return client.api.wait(container)

def checkIfDone(container):
    """ Checks if the docker has processed the files (non-blocking).
    To get the jobStatus you will need to call get status.

    @param container    The container object returned by startDocker.
    @return done        Returns True if stopped, False if running.
    """

    inspect = client.api.inspect_container(container['Id'])
    return inspect['State']['Running'] == False

def getStatus(container):
    """ Get the status of the docker job.

    @param container    The container object returned by startDocker.
    @return jobStatus   Returns 0 if docker ran successfully.
    """

    if not checkIfDone(container):
        raise Exception("Container not stopped.")

    inspect = client.api.inspect_container(container['Id'])
    return inspect['State']['ExitCode']

def finalizeJob(container, outputDir):
    """ Copy data out of docker and free resources.

    @param container    The container object returned by startDocker.
    @param outputDir    Directory name for the output MINC file.
    @return None
    """

    with tempfile.NamedTemporaryFile() as tmpfile:
        strm, stat = client.api.get_archive(container, OUTPUT_TARGET)

        for d in strm:
            tmpfile.write(d)
        tmpfile.seek(0)

        tar = tarfile.open(fileobj=tmpfile)
        tar.extractall(path=outputDir)
        tar.close()

