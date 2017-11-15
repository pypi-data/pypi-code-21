import logging
import zlib

LOGGER = logging.getLogger(__name__)

BLOCKSIZE = 200
class ZBuffer():
    ZIPPER = lambda: None
    def __init__(self, stream, blocksize=BLOCKSIZE):
        self.blocksize  = blocksize
        self.done       = False
        self.stream     = stream
        self.zipper     = self.ZIPPER()

    def __iter__(self):
        return self

    def __next__(self):
        if self.done:
            LOGGER.debug("Stopping iteration")
            raise StopIteration()
        block = self.read(self.blocksize)
        return block

    def close(self):
        self.stream.close()

    def read(self, size=None):
        result = b''
        while result == b'':
            if self.done:
                return result
            block = self.stream.read(size)
            if not block:
                LOGGER.debug("block is empty, flushing")
                self.done = True
                result = self.zipper.flush()
                LOGGER.debug("Flushed underlying zipped block and got %d bytes", len(result))
                return result
            result = self.process(block)
        LOGGER.debug("Providing zipped block of %d bytes from source of %d bytes", len(result), len(block))
        return result

    def process(self, block):
        raise NotImplementedError()

class ZipBuffer(ZBuffer):
    ZIPPER = zlib.compressobj
    def process(self, block):
        return self.zipper.compress(block)

class UnzipBuffer(ZBuffer):
    ZIPPER = zlib.decompressobj
    def process(self, block):
        return self.zipper.decompress(block)
