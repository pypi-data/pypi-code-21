import os.path as path
import boto3


def tokenize_s3path(s3path):
    if s3path.startswith('s3://'):
        s3path = s3path[5:]
    flds = s3path.split('/')
    bucket = flds[0]
    filename = flds[-1]
    key = '/'.join(flds[1:])
    return bucket, key, filename


def download_s3files(s3paths, download_dir):
    s3 = boto3.client('s3')
    localfiles = []
    for s3path in s3paths:
        bucket, key, filename = tokenize_s3path(s3path)
        localfile = path.join(download_dir, filename)
        s3.download_file(bucket, key, localfile)
        localfiles.append(localfile)
    return localfiles


def main():
    s3paths = ['s3://inrix-data-eval/RawData/Cuebiq_20161026/part_000099.tsv.gz',
               's3://inrix-data-eval/RawData/Cuebiq_20161026/part_000098.tsv.gz']
    localpaths = download_s3files(s3paths, '/Users/avilay.parekh/tmp')
    print('Files saved in -')
    [print(lp) for lp in localpaths]


if __name__ == '__main__':
    main()
