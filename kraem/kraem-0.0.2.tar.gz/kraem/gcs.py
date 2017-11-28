import progressbar
from google.cloud import storage

API = 'https://www.googleapis.com/upload/storage/v1/b/%s/o?uploadType=multipart'


def upload(bucket, files):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket)

    bar = progressbar.ProgressBar(max_value=len(files))

    for idx, file in enumerate(files):
        blob = bucket.blob(file)

        blob.upload_from_filename(file)

        bar.update(idx + 1)
