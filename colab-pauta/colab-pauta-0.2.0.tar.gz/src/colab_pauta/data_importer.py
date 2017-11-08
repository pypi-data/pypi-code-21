from colab.plugins.data import PluginDataImporter
from django.db.models.fields import DateTimeField
from django.utils.dateparse import parse_datetime
from requests.exceptions import ConnectionError
from colab_pauta import models
import requests
import urllib


class ColabPautaDataImporter(PluginDataImporter):
    app_label = 'colab_pauta'

    def get_request_url(self, path, **kwargs):
        upstream = self.config.get('upstream')
        if 'api_key' not in path:
            kwargs['api_key'] = self.config.get('api_key')
            params = '?' + urllib.urlencode(kwargs)
        else:
            params = ''

        if upstream[-1] == '/':
            upstream = upstream[:-1]

        if "/pauta" in path:
            path = path.replace("/pauta", "")

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
                if field.name == 'agenda':
                    agenda = models.PautaAgenda.objects.get(
                        pk=data['agenda']['id']
                    )
                    obj.agenda = agenda
                    continue

                if field.name == 'theme_slug':
                    obj.theme_slug = data['theme']['slug']
                    continue

                if field.name == 'theme_name':
                    obj.theme_name = data['theme']['name']
                    continue

                if isinstance(field, DateTimeField):
                    value = parse_datetime(data[field.name])
                else:
                    value = data[field.name]

                setattr(obj, field.name, value)
            except KeyError:
                continue

        return obj

    def fetch_agendas(self):
        json_data = self.get_json_data('agenda')
        for data in json_data:
            agenda = self.fill_object_data(models.PautaAgenda, data)
            agenda.save()

    def fetch_groups(self):
        json_data = self.get_json_data('proposalgroup')
        for data in json_data:
            group = self.fill_object_data(models.PautaGroup, data)
            group.save()

    def fetch_data(self):
        models.PautaAgenda.objects.all().delete()
        models.PautaGroup.objects.all().delete()
        self.fetch_agendas()
        self.fetch_groups()
