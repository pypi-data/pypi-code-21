# coding: utf-8
from django.db import models


class PhoneCodeManager(models.Manager):

    def by_phone(self, phone):
        first_code = phone[:3]
        last_code = phone[3:]
        if hasattr(self, 'get_queryset'):
            # django >= 1.6
            queryset = super(PhoneCodeManager, self).get_queryset()
        else:
            # django < 1.6
            queryset = super(PhoneCodeManager, self).get_query_set()
        return queryset.extra(where=[
            'first_code=%s',
            'to_code::int >= %s',
            'from_code::int <= %s',
        ], params=[first_code, int(last_code), int(last_code)])
