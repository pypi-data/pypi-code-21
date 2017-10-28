#
#   Copyright (c) 2014-2015 eGauge Systems LLC
# 	4730 Walnut St, Suite 110
# 	Boulder, CO 80301
# 	voice: 720-545-9767
# 	email: davidm@egauge.net
#
#   All rights reserved.
#
#   This code is the property of eGauge Systems LLC and may not be
#   copied, modified, or disclosed without any prior and written
#   permission from eGauge Systems LLC.
#
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from epic.models import Datasheet

def flush_caches(sender, **kwargs):
    """Any model class that maintains caches should register a
    'flush_caches' class method.  That method will then automatically
    be called if any instances of that model class are saved or
    deleted.
    """
    if hasattr(sender, 'flush_caches'):
        sender.flush_caches(sender, **kwargs)

@receiver(post_save, dispatch_uid='epic_signal_id')
def save_receiver(sender, **kwargs):
    flush_caches(sender, **kwargs)

@receiver(post_delete, dispatch_uid='epic_signal_id')
def delete_receiver(sender, **kwargs):
    flush_caches(sender, **kwargs)

@receiver(post_delete, sender=Datasheet)
def datasheet_delete(sender, instance, **kwargs):
    print('post_delete signal!! instance=%s' % instance)
    instance.ds_file.delete(False)
