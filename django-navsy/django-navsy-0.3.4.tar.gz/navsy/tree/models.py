# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils.encoding import python_2_unicode_compatible, force_text


@python_2_unicode_compatible
class NodeModel(models.Model):

    parent = models.ForeignKey(
        'self', related_name='children', on_delete=models.CASCADE,
        blank=True, null=True)

    parents_pks = models.CharField(
        max_length=500, blank=True, default='', editable=False)
    parents_count = models.PositiveSmallIntegerField(default=0, editable=False)

    children_pks = models.CharField(
        max_length=500, blank=True, default='', editable=False)
    children_count = models.PositiveSmallIntegerField(
        default=0, editable=False)

    siblings_pks = models.CharField(
        max_length=500, blank=True, default='', editable=False)
    siblings_count = models.PositiveSmallIntegerField(
        default=0, editable=False)

    priority = models.PositiveSmallIntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(9999)])
    priorities = models.CharField(
        max_length=100, blank=True, default='', editable=False)

    def get_parents(self):
        return list(self.__str_to_qs(self.parents_pks))

    def get_parents_pks(self):
        return self.__str_to_list(self.parents_pks)

    def get_children(self):
        return list(self.__str_to_qs(self.children_pks))

    def get_children_pks(self):
        return self.__str_to_list(self.children_pks)

    def get_siblings(self):
        return list(self.__str_to_qs(self.siblings_pks))

    def get_siblings_pks(self):
        return self.__str_to_list(self.siblings_pks)

    def __list_to_str(self, l):
        s = '|'.join([str(v) for v in l])
        return s

    def __str_to_list(self, s):
        l = [int(v) for v in s.split('|') if v]
        return l

    def __str_to_qs(self, s):
        pks = self.__str_to_list(s)
        qs = self.__class__.objects.filter(pk__in=pks).order_by('-priorities')
        return qs

    def __get_node_data(self, pk_max=0):

        data = {}

        # retrieve parents
        parent_obj = self.parent
        parents_list = []
        obj = parent_obj

        while obj:
            parents_list.insert(0, obj)
            obj = obj.parent

        parents_pks = [obj.pk for obj in parents_list]

        # update parents
        data['parents_pks'] = self.__list_to_str(parents_pks)
        data['parents_count'] = len(parents_list)

        # update children
        children_list = list(self.__class__.objects.filter(
            parent=self.pk).values_list('pk', flat=True))

        data['children_pks'] = self.__list_to_str(children_list)
        data['children_count'] = len(children_list)

        # update siblings
        siblings_list = list(self.__class__.objects.filter(
            parent=parent_obj).exclude(
            pk=self.pk).values_list('pk', flat=True))

        data['siblings_pks'] = self.__list_to_str(siblings_list)
        data['siblings_count'] = len(siblings_list)

        # update priorities
        priorities_objs = list(parents_list) + [self]
        priorities_list = [
            str(min(obj.priority, 9999)).zfill(4) +
            str(max(0, 99999 - obj.pk)).zfill(5) for obj in priorities_objs]
        priorities_list += ['9' * 9] * (10 - len(priorities_list))
        data['priorities'] = self.__list_to_str(priorities_list)

        return data

    @staticmethod
    @receiver(post_delete, dispatch_uid='post_delete_node')
    @receiver(post_save, dispatch_uid='post_save_node')
    def __update_nodes_data(sender, instance, **kwargs):

        if settings.DEBUG:
            import timeit
            start_time = timeit.default_timer()

        if not isinstance(instance, NodeModel):
            return

        objs_manager = sender.objects
        objs_filter = objs_manager.filter
        objs_qs = objs_manager.select_related(
            'parent').prefetch_related('children')
        objs_list = list(objs_qs)

        for obj in objs_list:
            obj_data = obj.__get_node_data()
            objs_filter(pk=obj.pk).update(**obj_data)

        if settings.DEBUG:
            elapsed = timeit.default_timer() - start_time
            print('navsy.tree.models.NodeModel -> update_nodes_data in %ss' % (elapsed, ))

    class Meta:
        abstract = True

    def __str__(self):
        return force_text(self.pk)
