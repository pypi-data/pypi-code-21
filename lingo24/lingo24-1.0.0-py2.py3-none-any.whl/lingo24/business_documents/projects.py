import datetime
import json
from decimal import Decimal

import requests

from ..exceptions import APIError, InvalidState, reraise
from .collections import SortablePaginatableAddressableCollection, PaginatableAddressableCollection
from .files import File, BaseFileCollection
from .jobs import Job
from .pricing import Charge, Price, TotalPrice, DP2


class ProjectCollection(SortablePaginatableAddressableCollection):
    url_path = 'projects/'

    def make_item(self, **kwargs):
        return Project(
            client=self.client,
            project_id=kwargs['id'],
            name=kwargs['name'],
            domain_id=kwargs['domainId'],
            status=kwargs['projectStatus'],
            created=datetime.datetime.utcfromtimestamp(kwargs['created']),
            callback_url=kwargs['projectCallbackUrl'],
            )

    def create(self, name, domain=None, callback_url=None):
        data = {
            'name': name,
        }
        if domain is not None:
            data['domainId'] = getattr(domain, 'id', domain)
        if callback_url is not None:
            data['projectCallbackUrl'] = callback_url
        try:
            response = self.client.api_post_json(
                path='projects',
                data=data,
            )
        except requests.RequestException:
            reraise(APIError)
        return self.make_item(**response)


class Project(object):
    def __init__(self, client, project_id, name, domain_id, status, created,
                 callback_url):
        self.client = client
        self.id = project_id
        self.domain_id = domain_id
        self.name = name
        self.status = status
        self.created = created
        self.callback_url = callback_url

        self.charges = ProjectChargeCollection(project=self, per_page=client.per_page)
        self.files = ProjectFileCollection(project=self, per_page=client.per_page)
        self.jobs = ProjectJobCollection(project=self, per_page=client.per_page)

    def __repr__(self):
        return '<Project {}: {}>'.format(self.id, self.name)

    def __eq__(self, other):
        return all((
            self.client == other.client,
            self.id == other.id,
            self.domain_id == other.domain_id,
            self.name == other.name,
            self.status == other.status,
            self.created == other.created,
            self.callback_url == other.callback_url,
            ))

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def url_path(self):
        return ProjectCollection(self.client).item_url_path(self.id)

    @property
    def domain(self):
        if self.domain_id is None:
            return None
        return self.client.domains.get(self.domain_id)

    @property
    def price(self):
        """
        Return the TotalPrice for this Project, or None if no pricing
        information is available.
        """
        path = '{}/price'.format(self.url_path)
        try:
            response = self.client.api_get_json(path)
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

    def refresh(self):
        updated = self.client.projects.get(self.id)
        self.__dict__ = updated.__dict__

    def request_quote(self):
        if self.status != 'CREATED':
            raise InvalidState(
                'Cannot accept the quote of a project with status {}'.format(
                    self.status
                )
            )
        data = {
            'projectStatus': 'QUOTED',
        }
        try:
            self.client.api_put_json(path=self.url_path, data=data)
        except requests.RequestException:
            reraise(APIError)
        self.status = 'PENDING'

    def cancel(self):
        if self.status not in ('CREATED', 'QUOTED'):
            raise InvalidState(
                'Cannot cancel a project with status {}'.format(self.status)
            )
        try:
            self.client.api_delete(self.url_path)
        except requests.RequestException:
            reraise(APIError)
        self.status = 'CANCELLED'

    def accept_quote(self):
        if self.status != 'QUOTED':
            raise InvalidState(
                'Cannot accept the quote of a project with status {}'.format(
                    self.status
                )
            )
        data = {
            'projectStatus': 'IN_PROGRESS',
        }
        try:
            self.client.api_put_json(path=self.url_path, data=data)
        except requests.RequestException:
            reraise(APIError)
        self.status = 'IN_PROGRESS'


class ProjectFileCollection(BaseFileCollection, PaginatableAddressableCollection):
    def __init__(self, project, *args, **kwargs):
        self.project = project
        client = kwargs.pop('client', project.client)
        super(ProjectFileCollection, self).__init__(client=client, *args, **kwargs)

    def __eq__(self, other):
        return all((
            super(ProjectFileCollection, self).__eq__(other),
            self.project == other.project,
            ))

    @property
    def url_path(self):
        return '{}/files'.format(self.project.url_path)

    def clone(self):
        return super(ProjectFileCollection, self).clone(project=self.project)

    def add(self, existing_file):
        data = {
            'id': existing_file.id,
        }
        try:
            self.client.api_post(
                path=self.url_path,
                data=json.dumps(data),
                headers={'Content-Type': 'application/json'},
            )
        except requests.RequestException:
            reraise(APIError)

    def remove(self, existing_file):
        path = self.item_url_path(existing_file.id)
        try:
            self.client.api_delete(
                path=path,
            )
        except requests.RequestException:
            reraise(APIError)


class ProjectJobCollection(PaginatableAddressableCollection):
    def __init__(self, project, *args, **kwargs):
        self.project = project
        client = kwargs.pop('client', project.client)
        super(ProjectJobCollection, self).__init__(client=client, *args, **kwargs)

    @property
    def url_path(self):
        return '{}/jobs'.format(self.project.url_path)

    def clone(self):
        return super(ProjectJobCollection, self).clone(project=self.project)

    def make_item(self, **kwargs):
        return Job(
            collection=self,
            job_id=kwargs['id'],
            status=kwargs['jobStatus'],
            service_id=kwargs['serviceId'],
            source_locale_id=kwargs['sourceLocaleId'],
            target_locale_id=kwargs['targetLocaleId'],
            source_file_id=kwargs['sourceFileId'],
            target_file_id=kwargs['targetFileId'],
            )

    def create(self, service, source_locale, source_file, target_locale):
        data = {
            'projectId': self.project.id,
            'serviceId': getattr(service, 'id', service),
            'sourceLocaleId': getattr(source_locale, 'id', source_locale),
            'sourceFileId': getattr(source_file, 'id', source_file),
            'targetLocaleId': getattr(target_locale, 'id', target_locale),
        }
        response = self.client.api_post_json(
            path=self.url_path,
            data=data,
        )
        return self.make_item(**response)


class ProjectChargeCollection(PaginatableAddressableCollection):
    def __init__(self, project, *args, **kwargs):
        self.project = project
        client = kwargs.pop('client', project.client)
        super(ProjectChargeCollection, self).__init__(client=client, *args, **kwargs)

    @property
    def url_path(self):
        return '{}/charges'.format(self.project.url_path)

    def clone(self):
        return super(ProjectChargeCollection, self).clone(project=self.project)

    def make_item(self, **kwargs):
        return Charge(
            collection=self,
            title=kwargs['title'],
            value=kwargs['value'],
        )
