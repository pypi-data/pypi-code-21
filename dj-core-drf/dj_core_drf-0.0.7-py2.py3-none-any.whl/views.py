from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import CoreJSONRenderer
from rest_framework.response import Response
from rest_framework.schemas import SchemaGenerator
from rest_framework_swagger.renderers import SwaggerUIRenderer, OpenAPIRenderer


def get_schema_view(title):
    @api_view()
    @renderer_classes([SwaggerUIRenderer, OpenAPIRenderer, CoreJSONRenderer])
    def schema_view(request):
        return Response(SchemaGenerator(title=title).get_schema(request))

    return schema_view
