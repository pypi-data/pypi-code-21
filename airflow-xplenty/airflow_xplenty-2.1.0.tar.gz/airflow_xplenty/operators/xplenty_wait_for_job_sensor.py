import logging
from airflow.operators.sensors import BaseSensorOperator
from airflow.utils.decorators import apply_defaults
from airflow_xplenty.client_factory import ClientFactory

"""Wait for a job to finish
"""
class XplentyWaitForJobSensor(BaseSensorOperator):
    SUCCESS_STATUSES = ['completed', 'stopped']
    FAILED_STATUSES = ['failed']

    @apply_defaults
    def __init__(self, start_job_task_id, **kwargs):
        self.start_job_task_id = start_job_task_id
        self.client = ClientFactory().client()

        super(XplentyWaitForJobSensor, self).__init__(**kwargs)

    def poke(self, context):
        job_id = context['task_instance'].xcom_pull(task_ids=self.start_job_task_id)
        if job_id is None:
            raise Exception('No job_id found in XComs')
        
        job = self.client.get_job(job_id)
        if job.status in self.FAILED_STATUSES:
            raise Exception('Job failed: %s' % job.errors)
        elif job.status in self.SUCCESS_STATUSES:
            logging.info('Job %d finished in state %s' % (job_id, job.status))
            return True
        else:
            progress = round(job.progress * 100, 1)
            logging.info('Job %d in state %s (%.1f%%)' % (job_id, job.status, progress))
            return False
