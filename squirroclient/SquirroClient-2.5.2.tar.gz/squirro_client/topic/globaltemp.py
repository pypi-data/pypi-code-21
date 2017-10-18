from squirro_client.exceptions import NotFoundError, UnknownError


class GlobalTempMixin(object):

    def new_tempfile(self, data):
        """Stores the `data` in a temp file.

        :param data: data to be stored in the temp file
        """

        url = '%(ep)s/v0/%(tenant)s/temp' % {
            'ep': self.topic_api_url,
            'tenant': self.tenant,
        }
        headers = {}
        res = self._perform_request(
            'post', url, files={'file': data}, headers=headers)
        return self._process_response(res, [201])

    def get_tempfile(self, filename):
        """Returns the content of the temp file with the name `filename`.

        :param filename: File name
        """

        url = '%(ep)s/v0/%(tenant)s/temp' % {
            'ep': self.topic_api_url,
            'tenant': self.tenant,
        }
        res = self._perform_request('get', url, params={'filename': filename})
        if res.status_code == 404:
            raise NotFoundError(res.status_code, 'Not found')
        elif res.status_code != 200:
            raise UnknownError(res.status_code, '')
        else:
            return res.content
