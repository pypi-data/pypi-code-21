import io
import json
import logging
import pprint
import tarfile
import time
import urllib.parse

import aiohttp
import arrow
import drophi.types

LOGGER = logging.getLogger(__name__)

class CommunicationError(Exception):
    "Parent class for any communications errors with Docker"
    def __init__(self, method, url, status, text, payload=None, params=None):
        super().__init__("Failed to communicate with docker on {} {} with payload {} and params {}: status {} content {}".format(
            method, url, payload, params, status, text)
        )
        LOGGER.debug("Communcation error with docker on %s %s with payload %s\n and params %s: status %s content %s",
            method, url, pprint.pformat(payload), params, status, text)
        self.method  = method
        self.payload = payload
        self.params  = params
        self.status  = status
        self.text    = text
        self.url     = url

class Client():
    def __init__(self):
        self.connector = aiohttp.UnixConnector(path='/var/run/docker.sock')
        self.session = aiohttp.ClientSession(connector=self.connector)

    def _url(self, path, **kwargs):
        if kwargs:
            return 'http://docker/v1.30{}?{}'.format(path, '&'.join(["{}={}".format(k, v) for k, v in kwargs.items()]))
        else:
            return 'http://docker/v1.30{}'.format(path)

    async def _check_response(self, method, url, response, payload=None, params=None):
        if not (response.status >= 200 and response.status < 300):
            raise CommunicationError(
                method,
                url,
                response.status,
                await response.text(),
                payload,
                params,
            )

    async def _delete(self, path, query=None):
        url = self._url(path)
        query = query if query else {}
        LOGGER.debug("DELETE %s", path)
        async with self.session.delete(url, params=query) as response:
            await self._check_response('DELETE', url, response)

    async def _get(self, path, query=None):
        url = self._url(path)
        LOGGER.debug("GET %s", path)
        async with self.session.get(url, params=query) as response:
            await self._check_response('GET', url, response)
            if response.headers['Content-Type'] == 'application/json':
                data = await response.json()
            else:
                data = await response.read()
            return data

    async def _post(self, path, payload, query=None):
        url = self._url(path)
        query = query if query else {}
        LOGGER.debug("POST %s", url)
        async with self.session.post(url, json=payload, params=query) as response:
            await self._check_response('POST', url, response, payload, query)
            return await response.json()

    async def _put(self, path, payload, query=None):
        url = self._url(path)
        query = query if query else {}
        LOGGER.debug("PUT %s", url)
        async with self.session.put(url, json=payload, params=query) as response:
            await self._check_response('PUT', url, response)
            return await response.json()

    async def _putraw(self, path, data, query=None, headers=None):
        url = self._url(path)
        query = query if query else {}
        LOGGER.debug("PUT raw %s", url)
        async with self.session.put(url, data=data, params=query, headers=headers) as response:
            await self._check_response('PUT', url, response)
            result = await response.text()
            LOGGER.debug("PUT raw %s resulted in %s: %s", url, response.status, result)
            return result

    async def container_archive_get(self, container_id, path):
        try:
            result = await self._get( path=f'/containers/{container_id}/archive', query={'path': path},)
            buf = io.BytesIO(result)
            archive = tarfile.open(mode='r', fileobj=buf)
            return archive
        except CommunicationError as e:
            LOGGER.debug("Failed to get file archive: %s", e)
            if e.status == 404:
                raise FileNotFoundError(path)
            raise

    async def container_archive_put(self, container_id, path, archive, no_overwrite_dir_non_dir=True):
        return await self._putraw(
            path=f'/containers/{container_id}/archive',
            data=archive,
            query={'path': path}, #, 'noOverwriteDirNonDir': str(no_overwrite_dir_non_dir)},
            headers={'Content-Type': 'application/gzip'},
        )

    async def close(self):
        LOGGER.debug("Closing aiohttp session")
        await self.session.close()

    async def ps(self):
        return await self._get('/containers/json')

    async def config_create(self, payload):
        result = await self._post('/configs/create', payload)
        return result

    async def config_ls(self):
        data = await self._get('/configs')
        return [drophi.types.Config.parse(c) for c in data]

    async def config_rm(self, id_):
        return await self._delete(
            f'/configs/{id_}',
        )

    async def container_rm(self, id_, v=False, force=False, link=False):
        return await self._delete(
            f'/containers/{id_}',
            query={'v': str(v), 'force': str(force), 'link': str(link)},
        )

    async def container_run(self, payload):
        result = await self._post('/containers/create', payload)
        return result

    async def network_create(self, payload):
        result = await self._post('/networks/create', payload)
        return result

    async def network_ls(self):
        data = await self._get('/networks')
        return [drophi.types.Network.parse(n) for n in data]

    async def secret_create(self, payload):
        result = await self._post('/secrets/create', payload)
        return result

    async def secret_ls(self):
        data = await self._get('/secrets')
        return [drophi.types.Secret.parse(c) for c in data]

    async def secret_rm(self, id_):
        return await self._delete(
            f'/secrets/{id_}',
        )

    async def service_ls(self):
        data = await self._get('/services')
        return [drophi.types.Service.parse(s) for s in data]

    async def service_create(self, payload):
        LOGGER.debug("Creating service with %s", pprint.pformat(payload))
        return await self._post('/services/create', payload)

    async def service_update(self, id_, version, payload):
        LOGGER.debug("Updating service %s with version %s to %s", id_, version, pprint.pformat(payload))
        return await self._post(f'/services/{id_}/update', payload, query={'version': version})

    async def streamevents(self):
        LOGGER.debug("Subscribing to docker events")
        url = self._url('/events', since=time.time())
        data_buffer = b''
        text_buffer = ''
        async with self.session.get(url, timeout=0) as response:
            while True:
                data_buffer += await response.content.read(4096)
                try:
                    text_buffer += data_buffer.decode('utf-8')
                    data_buffer = b''
                except ValueError:
                    LOGGER.debug("Failed to decode data as UTF-8, waiting for more")
                    continue
                newline = text_buffer.find('\n')
                if newline:
                    message = text_buffer[:newline]
                    text_buffer = text_buffer[newline+1:]
                else:
                    LOGGER.debug("Waiting for more data to fine a newline and break off a message")
                    continue
                try:
                    data = json.loads(message)
                    yield Event(data)
                except ValueError:
                    LOGGER.error("Failed to parse JSON from '%s'", message)

    async def task_ls(self):
        LOGGER.debug("Listing swarm tasks")
        return await self._get('/tasks')

    async def volume_create(self, payload):
        return await self._post('/volumes/create', payload)

    async def volume_ls(self):
        data = await self._get('/volumes')
        return [drophi.types.Volume.parse(v) for v in data['Volumes']] if data['Volumes'] else []

    async def volume_rm(self, name, force=False):
        return await self._delete(f'/volumes/{name}', query={'force': str(force)})

class Event():
    def __init__(self, data):
        self.data = data

    def __str__(self):
        return "Docker Event {} {} {} at {}".format(
            self.type,
            self.action,
            self.id,
            self.time,
        )

    @property
    def type(self):
        return self.data['Type']

    @property
    def action(self):
        return self.data['Action']

    @property
    def id(self):
        return self.data['id']

    @property
    def time(self):
        return arrow.get(self.data['time'])
