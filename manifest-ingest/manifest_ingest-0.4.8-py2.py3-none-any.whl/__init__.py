import argparse
import logging
import logging.handlers
import os
import six.moves.configparser as configparser

# -----------------------------------------------------------------------------

# Parse command line arguments
parser = argparse.ArgumentParser(
    description='Downloads a manifest and its media files.')
parser.add_argument('--config', help='Config file path',
                    default='manifest-ingest.cfg')
# parser.add_argument('-p,', '--password', help='SFTP Password')
parser.add_argument('-m', '--mode', help='Force download mode',
                    default='auto')
args = parser.parse_args()

# Read config
config_file = os.path.expanduser(args.config)
config = configparser.ConfigParser()
config.read(config_file)

# Create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create logging format
msg_fmt = '[%(levelname)s] [%(asctime)s] [%(name)s] %(message)s'
date_fmt = '%Y-%m-%d %I:%M:%S %p'
formatter = logging.Formatter(msg_fmt, date_fmt)

# Create file handler
logfile = os.path.expanduser(config.get('default', 'log'))
if not os.path.exists(os.path.dirname(logfile)):
    os.makedirs(os.path.dirname(logfile))
fh = logging.handlers.RotatingFileHandler(logfile, maxBytes=10485760, backupCount=5)
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)

# Create console handler
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)

# Add logging handlers
logger.addHandler(fh)
logger.addHandler(ch)
