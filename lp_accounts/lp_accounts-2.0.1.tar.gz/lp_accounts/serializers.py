import django.contrib.auth.password_validation as validators

from generic_relations.relations import GenericRelatedField
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import User, BaseAccount
from .factories import serializer_factory


class AccountSerializer(serializers.ModelSerializer):
    username = serializers.CharField(validators=[UniqueValidator(queryset=User.objects.all())])
    email = serializers.CharField(validators=[UniqueValidator(queryset=User.objects.all())], default='')
    account = GenericRelatedField(
        {cls: serializer_factory(cls)() for cls in BaseAccount.__subclasses__()},
        required=False
    )
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        exclude = [
            'is_superuser', 'is_staff', 'is_active', 'content_type', 'groups', 'user_permissions', 'account_id',
        ]

    def validate_password(self, value):
        try:
            validators.validate_password(value)
        except Exception as e:
            raise e

        return value

    def get_account_serializer(self, data):
        return self.get_fields()['account'].get_deserializer_for_data(data)

    def create(self, validated_data):
        account_data = validated_data.pop('account', None)

        # Create user
        user = super(AccountSerializer, self).create(validated_data)

        # Encrypt the password
        user.set_password(validated_data['password'])

        # Create account
        if account_data:
            account_serializer = self.get_account_serializer(account_data)
            user.account = account_serializer.Meta.model.objects.create(**account_data)

        user.save()
        return user


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError('This email does not exist')

        return value


class PasswordUpdateSerializer(serializers.Serializer):
    token = serializers.CharField()
    email = serializers.CharField()
    password = serializers.CharField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError('This email does not exist')

        return value

    def validate_password(self, value):
        try:
            validators.validate_password(value)
        except:
            return False

        return True
