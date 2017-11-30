from decimal import Decimal

import requests

from ..exceptions import APIError, reraise
from .collections import PaginatableAddressableCollection
from .files import File, BaseFileCollection
from .pricing import Price, TotalPrice, DP2


class Job(object):
    def __init__(self, collection, job_id, status, service_id, source_locale_id,
                 target_locale_id, source_file_id, target_file_id):
        self.collection = collection
        self.id = job_id
        self.status = status
        self.service_id = service_id
        self.source_locale_id = source_locale_id
        self.target_locale_id = target_locale_id
        self.source_file_id = source_file_id
        self.target_file_id = target_file_id

        self.files = JobFileCollection(job=self, per_page=self.client.per_page)

    def __repr__(self):
        return '<Job {}>'.format(self.id)

    def __eq__(self, other):
        return all((
            self.collection == other.collection,
            self.id == other.id,
            self.status == other.status,
            self.service_id == other.service_id,
            self.source_locale_id == other.source_locale_id,
            self.target_locale_id == other.target_locale_id,
            self.source_file_id == other.source_file_id,
            self.target_file_id == other.target_file_id,
            ))

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def url_path(self):
        return self.collection.item_url_path(self.id)

    @property
    def client(self):
        return self.collection.client

    @property
    def service(self):
        return self.collection.client.services.get(self.service_id)

    @property
    def source_locale(self):
        return self.collection.client.locales.get(self.source_locale_id)

    @property
    def target_locale(self):
        return self.collection.client.locales.get(self.target_locale_id)

    @property
    def source_file(self):
        return self.collection.client.files.get(self.source_file_id)

    @property
    def target_file(self):
        if self.target_file_id is None:
            return None
        return self.collection.client.files.get(self.target_file_id)

    @property
    def price(self):
        """
        Return the TotalPrice for this Job, or None if no pricing information is
        available.
        """
        path = '{}/price'.format(self.url_path)
        try:
            response = self.collection.client.api_get_json(path)
        except requests.RequestException as exc:
            if exc.response.status_code == 404:
                return None
            else:
                reraise(APIError)
        return TotalPrice(
            total_with_discount=Price(
                currency_code=response['currencyCode'],
                net=Decimal(str(response['totalWoVatWDiscount'])).quantize(DP2),
                gross=Decimal(str(response['totalWVatWDiscount'])).quantize(DP2),
            ),
            total_without_discount=Price(
                currency_code=response['currencyCode'],
                net=Decimal(str(response['totalWoVatWoDiscount'])).quantize(DP2),
                gross=Decimal(str(response['totalWVatWoDiscount'])).quantize(DP2),
            ),
        )

    @property
    def metrics(self):
        """
        Return a mapping (str -> Metric) of the metrics for this Job. If no
        metric information is available, the mapping will be empty.
        """
        path = '{}/metrics'.format(self.url_path)
        try:
            response = self.collection.client.api_get_json(path)
        except requests.RequestException as exc:
            if exc.response.status_code == 404:
                return {}
            else:
                reraise(APIError)

        def to_metric(data):
            return Metric(
                white_spaces=data['WHITE_SPACES'],
                segments=data['SEGMENTS'],
                words=data['WORDS'],
                characters=data['CHARACTERS'],
            )

        return {k: to_metric(d) for (k, d) in response['values'].items()}

    def refresh(self):
        updated = self.collection.jobs.get(self.id)
        self.__dict__ = updated.__dict__

    def delete(self):
        try:
            self.collection.client.api_delete(self.url_path)
        except requests.RequestException:
            reraise(APIError)


class Metric(object):
    def __init__(self, white_spaces, segments, words, characters):
        self.white_spaces = white_spaces
        self.segments = segments
        self.words = words
        self.characters = characters

    def __repr__(self):
        return '<Metric: White spaces {} | Segments {} | Words {} | Characters {}>'.format(
            self.white_spaces,
            self.segments,
            self.words,
            self.characters,
        )

    def __eq__(self, other):
        return all((
            self.white_spaces == other.white_spaces,
            self.segments == other.segments,
            self.words == other.words,
            self.characters == other.characters,
        ))

    def __ne__(self, other):
        return not self.__eq__(other)

    def __add__(self, other):
        return Metric(
            white_spaces=(self.white_spaces + other.white_spaces),
            segments=(self.segments + other.segments),
            words=(self.words + other.words),
            characters=(self.characters + other.characters),
        )

    def __nonzero__(self):
        return any((
            self.white_spaces,
            self.segments,
            self.words,
            self.characters,
        ))


class JobFileCollection(BaseFileCollection, PaginatableAddressableCollection):
    def __init__(self, job, *args, **kwargs):
        self.job = job
        client = kwargs.pop('client', job.client)
        super(JobFileCollection, self).__init__(client=client, *args, **kwargs)

    @property
    def url_path(self):
        return '{}/files'.format(self.job.url_path)

    def clone(self):
        return super(JobFileCollection, self).clone(job=self.job)
