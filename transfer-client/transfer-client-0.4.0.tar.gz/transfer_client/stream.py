import gzip
import hashlib
import os
import tarfile


class StreamMeta(object):
    chunk_size = 10737418240 # 10GB.

    """Make metadata for chunks of a stream."""
    def __init__(self, log_handle):
        """Initialise the class.

        :arg file log_handle: Open writable handle to a log file.
        """
        self._log_handle = log_handle

        self._hash_sum = hashlib.md5()
        self._len = 0
        self._index = 0
        self.info = []
        self.sizes = []

        self._log_message()

    def _current_file(self):
        return 'chunk_{:06d}'.format(self._index)

    def _log_message(self):
        self._log_handle.write('Calculating checksum for chunk: {}\n'.format(
            self._current_file()))

    def write(self, data):
        """Update checksum and take care of chunking.

        :arg str data: Block of data to write.
        """
        self._len += len(data)
        if self._len >= self.chunk_size:
            overhang = len(data) - (self._len - self.chunk_size)
            self._hash_sum.update(data[:overhang])
            self.flush(self.chunk_size)
            self._hash_sum = hashlib.md5()
            self._hash_sum.update(data[overhang:])
            self._len -= self.chunk_size
            self._index += 1
            self._log_message()
        else:
            self._hash_sum.update(data)

    def flush(self, size=0):
        self.info.append((self._current_file(), self._hash_sum.hexdigest()))
        self.sizes.append(size or self._len)


class Pipe(object):
    """Stream chunking pipe."""
    def __init__(self):
        """Initialisation."""
        read_fd, write_fd = os.pipe()
        read_handle = os.fdopen(read_fd)
        write_handle = os.fdopen(write_fd, 'w')

        self._read = read_handle.read
        self.write = write_handle.write
        self.flush = write_handle.flush

        self.set_file('', 0)

    def read(self, size=-1):
        """Read `size` bytes from the pipe.

        :arg int size: Number of bytes to read.

        :returns str: A block of data of length `size`.
        """
        send_size = min(self.len, size)
        self.len = max(0, self.len - size)

        return self._read(send_size)

    def skip(self, size):
        """Skip `size` bytes.

        :arg int size: Number of bytes to skip.
        """
        self.set_file('', size)
        while self.read(8192):
            pass

    def set_file(self, name, size):
        """Set the name and size of the file.

        :arg str name: Name of the file.
        :arg int size: Size of the file.
        """
        self.name = name
        self.len = size


def tgz_stream(fileobj, paths):
    """Stream a directory as a gzipped tar to a file object.

    :arg object fileobj: File object.
    :arg list paths: List of tuples (absolute path, archive path).
    """
    gzip_stream = gzip.GzipFile(mode='w', fileobj=fileobj, mtime=0)
    tar_stream = tarfile.open(mode='w|', fileobj=gzip_stream)
    for path, arc_path in paths:
        tar_stream.add(path, arcname=arc_path)
    tar_stream.close()
    gzip_stream.close()
