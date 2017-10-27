# coding: utf-8
import logging
from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from .managers import (
    RelatedFileManager,
)
from .models import (
    File,
)
from .utils import get_model
from .serializers import (
    FileSerializer,
    AttachDetachSerializer,
)
from .filters import (
    FileFilter,
)
logger = logging.getLogger(__name__)


class FilesViewSetMixIn(object):

    @detail_route(methods=['get'])
    def files(self, request, pk=None):
        """
        Returns all the files related with
        an object.
        This does not rely on the assumption
        that the developer added the Files
        object in their model.
        Uses RelatedFileManager directly.
        """
        instance = self.get_object()
        rel_file_man = RelatedFileManager(
            instance=instance,
            model=instance._meta.model
        )
        queryset = rel_file_man.objects.all()
        file_serializer = FileSerializer(queryset, many=True)
        return Response(file_serializer.data)


class FileViewSet(viewsets.ModelViewSet):

    queryset = File.objects.all()
    serializer_class = FileSerializer
    filter_class = FileFilter
    search_fields = (
        'id',
        'name',
        'description',
        'tags'
    )

    @detail_route(methods=['post'])
    def attach(self, request, pk=None):

        file = self.get_object()
        ad_serializer = AttachDetachSerializer(data=request.data)
        if not ad_serializer.is_valid():
            return Response(ad_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        model_name = ad_serializer.validated_data.get('model_name')
        model_id = ad_serializer.validated_data.get('model_id')
        model_class = get_model(model_name)
        if not model_class:
            return Response('not found', status=status.HTTP_404_NOT_FOUND)
        try:
            model = model_class.objects.get(pk=model_id)
            file.attach(model)
            return Response('success')
        except model_class.DoesNotExist:
            logger.warn('%s model with id %s does not exist', model_name, model_id)
            return Response('not found', status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            message = ex.message if hasattr(ex.message) else ''
            logger.error('error while attaching %s - %s to %s. error: %s', model_name, model_id, file, message)
            return Response('error', status=status.HTTP_500_SERVER_ERROR)

    @detail_route(methods=['post'])
    def detach(self, request, pk=None):

        file = self.get_object()
        ad_serializer = AttachDetachSerializer(data=request.data)
        if not ad_serializer.is_valid():
            return Response(ad_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        model_name = ad_serializer.validated_data.get('model_name')
        model_id = ad_serializer.validated_data.get('model_id')
        model_class = get_model(model_name)
        if not model_class:
            return Response('not found', status=status.HTTP_404_NOT_FOUND)
        try:
            model = model_class.objects.get(pk=model_id)
            file.detach(model)
            return Response('success')
        except model_class.DoesNotExist:
            logger.warn('%s model with id %s does not exist', model_name, model_id)
            return Response('not found', status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            message = ex.message if hasattr(ex.message) else ''
            logger.error('error while attaching %s - %s to %s. error: %s', model_name, model_id, file, message)
            return Response('error', status=status.HTTP_500_SERVER_ERROR)
