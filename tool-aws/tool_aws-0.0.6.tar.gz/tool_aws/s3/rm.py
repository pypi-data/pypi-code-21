#!/usr/bin/env python

import time
import os
import sys
import boto3
import logging
import multiprocessing
import argparse as ap
from textwrap import dedent
from poolmanager import PoolManager
from botocore.exceptions import ClientError
from tool_aws.s3.utils import S3Keys, getMaxChunkSize
from botocore.parsers import ResponseParserError


logging.basicConfig(level=logging.INFO)
logging.getLogger('boto3').setLevel(logging.CRITICAL)
logging.getLogger('botocore').setLevel(logging.CRITICAL)
logger = logging.getLogger(__name__)


def usage():
    logger.info('usage:\n%s [options]\n') % (os.path.basename(sys.argv[0]))
    logger.info('try -h or --help for extended help')


def prefixType(val):
    if val.endswith('/*'):
        val = val[:len(val) - 1]
    if not val.startswith('/'):
        usage()
        logger.error('Your prefix or path should start with a /')
        sys.exit(1)
    return val


def threadType(val):
    if val is not None:
        try:
            return int(val)
        except ValueError:
            usage()
            logger.error('The number of threads must be an integer.')
            sys.exit(1)
    return multiprocessing.cpu_count()


def bboxType(val):
    if val is not None:
        try:
            bx = [float(c) for c in val.split(',')]
        except Exception as e:
            logging.error('Bad bbox definition')
            logging.error('%s' % e)
            usage()
            sys.exit(1)
        if len(bx) != 4:
            logging.error(
                'bbox should be a comma separated list of 2 coordinates')
            usage()
            sys.exit(1)
        min_v = 1000000
        if bx[0] < min_v or bx[2] < min_v or bx[1] < min_v or bx[3] < min_v:
            logging.error('Bbox must be provided in lv95')
            usage()
            sys.exit(1)
        return bx


def imageFormatType(val):
    if val not in ('png', 'jpeg', 'pngjpeg'):
        logger.error('Unsupported image format %s' % val)
        usage()
        sys.exit(1)
    return val


def chunkType(val):
    if not val.isdigit():
        logger.error('Please provide a number for the chunks size')
        usage()
        sys.exit(1)
    if val is not None:
        val = int(val)
        if val > 1000:
            logger.info('Max chunk size is 1000... Using max value')
            val = 1000
    return val


def resolutionType(val):
    if val or not val.isdigit():
        logger.error('Please provide a numeric value for low resolution')
        usage()
        sys.exit(1)
    val = float(val)
    if val >= 0:
        return val


def createParser():
    parser = ap.ArgumentParser(
        description=dedent("""\
        Purpose:
            This script is intended for efficient and MASSIVE RECURSIVE
            DELETION of S3 'folders'. This mean that any resource matching with
            the PREFIX variable, will be DELETED IRREVERSIVELY.

            Use this script CAREFULLY.
            """),
        epilog=dedent("""\
        Disclaimer:
            This software is provided \"as is\" and
            is not granted to work in particular cases or without bugs.
            The author disclaims any responsability in case of data loss,
            computer damage or any other bad issue that could arise
            using this software.
            """),
        formatter_class=ap.RawDescriptionHelpFormatter)

    mandatory = parser.add_argument_group('Mandatory arguments')
    mandatory.add_argument(
        '-b', '--bucket-name',
        dest='bucketName',
        action='store',
        type=str,
        help='bucket name',
        required=True)
    mandatory.add_argument(
        '-p', '--prefix',
        dest='prefix',
        action='store',
        type=prefixType,
        help='Prefix (string) relative to the bucket base path.',
        required=True)

    optionGroup = parser.add_argument_group('Program options')
    optionGroup.add_argument(
        '--profile',
        dest='profileName',
        action='store',
        default='default',
        type=str,
        help='AWS profile',
        required=False)
    optionGroup.add_argument(
        '--bbox',
        dest='bbox',
        action='store',
        type=bboxType,
        default=None,
        help='a bounding box in lv95')
    optionGroup.add_argument(
        '-n', '--threads-number',
        dest='nbThreads',
        action='store',
        type=threadType,
        default=None,
        help='Number of threads (subprocess), default: machine number of CPUs')
    optionGroup.add_argument(
        '-s', '--chunk-size',
        dest='chunkSize',
        action='store',
        type=chunkType,
        default=None,
        help='Chunk size for S3 batch deletion, \
            default is set to 1000 (maximal value for S3)')
    optionGroup.add_argument(
        '-i', '--image-format',
        dest='imageFormat',
        action='store',
        type=imageFormatType,
        default=None,
        help='The image format')
    optionGroup.add_argument(
        '-lr', '--lowest-resolution',
        dest='lowRes',
        action='store',
        type=resolutionType,
        default=float('inf'),
        help='The lowest resolution in meters')
    optionGroup.add_argument(
        '-hr', '--highest-resolution',
        dest='highRes',
        action='store',
        type=resolutionType,
        default=0,
        help='The highest resolution in meters')
    optionGroup.add_argument(
        '-f', '--force',
        dest='force',
        action='store_true',
        default=False,
        help='force the removal, i.e. no prompt for confirmation.')

    return parser


def guessSrids(opts):
    srids = []
    if not opts.bbox:
        return srids
    supportedSrids = [21781, 2056, 4326, 3587]
    pathSplit = [p for p in opts.prefix.split('/') if p]
    if len(pathSplit) > 5:
        usage()
        logger.error(
            'Path should stop at the srid level definition')
        sys.exit(1)
    elif len(pathSplit) < 4:
        usage()
        logger.error(
            'Incorrect path definition, missing timestamp and/or layerid')
        sys.exit(1)
    elif len(pathSplit) == 5:
        srid = int(pathSplit[4])
        if srid not in supportedSrids:
            usage()
            logger.error('SRID %s is not supported' % srid)
            sys.exit(1)
        srids = [srid]
    else:
        srids = supportedSrids
    return srids


def parseArguments(parser, argv):
    opts = parser.parse_args(argv[1:])
    if opts.bbox:
        # Image format is required when a bbox is defined
        if not opts.imageFormat:
            usage()
            logger.error(
                'Image format is required when a bbox is defined (-i option)')
            sys.exit(1)
    return opts, guessSrids(opts)


def callback(counter, response):
    if response:
        logger.info('number batch delete requests: %s' % counter)
        logger.info('result: %s' % response)


def startJob(keys, force):
    if len(keys) == 0:
        logger.info('Actually, there\'s nothing to do... aborting')
        logger.info('Hint: if your prefix starts with \'/\'')
        logger.info('simply remove the first character.')
        return False

    # There is no way to count all keys without listing them all first.
    # We want to avoid listing them all several times,
    # so we only provide the size of the first batch.
    if keys.chunkSize == keys.maxKeys:
        logger.info('There are more than %s keys in total.\n' +
                    'These represents the first batch.' % keys.chunkSize)
    logger.info('Warning: the script will now start deleting:')
    logger.info(keys)

    if force:
        return True

    while True:
        userInput = raw_input(
            'Are you sure you want to continue (there is no way back)? y/n:')
        userInput = userInput.lower()
        if userInput not in (u'y', u'n'):
            logger.info('Error: unrecognized option \'%s\'' % userInput)
            logger.info('Please provide a valid input character...')
            continue
        else:
            break

    if userInput == u'n':
        logger.info('You have refused to proceed, the script will now abort.')
        return False
    return True


def deleteKeys(keys):
    # When using SSL and multithreading one need to create one connection
    # per process. See also: http://stackoverflow.com/questions/
    # 3724900/python-ssl-problem-with-multiprocessing
    session = boto3.session.Session(profile_name=profileName)
    s3 = session.resource('s3')
    S3Bucket = s3.Bucket(bucketName)
    logger.info('Worker pid %s and parent pid %s' % (
        multiprocessing.current_process().pid, os.getppid()))
    logger.info('Deleting %s keys at a time' % len(keys['Objects']))
    try:
        response = S3Bucket.delete_objects(Delete=keys)
    except ClientError as e:
        if e.response['Error']['Code'] == 'SlowDown':
            logger.info('We are going to fast for S3 it seems.')
            logger.info('Pausing for 30 sec...')
            time.sleep(30)
            return deleteKeys(keys)
        logger.error(e, exc_info=True)
        raise e
    # This error is triggered when the S3 XML response is invalid
    # S3 sometimes does that when you send too many requests
    except ResponseParserError as e:
        logger.error(e, exc_info=True)
        return deleteKeys(keys)
    except Exception as e:
        logger.error(e, exc_info=True)
        raise e
    return response


def deleteWithBBox(opts, S3Bucket, keys):
    # Use max chunkSize as we always delete the whole columns
    chunkSize = 1000
    keys.chunk(chunkSize)
    if startJob(keys, opts.force):
        logger.info('Deletion started...')
        previousNumberOfKeys = keys.maxKeys
        while len(keys) > 0 and previousNumberOfKeys == keys.maxKeys:
            if len(keys):
                pm = PoolManager(numProcs=opts.nbThreads)
                logger.info('New batch delete')
                logger.info(str(keys))
                # keys are pre-chunked in lists of chunksize
                # send one list per process
                pm.imap_unordered(
                    deleteKeys,
                    keys,
                    1,
                    callback=callback)
            previousNumberOfKeys = len(keys)
            keys.chunk(chunkSize)


def deleteWithPrefix(opts, S3Bucket, keys):
    pm = None
    chunkSize = opts.chunkSize or getMaxChunkSize(
        opts.nbThreads, len(keys))
    keys.chunk(chunkSize)
    if startJob(keys, opts.force):
        logger.info('Deletion started...')
        # Make sure we delete the first batch
        previousNumberOfKeys = keys.maxKeys
        while len(keys) > 0 and previousNumberOfKeys == keys.maxKeys:
            if pm:
                keys = S3Keys(S3Bucket, opts.prefix)
                keys.chunk(chunkSize)
                if len(keys):
                    logger.info('New batch delete')
                    logger.info(str(keys))
            if len(keys):
                pm = PoolManager(numProcs=opts.nbThreads)
                pm.imap_unordered(
                    deleteKeys,
                    keys,
                    1,
                    callback=callback)
            previousNumberOfKeys = len(keys)


def main():
    global bucketName, profileName
    parser = createParser()
    opts, srids = parseArguments(parser, sys.argv)
    bucketName = opts.bucketName
    profileName = opts.profileName

    # Maximum number of keys to be listed at a time
    session = boto3.session.Session(profile_name=opts.profileName)
    s3 = session.resource('s3')
    S3Bucket = s3.Bucket(opts.bucketName)
    keys = S3Keys(S3Bucket, opts.prefix, srids=srids,
                  bbox=opts.bbox, imageFormat=opts.imageFormat,
                  lowRes=opts.lowRes, highRes=opts.highRes)
    if opts.bbox:
        deleteWithBBox(opts, S3Bucket, keys)
    else:
        deleteWithPrefix(opts, S3Bucket, keys)
    logger.info('Deletion finished...')


if __name__ == '__main__':
    main()
