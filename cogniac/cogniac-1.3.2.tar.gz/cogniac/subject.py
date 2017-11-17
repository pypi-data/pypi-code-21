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

        resp = connection.session.post(url_prefix + "/subjects", json=data, timeout=connection.timeout)
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
        resp = connection.session.get(url_prefix + "/subjects/%s" % subject_uid, timeout=connection.timeout)
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
        resp = connection.session.get(url_prefix + '/subjects/all/search', timeout=connection.timeout)
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
        resp = self._cc.session.delete(url_prefix + "/subjects/%s" % self.subject_uid, timeout=self._cc.timeout)
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
            resp = self._cc.session.post(url_prefix + "/subjects/%s" % self.subject_uid, json=data, timeout=self._cc.timeout)
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

        resp = self._cc.session.post(url_prefix + "/subjects/%s/media" % self.subject_uid, json=data, timeout=self._cc.timeout)
        raise_errors(resp)

        return resp.json()['capture_id']

    def media_associations(self, start=None, end=None, reverse=True, probability_lower=0, probability_upper=1, consensus=None, sort_probability=False):
        """
        yield media associations for the subject sorted by last update timestamp or probability

        start (float)          filter by last update timestamp > start (seconds since epoch)
        end (float)            filter by last update timestamp < end   (seconds since epoch)
        reverse (bool)         reverse the sorting order: sort high to low
        probability_lower:     filter by probability > probability_lower
        probability_upper:     filter by probability < probability_upper
        consensus (string):    filter by consensus label: "True", "False", or "Uncertain"
        sort_probability(bool) Sort by probability instead of last update timestamp

        Returns (yield) association dictionary with the following fields:

        media_id        the media_id
        subject_uid		the subject_uid
        probability		current assessment of the probability in [0,1] that the subject_uid is associated with the media_id
		                1 = definitely associated
               			0 = definitely NOT associated
            			0.5 ~= uncertain association
        timestamp		time of last update
        app_data_type	optional app data type if applicable
        app_data        optional app data if applicable
        consensus		'True', 'False', or 'Uncertain', or None
                        'True' if there is consensus that the subject is associated with the media
                            (Media will be used as a positive training example of the subject)
		                'False' if there is consensus that the subject is not associated w/the media
		                    (Media will be used as a negative training example of the subject.)
		                'Uncertain' if there is consensus that the association between the media and subject is ambiguous
		                 None if if there is not enough evidence to reach consensus
		                 Some application types only support 'True' or None.
        """

        args = []
        if start is not None:
            args.append("start=%f" % start)
        if end is not None:
            args.append("end=%f" % end)
        if probability_lower is not None:
            args.append("probability_lower=%f" % probability_lower)
        if probability_upper is not None:
            args.append("probability_upper=%f" % probability_upper)
        if consensus is not None:
            assert(consensus in ['True', 'False', 'Uncertain'])
            args.append("consensus=%s" % consensus)
        if reverse:
            args.append('reverse=True')
        if sort_probability:
            args.append("sort=probability")

        url = url_prefix + "/subjects/%s/media?" % self.subject_uid
        url += "&".join(args)

        @retry(stop_max_attempt_number=8, wait_exponential_multiplier=500, retry_on_exception=server_error)
        def get_next(url):
            resp = self._cc.session.get(url, timeout=self._cc.timeout)
            raise_errors(resp)
            return resp.json()

        while url:
            resp = get_next(url)
            for sma in resp['data']:
                yield sma
            url = resp['paging'].get('next')

    @retry(stop_max_attempt_number=8, wait_exponential_multiplier=500, retry_on_exception=server_error)
    def detections(self, media):
        """
        return a list of detection dictionaries as follows for the specified media_id and this subject

        detection_id:     internal detection_id
        user_id:          a user_id if this was from a user
        model_id:         a model_id if this was from an app w/model
        app_id:           an app_id if this was from an app
        uncal_prob:       the raw uncalibrated user or model confidence (if any)
        timestamp:        the time of this detection
        prev_prob:        subject-media probability before this detection (if any)
        probability:      the resulting probability after this detection
        app_data_type     Optional type of extra app-specific data
        app_data          Optional extra app-specific data
        """
        url = url_prefix + "/subjects/%s/detections?media_id=%s" % (self.subject_uid, media.media_id)
        resp = self._cc.session.get(url, timeout=self._cc.timeout)
        raise_errors(resp)
        return resp.json()['detections']
