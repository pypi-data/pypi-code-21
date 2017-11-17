"""
CogniacMedia Object Client

Copyright (C) 2016 Cogniac Corporation
"""

from retrying import retry
from common import *
from os import stat


##
#  CogniacMedia
##
class CogniacMedia(object):
    """
    CogniacMedia objects contain metadata for media files that has been input into the Cogniac System.
    New CogniacMedia can be created by specifying a local filename containing a still image or video.
    Existing CogniacMedia can be retrieved by media_id.
    """

    @classmethod
    @retry(stop_max_attempt_number=8, wait_exponential_multiplier=500, retry_on_exception=server_error)
    def get(self, connection, media_id):
        """
        return a CogniacMedia object for an existing media item

        connnection (CogniacConnection):     Authenticated CogniacConnection object
        media_id (String):                   The media_id of the Cogniac Media item to return
        """
        resp = connection.session.get(url_prefix + "/media/%s" % media_id)
        raise_errors(resp)

        return CogniacMedia(connection, resp.json())

    def __init__(self, connection, media_dict):
        """
        create a CogniacMedia

        This is not normally called directly by users, instead use:
        CogniacConnection.create_media() or
        CogniacMedia.create()
        """
        self._cc = connection
        self._media_keys = media_dict.keys()
        for k, v in media_dict.items():
            super(CogniacMedia, self).__setattr__(k, v)

    def __str__(self):
        return "%s" % self.media_id

    def __setattr__(self, name, value):
        if hasattr(self, '_media_keys') and name in self._media_keys:
            raise AttributeError("%s is immutable" % name)
        super(CogniacMedia, self).__setattr__(name, value)

    @classmethod
    def create(cls,
               connection,
               filename,
               meta_tags=None,
               force_set=None,
               external_media_id=None,
               original_url=None,
               original_landing_url=None,
               license=None,
               author_profile_url=None,
               author=None,
               title=None):
        """
        Create a new CogniacMedia object and upload the media to the Cogniac System.

        connnection (CogniacConnection):  Authenticated CogniacConnection object
        filename (str):                   Local filename of image or video media file
        meta_tags ([str]):                Optional list of arbitrary strings to associate with the media
        force_set (str):                  Optionally force the media into the 'training', 'validation' or 'test' sets
        external_media_id (str):          Optional arbitrary external id for this media
        original_url(str):                Optional source url for this media
        original_landing_url (str):       Optional source landing url for this media
        license (str):                    Optional copyright licensing info for this media
        author_profile_url (str):         Optional media author url
        author (str):                     Optional author name
        title (str):                      Optional media title
        """

        args = dict()
        if meta_tags is not None:
            args['meta_tags'] = meta_tags
        if force_set is not None:
            args['force_set'] = force_set
        if external_media_id is not None:
            args['external_media_id'] = external_media_id
        if original_url is not None:
            args['original_url'] = original_url
        if original_landing_url is not None:
            args['original_landing_url'] = original_landing_url
        if license is not None:
            args['license'] = license
        if author_profile_url is not None:
            args['author_profile_url'] = author_profile_url
        if author is not None:
            args['author'] = author
        if title is not None:
            args['title'] = title

        if stat(filename).st_size > 12 * 1024 * 1024:
            # use the multipart interface for large files
            return CogniacMedia._create_multipart(connection, filename, args)

        @retry(stop_max_attempt_number=8, wait_exponential_multiplier=500, retry_on_exception=server_error)
        def upload():
            files = {'file': open(filename, 'rb')}
            resp = connection.session.post(url_prefix+"/media", data=args, files=files)
            raise_errors(resp)
            return resp

        resp = upload()
        return CogniacMedia(connection, resp.json())

    @classmethod
    def _create_multipart(connection, filename, args):
        """
        upload via the multipart api
        """
        def md5_hexdigest():
            """
            return the md5 hexdigest of a potentially very large file
            """
            md = md5()
            fp = open(filename)
            while True:
                block = fp.read(8*1024*1024)
                if not block:
                    return md.hexdigest()
                md.update(block)

        media_id = md5_hexdigest()

        @retry(stop_max_attempt_number=8, wait_exponential_multiplier=500, retry_on_exception=server_error)
        def post_data(data):
            resp = connection.session.post(url_prefix + "/media/resumable", json=data)
            raise_errors(resp)
            return resp.json()

        filesize = os.stat(filename).st_size

        data = {'upload_phase': 'start',
                'file_size':    filesize,
                'filename':     filename,
                'media_id':     media_id}

        rdata = post_data(data)
        upload_session_id = rdata['upload_session_id']
        chunk_size = rdata['chunk_size']

        @retry(stop_max_attempt_number=8, wait_exponential_multiplier=500, retry_on_exception=server_error)
        def upload_chunk(chunk, chunk_no, upload_session_id):

            data = {'upload_phase':        'transfer',
                    'upload_session_id':   upload_session_id,
                    'video_file_chunk_no': chunk_no}

            files = {'file': chunk}
            resp = connection.session.post(url_prefix + "/media/resumable", data=data, files=files)
            raise_errors(resp)
            return resp.json()

        mfp = open(filename, 'r')
        idx = 1
        while True:
            chunk = mfp.read(chunk_size)
            if not chunk:
                break
            upload_chunk(chunk, idx, upload_session_id)
            idx += 1

        # perform the final finihs phase post with the user args
        data = {'upload_phase':      'finish',
                'upload_session_id': upload_session_id}
        data.update(args)  # add user arg
        rdata = post_data(data)
        return CogniacMedia(connection, rdata)
