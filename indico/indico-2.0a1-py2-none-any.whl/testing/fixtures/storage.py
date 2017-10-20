# This file is part of Indico.
# Copyright (C) 2002 - 2017 European Organization for Nuclear Research (CERN).
#
# Indico is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 3 of the
# License, or (at your option) any later version.
#
# Indico is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Indico; if not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

from hashlib import md5
from io import BytesIO

import pytest

from indico.core import signals
from indico.core.storage.backend import Storage
from indico.modules.attachments.models.attachments import Attachment, AttachmentFile, AttachmentType
from indico.modules.attachments.models.folders import AttachmentFolder


@signals.get_storage_backends.connect
def _get_storage_backends(sender, **kwargs):
    return MemoryStorage


class MemoryStorage(Storage):
    name = 'mem'
    files = {}

    def _get_file_content(self, file_id):
        return self.files[file_id][2]

    def open(self, file_id):
        return BytesIO(self._get_file_content(file_id))

    def save(self, file_id, content_type, filename, fileobj):
        data = self._ensure_fileobj(fileobj).read()
        self.files[file_id] = (content_type, filename, data)
        return file_id, md5(data).hexdigest().decode('ascii')

    def delete(self, file_id):
        del self.files[file_id]

    def getsize(self, file_id):
        return len(self._get_file_content(file_id))


@pytest.fixture
def dummy_attachment(dummy_user):
    folder = AttachmentFolder(title='dummy_folder', description='a dummy folder')
    file_ = AttachmentFile(user=dummy_user, filename='dummy_file.txt', content_type='text/plain')
    return Attachment(folder=folder, user=dummy_user, title='dummy_attachment', type=AttachmentType.file, file=file_)
