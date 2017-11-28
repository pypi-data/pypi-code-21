import sys

from django.db.models.query import QuerySet
from django.db.models.sql.query import Query
from django.db.models.aggregates import Count
from django.utils import six
from django.db import (
    DJANGO_VERSION_PICKLE_KEY, IntegrityError, connections, router,
    transaction,
)
from twisted.internet.defer import Deferred

from .decorators import make_asynclike
from .exceptions import FetchNotCalled
from .common import AsyncIterator, TwModelIterable


class TwistedQuery(Query):
    defered = False

    async def get_count(self, using):
        """
        Performs a COUNT() query using the current filter constraints.
        """
        obj = self.clone()
        obj.add_annotation(Count('*'), alias='__count', is_summary=True)
        y = await obj.get_aggregation(using, ['__count'])
        number = y['__count']
        if number is None:
            number = 0
        return number

    @make_asynclike
    def get_aggregation(self, using, added_aggregate_names):
        return super(TwistedQuery, self).get_aggregation(using, added_aggregate_names)

    def clone(self, klass=None, memo=None, **kwargs):
        clone = super(TwistedQuery, self).clone(klass=klass, memo=memo, **kwargs)
        clone.defered = self.defered
        return clone


class TwistedQuerySetBase:
    defered = False
    def __init__(self, model=None, query=None, using=None, hints=None):
        query = query or TwistedQuery(model)
        super(TwistedQuerySetBase, self).__init__(model=model, query=query, using=using, hints=hints)
        self._iterable_class = TwModelIterable

    async def fetch(self):
        await self._fetch_all()
        return self

    def __check_fetch__(self):
        if not self.defered and self._result_cache is None:
            raise FetchNotCalled('You must call .fetch() at first.')

    def __len__(self):
        """
        You must call .fetch() method before calling __len__
        Some functions like objects.get() making a dbquery by asking len(qs).
        """
        self.__check_fetch__()
        return super(TwistedQuerySetBase, self).__len__()

    def __iter__(self):
        self.__check_fetch__()
        # self._fetch_all()
        return iter(self._result_cache)

    async def __aiter__(self):
        d = self._fetch_all()
        if isinstance(d, Deferred):
            await d
        return AsyncIterator(self._result_cache)

    def __bool__(self):
        """
        You must call .fetch() method before calling __bool__
        """
        self.__check_fetch__()
        return  super(TwistedQuerySetBase, self).__bool__()
    #
    # def iterator(self):
    #     return super(TwistedQuerySetBase, self).iterator()

    @make_asynclike
    def aggregate(self, *args, **kwargs):
        return super(TwistedQuerySetBase, self).aggregate(*args, **kwargs)

    async def count(self):
        """
        Performs a SELECT COUNT() and returns the number of records as an
        integer.

        If the QuerySet is already fully cached this simply returns the length
        of the cached results set to avoid multiple SELECT COUNT(*) calls.
        """
        if self._result_cache is not None:
            return len(self._result_cache)
        return await self.query.get_count(using=self.db)

    async def get(self, *args, **kwargs):
        """
        Performs the query and returns a single object matching the given
        keyword arguments.
        """
        clone = self.filter(*args, **kwargs)
        if self.query.can_filter() and not self.query.distinct_fields:
            clone = clone.order_by()
        await clone.fetch()
        num = len(clone)
        if num == 1:
            return clone._result_cache[0]
        if not num:
            raise self.model.DoesNotExist(
                "%s matching query does not exist." %
                self.model._meta.object_name
            )
        raise self.model.MultipleObjectsReturned(
            "get() returned more than one %s -- it returned %s!" %
            (self.model._meta.object_name, num)
        )

    @make_asynclike
    def create(self, **kwargs):
        return super(TwistedQuerySetBase, self).create(**kwargs)

    @make_asynclike
    def bulk_create(self, objs, batch_size=None):
        return super(TwistedQuerySetBase, self).bulk_create(objs, batch_size=batch_size)

    async def get_or_create(self, defaults=None, **kwargs):
        """
        Looks up an object with the given kwargs, creating one if necessary.
        Returns a tuple of (object, created), where created is a boolean
        specifying whether an object was created.
        """
        lookup, params = self._extract_model_params(defaults, **kwargs)
        # The get() needs to be targeted at the write database in order
        # to avoid potential transaction consistency problems.
        self._for_write = True
        try:
            result = await self.get(**lookup)
            return result, False
        except self.model.DoesNotExist:
            return await self._create_object_from_params(lookup, params)

    async def update_or_create(self, defaults=None, **kwargs):
        """
        Looks up an object with the given kwargs, updating one with defaults
        if it exists, otherwise creates a new one.
        Returns a tuple (object, created), where created is a boolean
        specifying whether an object was created.
        """
        defaults = defaults or {}
        lookup, params = self._extract_model_params(defaults, **kwargs)
        self._for_write = True
        with transaction.atomic(using=self.db):
            try:
                obj = await self.select_for_update().get(**lookup)
            except self.model.DoesNotExist:
                obj, created = await self._create_object_from_params(lookup, params)
                if created:
                    return obj, created
            for k, v in six.iteritems(defaults):
                setattr(obj, k, v() if callable(v) else v)
            await self.objsave(obj, using=self.db)
        return obj, False

    @make_asynclike
    def _create_object_from_params(self, lookup, params):
        try:
            with transaction.atomic(using=self.db):
                params = {k: v() if callable(v) else v for k, v in params.items()}
                obj = self.create(**params)
            return obj, True
        except IntegrityError:
            exc_info = sys.exc_info()
            try:
                return QuerySet.get(self, **lookup), False
            except self.model.DoesNotExist:
                pass
            six.reraise(*exc_info)

    async def objsave(self, obj, *args, **kwargs):
        return await self._objsave(obj, *args, **kwargs)

    @make_asynclike
    def _objsave(self, obj, *args, **kwargs):
        return obj.save(*args, **kwargs)

    @make_asynclike
    def delete(self):
        return super(TwistedQuerySetBase, self).delete()
    delete.alters_data = True
    delete.queryset_only = True

    @make_asynclike
    def update(self, **kwargs):
        return super(TwistedQuerySetBase, self).update(**kwargs)
    update.alters_data = True

    @make_asynclike
    def exists(self):
        return super(TwistedQuerySetBase, self).exists()

    ##################################################
    # PUBLIC METHODS THAT RETURN A QUERYSET SUBCLASS #
    ##################################################
    #
    # @make_asynclike
    # def _insert(self, objs, fields, return_id=False, raw=False, using=None):
    #     return super(TwistedQuerySetBase, self)._insert(objs, fields, return_id=False, raw=False, using=None)
    # _insert.alters_data = True
    # _insert.queryset_only = False

    def _clone(self, **kwargs):
        clone = super(TwistedQuerySetBase, self)._clone()
        clone.defered = self.defered
        return clone

    @make_asynclike
    def _fetch_all(self):
        return super(TwistedQuerySetBase, self)._fetch_all()


class TwistedQuerySet(TwistedQuerySetBase, QuerySet):
    pass


try:
    # https://github.com/aykut/django-bulk-update
    from django_bulk_update.query import BulkUpdateQuerySet
    class BulkTwistedQuerySet(TwistedQuerySetBase, BulkUpdateQuerySet):
        @make_asynclike
        def bulk_update(self, *args, **kwargs):
            return super(BulkTwistedQuerySet, self).bulk_update(*args, **kwargs)
except ImportError:
    pass