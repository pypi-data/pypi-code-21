from collections import OrderedDict
from functools import partial
from io import BytesIO
from typing import Dict, Any, Callable, Optional
import six
import cbor2

from yosaipy2.core import serialize_abcs, qualified_name

from yosaipy2.core.serialize.marshalling import default_marshaller, default_unmarshaller


@cbor2.shareable_encoder
def _encode_custom_type(encoder, obj, fp, serializer):
    # type: (cbor2.CBOREncoder, Any, Any, CBORSerializer) -> Any
    obj_type = obj.__class__
    typename, marshaller = serializer.marshallers[obj_type]
    state = marshaller(obj)
    serialized_state = encoder.encode_to_bytes(state)
    return encoder.encode_semantic(serializer.custom_type_tag, [typename, serialized_state], fp,
                                   disable_value_sharing=True)


def _decode_custom_type(decoder, value, fp, shareable_index, serializer):
    # type:(cbor2.CBORDecoder, Any, Any, Optional[int], CBORSerializer) -> Any
    typename, serialized_state = value
    try:
        cls, unmarshaller = serializer.unmarshallers[typename]
    except KeyError:
        value = 'no unmarshaller found for type "{}"'.format(typename)
        six.raise_from(value, None)
        return

    instance = cls.__new__(cls)
    if shareable_index is not None:
        decoder.shareables[shareable_index] = instance

    buf = BytesIO(serialized_state)
    state = decoder.decode(buf)
    unmarshaller(instance, state)
    return instance


class CBORSerializer(serialize_abcs.CustomizableSerializer):
    """
    Serializes objects using CBOR (Concise Binary Object Representation).

    To use this serializer backend, the ``cbor2`` library must be installed.
    A convenient way to do this is to install ``asphalt-serialization`` with the ``cbor``
    extra:

    .. code-block:: shell

        $ pip install asphalt-serialization[cbor]

    .. seealso:: `cbor2 documentation <https://pypi.io/project/cbor2/>`_

    :param encoder_options: keyword arguments passed to ``cbor2.dumps()``
    :param decoder_options: keyword arguments passed to ``cbor2.loads()``
    :param custom_type_tag: semantic tag used for marshalling of registered custom types
    """

    __slots__ = ('encoder_options', 'decoder_options', 'custom_type_tag', 'marshallers',
                 'unmarshallers')

    def __init__(self, encoder_options=None, decoder_options=None, custom_type_tag=4554):
        # type: ( Dict[str, Any], Dict[str, Any], int) -> Any
        self.encoder_options = encoder_options or {}
        self.decoder_options = decoder_options or {}
        self.custom_type_tag = custom_type_tag
        self.marshallers = OrderedDict()  # class -> (typename, marshaller function)
        self.unmarshallers = OrderedDict()  # typename -> (class, unmarshaller function)

    def serialize(self, obj):
        # type: (Any) -> bytes
        return cbor2.dumps(obj, **self.encoder_options)

    def deserialize(self, payload):
        # type: (bytes) -> Any
        return cbor2.loads(payload, **self.decoder_options)

    def register_custom_type(self, cls, marshaller=default_marshaller,
                             unmarshaller=default_unmarshaller, typename=None):
        # type: (type, Optional[Callable[[Any], Any]], Optional[Callable[[Any, Any], Any]], str) -> None
        typename = typename or qualified_name(cls)

        if marshaller:
            self.marshallers[cls] = typename, marshaller
            encoders = self.encoder_options.setdefault('encoders', {})
            encoders[cls] = partial(_encode_custom_type, serializer=self)

        if unmarshaller:
            self.unmarshallers[typename] = cls, unmarshaller
            decoders = self.decoder_options.setdefault('semantic_decoders', {})
            decoders[self.custom_type_tag] = partial(_decode_custom_type, serializer=self)

    @property
    def mimetype(self):
        return 'application/cbor'
