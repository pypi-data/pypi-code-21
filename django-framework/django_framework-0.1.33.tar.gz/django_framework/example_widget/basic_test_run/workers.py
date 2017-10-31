from django_framework.django_helpers.worker_helpers import register_worker
from django_framework.django_helpers.worker_helpers import BaseWorker, BaseWorkerJob, BaseWorkerJobRegistry


from django_framework.django_helpers.worker_helpers.common_jobs.self_update_job import SelfUpdateWorkerJob

BASIC_TEST_RUN_WORKER_JOB_REGISTRY = BaseWorkerJobRegistry()

BASIC_TEST_RUN_WORKER_JOB_REGISTRY.add_job(job = SelfUpdateWorkerJob)

class BasicTestRunWorker(BaseWorker):
    ALLOWED_JOBS = BASIC_TEST_RUN_WORKER_JOB_REGISTRY
    
        
register_worker(BasicTestRunWorker)