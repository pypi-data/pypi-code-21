from django.core.exceptions import ObjectDoesNotExist
from fuzzywuzzy import fuzz, process
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .authentication import TokenAuthentication
from .models import Domain, Entity
from .serializers import EntitySerializer


class AuthenticatedView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)


class BestMatch(AuthenticatedView):
    def domain_set(self, domain):
        self.entities = Entity.objects.filter(domain=domain)

    def match_set(self, match_attrs):
        self.entities = self.entities.filter(
            attributes__contains=match_attrs
        )

    def subset(self, request, domain_slug):
        try:
            domain = Domain.objects.get(slug=domain_slug)
        except ObjectDoesNotExist:
            Response(
                {"message": "No domain found."},
                status=status.HTTP_200_OK
            )
        self.user = request.user
        data = request.data
        self.domain_set(domain)
        match_attrs = data.get('match_attrs', None)
        if match_attrs:
            self.match_set(match_attrs)

    def get(self, request, domain):
        self.subset(request, domain)
        # data = request.data
        serializer = EntitySerializer(self.entities, many=True)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def post(self, request, domain):
        self.subset(request, domain)
        # user = request.user
        # data = request.data
        serializer = EntitySerializer(self.entities, many=True)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
