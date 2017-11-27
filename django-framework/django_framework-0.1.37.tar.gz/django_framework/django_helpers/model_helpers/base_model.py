from uuid import uuid4
from django.db import models
# from app_models import get_worker, get_model_name

from django_framework.django_helpers.worker_helpers.worker_registry import get_worker, get_worker_name_list
from django_framework.django_helpers.serializer_helpers import get_serializer
from django_framework.django_helpers.manager_helpers import get_manager


from model_registry import get_model_name


import arrow
from model_fields import UnixEpochDateTimeField


class BaseModel(models.Model):
    uuid = models.UUIDField(editable = False, default=uuid4, blank=True, null=True, db_index=True)
    created_at = UnixEpochDateTimeField(auto_now_add=True, db_index=True)
    last_updated = UnixEpochDateTimeField(auto_now=True)

    @classmethod
    def get_field_choice(cls, field_name=None, original_choice=None, alt=None):
        if field_name not in cls.get_concrete_field_names():
            message = "'{field_name}' is not a valid field name for this model"
            raise ValueError(message.format(field_name=field_name))
        choices = cls._meta.get_field(field_name).choices
        if not choices:
            message = "The '{field_name}' field in the '{model_name}' has no defined choices"
            raise ValueError(message.format(field_name=field_name, model_name=cls.__name__))

        if isinstance(original_choice, basestring) and original_choice.isdigit():
            original_choice = int(original_choice)

        option = None
        for choice in choices:
            if original_choice in choice or original_choice == choice:
                option = choice

        if option is None:
            message = "'{original_choice}' is not a valid choice for the field '{field_name}'"
            raise ValueError(message.format(original_choice=original_choice,
                                            field_name=field_name))

        if alt is False:
            response = option[0]
        elif alt is True:
            response = option[1]
        else:
            response = option

        return response

#     def save(self, *args, **kwargs):
#         current_time = arrow.utcnow().datetime
#         if not self.id:
#             self.created_at = current_time
#         self.last_updated = current_time
#         self.full_clean()
#         return super(BaseModel, self).save(*args, **kwargs)

    def get_worker(self, admin=False):
        full_name, model_name = get_model_name(model=self)
        
        Worker = get_worker(worker_name=model_name)
        return Worker(model=self, admin=admin)


    @classmethod
    def get_serializer(cls, version = 'default'):
        return get_serializer(serializer_name = cls.__name__, version = version)


    @classmethod
    def get_manager(cls):
        return get_manager(manager_name = cls.__name__)

    @classmethod
    def get_concrete_field_names(cls):
        fields = cls._meta.get_fields()
        return [f.name for f in fields if f.concrete]
    
    
    @classmethod
    def get_description_doc(cls):
        return "This model has not provided a description!"

    def __unicode__(self):
        return unicode('Model' + ": " + str(self.id))

    class Meta:
        abstract = True
