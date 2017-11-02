# -*- coding: utf-8 -*-

import os
import zipfile
import tarfile
from logging import Logger

__author__ = 'Daniel Scheffler'


def decompress(compressed_file, outputpath=None, logger=Logger('decompressor')):
    """Decompresses ZIP, TAR, TAR.GZ and TGZ archives to a given output path.
    :param compressed_file:
    :param outputpath:
    :param logger:      instance of logging.Logger
    """
    filepath, filename = os.path.split(compressed_file)
    logger.info('Extracting ' + filename + '...')
    outputpath = outputpath or os.path.join(filepath, filename.partition(".")[0])
    if not os.path.exists(outputpath):
        os.makedirs(outputpath)

    if compressed_file.endswith(".zip"):
        assert zipfile.is_zipfile(compressed_file), \
            logger.critical(compressed_file + " is not a valid zipfile!")
        zf = zipfile.ZipFile(compressed_file)
        names = zf.namelist()
        count_extracted = 0
        for n in names:
            if os.path.exists(os.path.join(outputpath, n)) and \
                    zipfile.ZipFile.getinfo(zf, n).file_size == os.stat(os.path.join(outputpath, n)).st_size:
                logger.warning("file '%s' from '%s' already exists in the directory: '%s'"
                               % (n, filename, outputpath))
            else:
                written = 0
                while written == 0:
                    try:
                        zf.extract(n, outputpath)
                        logger.info("Extracting %s..." % n)
                        count_extracted += 1
                        written = 1
                    except OSError as e:
                        if e.errno == 28:
                            print('No space left on device. Waiting..')
                        else:
                            raise
        if count_extracted == 0:
            logger.warning("No files of %s have been decompressed.\n" % filename)
        else:
            logger.info("Extraction of '" + filename + " was successful\n")
        zf.close()

    elif compressed_file.endswith(".tar") or compressed_file.endswith(".tar.gz") or compressed_file.endswith(".tgz"):
        tf = tarfile.open(compressed_file)
        names, members = tf.getnames(), tf.getmembers()
        count_extracted = 0
        for n, m in zip(names, members):
            if os.path.exists(os.path.join(outputpath, n)) and \
                    m.size == os.stat(os.path.join(outputpath, n)).st_size:
                logger.warning("file '%s' from '%s' already exists in the directory: '%s'"
                               % (n, filename, outputpath))
            else:
                written = 0
                while written == 0:
                    try:
                        tf.extract(n, outputpath)
                        logger.info("Extracting %s..." % n)
                        count_extracted += 1
                        written = 1
                    except OSError as e:
                        if e.errno == 28:
                            print('No space left on device. Waiting..')
                        else:
                            raise
        if count_extracted == 0:
            logger.warning("No files of %s have been decompressed.\n" % filename)
        else:
            logger.info("Extraction of '" + filename + " was successful\n")
        tf.close()
