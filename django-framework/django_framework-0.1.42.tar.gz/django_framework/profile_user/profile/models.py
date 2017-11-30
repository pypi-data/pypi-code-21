

from django_framework.django_helpers.model_helpers.model_registry import register_model

from django.db import models
from django_framework.django_helpers.model_helpers import BaseModel

from django_framework.django_helpers.model_helpers.model_fields import UnixEpochDateTimeField


class Profile(BaseModel):

    user = models.OneToOneField("auth.User", unique=True, db_index=True,)
    
    username = models.CharField(max_length=254, unique=True, db_index=True,)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)


    security_code = models.CharField(max_length=255, blank=True, null=True)
    security_code_valid_until = UnixEpochDateTimeField(auto_now=True)


    active = models.BooleanField(default=True, blank=True)
    
    class Meta:
        app_label = "profile_user" # this name needs to match the app model it is going in!
#         db_table = "chaiappliance_appliance_prototype"


        

register_model(Profile)  # this line is pretty important! it registers this model so it can be called properly

import serializers
import managers
import workers
import meta
import workers