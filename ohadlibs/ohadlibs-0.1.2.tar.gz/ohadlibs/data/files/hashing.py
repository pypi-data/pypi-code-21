import hashlib
import os


class HashCalculator:

    def __init__(self, path):
        self.path = path
        self.content = open(self.path, 'rb').read()

    def github_id(self):
        filesize_bytes = os.path.getsize(self.path)
        s = hashlib.sha1()
        s.update(("blob %u\0" % filesize_bytes).encode('utf-8'))
        s.update(self.content)
        return s.hexdigest()

    def sha1(self):
        hasher = hashlib.sha1()
        hasher.update(self.content)
        return hasher.hexdigest()

    def sha256(self):
        hasher = hashlib.sha256()
        hasher.update(self.content)
        return hasher.hexdigest()

    def md5(self):
        hasher = hashlib.md5()
        hasher.update(self.content)
        return hasher.hexdigest()
