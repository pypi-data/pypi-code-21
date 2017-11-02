from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.http import urlsafe_base64_encode as b64e
from enumfields.fields import EnumFieldMixin
from rest_auth.serializers import (
    LoginSerializer as RALoginSerializer,
    PasswordResetSerializer as RAPasswordResetSerializer)
from rest_framework.serializers import ModelSerializer as BaseModelSerializer

from .fields import LocalDateTimeField, RestEnumField


class ModelSerializer(BaseModelSerializer):
    serializer_field_mapping = BaseModelSerializer.serializer_field_mapping.copy()
    serializer_field_mapping.update({models.DateTimeField: LocalDateTimeField})

    def build_standard_field(self, field_name, model_field):
        cls, kwargs = super().build_standard_field(field_name, model_field)
        if isinstance(model_field, EnumFieldMixin):
            cls = RestEnumField
            kwargs['enum_type'] = model_field.enum
        return cls, kwargs


class UserDetailsSerializer(ModelSerializer):
    class Meta:
        model = get_user_model()
        read_only_fields = fields = list(set([
            'id', model.USERNAME_FIELD, model.EMAIL_FIELD]))


class LoginSerializer(RALoginSerializer):  # pylint: disable=abstract-method
    def validate_email(self, value):  # pylint: disable=no-self-use
        return value.lower()


class PasswordResetSerializer(RAPasswordResetSerializer):  # pylint: disable=abstract-method
    def get_email_context(self):
        return {
            'email_encoded': b64e(self.data['email'].lower().encode('utf-8')),
            'frontend_url': settings.DJCORE.FRONTEND_URL,
            'site_url': settings.DJCORE.SITE_URL,
        }

    def get_email_options(self):  # pylint: disable=no-self-use
        return {**super().get_email_options(), **{
            'email_template_name': 'registration/password_reset_email.txt',
            'html_email_template_name': 'registration/password_reset_email.html',
            'extra_email_context': self.get_email_context(),
        }}

    def validate_email(self, value):  # pylint: disable=no-self-use
        return super().validate_email(value.lower())
