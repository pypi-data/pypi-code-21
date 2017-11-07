from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.utils.translation import ugettext_lazy as _
from generic_relations.relations import GenericRelatedField
from rest_framework import serializers
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.authtoken.models import Token
from rest_framework.validators import UniqueValidator
from .models import User, BaseAccount
from .factories import serializer_factory
from .validators import get_validator

import django.contrib.auth.password_validation as validators
import random
import string


class AccountSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    username = serializers.CharField(required=True, validators=[
        UniqueValidator(queryset=User.objects.all())
    ])
    email = serializers.CharField(required=True, validators=[
        UniqueValidator(queryset=User.objects.all())
    ])
    type = serializers.ChoiceField(choices=User.TYPES)
    access_token = serializers.CharField(label=_('Access Token'), required=False)
    token = serializers.SerializerMethodField()
    account = GenericRelatedField(
        {cls: serializer_factory(cls)() for cls in BaseAccount.__subclasses__()},
        required=False
    )

    class Meta:
        model = User
        exclude = ['is_superuser', 'is_staff', 'is_active', 'content_type', 'groups', 'user_permissions']

    def get_token(self, instance):
        return Token.objects.get(user=instance).key

    def get_account_serializer(self, data):
        return self.get_fields()['account'].get_deserializer_for_data(data)

    def create(self, validated_data):
        validated_data.pop('access_token', None)
        account_data = validated_data.pop('account', None)

        user = super(AccountSerializer, self).create(validated_data)
        user.set_password(validated_data['password'])

        if account_data:
            account_serializer = self.get_account_serializer(account_data)
            user.account = account_serializer.Meta.model.objects.create(**account_data)

        user.save()
        return user

    def validate(self, attrs):
        account_type = attrs.get('type')
        access_token = attrs.get('access_token')
        password = attrs.get('password')
        request = self.context.get('request')

        if request.method == 'PATCH':
            account_data = attrs.pop('account', None)
            attrs = super(AccountSerializer, self).validate(attrs)

            if account_data:
                account_serializer = self.get_fields()['account'].get_deserializer_for_data(account_data)
                attrs['account'] = account_serializer.validate(attrs)

            return attrs

        if account_type is not User.TYPE_DEFAULT and access_token:
            validator = get_validator(attrs['type'])
            if validator.validate(access_token):
                attrs['password'] = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(16))
            else:
                raise serializers.ValidationError('access_token is not valid')
        elif account_type is not User.TYPE_DEFAULT:
            raise serializers.ValidationError('access_token is required')

        if account_type is User.TYPE_DEFAULT and password:
            validators.validate_password(password)
        elif account_type is User.TYPE_DEFAULT:
            raise serializers.ValidationError('password is required')

        return super(AccountSerializer, self).validate(attrs)


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            self.user = User.objects.get(email=value)
        except ObjectDoesNotExist as e:
            raise serializers.ValidationError(e)

        return value


class PasswordUpdateSerializer(serializers.Serializer):
    token = serializers.CharField()
    password = serializers.CharField()

    def validate_token(self, value):
        try:
            self.token = Token.objects.get(key=value)
            self.user = User.objects.get(id=self.token.user_id)
        except ObjectDoesNotExist as e:
            raise serializers.ValidationError(e)

        return value


class ConfirmEmailSerializer(serializers.Serializer):
    token = serializers.CharField()

    def validate_token(self, value):
        try:
            self.token = Token.objects.get(key=value)
            self.user = User.objects.get(id=self.token.user_id)
        except ObjectDoesNotExist as e:
            raise serializers.ValidationError(e)

        return value


class AuthTokenSerializer(AuthTokenSerializer):
    account_type = serializers.ChoiceField(label=_('Account Type'), choices=User.TYPES)
    access_token = serializers.CharField(label=_('Access Token'), required=False)
    password = serializers.CharField(label=_("Password"), style={'input_type': 'password'}, required=False)

    def validate(self, attrs):
        username = attrs.get('username')
        account_type = attrs.get('account_type')
        access_token = attrs.get('access_token')

        if account_type is not User.TYPE_DEFAULT and access_token:
            try:
                validator = get_validator(account_type)
            except ValidationError as e:
                raise serializers.ValidationError(e)

            if validator.validate(access_token):
                try:
                    attrs['user'] = User.objects.get(username=username)
                except ObjectDoesNotExist as e:
                    raise serializers.ValidationError('user with username ' + username + ' not found')
            else:
                raise serializers.ValidationError('access_token is not valid')
        elif account_type is not User.TYPE_DEFAULT:
            raise serializers.ValidationError('username, account_type, and access_token are required for social login')

        if account_type is User.TYPE_DEFAULT:
            attrs = super(AuthTokenSerializer, self).validate(attrs)

        return attrs
