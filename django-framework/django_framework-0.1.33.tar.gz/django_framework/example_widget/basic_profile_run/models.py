

from django_framework.django_helpers.model_helpers.model_registry import register_model

from django.db import models
from django_framework.django_helpers.model_helpers import BaseModel


from django_framework.django_helpers.model_helpers.model_fields import UnixEpochDateTimeField

class BasicProfileRun(BaseModel):

    profile = models.ForeignKey('profile_user.Profile', unique = True)
    
    
    class Meta:
        app_label = "example_widget" # this name needs to match the app model it is going in!
#         db_table = "chaiappliance_appliance_prototype"

register_model(BasicProfileRun)  # this line is pretty important! it registers this model so it can be called properly

import serializers
import managers
import workers
import meta
import workers