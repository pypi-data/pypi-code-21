"""
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License.
"""

from serializer import MarshmallowSerializer


class SerializationManager(object):
    """
    SerializationManager proxies serialization requests.

    TO-DO:  configure serialization scheme from yosai.core.settings json
    """

    _registered_schema = []

    def __init__(self):
        self.serializer = MarshmallowSerializer()

        for stype, schema in self._registered_schema:
            self.serializer.register_schema(stype, schema)

    @classmethod
    def register_schema(cls, stype, schema):
        cls._registered_schema.append((stype, schema))

    def serialize(self, obj):
        """
        :type obj: a Serializable object or a list of Serializable objects
        :returns: an encoded, serialized object
        """
        return self.serializer.serialize(obj)

    def deserialize(self, message):
        return self.serializer.deserialize(message)
