import math
from textwrap import dedent
from tool_aws.utils import reprojectBBox
from gatilegrid import getTileGrid


"""
Function that yields successive n-sized chunks from l.
"""


def chunks(l, n):
    for i in xrange(0, len(l), n):
        yield l[i:i + n]


"""
Function that returns how many keys should be deleted at a time per process.
"""


def getMaxChunkSize(nbProc, nbKeys, maxChunkSize=1000):
    chunkSize = float(nbKeys) / float(nbProc)
    chunkSize = 1 if chunkSize < 1 and chunkSize > 0 else math.floor(chunkSize)
    return int(min(chunkSize, maxChunkSize))


"""
Function that returns keys given a bucket object and prefix.
"""


def getKeysFromS3(s3Bucket, prefix, maxKeys):
    if prefix.startswith('/'):
        prefix = prefix[1:]
    return [{'Key': i.key}
            for i in s3Bucket.objects.filter(Prefix=prefix).limit(maxKeys)]


"""
Function that returns tiles keys given a prefix, a bbox and an image format.
"""


def getKeysTilingScheme(prefix, srids, bbox, imageFormat, lowRes, highRes):
    pathLength = len([p for p in prefix.split('/') if p])
    for s in srids:
        g = getTileGrid(s)(extent=reprojectBBox(bbox, s))
        minZoom = g.getClosestZoom(lowRes)
        maxZoom = g.getClosestZoom(highRes)
        for tileBounds, zoom, col, row in g.iterGrid(minZoom, maxZoom):
            if g.spatialReference == 21781:
                col, row = row, col
            if pathLength == 5:
                yield {
                    'Key': prefix + '%s/%s/%s.%s' % (zoom, col, row,
                                                     imageFormat)
                }
            elif pathLength == 4:
                yield {
                    'Key': prefix + '%s/%s/%s/%s.%s' % (g.spatialReference,
                                                        zoom, col, row,
                                                        imageFormat)
                }


class S3Keys:
    """
    This class is used to generate chunks of keys, based on prefix key.
    """

    def __init__(
            self, s3Bucket, prefix,
            chunkSize=1, srids=[], bbox=[],
            maxKeys=32000, imageFormat='png', lowRes=0, highRes=float('inf')):
        self._prefix = prefix
        self._chunkSize = chunkSize
        if not bbox:
            # Returns a list
            self._keys = getKeysFromS3(s3Bucket, prefix, maxKeys)
            self._keysGenerator = None
        else:
            # Returns a generator
            self._keys = []
            self._keysGenerator = getKeysTilingScheme(
                prefix, srids, bbox, imageFormat, lowRes, highRes)
        self._chunkedKeys = chunks(self._keys, self._chunkSize)
        self._bucketName = s3Bucket.name
        self._maxKeys = maxKeys
        self._srids = srids
        self._bbox = bbox

    def __str__(self):
        return dedent("""\\n
            Number of keys: %d
            Chunk size    : %d
            Prefix        : %s
            Bucket name   : %s
            """ % (len(self._keys), self._chunkSize,
                   self._prefix, self._bucketName))

    def __iter__(self):
        for cKeys in self._chunkedKeys:
            yield {'Objects': cKeys, 'Quiet': True}

    def __len__(self):
        return len(self._keys)

    def chunk(self, chunkSize):
        self._chunkSize = chunkSize
        if not self._bbox:
            self._chunkedKeys = chunks(self._keys, self._chunkSize)
        else:
            self._iterKeys()
            self._chunkedKeys = chunks(self._keys, self._chunkSize)

    def _iterKeys(self):
        i = 0
        self._keys = []
        for k in self._keysGenerator:
            self._keys.append(k)
            i += 1
            if i == self._maxKeys:
                break

    @property
    def prefix(self):
        return self._prefix

    @property
    def chunkedKeys(self):
        return self._chunkedKeys

    @property
    def chunkSize(self):
        return self._chunkSize

    @property
    def maxKeys(self):
        return self._maxKeys
