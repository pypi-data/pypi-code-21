import base64
import hashlib
import logging
import os

from .item_uploader import ItemUploader

log = logging.getLogger(__name__)


# Increased read timeout for file uploads, as file processing can take a
# moment.
TIMEOUT_SECS = 300


class DocumentUploader(object):
    """Document uploader class which simplifies the indexing of office
    documents. Default parameters are loaded from your home directories
    .squirrorc. See the documentation of [[ItemUploader]] for a complete
    list of options regarding project selection, source selection,
    configuration, etc.

    :param batch_size: Number of items to send in one request.
    :param batch_size_mb: Size of documents to send in one request. If this
        file size is reached, the client uploads the existing documents.
    :param metadata_mapping: A dictionary which contains the meta-data mapping.
    :param default_mime_type_keyword: If set to ``True`` a default keyword
        is added to the document which contains the mime-type.
    :param timeout_secs: How many seconds to wait for data before giving up
        (default 300).
    :param kwargs: Any additional keyword arguments are passed on to the
        [[ItemUploader]]. See the documentation of that class for details.

    Typical usage:

        >>> from squirro_client import DocumentUploader
        >>> import os
        >>> uploader = DocumentUploader(
        ...     project_title='My Project', token='<your token>',
        ...     cluster='https://demo.squirro.net/')
        >>> uploader.upload(os.path.expanduser('~/Documents/test.pdf'))
        >>> uploader.flush()

    Meta-data mapping usage:

    * By default (i.e. for all document mime-types) map the original document
      size to a keyword field named "Doc Size":

        >>> mapping = {'default': {'sq:size_orig': 'Doc Size',
        ...                        'sq:content-mime-type': 'Mime Type'}}
        >>> uploader = DocumentUploader(metadata_mapping=mapping)

    * For a specific mime-type (i.e.
      'application/vnd.oasis.opendocument.text') map the "meta:word-count"
      meta-data filed value to a keyword field named "Word Count":

        >>> mapping = {'application/vnd.oasis.opendocument.text': {
        ...     'meta:word-count': 'Word Count'}}
        >>> uploader = DocumentUploader(metadata_mapping=mapping)

    Default meta-data fields available for mapping usage:

    * ``sq:doc_size``: Converted document file size.
    * ``sq:doc_size_orig``: Original uploaded document file size.
    * ``sq:content-mime-type``: Document mime-type specified during upload
      operation.

    """

    def __init__(self, metadata_mapping=None, batch_size=10, batch_size_mb=150,
                 default_mime_type_keyword=True,
                 timeout_secs=TIMEOUT_SECS, **kwargs):

        if metadata_mapping is None:
            metadata_mapping = {}

        # assemble processing configuration
        proc_config = {
            'content-conversion': {
                'enabled': True,
                'metadata-mapping': {
                    'default': {}
                }
            }
        }
        mapping = proc_config['content-conversion']['metadata-mapping']
        mapping.update(metadata_mapping)

        if (default_mime_type_keyword and
                'sq:content-mime-type' not in mapping['default']):
            mapping['default']['sq:content-mime-type'] = 'MIME Type'

        # check for an explicit processing config
        if 'processing_config' in kwargs:
            pc = kwargs.get('processing_config')
            if pc:
                proc_config.update(pc)
            del kwargs['processing_config']

        # disable bulk indexing as document conversion is not supported
        if 'bulk_index' in kwargs:
            del kwargs['bulk_index']

        # item uploader
        self.batch_size = batch_size
        self.batch_size_mb = batch_size_mb
        self.uploader = ItemUploader(
            batch_size=batch_size, processing_config=proc_config,
            timeout_secs=timeout_secs, **kwargs)

        # internal state
        self._items = []
        self._items_size_mb = 0

    def upload(self, filename, mime_type=None, title=None, doc_id=None,
               keywords=None, link=None, created_at=None,
               filename_encoding=None, content_url=None):
        """Method which will use the provided ``filename`` to create a Squirro
        item for upload. Items are buffered internally and uploaded according
        to the specified batch size. If `mime_type` is not provided a simple
        filename extension based lookup is performed.

        :param filename: Read content from the provided filename.
        :param mime_type: Optional mime-type for the provided filename.
        :param title: Optional title for the uploaded document.
        :param doc_id: Optional external document identifier.
        :param keywords: Optional dictionary of document meta data keywords.
            All values must be lists of string.
        :param link: Optional URL which points to the origin document.
        :param created_at: Optional document creation date and time.
        :param filename_encoding: Encoding of the filename.
        :param content_url: Storage URL of this file. If this is set, the
            Squirro cluster will not copy the file.

        Example:

        >>> filename = 'test.pdf'
        >>> mime_type = 'application/pdf'
        >>> title = 'My Test Document'
        >>> doc_id = 'doc01'
        >>> keywords = {'Author': ['John Smith'], 'Tags': ['sales',
        ...                                                'marketing']}
        >>> link = 'http://example.com/test.pdf'
        >>> created_at = '2014-07-10T21:26:15'
        >>> uploader.upload(filename, mime_type, title, doc_id, keywords,
        ...                 link, created_at)
        """

        item_id = doc_id
        content_size = 0
        content = None

        if not content_url or not item_id:
            # read the raw file content and encode it
            raw = open(filename, 'rb').read()
            content = base64.b64encode(raw)
            content_size = len(content) / 1024 / 1024

            # build a checksum over the original file content and use it as the
            # item identifier
            if not item_id:
                item_id = hashlib.sha256(raw).hexdigest()

            # free up the memory
            raw = None

        # Upload the documents if the maximum size would be exceeded with this
        # new file.
        if self._items_size_mb + content_size >= self.batch_size_mb:
            self.flush()

        if isinstance(filename, unicode):
            decoded_name = filename.encode('utf8')
        elif filename_encoding:
            decoded_name = filename.decode(filename_encoding).encode('utf8')
        else:
            decoded_name = filename

        item = {
            'id': item_id,
            'files': [
                {
                    'name': os.path.basename(decoded_name),
                }
            ]
        }

        # Optional MIME type
        if mime_type:
            item['files'][0]['mime_type'] = mime_type

        # Optional storage URL
        if content_url:
            item['files'][0]['content_url'] = content_url
        else:
            item['files'][0]['content'] = content

        # check if an explicit title was provided, otherwise the content
        # conversion step will figure something out
        if title is not None:
            item['title'] = title

        # check for any other provided document attributes
        if keywords is not None:
            item['keywords'] = keywords
        if link is not None:
            item['link'] = link
        if created_at is not None:
            item['created_at'] = created_at

        # upload items
        self._items.append(item)
        self._items_size_mb += content_size

        if len(self._items) >= self.batch_size:
            self.flush()

    def flush(self):
        """Flush the internal buffer by uploading all documents."""
        if self._items:
            self.uploader.upload(self._items)
            self._items = []
            self._items_size_mb = 0
