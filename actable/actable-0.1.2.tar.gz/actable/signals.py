from actable.models import ActableEvent
from django.db.models.signals import post_save


def post_save_handler(sender, **kwargs):
    instance = kwargs['instance']
    created = kwargs['created']
    event = ActableEvent(
        content_object=instance,
        is_creation=created,
    )
    event.save()


def register_all(model_classes):
    for model_class in model_classes:
        post_save.connect(post_save_handler, sender=model_class)
