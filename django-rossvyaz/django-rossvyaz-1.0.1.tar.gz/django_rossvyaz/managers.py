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
        return queryset.filter(
            first_code=first_code,
            to_code__gte=last_code,
            from_code__lte=last_code,
        )
