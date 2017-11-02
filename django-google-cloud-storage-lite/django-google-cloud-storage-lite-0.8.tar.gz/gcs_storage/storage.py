from django.core.files.base import ContentFile
from django.core.files.storage import Storage
from django.conf import settings
from django.utils.text import slugify
from google.cloud import storage
import os, uuid


class GoogleCloudStorage(Storage):
    def __init__(self):
        bucket = settings.GOOGLE_CLOUD_STORAGE_BUCKET
        self.client = storage.Client()
        self.bucket = self.client.bucket(bucket)
        self.base_url = "https://storage.googleapis.com/%s" % bucket

    def get_available_name(self, name, max_length=None):
        name, ext = os.path.splitext(name)
        if ext:
            return "%s%s" % (slugify(name), ext)

        return uuid.uuid4()

    def _open(self, name, mode):
        blob = self.bucket.get_blob(name)
        return ContentFile(blob.download_as_string())

    def _save(self, name, content):
        blob = self.bucket.blob(name)
        blob.upload_from_file(content.file, size=content.size)
        return name

    def delete(self, name):
        self.bucket.delete_blob(name)

    def url(self, name):
        return self.base_url + "/" + name

    def exists(self, name):
        return self.bucket.blob(name).exists()

    def size(self, name):
        return self.bucket.get_blob(name).size
