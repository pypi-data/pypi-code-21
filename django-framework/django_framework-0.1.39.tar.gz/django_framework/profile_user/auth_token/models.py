
from uuid import uuid4
from django_framework.django_helpers.model_helpers.model_registry import register_model

from django.db import models
from django_framework.django_helpers.model_helpers import BaseModel
from django_framework.django_helpers.model_helpers.model_fields import UnixEpochDateTimeField

class AuthToken(BaseModel):
    
    user = models.OneToOneField("auth.User", unique=True)
    
    current_token = models.UUIDField(editable = False, default=uuid4, blank=False, null=False, db_index=True)
    expire_at = UnixEpochDateTimeField(null = False, blank=False)
    
    
    class Meta:
        app_label = "profile_user"

register_model(AuthToken)  # this line is pretty important! it registers this model so it can be called properly

import serializers
import managers
import workers
import meta