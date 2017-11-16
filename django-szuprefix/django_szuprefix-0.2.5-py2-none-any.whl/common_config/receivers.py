# -*- coding:utf-8 -*-
from django.dispatch import receiver
from django.db.models.signals import pre_delete, post_save
from .models import Trash,ExcelTask
from django.forms.models import model_to_dict
from django.contrib.contenttypes.models import ContentType

@receiver(pre_delete,sender=None)
def save_object_to_trash(sender,**kwargs):
    if sender==Trash:
        return
    instance = kwargs['instance']
    if not hasattr(instance,"id"):
        return
    ctype = ContentType.objects.get_for_model(instance)
    id = instance.id
    Trash.objects.update_or_create(content_type=ctype,object_id=id,defaults=dict(json_data=model_to_dict(instance)))


@receiver(post_save,sender=ExcelTask)
def start_excel_task(sender,**kwargs):
    instance = kwargs['instance']
    if instance.status == 0:
        instance.status = 1
        from .tasks import dump_excel_task
        dump_excel_task.delay(instance.id)
        instance.save()

