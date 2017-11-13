from __future__ import absolute_import

import celery
from celery.utils.log import get_task_logger

from ievv_opensource.ievv_batchframework.models import BatchOperation
from ievv_opensource.ievv_batchframework import batchregistry

logger = get_task_logger(__name__)


class BatchActionGroupTask(celery.Task):
    abstract = True

    def run_actiongroup(self, actiongroup_name, batchoperation_id, **kwargs):
        try:
            batchoperation = BatchOperation.objects.get(id=batchoperation_id,
                                                        status=BatchOperation.STATUS_UNPROCESSED)
        except BatchOperation.DoesNotExist:
            logger.warning('BatchOperation with id={} does not exist, or is already running.')
            return
        else:
            batchoperation.mark_as_running()

            registry = batchregistry.Registry.get_instance()
            full_kwargs = {
                'started_by': batchoperation.started_by,
                'context_object': batchoperation.context_object,
                'executed_by_celery': True
            }
            full_kwargs.update(kwargs)

            actiongroupresult = registry.get_actiongroup(actiongroup_name)\
                .run_blocking(**full_kwargs)
            batchoperation.finish(failed=actiongroupresult.failed,
                                  output_data=actiongroupresult.to_dict())


@celery.shared_task(base=BatchActionGroupTask)
def default(**kwargs):
    default.run_actiongroup(**kwargs)


@celery.shared_task(base=BatchActionGroupTask)
def highpriority(**kwargs):
    highpriority.run_actiongroup(**kwargs)
