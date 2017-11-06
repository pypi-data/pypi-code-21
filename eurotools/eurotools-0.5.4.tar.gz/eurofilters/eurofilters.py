import json
import time
from importlib import import_module
from django.apps import apps
get_model = apps.get_model


class EuroFilters(object):
    ''' Class '''
    def __init__(self, version_key, data_key, filters, redis_conn, events_channel, partition):
        self.version_key = version_key
        self.data_key = data_key
        self.filters = filters
        self.redis_conn = redis_conn
        self.events_channel = events_channel
        self.partition = partition
        self.active_fields = ('active', 'is_active', '_active')

    def checkVersionData(self, params):
        filters = params['filters'].split(',')
        versionsClient = self.getVersion(params, filters)
        versionsRedis = self.redis_conn.hgetall(self.partition + '_' + self.version_key)
        data = {}
        if versionsRedis:
            filtersToCreate = set(versionsClient.keys()) - set(versionsRedis.keys())
            if filtersToCreate:
                data = self.createFilters(filtersToCreate)
            filtersToUpdate = self.compareVersions(versionsRedis, versionsClient)
            data2 = self.getData(filtersToUpdate)
            data.update(data2)
        else:
            data = self.createFilters(filters)
        return data

    def clearRedisData(self):
        ''' Cleans the info present on Redis '''
        self.redis_conn.delete(self.partition + '_' + self.data_key)
        self.redis_conn.delete(self.partition + '_' + self.version_key)

    def sendUpdateEvent(self):
        self.redis_conn.publish('{0}_{1}'.format(self.partition, self.events_channel), 'updateVersion')

    def getActiveField(self, model, fields):
        ''' Returns the active field of the given model '''
        model_fields = [f.attname for f in model._meta.fields]
        fields_map = [field in model_fields for field in self.active_fields]
        if True in fields_map:
            fields.append(self.active_fields[fields_map.index(True)])
        return fields

    def createFilterFromDB(self, f):
        names = self.filters[f]['db'][0].split('_')
        model = get_model(names[0], names[1])
        fields = [self.filters[f]['db'][1], self.filters[f]['db'][2]]
        aux_value = []
        fields.reverse()
        if model:
            fields = self.getActiveField(model, fields)
            aux_value = model.objects.using(self.partition).values(*fields)
        else:
            tables = self.filters[f]['tables']
            for table in tables:
                model = get_model(names[0], table)
                fields = self.getActiveField(model, fields)
                aux_value += model.objects.using(self.partition).values(*fields)
        aux_value = self.removeDuplicates(aux_value)
        fields.reverse()
        aux_value = self.modifiedColumns(f, aux_value)
        return aux_value

    def createFilterFromFunction(self, f):
        module = import_module(self.filters[f]['module'])
        function = getattr(module, self.filters[f]['function'])
        aux_value = function()
        return aux_value

    def createFilter(self, f):
        if 'type' in self.filters[f]:
            return self.createFilterFromFunction(f)
        else:
            return self.createFilterFromDB(f)

    def createFilters(self, filters):
        filters_data = {}
        version = int(time.time() * 1000)
        for f in filters:
            aux_value = self.createFilter(f)
            filters_data[f] = aux_value
            self.redis_conn.hset(self.partition + '_' + self.data_key, f, filters_data[f])
            filters_data[f + '__version'] = version
            self.redis_conn.hset(self.partition + '_' + self.version_key, f, version)
        self.sendUpdateEvent()
        return filters_data

    def removeDuplicates(self, values):
        aux_values = []
        for value in values:
            if value not in aux_values:
                aux_values.append(value)
        return aux_values

    def modifiedColumns(self, fil, value):
        pk = self.filters[fil]['db'][1]
        name = self.filters[fil]['db'][2]
        new_value = []
        active_field = None
        if len(value):
            for f in self.active_fields:
                if f in value[0].keys():
                    active_field = f
        for k in value:
            if {'id': k[pk], 'text': k[name]} not in new_value:
                if active_field:
                    new_value.append({'id': k[pk], 'text': k[name], 'active': k[active_field]})
                else:
                    new_value.append({'id': k[pk], 'text': k[name]})
        new_value = sorted(new_value, key=lambda k: k['text'])
        return new_value

    def compareVersions(self, versionsRedis, versionsClient):
        filtersToUpdate = []
        for key in versionsClient.keys():
            if key in versionsRedis:
                if versionsClient[key] < versionsRedis[key]:
                    filtersToUpdate.append(key)
        return filtersToUpdate

    def getVersion(self, params, filters):
        versions = {}
        for f in filters:
            if f in params:
                versions[f] = params[f]
            else:
                versions[f] = 0
        return versions

    def getData(self, filters):
        filters_data = {}
        for f in filters:
            filters_data[f] = eval(self.redis_conn.hget(self.partition + '_' + self.data_key, f))
            filters_data[f + '__version'] = eval(self.redis_conn.hget(self.partition + '_' + self.version_key, f))
        return filters_data


def eurofiltersmodifyJson(json_data):
    if isinstance(json_data, str):
        json_data = json.loads(json_data)['results']
        if {"text": "----", "id": "NULL"} in json_data:
            json_data.pop(json_data.index({"text": "----", "id": "NULL"}))
        if {"text": "-- All --", "id": "NULL"} in json_data:
            json_data.pop(json_data.index({"text": "-- All --", "id": "NULL"}))
        return json.dumps(json_data)
    else:
        raise ValueError('Expected some kind of json serialized data')
