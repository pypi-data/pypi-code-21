
COMMAND = 'bccluster'
CMD = 'bcc'
VERSION = '1.3.1'

IT_MAP = {
    # 'ecs.t1.small': {'cpu': 1, 'memory': 1, 'name': 'ecs.t1.small'},
    # 'ecs.s3.large': {'cpu': 4, 'memory': 8, 'name': 'ecs.s3.large'},
    # 'ecs.m1.medium': {'cpu': 4, 'memory': 16, 'name': 'ecs.m1.medium'},
    # 'ecs.m2.medium': {'cpu': 4, 'memory': 32, 'name': 'ecs.m2.medium'},
    # 'ecs.c1.large':{'cpu': 8, 'memory': 16, 'name': 'ecs.c1.large'},
    # 'ecs.m1.xlarge': {'cpu': 8, 'memory': 32, 'name': 'ecs.m1.xlarge'},
    # 'ecs.m2.xlarge':{'cpu': 8, 'memory': 64, 'name': 'ecs.m2.xlarge'},
    # 'ecs.c2.medium':{'cpu': 16, 'memory': 16, 'name': 'ecs.c2.medium'},
    # 'ecs.c2.large':{'cpu': 16, 'memory': 32, 'name': 'ecs.c2.large'},
    # 'ecs.c2.xlarge':{'cpu': 16, 'memory': 64, 'name': 'ecs.c2.xlarge'},
    'bcs.a2.large':    {'cpu': 4, 'memory': 8, 'name': 'bcs.a2.large'},
    'bcs.a2.xlarge': {'cpu': 8, 'memory': 16, 'name': 'bcs.a2.xlarge'},
    'bcs.a2.3xlarge':  {'cpu': 16, 'memory': 32, 'name': 'bcs.a2.3xlarge'},
    'bcs.b2.3xlarge': {'cpu': 16, 'memory': 32, 'name': 'bcs.b2.3xlarge'},
    'bcs.b4.xlarge':{'cpu': 8, 'memory': 32, 'name':'bcs.b4.xlarge'},
    'bcs.b4.3xlarge': {'cpu': 16, 'memory': 64, 'name': 'bcs.b4.3xlarge'},
    'bcs.b4.5xlarge': {'cpu': 24, 'memory': 96, 'name': 'bcs.b4.5xlarge'},

    'bcs.a2.4xlarge': {'cpu': 20, 'memory': 40, 'name': 'bcs.a2.4xlarge', 'disk': 400},
    'bcs.b4.4xlarge': {'cpu': 20, 'memory': 80, 'name': 'bcs.b4.4xlarge', 'disk': 1000},
}

import sys


# Python 2 or Python 3 is in use.
PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3
WIN = sys.platform == 'win32'

# Definition of descriptor types.
if PY2:
    STRING = (str, unicode)
    NUMBER = (int, long)

if PY3:
    STRING = (str, bytes)
    NUMBER = int
