# coding: utf-8
from collections import OrderedDict
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.reverse import reverse
from taggit_serializer.serializers import (
    TagListSerializerField,
    TaggitSerializer
)
from file_context.serializers import (
    FilesMixInSerializer,
)
from common.serializers import LinkSerializer
from .models import (
    ProjectType,
    Project,
    TaskStatus,
    Task,
    TaskAttachment,
    Comment,
)
User = get_user_model()


class ProjectTypeSerializer(LinkSerializer):

    class Meta:

        model = ProjectType
        fields = (
            'id',
            'created_by',
            'date_created',
            'date_updated',
            'code',
            'description',
        )


class ProjectSerializer(TaggitSerializer,
                        LinkSerializer,
                        FilesMixInSerializer):

    def get_links(self, obj):

        request = self.context.get('request')
        detailUrl = reverse('project-detail', kwargs={'pk': obj.pk}, request=request)
        tasksUrl = reverse('task-list', request=request) + '?project={0}'.format(obj.pk)
        return OrderedDict([
            ('self', detailUrl),
            ('tasks', tasksUrl),
            ('clone', detailUrl + '/clone'),
            ('score', detailUrl + '/score'),
        ])

    tags = TagListSerializerField()

    class Meta:

        model = Project
        fields = (
            'id',
            'type',
            'responsible',
            'name',
            'description',
            'template',
            'files',
            'tags',
            'links',
        )


class TaskStatusSerializer(LinkSerializer):

    def get_links(self, obj):

        request = self.context.get('request')
        detailUrl = reverse('task-status-detail', kwargs={'pk': obj.pk}, request=request)
        return {
            'self': detailUrl,
        }

    class Meta:
        model = TaskStatus
        fields = (
            'id',
            'created_by',
            'date_created',
            'date_updated',
            'code',
            'description',
            'color',
            'is_system_status',
            'is_closing_status',
            'links',
        )


class TaskSerializer(TaggitSerializer,
                     LinkSerializer):

    def get_links(self, obj):

        request = self.context.get('request')
        detailUrl = reverse(
            'task-detail',
            kwargs={
                'pk': obj.pk
            },
            request=request
        )
        projectUrl = reverse(
            'project-detail',
            kwargs={
                'pk': obj.project_id
            },
            request=request
        )
        commentsUrl = reverse('comment-list', request=request) + '?task={0}'.format(obj.pk)
        return OrderedDict([
            ('self', detailUrl),
            ('project', projectUrl),
            ('comments', commentsUrl),
            ('change_status', detailUrl + '/change_status'),
            ('attach', detailUrl + '/attach'),
            ('detach', detailUrl + '/detach'),
            ('clone', detailUrl + '/clone'),
            ('score', detailUrl + '/score'),
            ('export', detailUrl + '/export'),
        ])

    tags = TagListSerializerField()

    class Meta:

        model = Task
        fields = (
            'id',
            'created_by',
            'date_created',
            'date_updated',
            'start_date',
            'end_date',
            'project',
            'parent',
            'responsible',
            'status',
            'weight',
            'name',
            'description',
            'tags',
            'links',
        )


class CommentSerializer(LinkSerializer):

    def get_links(self, obj):

        request = self.context.get('request')
        detailUrl = reverse(
            'comment-detail',
            kwargs={
                'pk': obj.pk
            },
            request=request
        )
        taskUrl = reverse(
            'task-detail',
            kwargs={
                'pk': obj.task_id
            },
            request=request
        )
        return OrderedDict([
            ('self', detailUrl),
            ('task', taskUrl),
        ])

    class Meta:
        model = Comment
        fields = (
            'id',
            'created_by',
            'date_created',
            'date_updated',
            'task',
            'text',
            'links'
        )


class TaskAttachmentSerializer(LinkSerializer):

    model_name = serializers.SerializerMethodField()

    def get_model_name(self, obj):
        return '{0}.{1}'.format(obj.content_type.app_label, obj.content_type.name)

    class Meta:
        model = TaskAttachment
        fields = (
            'id',
            'task',
            'content_type',
            'object_id',
            'model_name'
        )


class TaskChangeSerializer(serializers.Serializer):

    task = TaskSerializer()
    initial_target = TaskSerializer()
    action = serializers.CharField(max_length=64)
    status = TaskStatusSerializer()


class ListAllocationSerializer(serializers.Serializer):

    """
    Serializer that allows you to control
    filter for allocations
    """

    project = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(),
        required=False
    )

    min_date = serializers.DateField(
        required=False
    )

    max_date = serializers.DateField(
        required=False
    )


class AllocationSerializer(serializers.Serializer):

    user = serializers.SerializerMethodField()
    date_point = serializers.DateTimeField()
    tasks = TaskSerializer(many=True, read_only=True)
    weight = serializers.SerializerMethodField()

    def get_user(self, obj):
        return obj.user.username

    def get_weight(self, obj):
        return obj.weight


class AttachDetachSerializer(serializers.Serializer):
    """
    Serializer that validates and helps
    to construct the required request data
    for attach and detach endpoints
    """

    model_name = serializers.CharField()
    model_id = serializers.IntegerField()

    class Meta:
        fields = '__all__'


class ChangeStatusSerializer(serializers.Serializer):

    """
    Serializer that validates and helps
    to construct the required request data
    for change-status endpoint
    """

    status = serializers.IntegerField()
    dry_run = serializers.BooleanField(required=False)

    class Meta:
        fields = '__all__'


class ProjectCloneSerializer(serializers.Serializer):

    new_name = serializers.CharField()
    new_type = serializers.PrimaryKeyRelatedField(
        queryset=ProjectType.objects.all(),
        required=False
    )
    new_responsible = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False
    )
    new_date = serializers.DateTimeField(required=False)
    new_status = serializers.PrimaryKeyRelatedField(
        queryset=TaskStatus.objects.all(),
        required=False
    )
    keep_tasks = serializers.BooleanField(default=True)
    keep_comments = serializers.BooleanField(default=False)
    keep_attachments = serializers.BooleanField(default=False)
    keep_tags = serializers.BooleanField(default=True)

    class Meta:
        fields = '__all__'


class TaskCloneSerializer(serializers.Serializer):

    new_project = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.filter(template=False),
        required=False,
    )
    new_node = serializers.PrimaryKeyRelatedField(
        queryset=Task.objects.all(),
        required=False,
    )
    new_status = serializers.PrimaryKeyRelatedField(
        queryset=TaskStatus.objects.all(),
        required=False,
    )
    new_responsible = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
    )

    new_date = serializers.DateTimeField(required=False)
    keep_comments = serializers.BooleanField(default=False)
    keep_attachments = serializers.BooleanField(default=False)
    keep_tags = serializers.BooleanField(default=True)

    class Meta:
        fields = '__all__'
