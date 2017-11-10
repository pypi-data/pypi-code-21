# -*- coding: utf-8 -*-

from django.apps import apps
from django.db.models.signals import (
    post_delete, post_migrate, post_save, pre_save
)
from django.dispatch import receiver

from navsy import cache
from navsy.models import Page, Pattern, Route


app_config = apps.get_app_config('navsy')


@receiver(post_migrate, sender=app_config, dispatch_uid='post_migrate_app')
def post_migrate_app(sender, **kwargs):
    Pattern.create_default_objects()
    Page.create_default_objects()
    cache.update_data()


@receiver(post_save, sender=Page, dispatch_uid='post_save_page')
def post_save_page(sender, instance, **kwargs):
    instance.update_unique_home()
    cache.delete_data()


@receiver(post_delete, sender=Page, dispatch_uid='post_delete_page')
def post_delete_page(sender, instance, **kwargs):
    cache.delete_data()


@receiver(pre_save, sender=Pattern, dispatch_uid='pre_save_pattern')
def pre_save_pattern(sender, instance, **kwargs):
    instance.update_regex_strings()


@receiver(post_save, sender=Pattern, dispatch_uid='post_save_pattern')
def post_save_pattern(sender, instance, **kwargs):
    cache.delete_data()


@receiver(post_delete, sender=Pattern, dispatch_uid='post_delete_pattern')
def post_delete_pattern(sender, instance, **kwargs):
    cache.delete_data()


@receiver(post_save, sender=Route, dispatch_uid='post_save_route')
def post_save_route(sender, instance, **kwargs):
    cache.delete_data()


@receiver(post_delete, sender=Route, dispatch_uid='post_delete_route')
def post_delete_route(sender, instance, **kwargs):
    cache.delete_data()
