# -*- coding:utf-8 -*-
from rest_framework import decorators, response, status

__author__ = 'denishuang'


class BatchCreateModelMixin(object):
    @decorators.list_route(['POST'])
    def batch_create(self, request):
        errors = []
        ss = []
        for d in request.data:
            serializer = self.get_serializer(data=d)
            if not serializer.is_valid():
                errors.append({"object": d, "errors": serializer.errors})
            else:
                ss.append(serializer)
        if errors:
            return response.Response(errors, status=status.HTTP_400_BAD_REQUEST)
        for s in ss:
            self.perform_create(s)
        return response.Response({"success": len(ss)}, status=status.HTTP_201_CREATED)


class RestCreateMixin(object):
    def get_serializer_save_args(self):
        return {}

    def perform_create(self, serializer):
        serializer.save(**self.get_serializer_save_args())


class UserApiMixin(RestCreateMixin):
    def get_serializer_save_args(self):
        d = super(UserApiMixin, self).get_serializer_save_args()
        d['user'] = self.request.user
        return d
