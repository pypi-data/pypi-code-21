from requests.exceptions import ConnectionError
from django.db.models.fields import DateTimeField
from colab.plugins.data import PluginDataImporter
from django.utils.dateparse import parse_datetime
from django.contrib.auth import get_user_model
from django.template.defaultfilters import slugify
from colab_audiencias import models
import requests
import urllib
import logging

LOGGER = logging.getLogger('colab_audiencias')
User = get_user_model()


class ColabAudienciasPluginDataImporter(PluginDataImporter):
    app_label = 'colab_audiencias'

    def get_request_url(self, path, **kwargs):
        upstream = self.config.get('upstream')
        kwargs['api_key'] = self.config.get('api_key')
        params = urllib.urlencode(kwargs)

        if upstream[-1] == '/':
            upstream = upstream[:-1]
        return u'{}{}?{}'.format(upstream, path, params)

    def get_json_data(self, resource_name, page=1):
        api_url = '/api/{}/'.format(resource_name)
        url = self.get_request_url(api_url, page=page)
        full_json_data = []

        try:
            response = requests.get(url)
            json_data = response.json()
            full_json_data.extend(json_data['results'])
            if json_data['next']:
                page += 1
                json_page = self.get_json_data(resource_name, page)
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
                if field.name == 'user':
                    user = User.objects.get(email=data['user']['email'])
                    obj.user = user
                    continue

                if field.name == 'email':
                    if not data['email']:
                        email = slugify(data['username']) + "@email.com"
                    else:
                        email = data['email']
                    obj.email = email
                    continue

                if field.name == 'room':
                    obj.room_id = data['room']
                    continue

                if isinstance(field, DateTimeField):
                    dt_value = data[field.name]
                    if dt_value:
                        value = parse_datetime(dt_value)
                    else:
                        value = None
                else:
                    value = data[field.name]

                setattr(obj, field.name, value)
            except KeyError:
                continue

        return obj

    def fetch_users(self):
        json_data = self.get_json_data('user')
        already_users = User.objects.values_list('email', flat=True)
        for data in json_data:
            user = self.fill_object_data(User, data)
            if user.email not in already_users:
                user.save()

    def fetch_rooms(self):
        json_data = self.get_json_data('room')
        for data in json_data:
            room = self.fill_object_data(models.AudienciasRoom, data)
            room.save()

    def fetch_questions(self):
        json_data = self.get_json_data('question')
        for data in json_data:
            question = self.fill_object_data(models.AudienciasQuestion, data)
            question.save()

    def fetch_data(self):
        self.fetch_rooms()
        self.fetch_questions()
