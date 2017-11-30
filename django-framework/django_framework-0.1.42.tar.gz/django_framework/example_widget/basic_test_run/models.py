

from django_framework.django_helpers.model_helpers.model_registry import register_model

from django.db import models
from django_framework.django_helpers.model_helpers import BaseModel


from django_framework.django_helpers.model_helpers.model_fields import UnixEpochDateTimeField

class BasicTestRun(BaseModel):


    basic_profile_run_fk_field = models.ForeignKey("BasicProfileRun", null=True, blank=True, related_name = 'owner')
    
    basic_profile_run = models.ManyToManyField("BasicProfileRun", null=True, blank=True)
    
    normal_text_field = models.CharField(max_length = 256, null = True, blank = True)
    
    write_once_text_field = models.CharField(max_length = 256, null = True, blank = True)
    read_only_text_field = models.CharField(max_length = 256, null = True, blank = True)
    hidden_text_field = models.CharField(max_length = 256, null = True, blank = True)
    
    
    encrypted_text_field = models.CharField(max_length = 256, null = True, blank = True) # will unencrypt when requested
    encrypted_text_strict_field = models.CharField(max_length = 256, null = True, blank = True) # will not unencrypt when requested

    epoch_time_field = UnixEpochDateTimeField(null = True, blank = True)
    

    # LOAD TYPES
    CHOICE1 = (0, "Constant")
    CHOICE2   = (1, "OnOff")
    CHOICE3  = (2, "Multistage")
    CHOICE4  = (3, "Variable")
    
    CHOICE_TYPES = (
        CHOICE1, CHOICE2, CHOICE3, CHOICE4
    )
    
    choices_field = models.IntegerField(default=CHOICE_TYPES[0][0], choices=CHOICE_TYPES)
    
#     many_to_many_field = UnixEpochDateTimeField(null = True, blank = True)
#     choices_field = UnixEpochDateTimeField(null = True, blank = True)
    
#     ajson_field = UnixEpochDateTimeField(null = True, blank = True)
#     alist_field = UnixEpochDateTimeField(null = True, blank = True)
    
#     validator_field = UnixEpochDateTimeField(null = True, blank = True)
    
    
    class Meta:
        app_label = "example_widget" # this name needs to match the app model it is going in!
#         db_table = "chaiappliance_appliance_prototype"

register_model(BasicTestRun)  # this line is pretty important! it registers this model so it can be called properly

import serializers
import managers
import workers
import meta
import workers