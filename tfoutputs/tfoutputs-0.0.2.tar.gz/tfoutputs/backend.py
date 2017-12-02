import boto3
import tempfile


class Backend(object):
    def save(self):
        """
        Must always override this method to create a backend
        Should always return a local path to th e state file
        """
        pass


class S3Backend(Backend):
    def __init__(self, options):
        self.__bucket_name = options['bucket_name']
        self.__bucket_key = options['bucket_key']
        self.__bucket_region = options['bucket_region']

    def save(self):
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(self.__bucket_name)
        with tempfile.NamedTemporaryFile(delete=False) as fp:
            bucket.download_fileobj(self.__bucket_key, fp)
            fp.close()
            return fp.name


class FileBackend(Backend):
    def __init__(self, options):
        self.__path = options['path']

    def save(self):
        return self.__path
