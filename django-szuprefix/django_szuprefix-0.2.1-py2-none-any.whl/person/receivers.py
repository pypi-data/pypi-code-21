# -*- coding:utf-8 -*-
from django.dispatch import receiver
from django.db.models.signals import pre_delete, post_save
from . import models


