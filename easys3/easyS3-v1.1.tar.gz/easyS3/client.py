import json
import logging
import boto3


def _get_client(client_type, access_key, secret_key):
    if client_type == "s3":
        resource = boto3.resource(client_type, aws_access_key_id=access_key, aws_secret_access_key=secret_key)
        client = boto3.client(client_type, aws_access_key_id=access_key, aws_secret_access_key=secret_key)
        return resource, client


class Client:
    """
    Connect your s3Service and read all the files from a path
    """

    def __init__(self, access_key, secret_key):
        self.s3_resource, self.s3_client = _get_client("s3", access_key, secret_key)

    def get_all_files(self, bucket_name, s3_file_prefix):
        """
        Method returns files as objects. It connects to corresponding s3 buckets and filters all the
        files based on the file_path. 
        Method does not guarantee that correct file i.e same file could exists in different buckets will be retrieved.
        This error should be handled while parsing the files.
        :return: list of file_objs
        """
        s3 = None
        bucket = None
        try:
            s3 = self.s3_resource
            bucket = s3.Bucket(bucket_name)
        except Exception as e:
            logging.error("Exception occurred while establishing s3 connection", e)
        file_objs = []
        if s3 and bucket is not None:
            files = list(bucket.objects.filter(Prefix=s3_file_prefix.lstrip("/")))
            if len(files) > 0:
                for bucket_and_key in files:
                    file_obj = s3.Object(bucket_name, bucket_and_key.key)
                    file_objs.append(file_obj)
        return file_objs

    def get_file_meta_objs(self, bucket_name, s3_path):
        meta_content = self.s3_client.list_objects_v2(Bucket=bucket_name, Prefix=s3_path)
        if meta_content:
            return meta_content

    def get_file_obj_from_s3(self, bucket_name, file_path):
        s3 = self.s3_resource
        obj = s3.Object(bucket_name, file_path)
        return obj

    def read_file_obj(self, bucket_name, file_path):
        obj = self.get_file_obj_from_s3(bucket_name, file_path)
        if obj:
            return obj.get()["Body"].read().decode('utf-8'), obj.last_modified, file_path

    def upload_file_to_s3(self, bucket_name, local_data_path, s3_path):
        try:
            s3 = self.s3_resource
            s3.meta.client.upload_file(local_data_path, bucket_name, s3_path)
        except Exception as e:
            raise e

    def upload_file_obj_s3(self, bucket_name, file_obj, s3_path):
        self.s3_client.put_object(Body=json.dumps(file_obj), Bucket=bucket_name, Key=s3_path)
