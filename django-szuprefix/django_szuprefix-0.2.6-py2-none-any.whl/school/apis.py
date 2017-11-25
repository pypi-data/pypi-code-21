# -*- coding:utf-8 -*-
import django_filters
from rest_framework.filters import DjangoFilterBackend
from rest_framework.metadata import BaseMetadata, SimpleMetadata

from django_szuprefix.saas.mixins import PartyMixin
from .apps import Config

__author__ = 'denishuang'
from . import models, mixins
from rest_framework import serializers, viewsets, permissions, decorators, response, status
from django_szuprefix.api import register, mixins as api_mixins


class SchoolSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.School
        fields = ('name', 'type', 'create_time', 'url')


class SchoolViewSet(viewsets.ModelViewSet):
    queryset = models.School.objects.all()
    serializer_class = SchoolSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]


register(Config.label, 'school', SchoolViewSet)


class TeacherSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Teacher
        fields = ('name', 'url')


class TeacherViewSet(mixins.SchoolMixin, viewsets.ModelViewSet):
    queryset = models.Teacher.objects.all()
    serializer_class = TeacherSerializer
    # permission_classes = [permissions.IsAdminUser]


register(Config.label, 'teacher', TeacherViewSet)

class GradeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Grade
        fields = ('name',)


class GradeViewSet(mixins.SchoolMixin, api_mixins.BatchCreateModelMixin, viewsets.ModelViewSet):
    queryset = models.Grade.objects.all()
    serializer_class = GradeSerializer


register(Config.label, 'grade', GradeViewSet)


class SessionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Session
        fields = ('name',)


class SessionViewSet(mixins.SchoolMixin, api_mixins.BatchCreateModelMixin, viewsets.ModelViewSet):
    queryset = models.Session.objects.all()
    serializer_class = SessionSerializer

    def get_queryset(self):
        return super(SessionViewSet, self).get_queryset().filter(
            school=self.request.user.as_saas_worker.party.as_school)

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.as_saas_worker.party.as_school)


register(Config.label, 'session', SessionViewSet)


class ClazzSerializer(mixins.SchoolSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Clazz
        fields = ('name', 'entrance_session', 'number', 'primary_teacher', 'grade', 'teacher_names')


class ClazzViewSet(mixins.SchoolMixin, api_mixins.BatchCreateModelMixin, viewsets.ModelViewSet):
    queryset = models.Clazz.objects.all()
    serializer_class = ClazzSerializer


register(Config.label, 'clazz', ClazzViewSet)


class StudentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Student
        fields = ('name', 'number', 'clazz', 'grade', 'url')


class MinimalMetadata(SimpleMetadata):
    def get_field_info(self, field):
        field_info = super(MinimalMetadata, self).get_field_info(field)
        if isinstance(field, (serializers.RelatedField, serializers.ManyRelatedField)):
            field_info['choices_url'] = 'http://baidu.com'
        return field_info


class StudentViewSet(api_mixins.BatchCreateModelMixin, viewsets.ModelViewSet):
    queryset = models.Student.objects.all()
    serializer_class = StudentSerializer
    filter_fields = ('name', 'number')
    metadata_class = MinimalMetadata

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.as_saas_worker.party.as_school)

    def metadata(self, request, *args, **kwargs):
        return {"hello"}


register(Config.label, 'student', StudentViewSet)
