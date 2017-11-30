

from django_framework.django_helpers.model_helpers.model_registry import register_model

from django.db import models
from django_framework.django_helpers.model_helpers import BaseModel
from django_framework.django_helpers.model_helpers.model_fields import UnixEpochDateTimeField


class Job(BaseModel):
    model_name = models.CharField(max_length=200 )
    model_uuid = models.CharField(max_length=200)
    model_id   = models.IntegerField()
    
    command = models.CharField(max_length=200)
    action  = models.CharField(max_length=200)
    
    initial_payload = models.TextField() # looks like JSON


    ERROR_PROCESSING  = (-3, "error_processing")
    ERROR_TIMEOUT  = (-2, "error_timeout")
    ERROR  = (-1, "error")
    COMPLETED = (0, "completed")
    PENDING   = (1, "pending")
    RUNNING  = (2, "running")
    PROCESSING  = (3, "PROCESSING")
    
    STATUS_TYPES = (
        COMPLETED, PENDING, RUNNING, PROCESSING, ERROR, ERROR_TIMEOUT, ERROR_PROCESSING
    )

    
    status = models.IntegerField(default=1, choices=STATUS_TYPES)

    response_payload = models.TextField(null = True, blank = True)
    
    process_payload = models.TextField(null = True, blank = True)
    
    error_notes  = models.TextField(null = True, blank = True)


    job_timeout = models.IntegerField(default = 3600) # the grace period before we timeout the JOB!
    timeout_at = UnixEpochDateTimeField(null = True, blank = True) # the grace period before we timeout the JOB!


    JOB_TYPES = (
        ('synchronous', 'synchronous'),
        ('local', 'local'),
        ('asynchronous', 'asynchronous'),
    )

    job_type = models.CharField(max_length=200, choices = JOB_TYPES, default = 'local') # the grace period before we timeout the JOB!
    
    
    run_at = UnixEpochDateTimeField(null = True, blank = True) # this is when it should be run, this is really only relavent to "local" and "async"
    response_at  = UnixEpochDateTimeField(null = True, blank = True)
    completed_at = UnixEpochDateTimeField(null = True, blank = True) # mark when it is completed! or errored out
    
    class Meta:
        app_label = "worker"
#         db_table = "chaiappliance_appliance_prototype"

register_model(Job)  # this line is pretty important! it registers this model so it can be called properly

import serializers
import managers
import workers
import meta