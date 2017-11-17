"""
CogniacApplication Object Client

Copyright (C) 2016 Cogniac Corporation
"""

from retrying import retry
from common import *


class CogniacApplication(object):
    """
    CogniacApplication
    Applications are the main locus of activity within the Cogniac System.

    This classes manages applications within the Cogniac System via the
    Cogniac public API application endpoints.

    Create a new application with
    CogniacConnection.create_application() or CogniacApplication.create()

    Get an existing application with
    CogniacConnection.get_application() or CogniacApplication.get()

    Get all tenant's applications with
    CogniacConnection.get_all_applications() or CogniacApplication.get_all()

    Writes to mutable CogniacApplication attributes are saved immediately via the Cogniac API.
    """

    ##
    #  create
    ##
    @classmethod
    @retry(stop_max_attempt_number=8, wait_exponential_multiplier=500, retry_on_exception=server_error)
    def create(cls,
               connection,
               name,
               application_type,
               description=None,
               active=True,
               input_subjects=None,
               output_subjects=None):
        """
        Create a new CogniacApplication

        connnection (CogniacConnection):     Authenticated CogniacConnection object
        name (String):                       Name of new application
        application_type (String)            Cogniac Application Type name
        description (String):                Optional description of the application
        active (Boolean):                    Application operational state
        input_subjects ([CogniacSubjects]):  List of CogniacSubjects inputs to this application
        output_subjects ([CogniacSubjects]): List of CogniacSubjects outputs for this application
        """
        data = dict(name=name, active=active, type=application_type)

        if description:
            data['description'] = description
        if input_subjects:
            if type(inputs_subject[0]) == str:
                data['input_subjects'] = input_subjects
            else:
                data['input_subjects'] = [s.subject_uid for s in input_subjects]
        if output_subjects:
            if type(output_subjects[0]) == str:
                data['output_subjects'] = output_subjects
            else:
                data['output_subjects'] = [s.subject_uid for s in output_subjects]

        resp = connection.session.post(url_prefix + "/applications", json=data)
        raise_errors(resp)

        return CogniacApplication(connection, resp.json())

    ##
    #  get
    ##
    @classmethod
    @retry(stop_max_attempt_number=8, wait_exponential_multiplier=500, retry_on_exception=server_error)
    def get(cls,
            connection,
            application_id):
        """
        return an existing CogniacApplication

        connnection (CogniacConnection):     Authenticated CogniacConnection object
        application_id (String):             The application_id of the Cogniac application to return
        """
        resp = connection.session.get(url_prefix + "/applications/%s" % application_id)
        raise_errors(resp)
        return CogniacApplication(connection, resp.json())

    ##
    #  get_all
    ##
    @classmethod
    def get_all(cls, connection):
        """
        return CogniacApplications for all applications belonging to the currently authenticated tenant

        connnection (CogniacConnection):     Authenticated CogniacConnection object
        """
        resp = connection.session.get(url_prefix + '/organizations/%s/applications' % connection.tenant.tenant_id)
        raise_errors(resp)
        apps = resp.json()['data']
        return [CogniacApplication(connection, appd) for appd in apps]

    ##
    #  __init__
    ##
    def __init__(self, connection, application_dict):
        """
        create a CogniacApplication

        This is not normally called directly by users, instead use:
        CogniacConnection.create_application() or
        CogniacApplication.create()
        """
        self._cc = connection
        self._app_keys = application_dict.keys()
        for k, v in application_dict.items():
            super(CogniacApplication, self).__setattr__(k, v)

    ##
    #  delete
    ##
    @retry(stop_max_attempt_number=8, wait_exponential_multiplier=500, retry_on_exception=server_error)
    def delete(self):
        """
        Delete the application.
        This will delete existing models but will not delete associated subjects or media.
        """
        resp = self._cc.session.delete(url_prefix + "/applications/%s" % self.application_id)
        raise_errors(resp)
        for k in self._app_keys:
            delattr(self, k)
        self._app_keys = None
        self.connection = None
        self.requests = None

    def __setattr__(self, name, value):
        if name in ['application_id', 'created_at', 'created_by', 'modified_at', 'modified_by']:
            raise AttributeError("%s is immutable" % name)
        if name in ['name', 'description', 'active', 'input_subjects', 'output_subjects']:
            data = {name: value}
            resp = self._cc.session.post(url_prefix + "/applications/%s" % self.application_id, json=data)
            raise_errors(resp)
            for k, v in resp.json().items():
                super(CogniacApplication, self).__setattr__(k, v)
            return
        super(CogniacApplication, self).__setattr__(name, value)

    def __str__(self):
        return "%s (%s)" % (self.name, self.application_id)

    def __repr__(self):
        return "%s (%s)" % (self.name, self.application_id)

    def add_output_subject(self, subject):
        """
        Add a the specified subject the the Application's outputs.

        subject (CogniacSubject):   the subject to add
        """
        self.output_subjects = self.output_subjects + [subject.subject_uid]

    def add_input_subject(self, subject):
        """
        Add a the specified subject the the Application's inputs.

        subject (CogniacSubject):   the subject to add
        """
        self.input_subjects = self.input_subjects + [subject.subject_uid]

    ##
    #  pending_feedback
    ##
    @retry(stop_max_attempt_number=8, wait_exponential_multiplier=500, retry_on_exception=server_error)
    def pending_feedback(self):
        """
        Return the integer number of feedback requests pending for this application.
        This is useful for controlling the flow of images input into the system to avoid creating too many backlogged feedback requests.
        """
        resp = self._cc.session.get(url_prefix + "/feedback/pending?application_id=%s" % self.application_id)
        raise_errors(resp)

        return resp.json()['pending']

    ##
    #  model_name
    ##
    @retry(stop_max_attempt_number=8, wait_exponential_multiplier=500, retry_on_exception=server_error)
    def model_name(self):
        """
        return the modelname for the current best model for this application
        """
        resp = self._cc.session.get(url_prefix + "/applications/%s/ccp" % self.application_id)

        raise_errors(resp)
        resp = resp.json()

        url = resp['best_model_ccp_url']
        modelname = url.split('/')[-1]
        return modelname

    ##
    #  download_model
    ##
    @retry(stop_max_attempt_number=8, wait_exponential_multiplier=500, retry_on_exception=server_error)
    def download_model(self):
        """
        Download the current active model for this application to a file in the current working directory and
        return the local filename which will be the same as the model name.
        """
        resp = self._cc.session.get(url_prefix + "/applications/%s/ccp" % self.application_id)
        raise_errors(resp)

        resp = resp.json()
        url = resp['best_model_ccp_url']
        modelname = url.split('/')[-1]

        resp = self._cc.session.get(url)
        raise_errors(resp)

        fp = open(modelname, "w")
        fp.write(resp.content)
        fp.close()
        return modelname
