import minio
import io
import os
import shutil
import tempfile
import uuid

from qwertyui import urlparse


def get_minio_client(url, access_key, secret_key, region='eu-central-1', bucket=None):
    """
    Wrapper for getting minio.Minio class.
    Can optionally generate a bucket if parameter is provided.
    """

    parsed = urlparse(url)
    secure = parsed.scheme == 'https'

    mc = minio.Minio(
        parsed.netloc,
        access_key,
        secret_key,
        region=region,
        secure=secure
    )

    if not bucket:
        return mc

    if not mc.bucket_exists(bucket):
        mc.make_bucket(bucket, location=region)

    return mc


def exists(client, bucket, path):
    return any(
        obj
        for obj in client.list_objects(bucket, path)
        if obj.object_name.strip(os.path.sep) == path.strip(os.path.sep)
    )


def listdir(client, bucket, path):
    # 'recursive' option recurses into the whole tree, we limit only to first level
    if path and not path.endswith('/'):
        path = '%s/' % path
    lst = [
        obj.object_name.replace(path, '', 1)
        for obj in client.list_objects(bucket, path, recursive=False)
    ]
    directories = set(
        p.split('/')[0]
        for p in lst
        if p.endswith('/')
        #if os.path.dirname(p)
    )

    # Tuple of directories, files
    return (
        sorted(directories), [
            p
            for p in lst
            if not p.endswith('/')
            #if not os.path.dirname(p)
        ]
    )


def remove(client, bucket, path):
    return client.remove_object(bucket, path)


def remove_recursive(client, bucket, path):
    directories, files = listdir(client, bucket, path)

    for file_name in files:
        remove(client, bucket, os.path.join(path, file_name))

    for directory in directories:
        remove_recursive(client, bucket, os.path.join(path, directory))


def open(client, bucket, path):
    return client.get_object(
        bucket,
        path
    )


def download_to_tempfile(client, bucket, src):
    path, ext = os.path.splitext(src)

    temp_file = tempfile.NamedTemporaryFile(suffix=ext)
    shutil.copyfileobj(open(client, bucket, src), temp_file)
    temp_file.seek(0)

    return temp_file


def upload_file(client,
                bucket,
                file_path,
                minio_file_path,
                content_type=None,
                metadata=None):
    """
    Uploads single file directly to a minio_path.
    """

    size = os.stat(file_path).st_size

    with io.open(file_path, 'rb') as f:
        client.put_object(
            bucket,
            minio_file_path,
            f,
            size,
            content_type=content_type or 'application/octet-stream',
            metadata=metadata
        )

    return minio_file_path


def upload_file_to_minio_directory(client,
                                   bucket,
                                   file_path,
                                   minio_directory,
                                   content_type=None,
                                   metadata=None):
    """
    Uploads single file to a minio directory.
    minio_directory path is joined with filename from file_path.
    """

    file_name = os.path.split(file_path)[1]
    # TODO: can be problematic on Windows but well... I'm too lazy for this
    minio_file_path = os.path.join(minio_directory, file_name)

    return upload_file(
        client,
        bucket,
        file_path,
        minio_file_path,
        content_type=content_type,
        metadata=metadata
    )


def upload_directory(client, bucket, directory_path, minio_directory):
    """
    Uploads whole directory structure to minio (recursively).
    """

    file_paths = []

    for directory, directories, files in os.walk(directory_path):
        # TODO: can be problematic on Windows but well... I'm too lazy for this
        d = directory.replace(directory_path, '').lstrip(os.path.sep)
        destination_directory = os.path.join(minio_directory, d)

        for filename in files:
            minio_file_path = upload_file_to_minio_directory(
                client,
                bucket,
                os.path.join(directory, filename),
                destination_directory
            )
            file_paths.append(minio_file_path)

    return file_paths


def write_content(client, bucket, path, content):
    temp_file = tempfile.NamedTemporaryFile()
    if isinstance(content, str):
        content = content.encode('utf-8')
    temp_file.file.write(content)
    temp_file.file.flush()

    return upload_file(client, bucket, temp_file.name, path)


def size(client, bucket, file_path):
    return client.stat_object(bucket, file_path).size


def copy(client, bucket, src, dst):
    client.copy_object(
        bucket,
        dst,
        os.path.join(bucket, src)
    )


def get_content_type(client, bucket, path):
    return client.stat_object(
        bucket,
        path
    ).content_type


def reserve_temp_dir(client, bucket, root_dir, empty_file_name='_'):
    """
    Reserves a temp dir on Minio.
    Normally, Minio does not have directories, only files.
    That's why we write an empty file in that reserved directory.
    You can customize its name by setting the empty_file_name variable.
    """

    while True:
        dir_name = str(uuid.uuid4())
        dir_path = os.path.join(root_dir, dir_name)
        try:
            next(client.list_objects(bucket, prefix=dir_path))
            continue
        except StopIteration:
            write_content(
                client,
                bucket,
                os.path.join(dir_path, empty_file_name),
                ''
            )
            return dir_path
