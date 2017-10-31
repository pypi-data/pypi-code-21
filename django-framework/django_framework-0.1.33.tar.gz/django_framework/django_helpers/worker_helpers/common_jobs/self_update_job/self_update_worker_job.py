
from django_framework.django_helpers.worker_helpers.base_worker_job import BaseWorkerJob
from generate_payload import GeneratePayload
from generate_response import GenerateResponse
from process_response import ProcessResponse


SelfUpdateWorkerJob = BaseWorkerJob(
    
    command = 'self', action='update', 
    allowed_job_types=['synchronous', 'local', 'asynchronous'], 
    allowed_priorities=[], timeout_ttl=3600,
    
     initial_payload_class = GeneratePayload,
     response_generator_class = GenerateResponse,
     process_response_class  = ProcessResponse,
    )