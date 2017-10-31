
from django_framework.django_helpers.worker_helpers import BaseWorker, BaseWorkerJob, BaseWorkerJobRegistry
from django_framework.django_helpers.worker_helpers import register_worker


from django_framework.django_helpers.worker_helpers.common_jobs.self_update_job import SelfUpdateWorkerJob

PROFILE_WORKER_JOB_REGISTRY = BaseWorkerJobRegistry()

PROFILE_WORKER_JOB_REGISTRY.add_job(job = SelfUpdateWorkerJob)


class ProfileWorker(BaseWorker):
    ALLOWED_JOBS = PROFILE_WORKER_JOB_REGISTRY

        
register_worker(ProfileWorker)