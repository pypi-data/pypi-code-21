# coding: utf-8
import logging
from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route
from .allocation import (
    AllocationHandler,
)
from .rest import (
    Responses
)
from .utils import (
    TaskHandler,
    get_model,
)
from .exporters import (
    XLSXTaskExport,
    ICALTaskExport,
)
from .models import (
    ProjectType,
    Project,
    TaskStatus,
    Task,
    Comment
)
from .filters import (
    ProjectTypeFilter,
    ProjectFilter,
    TaskStatusFilter,
    TaskFilter,
    CommentFilter,
)
from .serializers import (
    ProjectTypeSerializer,
    ProjectSerializer,
    TaskStatusSerializer,
    TaskSerializer,
    TaskAttachmentSerializer,
    TaskChangeSerializer,
    CommentSerializer,
    AllocationSerializer,
    ChangeStatusSerializer,
    AttachDetachSerializer,
    ProjectCloneSerializer,
    TaskCloneSerializer,
    ListAllocationSerializer,
)
User = get_user_model()
logger = logging.getLogger(__name__)


class ProjectTypeViewSet(viewsets.ModelViewSet):

    queryset = ProjectType.objects.all()
    serializer_class = ProjectTypeSerializer
    filter_class = ProjectTypeFilter
    search_fields = (
        'id',
        'code',
        'description',
    )


class BaseProjectViewSet(viewsets.ModelViewSet):

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    filter_class = ProjectFilter
    search_fields = (
        'id',
        'name',
        'type',
        'responsible',
        'description',
        'tags',
    )

    @detail_route(methods=['post'])
    def clone(self, request, pk=None):
        project = self.get_object()
        pcs = ProjectCloneSerializer(data=request.data)
        if not pcs.is_valid():
            return Response(pcs.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            new_project = project.clone(
                pcs.validated_data.get('new_name'),
                pcs.validated_data.get('new_type'),
                pcs.validated_data.get('new_responsible'),
                pcs.validated_data.get('new_date'),
                pcs.validated_data.get('new_status'),
                pcs.validated_data.get('keep_tasks'),
                pcs.validated_data.get('keep_comments'),
                pcs.validated_data.get('keep_attachments'),
                pcs.validated_data.get('keep_tags')
            )
            project_serializer = ProjectSerializer(new_project, context={'request': request})
            return Response(project_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as ex:
            message = ex.message if hasattr(ex, 'message') else ''
            logger.error('error while cloning project %s. error: %s', project, message, exc_info=True)
            return Responses.server_error(message)

    @detail_route(methods=['get'])
    def score(self, request, pk=None):
        project = self.get_object()
        return Response({'project': project.pk, 'score': project.score.score})


class ProjectTemplateViewSet(BaseProjectViewSet):

    queryset = Project.objects.filter(template=True)


class ProjectViewSet(BaseProjectViewSet):

    queryset = Project.objects.filter(template=False)


class TaskStatusViewSet(viewsets.ModelViewSet):

    queryset = TaskStatus.objects.all()
    serializer_class = TaskStatusSerializer
    filter_class = TaskStatusFilter
    search_fields = (
        'id',
        'code',
        'description',
        'is_system_status',
        'is_closing_status'
    )


class TaskViewSet(viewsets.ModelViewSet):

    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    filter_class = TaskFilter
    search_fields = (
        'id',
        'project',
        'parent',
        'responsible',
        'status',
        'name',
        'description',
        'tags',
    )
    exporters = {
        'XLSX': XLSXTaskExport,
        'ICAL': ICALTaskExport,
    }

    @list_route(methods=['get'])
    def export(self, request, *args, **kwargs):
        extension = request.data.get('format', 'XLSX')
        queryset = self.filter_queryset(self.get_queryset())
        if extension not in self.exporters:
            return Responses.client_error()
        try:
            exporter = self.exporters[extension](publish_url=True, request=request)
            return exporter.respond(queryset)
        except Exception as ex:
            message = ex.message if hasattr(ex, 'message') else ''
            logger.error('error while trying to export tasks to %s format. error: ', extension, message, exc_info=True)
            return Responses.server_error()

    @detail_route(methods=['get'])
    def score(self, request, pk=None):
        task = self.get_object()
        return Response({'task': task.pk, 'score': task.score.score})

    @detail_route(methods=['post'])
    def clone(self, request, pk=None):
        task = self.get_object()
        tcs = TaskCloneSerializer(data=request.data)
        if not tcs.is_valid():
            return Response(tcs.errors, status=status.HTTP_400_BAD_REQUEST)

        new_project = tcs.validated_data.get('new_project')
        new_node = tcs.validated_data.get('new_node')
        new_status = tcs.validated_data.get('new_status')
        new_date = tcs.validated_data.get('new_date')
        new_responsible = tcs.validated_data.get('new_responsible')
        keep_comments = tcs.validated_data.get('keep_comments')
        keep_attachments = tcs.validated_data.get('keep_attachments')
        keep_tags = tcs.validated_data.get('keep_tags')

        try:
            new_task = task.clone(
                new_project,
                new_node,
                new_status,
                new_date,
                new_responsible,
                keep_comments,
                keep_attachments,
                keep_tags
            )
            task_serializer = TaskSerializer(new_task)
            return Response(
                task_serializer.data,
            )
        except Exception as ex:
            message = ex.message if hasattr(ex, 'message') else ''
            logger.error('failed to clone task %s. error: %s', task, message, exc_info=True)
            return Responses.server_error(message)

    @detail_route(methods=['post'])
    def attach(self, request, pk=None):
        task = self.get_object()
        ads = AttachDetachSerializer(data=request.data)
        if not ads.is_valid():
            return Response(ads.errors, status=status.HTTP_400_BAD_REQUEST)
        model_name = ads.validated_data.get('model_name')
        model_id = ads.validated_data.get('model_id')
        model_class = get_model(model_name)
        if not model_class:
            return Responses.not_found('model not found')
        try:
            user = request.user if not request.user.is_anonymous else None
            model = model_class.objects.get(pk=model_id)
            attachment = task.attach(model, user=user)
            att_serializer = TaskAttachmentSerializer(attachment)
            return Response(att_serializer.data)
        except model_class.DoesNotExist:
            logger.warn('%s model with id %s does not exist', model_name, model_id)
            return Responses.not_found()
        except Exception as ex:
            message = ex.message if hasattr(ex.message) else ''
            logger.error('error while attaching %s - %s to %s. error: %s', model_name, model_id, task, message)
            return Responses.server_error(message)

    @detail_route(methods=['post'])
    def detach(self, request, pk=None):
        task = self.get_object()
        ads = AttachDetachSerializer(data=request.data)
        if not ads.is_valid():
            return Response(ads.errors, status=status.HTTP_400_BAD_REQUEST)
        model_name = ads.validated_data.get('model_name')
        model_id = ads.validated_data.get('model_id')
        model_class = get_model(model_name)
        if not model_class:
            return Responses.not_found('model not found')
        try:
            model = model_class.objects.get(pk=model_id)
            task.detach(model)
            return Responses.success('Detach succeeded')
        except model_class.DoesNotExist:
            logger.warn('model %s with id %s does not exist', model_name, model_id)  # noqa
            return Responses.not_found()
        except Exception as ex:
            message = ex.message if hasattr(ex, 'message') else ''
            logger.error('error while detaching %s - %s from %s. error: %s', model_name, model_id, task, message)  # noqa
            return Responses.server_error(message)

    @detail_route(methods=['post'])
    def change_status(self, request, pk=None):
        task = self.get_object()
        css = ChangeStatusSerializer(data=request.data)
        if not css.is_valid():
            logger.info('invalid request for change_status')
            return Response(css.errors, status=status.HTTP_400_BAD_REQUEST)

        change = css.validated_data
        user = None if request.user.is_anonymous() else request.user
        try:
            new_status = TaskStatus.objects.get(pk=change.get('status'))
            handler = TaskHandler()
            changes = handler.to_status(
                task=task,
                status=new_status,
                dry_run=change.get('dry_run', True),
                user=user
            )
            if not changes:
                logger.info('change_status is not allowed. from %s to %s.', task.status, new_status)
                return Responses.succeeded('No changes detected, no changes executed.')

            logger.info('executing status changes')
            flat_changes = TaskHandler.flatten(changes)
            change_serializer = TaskChangeSerializer(flat_changes, many=True)
            return Response(data=change_serializer.data)

        except TaskStatus.DoesNotExist:
            logger.warn('status selected by the user does not exist.')
            return Responses.not_found()
        except Exception as ex:
            error_msg = getattr(ex, 'message', '')
            logger.error('something wrong happened while trying to change task status. %s', error_msg, exc_info=True)
            return Responses.server_error(error_msg)


class CommentViewSet(viewsets.ModelViewSet):

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    filter_class = CommentFilter
    search_fields = (
        'id',
        'created_by',
        'task',
        'text',
    )


class AllocationViewSet(viewsets.ViewSet):

    """
    Viewset that allows you to see how your resources
    are allocated
    """

    def list(self, request):
        try:
            list_allocation_serializer = ListAllocationSerializer(data=request.data)
            if not list_allocation_serializer.is_valid():
                return Response(data=list_allocation_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            project = list_allocation_serializer.validated_data.get('project')
            min_date = list_allocation_serializer.validated_data.get('min_date')
            max_date = list_allocation_serializer.validated_data.get('max_date')

            users = User.objects.all()

            allocation_handler = AllocationHandler()
            allocations = allocation_handler.get_allocations(users, min_date, max_date, project)
            allocation_serial = AllocationSerializer(allocations, many=True)
            return Response(allocation_serial.data)
        except Exception as ex:
            message = ex.message if hasattr(ex, 'message') else ''
            logger.error('error while fetching list of allocations. Error: %s', message, exc_info=True)
            return Responses.server_error(message)

    def retrieve(self, request, pk=None):

        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Responses.not_found()

        try:
            las = ListAllocationSerializer(data=request.data)
            if not las.is_valid():
                return Response(data=las.errors, status=status.HTTP_400_BAD_REQUEST)

            project = las.validated_data.get('project')
            min_date = las.validated_data.get('min_date')
            max_date = las.validated_data.get('max_date')

            allocation_handler = AllocationHandler()
            allocations = allocation_handler.get_user_allocations(user, min_date, max_date, project)
            allocation_serializer = AllocationSerializer(allocations, many=True)
            return Response(allocation_serializer.data)
        except Exception as ex:
            message = ex.message if hasattr(ex, 'message') else ''
            logger.error('error while fetching allocation for user %s. Error: %s', user, message, exc_info=True)
            return Responses.server_error(message)
