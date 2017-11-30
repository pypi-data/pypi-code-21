# Copyright (C) 2008 Abiquo Holdings S.L.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import requests, json

class Abiquo(object):
    def __init__(self, url, auth=None, headers=None, verify=True):
        self.url = url
        self.auth = auth
        self.headers = {url : headers}
        self.verify = verify
        self.session = requests.session()

    def __getattr__(self, key):
        try:
            return self.__dict__[key]
        except:
            self.__dict__[key] = Abiquo(self._join(self.url, key), auth=self.auth,
                    verify=self.verify)
            return self.__dict__[key]

    def __call__(self, *args):
        if not args:
            return self
        return Abiquo(self._join(self.url, *[str(i) for i in args]), auth=self.auth,
                verify=self.verify)

    def get(self, id=None, params=None, headers=None):
        return self._request('get', self._join(self.url, id), 
            params=params, headers=headers)

    def post(self, id=None, params=None, headers=None, data=None):
        return self._request('post', self._join(self.url, id), 
            params=params, headers=headers, data=data)

    def put(self, id=None, params=None, headers=None, data=None):
        return self._request('put', self._join(self.url, id), 
            params=params, headers=headers, data=data)

    def delete(self, id=None, params=None, headers=None):
        return self._request('delete', self._join(self.url, id), 
            params=params, headers=headers)        

    def _request(self, method, url, params=None, headers=None, data=None):
        parent_headers = self.headers[url] if url in self.headers else {}
        response = self.session.request(method, 
                                        url, 
                                        auth=self.auth, 
                                        params=params, 
                                        data=data,
                                        verify=self.verify,
                                        headers=self._merge_dicts(parent_headers, headers))
        response_dto = None
        if len(response.text) > 0:
            try:
                response_dto = ObjectDto(response.json(), auth=self.auth, 
                    content_type=response.headers.get('content-type', None),
                    verify=self.verify)
            except ValueError:
                pass
        return response.status_code, response_dto

    def _merge_dicts(self, x, y):
        new_dict = {}
        if x:
            new_dict.update(x)
        if y:
            new_dict.update(y)
        return new_dict

    def _join(self, *args):
        return "/".join(filter(None, args))

class ObjectDto(object):
    def __init__(self, json, auth=None, content_type=None, verify=True):
        self.auth = auth
        self.content_type = content_type
        self.verify = verify

        # JSON needs to be at the end because of the implementation in __setattr__
        self.json = json

    def __getattr__(self, key):
        if key in self.__dict__:
            return self.__dict__[key]
        else:
            return self._find_or_raise(key)

    def __setattr__(self, key, value):
        if key in self.__dict__:
            self.__dict__[key] = value
        else:
            if 'json' in self.__dict__:
                self.__dict__['json'][key] = value
            else:
                self.__dict__[key] = value
            
    def _find_or_raise(self, key):
        if key in self.json:
            return self.json[key]
        else:
            try:
                return self.follow(key)
            except:
                raise KeyError

    def refresh(self):
        self.follow('edit' if self._has_link('edit') else 'self').get()
        
    def put(self):
        if not self._has_link('edit'):
            raise TypeError('object is not editable')
        link_type = self._extract_link('edit')['type']
        return self.follow('edit').put(headers={'Content-Type': link_type}, data=json.dumps(self.json))

    def delete(self):
        self.follow('edit' if self._has_link('edit') else 'self').delete()

    def follow(self, rel):
        link = self._extract_link(rel)
        if not link:
            raise KeyError("link with rel %s not found" % rel)
        return Abiquo(url=link['href'], auth=self.auth, headers={'accept' : link['type']},
                verify=self.verify)

    def __len__(self):
        try:
            if 'totalSize' in self.json:
                return self.json['totalSize']
            return len(self.json['collection'])
        except KeyError:
            raise TypeError('object has no len()')

    def __iter__(self):
        try:
            for json in self.json['collection']:
                yield ObjectDto(json, auth=self.auth, verify=self.verify)

            current_page = self
            while current_page._has_link('next'):
                link = self._extract_link('next')
                client = Abiquo(url=link['href'], 
                                auth=self.auth, 
                                headers={'Accept' : link.get('type', self.content_type)},
                                verify=self.verify)
                sc, current_page = client.get()
                if sc == 200 and current_page:
                    for json in current_page.json['collection']:
                        yield ObjectDto(json, auth=self.auth, verify=self.verify)
        except KeyError:
            raise TypeError('object is not iterable')

    def __dir__(self):
        return dir(type(self)) + self.json.keys()

    def _extract_link(self, rel):
        return next((link for link in self.json['links'] if link['rel'] == rel), None)

    def _has_link(self, rel):
        return True if self._extract_link(rel) else False


def check_response(expected_code, code, errors):
    if code != expected_code:
	try:
	    first_error = errors.json['collection'][0]
	except:
	    # If it is not an Abiquo controlled error, throw a generic error
	    raise Exception("HTTP(%s) Operation failed!" % code)
	# If it is an Abiquo error, properly show the error code and error details
	raise Exception("HTTP(%s) %s: %s" % (code, first_error['code'], first_error['message']))
