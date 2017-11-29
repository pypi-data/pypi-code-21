import collate_cs
import sys

if len(sys.argv) < 4:
    print('usage:')
    print('collate before_path after_path depth')
    exit()

collate_cs._(sys.argv[1], sys.argv[2], int(sys.argv[3]))


__version__ = "0.22"

__title__ = "collate_cs"
__description__ = "thin -> cs"
__uri__ = "https://bitbucket.org/Cogbot/collate_cs"

__author__ = "Luke Aver"
__email__ = "luke.avery@live.co.uk"

__license__ = "MIT"
__copyright__ = "Copyright (c) 2017 Luke Avery"
