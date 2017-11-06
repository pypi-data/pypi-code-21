import json
import random
import string
import subprocess
import requests
import boto3
import credstash
from cached_property import cached_property
from .lock import Lock


class Instance(object):
    tags = {}

    def __init__(self):
        self.tags = self.fetch_instance_tags()

    @property
    def role(self):
        return self.tags['Role']

    @property
    def environment(self):
        return self.tags['Environment']

    @cached_property
    def instance_id(self):
        return requests.get('http://169.254.169.254/latest/meta-data/instance-id').text

    @cached_property
    def instance_region(self):
        doc = json.loads(requests.get('http://169.254.169.254/latest/dynamic/instance-identity/document').text)
        return doc['region']

    @cached_property
    def rng(self):
        return random.SystemRandom()

    @property
    def credstash_key(self):
        return 'alias/credstash-%(environment)s'.format(environment=self.environment)

    @property
    def credstash_table(self):
        return 'credential-store-%(environment)s'.format(environment=self.environment)

    def credstash_put(self, key, secret, version=""):
        return credstash.putSecret(key, secret, version, kms_key=self.credstash_key,
                                   region=self.instance_region, table=self.credstash_table)

    def credstash_get(self, key, version=""):
        return credstash.getSecret(key, version, region=self.instance_region, table=self.credstash_table)

    def random_string(self, length=32):
        return ''.join([self.rng.choice(string.ascii_letters + string.digits) for _ in range(length)])

    def fetch_instance_tags(self):
        tags = {}
        ec2 = boto3.resource('ec2')
        ec2instance = ec2.Instance(self.instance_id)
        for tag in ec2instance.tags:
            tags[tag['Key']] = tag['Value']
        return tags

    def run(self, cmd):
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in p.stdout.readlines():
            print(line)
        return p.wait()

    def once(self, key, version=1, timeout=60):
        def func_wrapper(func):
            print('%s[%d]...' % (key, version))
            lock = Lock(key, timeout)
            try:
                was_acquired = lock.acquire(fail_hard=False)
                if was_acquired and lock.version < version:
                    result = func()
                    if result:
                        lock.version = version
            finally:
                lock.release()
            return func
        return func_wrapper

    def every(self):
        def func_wrapper(func):
            func()
        return func_wrapper
