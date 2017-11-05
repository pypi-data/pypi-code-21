from pynlp.config import SERIALIZER_CLASS, DEFAULT_PORT, DEFAULT_ANNOTATORS
import requests
import json
import corenlp_protobuf as core
from pynlp.wrapper import Document
from threading import Thread
from queue import Queue
import os


SERIALIZE_PROPS = {
    'outputFormat': 'serialized',
    'serializer': SERIALIZER_CLASS
}

DESERIALIZE_PROPS = {
    'inputFormat': 'serialized',
    'inputSerializer': SERIALIZER_CLASS
}


def _corenlp_request(input_data, props, port=DEFAULT_PORT):
    server = 'http://localhost:{}/'.format(port)
    params = (('properties', json.dumps(props)),)
    return requests.post(url=server, params=params, data=input_data)


def _annotate_binary(text, annotators=DEFAULT_ANNOTATORS, options=None, port=DEFAULT_PORT):
    props = dict(SERIALIZE_PROPS, **{'annotators': annotators})
    if options:
        props = dict(props, **options)
    return _corenlp_request(input_data=text.encode('utf-8'), props=props, port=port).content


def _annotate(text, annotators=DEFAULT_ANNOTATORS, options=None, port=DEFAULT_PORT):
    return from_bytes(_annotate_binary(text.encode('utf-8'), annotators, options, port))


def from_bytes(protobuf):
    doc = core.Document()
    core.parseFromDelimitedString(doc, protobuf)
    return doc


def to_bytes(proto_doc):
    stream = core.writeToDelimitedString(proto_doc)
    buf = stream.getvalue()
    stream.close()
    return buf


def stanford_core_nlp(annotators=DEFAULT_ANNOTATORS, options=None, port=DEFAULT_PORT):
    def annotate(text):
        return _annotate(text, annotators, options, port)
    return annotate


class StanfordCoreNLP:

    def __init__(self, port=DEFAULT_PORT, annotators=DEFAULT_ANNOTATORS, options=None):
        self._annotators = annotators
        self._options = options
        self.port = port

    def __call__(self, documents, threads=0):
        docs = [self.annotate(doc) for doc in documents]
        return docs if len(docs) > 1 else docs[0]

    @property
    def annotators(self):
        return self._annotators.split(', ')

    def annotate(self, documents, threads=0):

        if threads == 0:
            threads = os.cpu_count()

        annotated = []
        queue = Queue()

        def corenlp_request():
            while True:
                doc = queue.get()
                if not document:
                    break
                proto_doc = _annotate(doc, self._annotators, self._options)
                annotated.append(Document(proto_doc))
            queue.task_done()

        threads_pool = []
        for i in range(threads):
            thread = Thread(target=corenlp_request)
            thread.start()
            threads_pool.append(thread)

        for document in documents:
            queue.put(document)

        queue.join()

        for i in range(threads):
            queue.put(None)
        for t in threads_pool:
            t.join()