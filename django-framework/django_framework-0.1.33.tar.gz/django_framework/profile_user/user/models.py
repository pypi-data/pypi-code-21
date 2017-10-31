

from django_framework.django_helpers.model_helpers.model_registry import register_model

from django.contrib.auth.models import User
register_model(User)  # this line is pretty important! it registers this model so it can be called properly

import serializers
import managers
import workers
import meta