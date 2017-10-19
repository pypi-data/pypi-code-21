from pkg_resources import get_distribution
__version__ = get_distribution('gcloud-aio-taskqueue').version

from gcloud.aio.taskqueue.taskqueue import LocalTaskQueue
from gcloud.aio.taskqueue.taskqueue import TaskQueue


__all__ = ['__version__', 'LocalTaskQueue', 'TaskQueue']
