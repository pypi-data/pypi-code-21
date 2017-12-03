from django.http import JsonResponse
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.viewsets import ViewSet

from scatl.api.serializers.query_data import QueryDataDeserializer, \
    QueryDataSerializer
from scatl.services.query_data.complementer import complement_query_data_from_db


class QueryDataViewSet(ViewSet):
    permission_classes = [AllowAny]
    
    def list(self, request: Request) -> JsonResponse:
        query_data = QueryDataDeserializer(request).deserialize()
        complement_query_data_from_db(query_data)
        query_data_json = QueryDataSerializer(query_data).serialize()
        return JsonResponse(data=query_data_json, content_type='application/json')
