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

from abc import ABCMeta, abstractmethod
import six


@six.add_metaclass(ABCMeta)
class Serializer(object):
    """
    This abstract class defines the serializer API.

    Each serializer is required to support the serialization of the following Python types,
    at minimum:

    * :class:`str`
    * :class:`int`
    * :class:`float`
    * :class:`list`
    * :class:`dict` (with ``str`` keys)

    A subclass may support a wider range of types, along with hooks to provide serialization
    support for custom types.
    """

    @abstractmethod
    def serialize(self, obj):
        """Serialize a Python object into bytes."""

    @abstractmethod
    def deserialize(self, payload):
        """Deserialize bytes into a Python object."""

    @property
    @abstractmethod
    def mimetype(self):
        """Return the MIME type for this serialization format."""

