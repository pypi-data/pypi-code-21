from requests.exceptions import ConnectionError
from django.db.models.fields import DateTimeField
from django.db import IntegrityError, OperationalError
from colab.plugins.data import PluginDataImporter
from django.utils.dateparse import parse_datetime
from django.contrib.auth import get_user_model
from colab_wikilegis import models
import requests
import urllib
import logging
import re

LOGGER = logging.getLogger('colab_wikilegis')
User = get_user_model()


class ColabWikilegisPluginDataImporter(PluginDataImporter):
    app_label = 'colab_wikilegis'

    def get_request_url(self, path, **kwargs):
        upstream = self.config.get('upstream')
        if 'api_key' not in path:
            kwargs['api_key'] = self.config.get('api_key')
            params = '?' + urllib.urlencode(kwargs)
        else:
            params = ''

        if upstream[-1] == '/':
            upstream = upstream[:-1]

        if "/wikilegis" in path:
            path = path.replace("/wikilegis", "")

        return u'{}{}{}'.format(upstream, path, params)

    def get_json_data(self, resource_name='', next_path=''):
        if not next_path and resource_name:
            api_url = '/api/v1/{}/'.format(resource_name)
            url = self.get_request_url(api_url)
        else:
            url = self.get_request_url(next_path)
        full_json_data = []
        try:
            response = requests.get(url)
            json_data = response.json()
            full_json_data.extend(json_data['objects'])
            if json_data['meta']['next']:
                json_page = self.get_json_data(
                    next_path=json_data['meta']['next']
                )
                full_json_data.extend(json_page)
        except ConnectionError:
            pass
        except ValueError:
            pass

        return full_json_data

    def fill_object_data(self, model_class, data):
        try:
            obj = model_class.objects.get(id=data['id'])
        except model_class.DoesNotExist:
            obj = model_class()
        except KeyError:
            obj = model_class()

        for field in obj._meta.fields:
            try:
                if field.name == 'username':
                    obj.username = re.sub('@.*', '', data['email'])
                    continue

                if field.name == 'user':
                    user = User.objects.get(email=data['user']['email'])
                    obj.user = user
                    continue

                if field.name == 'author':
                    author = data['author']
                    if author:
                        user = User.objects.get(email=author['email'])
                    else:
                        user = None
                    obj.author = user
                    continue

                if field.name == 'segment_type':
                    segment_type = models.WikilegisSegmentType.objects.get(
                        name=data['segment_type']['name']
                    )
                    obj.segment_type = segment_type
                    continue

                if field.name == 'theme':
                    theme = models.WikilegisBillTheme.objects.get(
                        slug=data['theme']['slug']
                    )
                    obj.theme = theme
                    continue

                if field.name == 'reporting_member':
                    reporting_member = data["reporting_member"]
                    if reporting_member:
                        user = User.objects.get(
                            email=reporting_member['email'])
                    else:
                        user = None
                    obj.user = user
                    continue

                if field.name == 'replaced':
                    obj.replaced_id = data['replaced']
                    continue

                if field.name == 'type':
                    obj.type_id = data['type']
                    continue

                if field.name == 'bill':
                    bill = models.WikilegisBill.objects.get(
                        id=data['bill']['id']
                    )
                    obj.bill = bill
                    continue

                if isinstance(field, DateTimeField):
                    value = parse_datetime(data[field.name])
                else:
                    value = data[field.name]

                setattr(obj, field.name, value)
            except KeyError:
                continue

        return obj

    def fetch_segment_types(self):
        json_data = self.get_json_data('segmenttype')
        for data in json_data:
            segment_type = self.fill_object_data(models.WikilegisSegmentType,
                                                 data)
            segment_type.save()

    def fetch_bills(self):
        json_data = self.get_json_data('bill')
        for data in json_data:
            bill = self.fill_object_data(models.WikilegisBill, data)
            bill.save()

    def fetch_segments(self, json_data=None):
        if json_data is None:
            json_data = self.get_json_data('billsegment')

        retry = False
        retry_data = []
        for data in json_data:
            while True:
                segment = self.fill_object_data(models.WikilegisSegment, data)
                try:
                    segment.save()
                    break
                except IntegrityError:
                    retry = True
                    retry_data = [data] + retry_data
                    break
                    continue
                except OperationalError:
                    pass

        if retry:
            self.fetch_segments(retry_data)

    def fetch_comments(self):
        json_data = self.get_json_data('comments')

        for data in json_data:
            comment = self.fill_object_data(models.WikilegisComment, data)
            comment.save()

    def fetch_themes(self):
        json_data = self.get_json_data('billtheme')
        for data in json_data:
            theme = self.fill_object_data(models.WikilegisBillTheme, data)
            theme.save()

    def fetch_users(self):
        json_data = self.get_json_data('user')
        user_list = []
        for data in json_data:
            user = self.fill_object_data(User, data)
            user_list.append(user)
        return user_list

    def fetch_data(self):
        models.WikilegisBillTheme.objects.all().delete()
        models.WikilegisBill.objects.all().delete()
        models.WikilegisSegmentType.objects.all().delete()
        models.WikilegisSegment.objects.all().delete()

        self.fetch_themes()
        self.fetch_bills()
        self.fetch_segment_types()
        self.fetch_segments()
