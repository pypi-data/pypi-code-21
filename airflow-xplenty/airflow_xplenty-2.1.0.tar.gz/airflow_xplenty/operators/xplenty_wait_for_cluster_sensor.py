import logging
from airflow.operators.sensors import BaseSensorOperator
from airflow.utils.decorators import apply_defaults
from airflow_xplenty.client_factory import ClientFactory

"""Wait for a cluster to be in the ready or terminating state
"""
class XplentyWaitForClusterSensor(BaseSensorOperator):
    TERMINATING_STATUSES = ['pending_terminate', 'terminating', 'terminated', 'error']
    READY_STATUSES = ['available', 'idle']

    @apply_defaults
    def __init__(self, start_cluster_task_id, **kwargs):
        self.start_cluster_task_id = start_cluster_task_id
        self.client = ClientFactory().client()

        super(XplentyWaitForClusterSensor, self).__init__(**kwargs)

    def poke(self, context):
        cluster_id = context['task_instance'].xcom_pull(task_ids=self.start_cluster_task_id)
        if cluster_id is None:
            raise Exception('No cluster_id found in XComs')

        cluster = self.client.get_cluster(cluster_id)
        if cluster.status in self.READY_STATUSES:
            logging.info('Cluster %d is ready.' % cluster.id)
            return True
        elif cluster.status in self.TERMINATING_STATUSES:
            raise Exception('Cluster failed to start, in status: %s' % cluster.status)
        else:
            logging.info('Waiting for cluster %d to start.' % cluster.id)
            return False
