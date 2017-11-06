# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from rest_framework import viewsets, mixins
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
import serializers
import models

class PageViewSet(viewsets.ModelViewSet):
    queryset = models.Page.objects.all()
    serializer_class = serializers.PageSerializer

class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening

class ContactViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    queryset = models.Contact.objects.all()
    serializer_class = serializers.ContactSerializer

