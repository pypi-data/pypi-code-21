# coding: utf-8
"""
This module is responsible to figure out the allocation
for each user in hours/days.
"""
from datetime import timedelta
from django.db.models import Min, Max
from django.contrib.auth import get_user_model
from .models import Task
User = get_user_model()


class Allocation(object):

    user = None
    date_point = None
    tasks = None

    def __init__(self, user, date_point, tasks):
        """
        Initializes a new allocation record.
        """
        self.user = user
        self.date_point = date_point
        self.tasks = tasks

    @property
    def weight(self):
        return sum([task.weight for task in self.tasks])


class AllocationHandler(object):

    def get_allocations(self, users_queryset=None, min_date=None, max_date=None, project=None):
        allocations = list()
        if not users_queryset:
            users_queryset = User.objects.all()

        for user in users_queryset:
            allocations.extend(self.get_user_allocations(user, min_date, max_date, project))
        return allocations

    def get_user_allocations(self, user, min_date=None, max_date=None, project=None):
        temp = dict()
        allocs = list()
        tasks = Task.objects.filter(
            responsible=user,
            status__is_closing_status=False,
        ).exclude(
            start_date=None,
            end_date=None
        )
        if project:
            tasks = tasks.filter(project=project)
        if not min_date:
            # the usage of .all here is because
            # when you call all, it will clone the current
            # queryset, allowing you to add more queries to it,
            # without changing what is already filtered.
            min_date = tasks.all().aggregate(Min('start_date'))
            min_date = min_date.get('start_date__min')
        if not max_date:
            max_date = tasks.all().aggregate(Max('end_date'))
            max_date = max_date.get('end_date__max')
        if not min_date and not max_date:
            return allocs
        # inclusive range here, because range = 0 means
        # the start date and the last date we want is
        # max_date, so we add 1o max_date
        tasks.filter(start_date__gte=min_date, end_date__lte=max_date)
        for t in tasks:
            for day in range(0, t.duration.days + 1):
                current_datetime = t.start_date + timedelta(days=day)
                if temp.get(current_datetime):
                    temp[current_datetime].append(t)
                else:
                    temp[current_datetime] = [t]
        return [Allocation(user=user, date_point=dt, tasks=ts) for dt, ts in temp.items()]
