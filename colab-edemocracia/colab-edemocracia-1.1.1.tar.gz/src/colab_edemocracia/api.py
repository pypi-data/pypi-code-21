# -*- encoding: utf-8 -*-
from django.contrib.auth import get_user_model
from rest_framework import filters, generics
from colab_edemocracia.serializers import UserSerializer


class UserListAPI(generics.ListAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter)
    filter_fields = ('id', )
    search_fields = ('username', 'first_name', 'last_name')
