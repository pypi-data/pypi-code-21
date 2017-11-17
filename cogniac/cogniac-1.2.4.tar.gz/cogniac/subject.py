"""
CogniacSubject Object Client

Copyright (C) 2016 Cogniac Corporation
"""

import json
from retrying import retry
from common import *


##
#  CogniacSubject
##
class CogniacSubject(object):
    """
    CogniacSubject
    Subjects are a central organizational mechanism in the Cogniac system.
    A subject is any user-defined concept that is relevant to images or video.
    More generally a subject can represent any logical grouping of images of video.

    Most Cogniac applications work by taking input media from user-defined subjects
    and outputing those media to other user-defined subjects based on the content
    of the media.

    Create a new subject with
    CogniacConnection.create_subject() or CogniacSubject.create()

    Get an existing subject with
    CogniacConnection.get_subject() or CogniacSubject.get()

    Get all tenant's subject with
    CogniacConnection.get_all_subjects() or CogniacSubject.get_all()

    Writes to mutable CogniacSubjects attributes are saved immediately via the Cogniac API.
    """

    ##
    #  create
    ##
    @classmethod
    @retry(stop_max_attempt_number=8, wait_exponential_multiplier=500, retry_on_exception=server_error)
    def create(cls,
               connection,
               name,
               description=None,
               public_read=False,
               public_write=False):
        """
        Create a CogniacSubject

        connnection (CogniacConnection):     Authenticated CogniacConnection object
        name (String):                       Name of new application
        description (String):                Optional description of the subject
        public_read(Bool):                   Subject media is accessible to other tenants and can be input into other tenant's apps.
        public_write(Bool):                  Other tenants can access and associate media with this subject.
        """
        if public_write:
            public_read = True

        data = dict(name=name, public_read=public_read, public_write=public_write)
        if description:
            data['description'] = description

        resp = connection.session.post(url_prefix + "/subjects", json=data)
        raise_errors(resp)

        return CogniacSubject(connection, resp.json())

    ##
    #  get
    ##
    @classmethod
    @retry(stop_max_attempt_number=8, wait_exponential_multiplier=500, retry_on_exception=server_error)
    def get(cls,
            connection,
            subject_uid):
        """
        return an existing CogniacSubject

        connnection (CogniacConnection):     Authenticated CogniacConnection object
        subject_id (String):                 The subject_id of the Cogniac Subject to return
        """
        resp = connection.session.get(url_prefix + "/subjects/%s" % subject_uid)
        raise_errors(resp)
        return CogniacSubject(connection, resp.json())

    ##
    #  get_all
    ##
    @classmethod
    def get_all(cls, connection):
        """
        return CogniacSubjects for all subjects belonging to the currently authenticated tenant

        connnection (CogniacConnection):     Authenticated CogniacConnection object
        """
        resp = connection.session.get(url_prefix + '/subjects/all/search')
        raise_errors(resp)
        subs = resp.json()['data']
        return [CogniacSubject(connection, s) for s in subs]

    ##
    #  __init__
    ##
    def __init__(self, connection, subject_dict):
        """
        create a CogniacSubject

        This is not normally called directly by users, instead use:
        CogniacConnection.create_subject() or
        CogniacSubject.create()
        """
        self._cc = connection
        self._sub_keys = subject_dict.keys()
        for k, v in subject_dict.items():
            super(CogniacSubject, self).__setattr__(k, v)

    ##
    #  delete
    ##
    @retry(stop_max_attempt_number=8, wait_exponential_multiplier=500, retry_on_exception=server_error)
    def delete(self):
        """
        Delete the subject.
        """
        resp = self._cc.session.delete(url_prefix + "/subjects/%s" % self.subject_uid)
        raise_errors(resp)
        for k in self._sub_keys:
            delattr(self, k)
        self._sub_keys = None
        self.connection = None
        self.requests = None

    def __setattr__(self, name, value):
        if name in ['subject_uid', 'created_at', 'created_by', 'modified_at', 'modified_by']:
            raise AttributeError("%s is immutable" % name)
        if name in ['name', 'description', 'public_read', 'public_write']:
            data = {name: value}
            resp = self._cc.session.post(url_prefix + "/subjects/%s" % self.subject_uid, json=data)
            raise_errors(resp)
            for k, v in resp.json().items():
                super(CogniacSubject, self).__setattr__(k, v)
            return
        super(CogniacSubject, self).__setattr__(name, value)

    def __str__(self):
        return "%s (%s)" % (self.name, self.subject_uid)

    def __repr__(self):
        return "%s (%s)" % (self.name, self.subject_uid)

    #
    # capture_media
    #
    @retry(stop_max_attempt_number=8, wait_exponential_multiplier=500, retry_on_exception=server_error)
    def associate_media(self, media, force_feedback=None):
        """
        Associate the media with this subject.

        returns the unique capture_id
        """
        data = {'media_id': media.media_id}

        if force_feedback is not None:
            data['force_feedback'] = force_feedback

        resp = self._cc.session.post(url_prefix + "/subjects/%s/media" % self.subject_uid, json=data)
        raise_errors(resp)

        return resp.json()['capture_id']
