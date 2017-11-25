# -*- coding:utf-8 -*-
from django.http import JsonResponse
from rest_framework.generics import GenericAPIView
from rest_framework.parsers import JSONParser

from .apps import Config
from rest_framework import serializers, viewsets, mixins, decorators
from django_szuprefix.api import register
from django.contrib.auth import models, authenticate, login as auth_login

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.User
        fields = ('url', 'username', 'email', 'groups')

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, allow_blank=False, max_length=100)
    password = serializers.CharField(required=True, allow_blank=False, max_length=100)


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Group
        fields = ('url', 'name')

class UserViewSet(viewsets.GenericViewSet):
    def get_object(self):
        return self.request.user

    # @decorators.detail_route(['post'])
    def login(self, request, *args, **kwargs):
        data = JSONParser().parse(request)
        serializer = LoginSerializer(data=data)
        if serializer.is_valid():
            user = authenticate(username=serializer.data.username,
                                           password=serializer.data.password)
            if user:
                auth_login(request, user)
                return JsonResponse(UserSerializer(user).data)
        return JsonResponse(serializer.errors, status=400)


    login.bind_to_methods = ['post']
    login.detail = False
    login.kwargs = {}
    # def retrieve(self, request, *args, **kwargs):
    #     content = {
    #         'user': unicode(request.user),  # `django.contrib.auth.User` instance.
    #         'auth': unicode(request.auth),  # None
    #     }
    #     return Response(content)

register(Config.label, 'user', UserViewSet, base_name='user')

#
# class UserSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = models.User
#         fields = ('username', )
#
#
# class UserViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
#     queryset = models.User.objects.all()
#     serializer_class = UserSerializer
#
#
# register(Config.label, 'user', UserViewSet)
