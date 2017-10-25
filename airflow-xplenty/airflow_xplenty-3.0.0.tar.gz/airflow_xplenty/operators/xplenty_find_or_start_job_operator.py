import logging
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow_xplenty.client_factory import ClientFactory

RUNNING_STATUSES = ['idle', 'pending', 'running']

def _find_package(client, name):
    offset = 0
    page_size = 100
    while True:
        packages = client.get_packages(offset=offset, limit=page_size)
        if len(packages) == 0:
            return None

        for package in packages:
            if package.name == name:
                return package

        offset += page_size

"""Operator start a job on an Xplenty cluster
"""
class XplentyFindOrStartJobOperator(BaseOperator):
    @apply_defaults
    def __init__(self, start_cluster_task_id, package_id=None, package_name=None, **kwargs):
        if package_id is None and package_name is None:
            raise TypeError('__init__ requires either package_id or package_name')

        if package_id is not None and package_name is not None:
            raise TypeError('Do not supply both package_id and package_name')

        self.package_id = package_id
        self.package_name = package_name
        self.start_cluster_task_id = start_cluster_task_id
        self.client = ClientFactory().client()

        super(XplentyFindOrStartJobOperator, self).__init__(**kwargs)

    def execute(self, context):
        cluster_id = context['task_instance'].xcom_pull(task_ids=self.start_cluster_task_id)
        if cluster_id is None:
            raise Exception('No cluster_id found in XComs')

        if self.package_name is not None:
            package = _find_package(self.client, self.package_name)
            if package is None:
                raise Exception('Package %s not found' % self.package_name)
            self.package_id = package.id

        for job in self.client.jobs:
            if job.package_id == self.package_id and job.status in RUNNING_STATUSES:
                logging.info('Found already running job %d' % job.id)
                return job.id

        job = self.client.add_job(cluster_id, self.package_id, {})
        logging.info('Starting job %d' % job.id)
        return job.id
