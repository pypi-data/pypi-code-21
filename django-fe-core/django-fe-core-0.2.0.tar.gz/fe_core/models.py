# -*- coding:utf-8 -*-
import uuid

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from fe_core.base_models import UUIDModel


class EntityManager(BaseUserManager):
    def create_entity(self, name=None):
        if name is None:
            name = str(uuid.uuid4())
        return self.create(name=name)


class Entity(UUIDModel):
    name = models.CharField(max_length=40, null=True, blank=True)

    objects = EntityManager()

    def __str__(self):
        return self.name if self.name else str(self.uuid)[0:8]

    class Meta:
        verbose_name = "entidade"
        verbose_name_plural = "entidades"


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, entity=None):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.entity = entity
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(email, password=password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(UUIDModel, AbstractBaseUser, PermissionsMixin):
    entity = models.ForeignKey(Entity, null=True, blank=True)
    email = models.EmailField(unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    objects = UserManager()

    USERNAME_FIELD = 'email'

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email
