#!/usr/bin/env python

"""
This module simply sends request to the
`EIS RESTful API <https://wiki.eis.utoronto.ca/display/API/>`_,
and returns their response as a dict.
"""
import os
import requests
import datetime
from pyvss import __version__
from time import sleep
import json as json_module
from pyvss.helper import HTTPBasicAuth
from pyvss.exceptions import VssError

API_ENDPOINT_BASE = 'https://vss-api.eis.utoronto.ca'
VSKEY_STOR_ENDPOINT = 'https://vskey-stor.eis.utoronto.ca'
DATETIME_FMT = '%Y-%m-%d %H:%M'
VALID_VM_USAGE = [('Production', 'Prod'),
                  ('Testing', 'Test'),
                  ('Development', 'Dev'),
                  ('QA', 'QA')]
VALID_VM_BUILD_PROCESS = ['clone', 'template', 'image', 'os_install']


class VssManager(object):
    user_agent = 'pyvss/{}'.format(__version__)
    content_type = 'application/json'
    """
    Class containing methods to interact with the VSS REST API

    Example::

        vss = VssManager(tk='access-token')
        vss.whoami()


    If tk is none it will get the token from the
    ``VSS_API_TOKEN`` environment variable.

    Example::

        vss = VssManager()
        vss.whoami()


    """
    def __init__(self, tk=None, api_endpoint=None, debug=False):
        """
        VSS Manager to interact with the REST API

        :param tk: REST API access token
        :param api_endpoint: REST API endpoint defaults to
         https://vss-api.eis.utoronto.ca
        :type tk: str

        """
        self.api_endpoint_base = api_endpoint or API_ENDPOINT_BASE
        self.api_endpoint = '{}/v2'.format(api_endpoint or API_ENDPOINT_BASE)
        self.token_endpoint = '{}/auth/request-token'.format(api_endpoint)
        self.api_token = tk or os.environ.get('VSS_API_TOKEN')
        self.vskey_stor = None
        self.debug = debug

    def get_token(self, user=None, password=None):
        """
        Generates token based on two environment variables or
        provided OR and password:

        - ``VSS_API_USER``: username
        - ``VSS_API_USER_PASS``: password

        :param user: Username
        :type user: str
        :param password: Username password
        :type password: str
        :return: generated token or VssError

        """
        username = user or os.environ.get('VSS_API_USER')
        password = password or os.environ.get('VSS_API_USER_PASS')
        username_u = username.decode('utf-8') \
            if isinstance(username, bytes) else username
        password_u = password.decode('utf-8') \
            if isinstance(password, bytes) else password
        tk_request = self.request_v2(self.token_endpoint,
                                     method='POST',
                                     auth=HTTPBasicAuth(username_u,
                                                        password_u))
        if tk_request.get('token'):
            self.api_token = tk_request.get('token')
            return self.api_token
        else:
            raise VssError('Could not generate token')

    def get_vskey_stor(self, **kwargs):
        """
        Instantiates a WebDav Client to interact with VSKEY-STOR

        :param kwargs: keyword arguments with

        .. warning::
         `WebdavClient <http://designerror.github.io/webdav-client-python/>`_
         module is required

        Example::

            # Creating an instance with username and password if
            # no env var was set
            vss.get_vskey_stor(webdav_login='user',
            webdav_password='P455w00rD')

            # Download inventory file
            vss.vskey_stor.download_sync(
            remote_path='inventory/584e7ada-efbf-4bf8-915c-c6ef02f70547.csv',
            local_path='~/Downloads/584e7ada-efbf-4bf8-915c-c6ef02f70547.csv')

            # Upload image
            vss.vskey_stor.upload_sync(
            remote_path='images/coreos_production_vmware_ova.ova',
            local_path='~/Downloads/coreos_production_vmware_ova.ova')


        """
        from webdav import client as wc
        opts = dict(webdav_login=os.environ.get('VSS_API_USER'),
                    webdav_password=os.environ.get('VSS_API_USER_PASS'),
                    webdav_hostname=VSKEY_STOR_ENDPOINT)
        opts.update(kwargs)
        self.vskey_stor = wc.Client(options=opts)
        return self.vskey_stor.valid()

    # User Management methods
    def get_user_isos(self):
        """
        .. _VSKEY-STOR: https://vskey-stor.eis.utoronto.ca

        Obtain list of user ISO images in personal store. If you have
        uploaded an iso to VSKEY-STOR_ already and is not listed, run
        :py:func:`sync_user_isos`.

        :return: list
        """
        json = self.request_v2('/user/image/iso', method='GET')
        return json.get('data')

    def sync_user_isos(self):
        """
        Submit an ISO Image Synchronization request between VSKEY-STOR_
        and API. Verify status with :py:func:`get_image_sync_request`.
        :return: request object
        """
        json = self.request_v2('/user/image/iso', method='PATCH')
        return json.get('data')

    def get_user_floppies(self):
        """
        .. _VSKEY-STOR: https://vskey-stor.eis.utoronto.ca

        Obtain list of user Floppy images in personal store. If you have
        uploaded a .flp image to VSKEY-STOR_ already and is not listed, run
        :py:func:`sync_user_floppies`.

        :return: list
        """
        json = self.request_v2('/user/image/floppy', method='GET')
        return json.get('data')

    def sync_user_floppies(self):
        """
        Submit an Floppy Image Synchronization request between VSKEY-STOR_
        and API. Verify status with :py:func:`get_image_sync_request`.
        :return: request object
        """
        json = self.request_v2('/user/image/floppy', method='PATCH')
        return json.get('data')

    def get_user_vm_images(self):
        """
        .. _VSKEY-STOR: https://vskey-stor.eis.utoronto.ca

        Obtain list of user OVA/OVF virtual machine images in personal store.
        If you have uploaded a OVF/OVA image to VSKEY-STOR_ already and
        is not listed, run :py:func:`sync_user_vm_images`.

        :return: list
        """
        json = self.request_v2('/user/image/vm', method='GET')
        return json.get('data')

    def sync_user_vm_images(self):
        """
        .. _VSKEY-STOR: https://vskey-stor.eis.utoronto.ca

        Submit an OVA/OVF VM Image Synchronization request between VSKEY-STOR_
        and API. Verify status with :py:func:`get_image_sync_request`.
        :return: request object
        """
        json = self.request_v2('/user/image/vm', method='PATCH')
        return json.get('data')

    def get_user_roles(self):
        """
        Gets both request and access roles of current user

        :return: object

        """
        json = self.request_v2('/user/role', method='GET')
        return json.get('data')

    def get_user_status(self):
        """
        Gets your current status including:

        - active: whether user is active or not
        - created_on: time stamp when user was created
        - last_access: most recent access time stamp
        - updated_on: last time user was updated

        :return: object
        """
        json = self.whoami()
        return json.get('status')

    def get_user_personal(self):
        """
        Returns your personal info, such as email, phone, username
        and full name.

        :return: object
        """
        json = self.request_v2('/user/personal', method='GET')
        return json.get('data')

    def get_user_ldap(self):
        """
        Gets LDAP related information about your account including

        - pwdAccountLockedTime: shows whether your LDAP account is locked
        - pwdChangeTime: time stamp when you changed your pwd
        - mail: associated emails
        - authTimestamp: last authenticated time stamp

        :return: object
        """
        json = self.request_v2('/user/ldap', method='GET')
        return json.get('data')

    def get_user_groups(self):
        """
        Gets current user groups

        :return: list of str
        """
        json = self.request_v2('/user/group', method='GET')
        return json.get('data')

    def get_user_group(self, cn, member=False):
        """
        Gets user group info and members

        :param cn: group common name
        :type cn: str
        :param member: whether to return member list
        :type member: bool
        :return: list of str
        """
        payload = None
        if member:
            payload = dict(member=member)
        json = self.request_v2('/user/group/{cn}'.format(cn=cn), method='GET',
                               params=payload)
        return json.get('data')

    def get_user_token(self, token_id):
        """
        Obtains given token id data such as:

        - value
        - status

        :param token_id: Access token id to manage
        :type token_id: int
        :return: object

        """
        json = self.request_v2('/user/token/{tk}'.format(tk=token_id),
                               method='GET')
        return json.get('data')

    def disable_user_token(self, token_id):
        """
        Disables given access token id

        :param token_id: token id to disable
        :type token_id: int
        :return: status dict

        """
        json = self.request_v2('/user/token/{tk}'.format(tk=token_id),
                               method='PUT')
        return json

    def get_user_tokens(self, show_all=False, **kwargs):
        """
        Gets user tokens

        :param show_all: Whether to show all tokens or just
         the default count
        :type show_all: bool

        :return: list of objects

        .. note:: keyword arguments implement filters such as
          paging, filtering and sorting. Refer to the official
          documentation for further details. See
          `User <https://wiki.eis.utoronto.ca/x/tgGC>`_

        Example::

            vss.get_user_tokens(filter='active,eq,true',
                                per_page=10)

        """
        data = self._get_objects(pag_resource='/user/token',
                                 show_all=show_all,
                                 **kwargs)
        return data

    def delete_user_token(self, token_id):
        """
        Deletes given token id

        :param token_id: Token id to delete
        :type token_id: int
        :return: dict with request status
        """
        json = self.request_v2('/user/token/{tk}'.format(tk=token_id),
                               method='DELETE')
        return json

    def get_user_email_settings(self):
        """
        Returns current user email settings

        Email settings currently are:

        - all: receive email notifications
        - completion: receive email notification upon completion
        - error: receive email notifications only when error
        - none: no email notifications
        - submission: receive email notification when submitted

        :return: object
        """
        json = self.request_v2('/user/setting/email', method='GET')
        return json.get('data')

    def disable_user_email(self):
        """
        Disables all email notification

        :return: updated email settings object
        """
        json = self.update_user_email_settings(attribute='none',
                                               value=True)
        return json

    def enable_user_email(self):
        """
        Enables all email notification

        :return: updated email settings object
        """
        json = self.update_user_email_settings(attribute='all',
                                               value=True)
        return json

    def enable_user_email_error(self):
        """
        Updates email notification settings to get just errors

        :return: updated email settings object
        """
        json = self.update_user_email_settings(attribute='error',
                                               value=True)
        return json

    def update_user_email_settings(self, attribute, value):
        """
        Updates user email notification settings for a given
        attribute and value

        :param attribute: attribute to update. could be
         ``<error|none|completion|submission>``
        :type attribute: str
        :param value: True or false
        :type value: bool
        :return: updated email settings object

        """
        json_payload = dict(attribute=attribute, value=value)
        json = self.request_v2('/user/setting/email', method='PUT',
                               payload=json_payload)
        json.update(self.get_user_email_settings())
        return json

    def whoami(self):
        """
        Retrieves current user summary

        :return: object
        """
        json = self.request_v2('/user')
        return json.get('data')

    # Operating systems
    def get_os(self, name=False, show_all=True, **kwargs):
        """
        Gets Virtual Machine supported Guest Operating systems

        - name: Guest operating system full name. i.e. CentOS 4/5
        - id: Guest operating system id. i.e. centosGuest

        :param show_all: Whether to show all requests or just
         the default count
        :param name: Filter by Guest OS full name
        :type show_all: bool
        :param kwargs: arguments to pass such as:
            - guestId: Guest OS identifier
            - guestFullName: Guest OS full name.

        :return: list of objects

        .. note:: keyword arguments implement filters such as
          paging, filtering and sorting. Refer to the official
          documentation for further details. See
          `Operating Systems <https://wiki.eis.utoronto.ca/x/EQGC>`_

        Example::

            vss.get_os(sort='created_on,desc', per_page=100)


        """
        if name:
            kwargs.update(
                {'filter': 'guestFullName,like,{name}%'.format(name=name)}
            )
        data = self._get_objects(pag_resource='/os',
                                 show_all=show_all,
                                 **kwargs)
        return data

    # inventory management
    def create_inventory_file(self, props=None, fmt='json'):
        """ Submits a request to generate a full inventory
        report of your Virtual Machines.

        .. _VSKEY-STOR: https://vskey-stor.eis.utoronto.ca

        The report will be transferred to your space at VSKEY-STOR_ and also
        be available via :py:func:`download_inventory_result`

        :param props: properties to include in report
        :type props: list
        :param fmt: report format <json|csv>. default json
        :type fmt: str
        :return: inventory request object

        .. note:: See `Inventory Docs <https://wiki.eis.utoronto.ca/x/_gCC>`_
          for more information

        """
        props = props if props else ['uuid', 'name']
        json_payload = dict(properties=props, format=fmt)
        json = self.request_v2('/inventory', payload=json_payload,
                               method='POST')
        return json.get('data')

    def download_inventory_result(self, request_id, directory=None):
        """ Download given inventory report

        :param request_id: Inventory request id
        :param directory: Directory to download file
        :return: full path to written file

        Example::

            vss.download_inventory_result(request_id=123,
                                          directory='~/Downloads')

            vss.download_inventory_result(request_id=123)


        .. note:: See `Inventory Docs <https://wiki.eis.utoronto.ca/x/_gCC>`_
          for more information

        """
        response = self.request_v2('/inventory/{}'.format(request_id),
                                   method='GET')
        import re
        if response:
            _directory = os.path.expanduser(directory) if directory \
                else os.path.curdir
            if not os.path.isdir(_directory):
                os.mkdir(_directory)
            _file_name = re.findall(
                r'filename=(.*)',
                response.headers.get('Content-Disposition'))[0]
            # full_path
            _full_path = os.path.join(_directory, _file_name)
            with open(_full_path, 'wb') as f:
                f.write(response.content)
            return _full_path
        else:
            raise VssError('Invalid response')

    # Request management
    def get_requests(self, **kwargs):
        """
        Get Summary of current requests submitted

        :return: list of objects

        """
        json = self.request_v2('/request', params=kwargs)
        return json.get('data')

    def _get_objects(self, pag_resource, show_all=False, **kwargs):
        params = dict(expand=1)
        params.update(kwargs)
        json = self.request_v2(pag_resource,
                               params=params)
        result = list()
        result_extend = result.extend
        while True:
            result_extend(json.get('data'))
            meta = json.get('meta').get('pages')
            next_url = meta.get('next_url')
            if not show_all or not meta or not next_url:
                break
            json = self.request_v2(next_url)
        return result

    def get_new_requests(self, show_all=False, **kwargs):
        """
        Gets new vm deployment requests.

        :param show_all: Whether to show all requests or just
         the default count
        :type show_all: bool

        :return: list of objects

        .. note:: keyword arguments implement filters such as
          paging, filtering and sorting. Refer to the official
          documentation for further details. See
          `Request <https://wiki.eis.utoronto.ca/x/fACW>`_

        Example::

            vss.get_new_requests(sort='created_on,desc', per_page=100)

        """
        data = self._get_objects(pag_resource='/request/new',
                                 show_all=show_all,
                                 **kwargs)
        return data

    def get_new_request(self, request_id):
        """
        Gets given new request data

        :param request_id: new request id to get
        :type request_id: int
        :return: object

        """
        json = self.request_v2('/request/new/{id}'.format(id=request_id))
        return json.get('data')

    def get_new_request_meta_data(self, request_id):
        """
        Gets given new request meta data

        :param request_id: new request id to get
        :type request_id: int
        :return: object

        """
        json = self.request_v2('/request/new/{id}/meta_data'.format(
            id=request_id))
        return json.get('data')

    def get_new_request_user_data(self, request_id, decode=False):
        """
        Gets given new request submitted user data.
        Cloud-init user_data to preconfigure the guest os upon first boot.

        .. note:: Experimental feature and currently tested with Ubuntu
          Cloud Images and VMware Photon OS. Only supported on OVA/OVF
          deployments.

        :param request_id: new request id to get
        :type request_id: int
        :param decode: whether to decode user_data
        :type decode: bool
        :return: object

        """
        params = dict(decode=1) if decode else None
        json = self.request_v2('/request/new/{id}/user_data'.format(
            id=request_id, params=params))
        return json.get('data')

    def get_new_request_custom_spec(self, request_id):
        """
        Gets given new request submitted custom specification.

        :param request_id: new request id to get
        :type request_id: int
        :return: object
        """
        json = self.request_v2('/request/new/{id}/custom_spec'.format(
            id=request_id))
        return json.get('data')

    def retry_new_request(self, request_id):
        """
        Retry given new request only if it has an "Error Processed" status.

        :param request_id: new request id to get
        :type request_id: int
        :return: object
        """
        json = self.request_v2('/request/new/{id}'.format(id=request_id),
                               method='PATCH')
        return json.get('data')

    def get_change_requests(self, show_all=False, **kwargs):
        """
        Gets change requests submitted for every change to a given
        virtual machine.

        :param show_all: Whether to show all requests or just
         the default count
        :type show_all: bool

        :return: list of objects

        .. note:: keyword arguments implement filters such as
          paging, filtering and sorting. Refer to the official
          documentation for further details. See
          `Request <https://wiki.eis.utoronto.ca/x/fACW>`_

        Example::

            vss.get_change_requests(filter='status,eq,Error Processed',
                                    per_page=100)

        """
        data = self._get_objects(pag_resource='/request/change',
                                 show_all=show_all,
                                 **kwargs)
        return data

    def get_change_request(self, request_id):
        """
        Gets given change request data

        :param request_id: change request id to get
        :type request_id: int
        :return: object

        """
        json = self.request_v2('/request/change/{id}'.format(id=request_id))
        return json.get('data')

    def cancel_scheduled_change_request(self, request_id):
        """
        Cancels scheduled execution of a given change request

        :param request_id: Change request id
        :type request_id: int
        :return: request status

        """
        payload = dict(scheduled=False)
        json = self.request_v2('/request/change/{id}'.format(id=request_id),
                               payload=payload, method='PUT')
        return json

    def reschedule_change_request(self, request_id, date_time):
        """
        Reschedules a given change request

        :param request_id: Change request id
        :type request_id: int
        :param date_time: Timestamp with the following format
         ``%Y-%m-%d %H:%M``. If date is in the past, the change
         request will be processed right away, otherwise it will wait.
        :type date_time: str
        :return: request status

        """
        date_time_v = datetime.datetime.strptime(date_time, DATETIME_FMT)
        payload = dict(scheduled_datetime=date_time)
        json = self.request_v2('/request/change/{id}'.format(id=request_id),
                               payload=payload, method='PUT')
        return json

    def retry_change_request(self, request_id):
        """
        Retry given change request only if it has an "Error Processed" status.

        :param request_id: new request id to get
        :type request_id: int
        :return: object
        """
        json = self.request_v2('/request/change/{id}'.format(id=request_id),
                               method='PATCH')
        return json.get('data')

    def get_snapshot_requests(self, show_all=False, **kwargs):
        """
        Gets snapshot requests

        :param show_all: Whether to show all requests or just
         the default count
        :type show_all: bool

        :return: list of objects

        .. note:: keyword arguments implement filters such as
          paging, filtering and sorting. Refer to the official
          documentation for further details. See
          `Request <https://wiki.eis.utoronto.ca/x/fACW>`_

        Example::

            vss.get_snapshot_request(filter='status,eq,Processed',
                                    per_page=100)

        """
        data = self._get_objects(pag_resource='/request/snapshot',
                                 show_all=show_all,
                                 **kwargs)
        return data

    def get_snapshot_request(self, request_id, **kwargs):
        """
        Gets given snapshot request data

        :param request_id: snapshot request id to get
        :type request_id: int
        :return: object

        """
        json = self.request_v2('/request/snapshot/{id}'.format(
            id=request_id), params=kwargs)
        return json.get('data')

    def extend_snapshot_request(self, request_id, duration):
        """
        Extends valid snapshot request to a given number of hours

        :param request_id: Snapshot request id
        :type request_id: int
        :param duration: new duration
        :type duration: int
        :return: tuple with status and new snapshot data

        """
        payload = dict(attribute='duration', value=duration)
        request = self.request_v2('/request/snapshot/{id}'.format(
            id=request_id))
        # check if lifetime is done
        if request.get('data').get('status') not in ['Scheduled']:
            raise VssError('Only scheduled snapshot requests can '
                           'be extended.')
        # update
        json = self.request_v2('/request/snapshot/{id}'.format(
            id=request_id), method='PUT', payload=payload)
        if json.get('status') != 204:
            raise VssError('An error occurred extending request.')
        # return
        request = self.request_v2('/request/snapshot/{id}'.format(
            id=request_id))
        return json, request.get('data')

    def get_inventory_requests(self, show_all=False, **kwargs):
        """
        Gets inventory requests

        :param show_all: Whether to show all requests or just
         the default count
        :type show_all: bool

        :return: list of objects

        .. note:: keyword arguments implement filters such as
          paging, filtering and sorting. Refer to the official
          documentation for further details. See
          `Request <https://wiki.eis.utoronto.ca/x/fACW>`_

        Example::

            vss.get_inventory_requests(filter='transferred,eq,true',
                                       per_page=100)

        """
        data = self._get_objects(pag_resource='/request/inventory',
                                 show_all=show_all,
                                 **kwargs)
        return data

    def get_inventory_request(self, request_id, **kwargs):
        """
        Gets given inventory request data

        :param request_id: inventory request id to get
        :type request_id: int
        :return: object

        """
        json = self.request_v2('/request/inventory/{id}'.format(
            id=request_id), params=kwargs)
        return json.get('data')

    def get_export_requests(self, show_all=False, **kwargs):
        """
        Gets virtual machine export requests

        :param show_all: Whether to show all requests or just
         the default count
        :type show_all: bool

        :return: list of objects

        .. note:: keyword arguments implement filters such as
          paging, filtering and sorting. Refer to the official
          documentation for further details. See
          `Request <https://wiki.eis.utoronto.ca/x/fACW>`_

        Example::

            vss.get_export_requests(filter='status,eq,Processed',
                                    per_page=100)

        """
        data = self._get_objects(pag_resource='/request/export',
                                 show_all=show_all,
                                 **kwargs)
        return data

    def get_export_request(self, request_id, **kwargs):
        """
        Gets given export request data

        :param request_id: export request id to get
        :type request_id: int
        :return: object

        """
        json = self.request_v2('/request/export/{id}'.format(id=request_id),
                               params=kwargs)
        return json.get('data')

    def get_folder_requests(self, show_all=False, **kwargs):
        """
        Gets folder requests

        :param show_all: Whether to show all requests or just
         the default count
        :type show_all: bool

        :return: list of objects

        .. note:: keyword arguments implement filters such as
          paging, filtering and sorting. Refer to the official
          documentation for further details. See
          `Request <https://wiki.eis.utoronto.ca/x/fACW>`_

        Example::

            vss.get_folder_requests(filter='status,eq,Processed',
                                    per_page=100)

        """
        data = self._get_objects(pag_resource='/request/folder',
                                 show_all=show_all,
                                 **kwargs)
        return data

    def get_folder_request(self, request_id, **kwargs):
        """
        Gets given folder request data

        :param request_id: folder request id to get
        :type request_id: int
        :return: object

        """
        json = self.request_v2('/request/folder/{id}'.format(id=request_id),
                               params=kwargs)
        return json.get('data')

    def get_image_sync_requests(self, show_all=False, **kwargs):
        """
        Gets image synchronization requests

        :param show_all: Whether to show all requests or just
         the default count
        :type show_all: bool

        :return: list of objects

        .. note:: keyword arguments implement filters such as
          paging, filtering and sorting. Refer to the official
          documentation for further details. See
          `Request <https://wiki.eis.utoronto.ca/x/fACW>`_

        Example::

            vss.get_image_sync_requests(filter='status,eq,Processed',
                                        per_page=100)

        """
        data = self._get_objects(pag_resource='/request/image_sync',
                                 show_all=show_all,
                                 **kwargs)
        return data

    def get_image_sync_request(self, request_id, **kwargs):
        """
        Gets image synchronization request data

        :param request_id: image synchronization request id to get
        :type request_id: int
        :return: object

        """
        json = self.request_v2('/request/image_sync/{id}'.format(
            id=request_id), params=kwargs)
        return json.get('data')

    # Domain management
    def get_domains(self, **kwargs):
        """
        Get available Fault Domains

        :param kwargs: filters

        - moref: managed object reference
        - name: domain name

        :return: list of objects

        """
        json = self.request_v2('/domain', params=kwargs)
        return json.get('data')

    def get_domain(self, moref, **kwargs):
        """
        Get fault domain data

        :param moref: managed object reference
        :type moref: str
        :param kwargs: filter keyword arguments

        - summary: list vms running on fault domain

        :return: object

        """
        json = self.request_v2('/domain/{moId}'.format(moId=moref),
                               params=kwargs)
        return json.get('data')

    def get_vms_by_domain(self, domain_moref):
        """
        Get Virtual Machines on given Fault Domain

        :param domain_moref: Domain managed object reference
        :type domain_moref: str
        :return: list of vm objects

        """
        json = self.get_domain(domain_moref, summary=1)
        return json.get('vms')

    # Image Management
    def get_images(self, show_all=False, per_page=250, **kwargs):
        """
        Get list of global OVA/OVF images.

        :param show_all: Whether to show all OVA/OVF VM images or just
         the default count
        :type show_all: bool
        :param per_page: how many results per page
        :type per_page: int
        :return: list of objects

        .. note:: keyword arguments implement
          paging, filtering and sorting. Refer to the official
          documentation for further details. See
          `OVA/OVF Images <https://wiki.eis.utoronto.ca/x/aAGC>`_

        Example::

            vss.get_isos(filter='name,like,ub%', sort='name,asc')

            vss.get_isos(filter='name,like,Win%', sort='path,desc')


        """
        kwargs.update({'per_page': per_page})
        data = self._get_objects(pag_resource='/image',
                                 show_all=show_all,
                                 **kwargs)
        return data

    # ISO Management
    def get_isos(self, show_all=False, per_page=250, **kwargs):
        """
        Get list of global iso images.

        :param show_all: Whether to show all ISO images or just
         the default count
        :type show_all: bool
        :param per_page: how many results per pege
        :type per_page: int
        :return: list of objects

        .. note:: keyword arguments implement
          paging, filtering and sorting. Refer to the official
          documentation for further details. See
          `ISO Images <https://wiki.eis.utoronto.ca/x/IAGC>`_

        Example::

            vss.get_isos(filter='name,like,ub%', sort='name,asc')

            vss.get_isos(filter='name,like,Win%', sort='path,desc')


        """
        kwargs.update({'per_page': per_page})
        data = self._get_objects(pag_resource='/iso',
                                 show_all=show_all,
                                 **kwargs)
        return data

    # Floppy Management
    def get_floppies(self, show_all=False, per_page=250, **kwargs):
        """
        Get list of global floppy images.

        :param show_all: Whether to show all floppy images or just
         the default count
        :type show_all: bool
        :param per_page: how many results per pege
        :type per_page: int
        :return: list of objects

        .. note:: keyword arguments implement
          paging, filtering and sorting. Refer to the official
          documentation for further details. See
          `Floppy Images <https://wiki.eis.utoronto.ca/x/OIC2>`_

        Example::

            vss.get_floppies(filter='name,like,pvscsi%')


        """
        kwargs.update({'per_page': per_page})
        data = self._get_objects(pag_resource='/floppy',
                                 show_all=show_all,
                                 **kwargs)
        return data

    # Network Management
    def get_networks(self, **kwargs):
        """
        Get list networks you are allowed to access

        :param kwargs: filters

        - name: filter by name
        - moref: filter by network managed object reference
        - sort: sort results by name, moref or if summary enabled
         sort by subnet, label, ports or description
        - summary: show network summary

        :return: list of objects

        Example::

            vss.get_networks(summary=1, sort='subnet'):

        """
        json = self.request_v2('/network', params=kwargs)
        return json.get('data')

    def get_network(self, moref, **kwargs):
        """
        Get details of given network

        :param moref: network managed object reference
        :param kwargs: additional parameters

        - summary: show vms on this network

        :return: list of virtual machine objects

        """
        json = self.request_v2('/network/{moId}'.format(moId=moref),
                               params=kwargs)
        return json.get('data')

    def get_vms_by_network(self, moref):
        """
        Get Virtual Machines on given network

        :param moref: network managed object reference
        :return: list of objects
        """
        json = self.get_network(moref, summary=1)
        return json.get('vms')

    # Folder Management
    def get_folders(self, **kwargs):
        """
        Get list of logical folders

        :param kwargs: arguments to pass such as:

        - moref: filter by managed object reference
        - name: filter by name
        - parent: filter by parent name
        - sort: sort folder by name or moref. If summary enabled
         sort by parent or path.
        - summary: show folder summary

        :return: list of objects

        Example::

            vss.get_folders(summary=1, sort='path')

        """
        json = self.request_v2('/folder', params=kwargs)
        return json.get('data')

    def get_folder(self, moref, **kwargs):
        """
        Get logical folder data

        :param moref: managed object reference
        :type moref: str
        :param kwargs: arguments to pass such as:

        - summary: enables children vm listing

        :return: object
        """
        json = self.request_v2('/folder/{moId}'.format(moId=moref),
                               params=kwargs)
        return json.get('data')

    def create_folder(self, moref, name):
        """
        Creates logical folder under given managed object
        reference

        :param moref: Parent folder managed object reference
        :param name: New folder name
        :return: folder request object
        """
        json_payload = dict(name=name)
        json = self.request_v2('/folder/{moId}'.format(moId=moref),
                               payload=json_payload,
                               method='POST')
        return json.get('data')

    def move_folder(self, moref, new_moref):
        """
        Moves given folder to new parent

        :param moref: folder to move managed object
         reference
        :param new_moref: target parent managed object
         reference to move folder to
        :return: folder request object

        """
        json_payload = dict(attribute='parent', value=new_moref)
        json = self.request_v2('/folder/{moId}'.format(moId=moref),
                               payload=json_payload,
                               method='PUT')
        return json.get('data')

    def rename_folder(self, moref, name, **kwargs):
        """
        Renames given logical folder

        :param moref: folder managed object reference
        :param name: folder new name
        :return: folder request object
        """
        json_payload = dict(attribute='name', value=name)
        json_payload.update(kwargs)
        json = self.request_v2('/folder/{moref}'.format(moref=moref),
                               payload=json_payload,
                               method='PUT')
        return json.get('data')

    # Virtual Machine Management
    def get_templates(self, **kwargs):
        """
        Get list of your templates

        :param kwargs: filters and flags

        - name: filters by name
        - summary: displays summary of template

        :return: list of virtual machine objects

        """
        json = self.request_v2('/template', params=kwargs)
        return json.get('data')

    def get_vms(self, **kwargs):
        """
        Get list of virtual machines

        :param kwargs: filters and flags

        - **dns**: filter by main dns name
        - **ip**: filter by main ip address
        - **name**: filter by name
        - **path**: filter by VM path
        - **summary**: show VMs summary or not
        - **sort**: name or uuid. If ``summary=1``,
          vms could be sorted by overallStatus,
          powerState, memoryGB, guestFullName and cpuCount.

        :return: list of virtual machine objects

        Example::

            vss.get_vms(sort='name')
            vss.get_vms(summary=1, sort='powerState')

        """
        json = self.request_v2('/vm', params=kwargs)
        return json.get('data')

    def get_vm(self, uuid, **kwargs):
        """
        Get basic information of given virtual machine

        :param uuid: virtual machine uuid
        :type uuid: str

        :return: object

        Virtual Machine attributes include:

        - storage
        - state
        - snapshot
        - note
        - devices
        - memory
        - cpu
        - guest
        - folder

        .. note:: more information about required attributes
          available in `Virtual Machine <https://wiki.eis.utoronto.ca/x/pgCC>`_

        """
        json = self.request_v2('/vm/{uuid}'.format(uuid=uuid),
                               params=kwargs)
        return json.get('data')

    def get_vm_spec(self, uuid):
        """
        Get given virtual Machine specification

        :param uuid: virtual machine uuid
        :type uuid: str
        :return: object

        .. note:: useful to create a ``shell clone``

        """
        json = self.request_v2('/vm/{uuid}/spec'.format(uuid=uuid))
        return json.get('data')

    def get_vm_name(self, uuid):
        """
        Gets given Virtual Machine full name

        :param uuid: Virtual Machine uuid
        :type uuid: str
        :return: object
        """
        json = self.request_v2('/vm/{uuid}/name'.format(uuid=uuid))
        return json.get('data')

    def get_vm_state(self, uuid):
        """
        Gets given Virtual Machine state info

        :param uuid: Virtual Machine uuid
        :type uuid: str
        :return: object

        Virtual Machine attributes include:

        - bootTime
        - domain
        - connectionState
        - powerState

        """
        json = self.request_v2('/vm/{uuid}/state'.format(uuid=uuid))
        return json.get('data')

    def update_vm_state(self, uuid, state, **kwargs):
        """
        Updates given Virtual Machine power state

        :param uuid: Virtual Machine uuid
        :type uuid: str
        :param state: Desired state
        :type state: str
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        """
        if state not in ['poweredOff', 'poweredOn', 'reset', 'reboot',
                         'shutdown']:
            raise VssError('Unsupported {state} state'.format(state=state))
        json_payload = dict(value=state)
        json_payload.update(kwargs)
        json = self.request_v2('/vm/{uuid}/state'.format(uuid=uuid),
                               method='PUT',
                               payload=json_payload)
        return json.get('data')

    def get_vm_domain(self, uuid):
        """
        Get domain where Virtual Machine is running

        :param uuid: Virtual Machine uuid
        :type uuid: str
        :return: object
        """
        json = self.request_v2('/vm/{uuid}/domain'.format(uuid=uuid))
        return json.get('data')

    def update_vm_domain(self, uuid, moref, power_on=False,
                         force=False, **kwargs):
        """
        Updates fault domain of given VM

        :param uuid: Virtual Machine uuid
        :type uuid: str
        :param moref: Target domain managed object reference
        :type moref: str
        :param power_on: Whether VM will be powered of after migration
        :type power_on: bool
        :param force: If set to True, VM will be powered off prior migration
        :type force: bool
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        .. seealso:: :py:func:`get_domains` for domain parameter

        """
        valid_domain = self.get_domains(moref=moref)
        json_payload = dict(value=moref, poweron=power_on, force=force)
        json_payload.update(kwargs)
        json = self.request_v2('/vm/{uuid}/domain'.format(uuid=uuid),
                               method='PUT',
                               payload=json_payload)
        return json.get('data')

    # Virtual Machine Configuration
    def get_vm_boot(self, uuid):
        """
        Queries given Virtual Machine boot configuration

        :param uuid: Virtual Machine UUid
        :type uuid: int
        :return: object

        Configuration includes:

        - enterBIOSSetup
        - bootRetryDelayMs
        - bootDelayMs

        .. note:: more information about required attributes available in
          `Virtual Machine Attributes <https://wiki.eis.utoronto.ca/x/5ACC>`_

        """
        json = self.request_v2('/vm/{uuid}/boot'.format(uuid=uuid))
        return json.get('data')

    def update_vm_boot_bios(self, uuid, boot_bios, **kwargs):
        """
        Updates boot to bios configuration

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :param boot_bios: Enable or disable
        :type boot_bios: bool
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        """
        json = self.update_vm_boot(uuid, attribute='bootbios',
                                   value=boot_bios, **kwargs)
        return json

    def update_vm_boot_delay(self, uuid, boot_delay_ms, **kwargs):
        """
        Updates boot bios delay configuration

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :param boot_delay_ms: boot delay in milliseconds
        :type boot_delay_ms: int
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time
        """
        json = self.update_vm_boot(uuid, attribute='bootdelay',
                                   value=boot_delay_ms, **kwargs)
        return json

    def update_vm_boot(self, uuid, attribute, value, **kwargs):
        """
        Helper function to update boot configuration

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :param attribute: Either boot bios or boot delay
        :param value: int or bool
        :return: change request object

        .. note:: keywords arguments include schedule to process request
          on a given date and time
        """
        if attribute not in ['bootbios', 'bootdelay']:
            raise VssError('Boot attribute {} not supported'.format(attribute))
        json_payload = dict(attribute=attribute, value=value)
        json_payload.update(kwargs)
        json = self.request_v2('/vm/{uuid}/boot'.format(uuid=uuid),
                               method='PUT',
                               payload=json_payload)
        return json.get('data')

    def get_vm_os(self, uuid):
        """
        Gets Virtual Machine configured Operating System

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :return: object
        """
        json = self.request_v2('/vm/{uuid}/os'.format(uuid=uuid))
        return json.get('data')

    def update_vm_os(self, uuid, os, **kwargs):
        """
        Updates Virtual Machine Operating System configuration

        :param uuid: Virtual Machine uuid
        :type uuid: str
        :param os: Operating system id.
        :type os: str
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time
        .. seealso:: :py:func:`get_os` for os parameter

        """
        json_payload = dict(value=os)
        json_payload.update(kwargs)
        json = self.request_v2('/vm/{uuid}/os'.format(uuid=uuid),
                               method='PUT',
                               payload=json_payload)
        return json.get('data')

    def get_vm_folder(self, uuid):
        """
        Gets given Virtual Machine parent folder information

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :return: object

        attributes include:

        - full_path
        - name
        - parent
        - reference to folder resource

        .. seealso:: :py:func:`get_folder` for further information
          about a given folder

        """
        json = self.request_v2('/vm/{uuid}/folder'.format(uuid=uuid))
        return json.get('data')

    def update_vm_folder(self, uuid, folder_moId, **kwargs):
        """
        Moves VM to a given folder

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :param folder_moId: folder managed object reference
        :type folder_moId: str
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        """
        folder = self.get_folder(moref=folder_moId)
        json_payload = dict(value=folder_moId)
        json_payload.update(kwargs)
        json = self.request_v2('/vm/{uuid}/folder'.format(uuid=uuid),
                               method='PUT', payload=json_payload)
        return json.get('data')

    def get_vm_version(self, uuid):
        """
        Given Virtual Machine VMX version

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :return: object

        """
        json = self.request_v2('/vm/{uuid}/version'.format(uuid=uuid))
        return json.get('data')

    def upgrade_vm_version(self, uuid, when, **kwargs):
        """

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :param when: perform upgrade now or on next boot
        :type when: str
        :return: change request object

        """
        when = when if when in ['boot', 'now'] else 'boot'
        json_payload = dict(parameter='upgrade', value=when)
        json_payload.update(kwargs)
        json = self.request_v2('/vm/{uuid}/version'.format(uuid=uuid),
                               method='PUT', payload=json_payload)
        return json.get('data')

    # Virtual Machine Guest
    def get_vm_guest_os(self, uuid):
        """
        Gets Virtual Machine Guest Operating System

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :return: object

        """
        json = self.request_v2('/vm/{uuid}/guest/os'.format(uuid=uuid))
        return json.get('data')

    def run_cmd_guest_vm(self, uuid, user, pwd, cmd, arg, **kwargs):
        """
        Executes command in Guest Operating System

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :param user: Guest Operating Username
        :type user: str
        :param pwd: Guest Operating Username password
        :type pwd: str
        :param cmd: Command to execute
        :type cmd: str
        :param arg: Command arguments
        :type arg: str
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        .. note:: more information about required attributes
          available in
          `Virtual Machine Attributes <https://wiki.eis.utoronto.ca/x/5ACC>`_

        """
        json_payload = {'user': user, 'pass': pwd,
                        'args': arg, 'cmd': cmd}
        json_payload.update(kwargs)
        json = self.request_v2('/vm/{uuid}/guest/cmd'.format(uuid=uuid),
                               method='POST',
                               payload=json_payload)
        return json.get('data')

    def get_vm_guest_process_id(self, uuid, user, pwd, pid):
        """
        Gets given process id info

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :param user: Guest Operating Username
        :type user: str
        :param pwd: Guest Operating Username password
        :type pwd: str
        :param pid: Process Id to query
        :type pid: int
        :return: list of objects

        .. note:: Processes running in the guest operating system can be listed
          using the API via VMware Tools. If VMware Tools has not been
          installed or is not running, this resource will not work properly.

        .. note:: more information about required attributes
          available in
          `Virtual Machine Attributes <https://wiki.eis.utoronto.ca/x/5ACC>`_

        """
        json_payload = {'user': user, 'pass': pwd}
        json = self.request_v2('/vm/{uuid}/guest/cmd/{pid}'.format(uuid=uuid,
                                                                   pid=pid),
                               method='GET',
                               payload=json_payload)
        return json.get('data')

    def get_vm_guest_processes(self, uuid, user, pwd):
        """
        Gets given process id info

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :param user: Guest Operating Username
        :type user: str
        :param pwd: Guest Operating Username password
        :type pwd: str
        :return: list of objects

        .. note:: Processes running in the guest operating system can be listed
          using the API via VMware Tools. If VMware Tools has not been
          installed or is not running, this resource will not work properly.

        .. note:: more information about required attributes
          available in
          `Virtual Machine Attributes <https://wiki.eis.utoronto.ca/x/5ACC>`_

        """
        json_payload = {'user': user, 'pass': pwd}
        json = self.request_v2('/vm/{uuid}/guest/cmd'.format(uuid=uuid),
                               method='GET',
                               payload=json_payload)
        return json.get('data')

    def get_vm_guest_ip(self, uuid):
        """
        Get Virtual Machine IP and Mac addresses via
        VMware tools

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :return: list of objects
        """
        json = self.request_v2('/vm/{uuid}/guest/net/ip'.format(uuid=uuid))
        return json.get('data')

    # VMWare Tools
    def get_vm_tools(self, uuid):
        """
        Get VMware Tools status on given Virtual Machine

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :return: object

        attributes include:

        - runningStatus
        - version
        - versionStatus
        """
        json = self.request_v2('/vm/{uuid}/guest/tools'.format(uuid=uuid),
                               method='GET')
        return json.get('data')

    def upgrade_vm_tools(self, uuid, **kwargs):
        """
        Upgrade VMware Tools if Virtual Machine is using the
        official VMware Tools version.

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :return: change request object

        .. note:: This method fails if Guest OS is running
          an unmanaged distribution of VMware Tools.

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        """
        json = self.update_vm_tools(uuid, 'upgrade', **kwargs)
        return json

    def mount_vm_tools(self, uuid, **kwargs):
        """
        Mounts VMware official distribution of VMware Tools
        in Guest Operating system

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :return: change request object

        .. note:: This method fails if Guest OS is running
          an unmanaged distribution of VMware Tools.

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        """
        json = self.update_vm_tools(uuid, 'mount', **kwargs)
        return json

    def unmount_vm_tools(self, uuid, **kwargs):
        """
        Unmounts VMware official distribution of VMware Tools
        in Guest Operating system

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :return: change request object

        .. note:: This method fails if VMware Tools ISO is not
          mounted in guest OS

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        """
        json = self.update_vm_tools(uuid, 'unmount', **kwargs)
        return json

    def update_vm_tools(self, uuid, action, **kwargs):
        """
        Helper method to manage VMware tools on Virtual Machiene.

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :param action: Either mount, unmount or upgrade actions
        :type action: str
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        """
        if action not in ['mount', 'unmount', 'upgrade']:
            raise VssError('Unsupported {} action'.format(action))
        json_payload = dict(value=action)
        json_payload.update(kwargs)
        json = self.request_v2('/vm/{uuid}/guest/tools'.format(uuid=uuid),
                               method='PUT', payload=json_payload)
        return json.get('data')

    # Virtual Machine Snapshot Management
    def has_vm_snapshot(self, uuid):
        """
        Validates if Virtual Machine has snapshots

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :return: bool
        """
        json = self.get_vm(uuid)
        snapshot = json.get('snapshot')
        return snapshot.get('exist')

    def create_vm_snapshot(self, uuid, desc, date_time, valid):
        """
        Creates a Virtual Machine snapshot on a given date and time

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :param desc: A brief description of the snapshot.
        :type desc: str
        :param date_time: Timestamp with the following format
         ``%Y-%m-%d %H:%M``. If date is in the past, the change
         request will be processed right away, otherwise it will wait.
        :type desc: str
        :param valid: Number of hours (max 72) the snapshot will live
        :type valid: int
        :return: snapshot request object

        """
        date_time_v = datetime.datetime.strptime(date_time, DATETIME_FMT)
        json_payload = dict(description=desc,
                            from_date=date_time,
                            valid_for=valid)
        json = self.request_v2('/vm/{uuid}/snapshot'.format(uuid=uuid),
                               method='POST',
                               payload=json_payload)
        return json.get('data')

    def get_vm_snapshots(self, uuid):
        """
        Listing existent Virtual Machine snapshots

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :return: list of objects

        """
        json = self.request_v2('/vm/{uuid}/snapshot'.format(uuid=uuid))
        return json.get('data')

    def get_vm_snapshot(self, uuid, snapshot):
        """
        Get given Virtual Machine Snapshot information

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :param snapshot: Snapshot Id
        :type snapshot: int
        :return: object

        """
        json = self.request_v2('/vm/{uuid}/snapshot/{id}'.format(
            uuid=uuid, id=snapshot))
        return json.get('data')

    def delete_vm_snapshot(self, uuid, snapshot):
        """
        Deletes given Virtual Machine snapshot

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :param snapshot: Snapshot Id
        :type snapshot: int
        :return: snapshot request object

        """
        json = self.request_v2('/vm/{uuid}/snapshot/{id}'.format(
            uuid=uuid, id=snapshot), method='DELETE')
        return json.get('data')

    def revert_vm_snapshot(self, uuid, snapshot):
        """
        Reverts to given Virtual Machine snapshot

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :param snapshot: Snapshot Id
        :type snapshot: int
        :return: snapshot request object

        """
        json = self.request_v2('/vm/{uuid}/snapshot/{id}'.format(
            uuid=uuid, id=snapshot), method='PATCH')
        return json.get('data')

    def get_vm_consolidation(self, uuid):
        """
        Gets current Virtual Machine disks consolidation state

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :return: object

        """
        json = self.request_v2(
            '/vm/{uuid}/snapshot/consolidate'.format(uuid=uuid))
        return json.get('data')

    def consolidate_vm_disks(self, uuid, **kwargs):
        """
        Submits a Virtual Machine disk consolidation

        :param uuid:
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        """
        payload = dict()
        payload.update(kwargs)
        json = self.request_v2(
            '/vm/{uuid}/snapshot/consolidate'.format(uuid=uuid),
            method='PUT', payload=payload)
        return json.get('data')

    # Virtual Machine alarms
    def get_vm_alarms(self, uuid):
        """
        Gets Virtual Machine Alarms

        :param uuid: Virtual Machine uuid
        :type uuid: str
        :return: list of objects

        """
        json = self.request_v2('/vm/{uuid}/alarm'.format(uuid=uuid))
        return json.get('data')

    def get_vm_alarm(self, uuid, moref):
        """
        Get Virtual Machine Alarm

        :param uuid: Virtual Machine uuid
        :type uuid: str
        :param moref: Alarm managed object reference
        :type moref: str
        :return: list of objects

        """
        json = self.request_v2('/vm/{uuid}/alarm/{moref}'.format(uuid=uuid,
                                                                 moref=moref))
        return json.get('data')

    def clear_vm_alarm(self, uuid, moref, **kwargs):
        """
        Clears given Virtual Machine alarm

        :param uuid: Virtual Machine uuid
        :type uuid: str
        :param moref: Virtual Machine Alarm managed object
                      reference
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        """
        return self.update_vm_alarm(uuid=uuid, moref=moref,
                                    value='clear', **kwargs)

    def ack_vm_alarm(self, uuid, moref, **kwargs):
        """
        Acknowledges given Virtual Machine alarm

        :param uuid: Virtual Machine uuid
        :type uuid: str
        :param moref: Virtual Machine Alarm managed object
                      reference
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        """
        return self.update_vm_alarm(uuid=uuid, moref=moref,
                                    value='ack', **kwargs)

    def update_vm_alarm(self, uuid, moref, **kwargs):
        """
        Updates given Virtual Machine Alarm

        :param uuid: Virtual Machine uuid
        :type uuid: str
        :param moref: Virtual Machine Alarm managed object
         reference
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        """
        json_payload = dict()
        json_payload.update(kwargs)
        json = self.request_v2(
            '/vm/{uuid]/alarm/{moref}'.format(uuid=uuid,
                                              moref=moref),
            method='PUT',
            payload=json_payload)
        return json.get('data')

    # Virtual Machine events
    def get_vm_events(self, uuid, hours=1):
        """
        Queries Virtual Machine events in vCenter

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :param hours: Time window to get events from
        :type hours: int
        :return: list of events

        """
        event_uri = '/event/{}'.format(hours) if hours > 1 else '/event'
        json = self.request_v2('/vm/{uuid}{events}'.format(uuid=uuid,
                                                           events=event_uri))
        return json.get('data')

    # Virtual Machine performance
    def get_vm_performance_cpu(self, uuid):
        """
        Queries given Virtual Machine CPU
        performance counters. VM has to be powered On.

        :param uuid: Virtual Machine uuid
        :type uuid: str
        :return: object

        Performance counters include:

        - readyAvgPct
        - readyMaxPct
        - usagePct

        """
        json = self.request_v2(
            '/vm/{uuid}/performance/cpu'.format(uuid=uuid))
        return json.get('data')

    def get_vm_performance_memory(self, uuid):
        """
        Queries given Virtual Machine Memory
        performance counters. VM has to be powered On.

        :param uuid: Virtual Machine uuid
        :type uuid: str
        :return: object

        Performance counters include:

        - activeMb
        - activePct
        - balloonMb
        - balloonPct
        - dateTime
        - name
        - sharedMb
        - sharedPct
        - swappedMb
        - swappedPct
        - usagePct

        """
        json = self.request_v2(
            '/vm/{uuid}/performance/memory'.format(uuid=uuid))
        return json.get('data')

    def get_vm_performance_io(self, uuid):
        """
        Queries given Virtual Machine IO (datastore)
        performance counters. VM has to be powered On.

        :param uuid: Virtual Machine uuid
        :type uuid: str
        :return: object

        Performance counters include:

        - ioReadIops
        - ioWriteIops
        - latReadMs
        - latWriteMs

        """
        json = self.request_v2(
            '/vm/{uuid}/performance/io'.format(uuid=uuid))
        return json.get('data')

    def get_vm_performance_net(self, uuid):
        """
        Queries given Virtual Machine Network
        performance counters. VM has to be powered On.

        :param uuid: Virtual Machine uuid
        :type uuid: str
        :return: object

        Performance counters include:

        - rxErrors
        - rxMbps
        - txErrors
        - txMbps

        """
        json = self.request_v2(
            '/vm/{uuid}/performance/net'.format(uuid=uuid))
        return json.get('data')

    # Virtual Machine creation and deployment
    def export_vm(self, uuid):
        """
        Export given Virtual Machine to OVF.

        :param uuid: Virtual Machine uuid
        :type uuid: str
        :return: export request object

        .. _VSKEY-STOR: https://vskey-stor.eis.utoronto.ca

        .. note:: Once the export completes, will be transferred to
          VSKEY-STOR_

        """
        json = self.request_v2('/vm/{uuid}/export'.format(uuid=uuid),
                               method='POST')
        return json.get('data')

    def delete_vm(self, uuid, force=False):
        """
        Deletes given Virtual Machine

        :param uuid: Virtual Machine uuid
        :type uuid: str
        :param force: Force deletion if vm is on
        :type force: bool
        :return: change request object

        """
        if self.is_powered_on_vm(uuid=uuid) and not force:
            raise VssError('VM is powered on. Please use force=True')
        json = self.request_v2('/vm/{uuid}'.format(uuid=uuid),
                               method='DELETE')
        return json.get('data')

    def create_vm(self, os, built, bill_dept,
                  description, folder, networks, disks,
                  name=None, iso=None,
                  notes=None, usage='Test', cpu=1, memoryGB=1,
                  high_io=False, **kwargs):
        """
        Creates single Virtual Machine. Names are generated
        by appending name_number

        :param os: Operating system id.
        :type os: str
        :param built: built process
        :param bill_dept: Billing department
        :type bill_dept: str
        :param description: VM description
        :type description: str
        :param folder: Target VM folder moref
        :type folder: str
        :param networks: list of networks moref
        :type networks: list
        :param disks: list of disk sizes in GB
        :type disks: list
        :param name: name of the new virtual machine
        :type name: str
        :param iso: ISO image path to be mounted after creation
        :type iso: str
        :param notes: Custom Notes in key value format to
         store in the Virtual Machine annotation as meta-data.
        :type notes: dict
        :param usage: virtual machine usage
        :type usage: str
        :param cpu: vCPU count
        :type cpu: int
        :param memoryGB: Memory size in GB
        :type memoryGB: int
        :param high_io: If set to true,VM will be created
         with a VMware Paravirtual SCSIController.
        :type high_io: bool
        :return: new request objects

        .. seealso:: :py:func:`get_os` for os parameter,
          :py:func:`get_images` for image, :py:func:`get_folder` for folder,
          :py:func:`get_networks` for networks, :py:func:`get_isos` for isos

        .. note:: more information about required attributes
          available in `Virtual Machine <https://wiki.eis.utoronto.ca/x/pgCC>`_

        """
        # validate input
        usage = self.validate_usage(usage)
        built_from = self.validate_build_process(built)
        disks = disks if disks else [40]
        assert self.get_folder(folder), 'Invalid folder moref'
        assert [self.get_network(net) for net in networks],\
            'Invalid networks found'
        # generating payload
        json_payload = dict(os=os, built_from=built_from,
                            bill_dept=bill_dept,
                            cpu=cpu, memory=memoryGB, usage=usage,
                            high_io=high_io,
                            description=description, folder=folder,
                            networks=networks, disks=disks)
        if name:
            json_payload['name'] = name
        if notes:
            json_payload['notes'] = notes
        if iso:
            self.get_isos(path=iso)
            json_payload['iso'] = iso
        json_payload.update(kwargs)
        json = self.request_v2('/vm', payload=json_payload, method='POST')
        return json.get('data')

    def create_vms(self, count, name, os, built, bill_dept,
                   description, folder, networks, disks, iso=None,
                   notes=None, usage='Test', cpu=1, memoryGB=1,
                   high_io=False, **kwargs):
        """
        Creates multiple Virtual Machines. Names are generated
        by appending name_number

        :param count: number of virtual machines to deploy
        :type count: int
        :param name: name of the new virtual machines
        :type name: str
        :param os: Operating system id.
        :type os: str
        :param built: built process
        :param bill_dept: Billing department
        :type bill_dept: str
        :param description: Brief description of what the virtual
          machine will host.
        :type description: str
        :param folder: Target folder moref. This is the logical folder
         storing the new virtual machine.
        :type folder: str
        :param networks: list of networks moref. Network adapters are
         created based on the network index, then first item in the list
         is mapped to network adapter 1.
        :type networks: list
        :param disks: list of disk sizes in GB. Same as networks, each
         disk item is mapped to a hard disk drive of a given size.
        :type disks: list
        :param iso: ISO image path to be mounted after creation
        :type iso: str
        :param notes: Custom Notes in key value format to
         store in the Virtual Machine annotation as meta-data.
        :type notes: dict
        :param usage: virtual machine usage
        :type usage: str
        :param cpu: vCPU count. Defaults to 1vCPU
        :type cpu: int
        :param memoryGB: Memory size in GB. Defaults to 1GB
        :type memoryGB: int
        :param high_io: If set to true,VM will be created
         with a VMware Paravirtual SCSIController. Defaults to False.
        :type high_io: bool
        :return: new request objects

        .. seealso:: :py:func:`get_os` for os parameter,
          :py:func:`get_images` for image, :py:func:`get_folder` for folder,
          :py:func:`get_networks` for networks, :py:func:`get_isos` for isos

        .. note:: more information about required attributes
          available in `Virtual Machine <https://wiki.eis.utoronto.ca/x/pgCC>`_

        """
        # validate basic items
        usage = self.validate_usage(usage)
        built_from = self.validate_build_process(built)
        disks = disks if disks else [40]
        assert self.get_folder(folder), 'Invalid folder moref'
        assert [self.get_network(net) for net in networks],\
            'Invalid networks found'
        names = ['%s_%s' % (name, i) for i in range(0, count)]
        # generating payload
        json_payload = dict(os=os, built_from=built_from, bill_dept=bill_dept,
                            cpu=cpu, memory=memoryGB, usage=usage,
                            high_io=high_io,
                            description=description, folder=folder,
                            names=names, disks=disks, networks=networks)
        if notes:
            json_payload['notes'] = notes
        if iso:
            self.get_isos(path=iso)
            json_payload['iso'] = iso
        json_payload.update(kwargs)
        json = self.request_v2('/vm', payload=json_payload, method='POST')
        return json.get('data')

    def create_vm_from_image(self, os, image, bill_dept,
                             description, folder, networks, disks,
                             notes=None, usage='Test', name=None,
                             cpu=1, memoryGB=1,
                             high_io=False, **kwargs):
        """
        Creates a new Virtual Machine from OVA or OVF

        :param os: Operating system id.
        :type os: str
        :param image: OVA/OVF filename
        :type image: str
        :param bill_dept: Billing department
        :type bill_dept: str
        :param description: Brief description of what the virtual
          machine will host.
        :type description: str
        :param folder: Target folder moref. This is the logical folder
         storing the new virtual machine.
        :type folder: str
        :param networks: list of networks moref. Network adapters are
         created based on the network index, then first item in the list
         is mapped to network adapter 1.
        :type networks: list
        :param disks: list of disk sizes in GB. Same as networks, each
         disk item is mapped to a hard disk drive of a given size.
        :type disks: list
        :param notes: Custom Notes in key value format to
         store in the Virtual Machine annotation as meta-data.
        :type notes: dict
        :param usage: virtual machine usage. Defaults to Test
        :type usage: str
        :param name: Virtual Machine name. If not set, will be generated
         dynamically by the API
        :type name: str
        :param cpu: vCPU count. Defaults to 1vCPU
        :type cpu: int
        :param memoryGB: Memory size in GB. Defaults to 1GB
        :type memoryGB: int
        :param high_io: If set to true,VM will be created
         with a VMware Paravirtual SCSIController. Defaults to False.
        :type high_io: bool
        :return: new request object

        .. seealso:: :py:func:`get_os` for os parameter,
          :py:func:`get_images` for image, :py:func:`get_folder` for folder,
          :py:func:`get_networks` for networks.

        .. note:: more information about required attributes
          available in `Virtual Machine <https://wiki.eis.utoronto.ca/x/pgCC>`_

        """
        # validate basic items
        usage = self.validate_usage(usage)
        disks = disks if disks else [40]
        assert self.get_folder(folder), 'Invalid folder moref'
        assert [self.get_network(net) for net in networks],\
            'Invalid networks found'
        # generate payload
        json_payload = dict(os=os, cpu=cpu, memory=memoryGB,
                            built_from='image', bill_dept=bill_dept,
                            description=description, folder=folder,
                            high_io=high_io,
                            networks=networks, disks=disks,
                            source_image=image, usage=usage)
        if name:
            json_payload['name'] = name
        if notes:
            json_payload['notes'] = notes
        json_payload.update(kwargs)
        json = self.request_v2('/vm', payload=json_payload,
                               method='POST')
        return json.get('data')

    def create_vm_from_clone(self, source_vm, description, name=None,
                             os=None, bill_dept=None,
                             folder=None, networks=None,
                             disks=None, notes=None, usage=None,
                             cpu=None, memoryGB=None, high_io=None,
                             custom_spec=None,
                             **kwargs):
        """
        Deploy virtual machine by cloning from any given source

        :param source_vm: Source virtual machine uuid
        :type source_vm: str
        :param description: Brief description of what the virtual
          machine will host
        :type description: str
        :param name: Virtual machine name. If not specified, will
         create a new name based on source
        :type name: str
        :param os: Operating system id. If not specified, will be
         same as source.
        :type os: str
        :param bill_dept: Billing department. If not specified, will be
         same as source.
        :type bill_dept: str
        :param folder: Target folder moref. This is the logical folder
         storing the new virtual machine. If not specified, will be
         same as source.
        :type folder: str
        :param networks: list of networks moref. Network adapters are
         created based on the network index, then first item in the list
         is mapped to network adapter 1. If not specified, will be
         same as source.
        :type networks: list
        :param disks: list of disk sizes in GB. Same as networks, each
         disk item is mapped to a hard disk drive of a given size.
         If not specified, will be same as source.
         :type disks: list
        :param notes: Custom Notes in key value format to
         store in the Virtual Machine annotation as meta-data.
        :type notes: dict
        :param usage: virtual machine usage. If not specified,
         will be same as source.
        :type usage: str
        :param cpu: vCPU count. If not specified, will be same as source.
        :type cpu: int
        :param memoryGB: Memory size in GB. If not specified,
         will be same as source.
        :type memoryGB: int
        :param high_io: If set to true,VM will be created
         with a VMware Paravirtual SCSIController. If not specified,
         will be same as source.
        :type high_io: bool
        :param custom_spec: OS customization specification. Required if
         the resulting virtual machine needs to be reconfigure upon first
         boot. The current version of VMware Tools must be installed on
         the virtual machine or template to customize
         the guest operating system during cloning or deployment.
        :type custom_spec: dict
        :param kwargs:
        :return: new request object

        .. seealso:: :py:func:`get_os` for os parameter,
          :py:func:`get_images` for image, :py:func:`get_folder` for folder,
          :py:func:`get_networks` for networks, :py:func:`get_custom_spec` for
          customization specification.

        .. note:: more information about required attributes
          available in `Virtual Machine <https://wiki.eis.utoronto.ca/x/pgCC>`_

        """
        # get source virtual machine specification
        source_vm_spec = self.get_vm_spec(source_vm)
        # new vm specification
        new_vm_spec = dict(description=description, built_from='clone',
                           source_vm=source_vm)
        new_vm_spec['name'] = name if name \
            else '{}-Clone'.format(source_vm_spec['name'])
        # set valid and not none params in new spec
        new_vm_spec['os'] = os if os else source_vm_spec['os']
        new_vm_spec['disks'] = disks if disks \
            else source_vm_spec['disks']
        new_vm_spec['cpu'] = cpu if cpu \
            else source_vm_spec['cpu']
        new_vm_spec['memory'] = memoryGB if memoryGB \
            else source_vm_spec['memory']
        new_vm_spec['usage'] = self.validate_usage(usage) \
            if usage else source_vm_spec['usage']
        new_vm_spec['high_io'] = high_io if high_io else False
        # bill dept
        if bill_dept:
            new_vm_spec['bill_dept'] = bill_dept
        # folder
        if folder:
            self.get_folder(folder)
            new_vm_spec['folder'] = folder
        # network adapters
        if networks:
            assert [self.get_network(net) for net in networks], \
                'Invalid networks found'
            new_vm_spec['networks'] = networks
        # client notes
        if notes:
            new_vm_spec['notes'] = notes
        if custom_spec:
            new_vm_spec['custom_spec'] = custom_spec
        # creating payload
        json_payload = source_vm_spec
        # overriding source spec with new vm spec
        json_payload.update(new_vm_spec)
        # update any additional k-v args
        json_payload.update(kwargs)
        json = self.request_v2('/vm', payload=json_payload, method='POST')
        return json.get('data')

    def deploy_vm_from_template(self, source_template, description, name=None,
                                os=None, bill_dept=None,
                                folder=None, networks=None,
                                disks=None, notes=None, usage=None,
                                cpu=None, memoryGB=None, high_io=None,
                                custom_spec=None,
                                **kwargs):
        """
        Deploy single virtual machine from template.

        Recommended approach for multiple virtual machine deployment
        from template with independent specification, including
        `custom_spec` configuration.

        :param source_template: Source virtual machine template
        :param description: Brief description of what the virtual
          machine will host
        :type description: str
        :param name: Virtual machine name. If not specified, will
         create new virtual machine based on source template name
         appending the -clone suffix.
        :type name: str
        :param os: Operating system id. If not specified, will be
         same as source.
        :type os: str
        :param bill_dept: Billing department. If not specified, will be
         same as source.
        :type bill_dept: str
        :param folder: Target folder moref. This is the logical folder
         storing the new virtual machine. If not specified, will be
         same as source.
        :type folder: str
        :param networks: list of networks moref. Network adapters are
         created based on the network index, then first item in the list
         is mapped to network adapter 1. If not specified, will be
         same as source.
        :type networks: list
        :param disks: list of disk sizes in GB. Same as networks, each
         disk item is mapped to a hard disk drive of a given size.
         If not specified, will be same as source.
         :type disks: list
        :param notes: Custom Notes in key value format to
         store in the Virtual Machine annotation as meta-data.
        :type notes: dict
        :param usage: virtual machine usage. If not specified,
         will be same as source.
        :type usage: str
        :param cpu: vCPU count. If not specified, will be same as source.
        :type cpu: int
        :param memoryGB: Memory size in GB. If not specified,
         will be same as source.
        :type memoryGB: int
        :param high_io: If set to true,VM will be created
         with a VMware Paravirtual SCSIController. If not specified,
         will be same as source.
        :type high_io: bool
        :param custom_spec: OS customization specification. Required if
         the resulting virtual machine needs to be reconfigure upon first
         boot. The current version of VMware Tools must be installed on
         the virtual machine or template to customize
         the guest operating system during cloning or deployment.
        :type custom_spec: dict
        :param kwargs:
        :return: new request object

        .. seealso:: :py:func:`get_templates` for virtual machine templates
          :py:func:`get_os` for os parameter,
          :py:func:`get_images` for image, :py:func:`get_folder` for folder,
          :py:func:`get_networks` for networks, :py:func:`get_custom_spec` for
          customization specification.

        .. note:: more information about required attributes
          available in `Virtual Machine <https://wiki.eis.utoronto.ca/x/pgCC>`_

        """
        assert self.is_vm_template(source_template).get('isTemplate'),\
            'Source is not a template'
        # get source virtual machine specification
        source_template_spec = self.get_vm_spec(source_template)
        new_vm_spec = dict(description=description, built_from='template',
                           source_template=source_template)
        # set valid and not none params in new spec
        new_vm_spec['name'] = name if name \
            else '{}-clone'.format(source_template_spec['name'])
        new_vm_spec['os'] = os if os else source_template_spec['os']
        new_vm_spec['disks'] = disks if disks \
            else source_template_spec['disks']
        new_vm_spec['cpu'] = cpu if cpu else \
            source_template_spec['cpu']
        new_vm_spec['memory'] = memoryGB if memoryGB else \
            source_template_spec['memory']
        new_vm_spec['usage'] = self.validate_usage(usage) \
            if usage else source_template_spec['usage']
        new_vm_spec['high_io'] = high_io if high_io else False
        # bill dept
        if bill_dept:
            new_vm_spec['bill_dept'] = bill_dept
        # folder
        if folder:
            self.get_folder(folder)
            new_vm_spec['folder'] = folder
        # network adapters
        if networks:
            assert [self.get_network(net) for net in networks], \
                'Invalid networks found'
            new_vm_spec['networks'] = networks
        # client notes
        if notes:
            new_vm_spec['notes'] = notes
        if custom_spec:
            new_vm_spec['custom_spec'] = custom_spec
        # creating payload
        json_payload = source_template_spec
        # overriding source spec with new vm spec
        json_payload.update(new_vm_spec)
        # update any additional k-v args
        json_payload.update(kwargs)
        json = self.request_v2('/vm', payload=json_payload, method='POST')
        return json.get('data')

    def deploy_vms_from_template(self, source_template, description, count=1,
                                 name=None, os=None, bill_dept=None,
                                 folder=None, networks=None,
                                 disks=None, notes=None, usage=None,
                                 cpu=None, memoryGB=None, high_io=None,
                                 custom_spec=None,
                                 **kwargs):
        """
        Deploy multiple or a single virtual machine from template.

        Useful when you need to deploy multiple virtual machine instances
        from a single source. Not recommended when using `custom_spec` for
        guest OS customization specification.

        Use :py:func:`deploy_vm_from_template` in a loop for deploying multiple
        virtual machines with different `custom_spec`.

        :param source_template: Source virtual machine template
        :param description: Brief description of what the virtual
          machine will host
        :type description: str
        :param count: Number or virtual machines to deploy. Defaults
         to 1.
        :param name: Virtual machine name. If not specified, will
         create all new virtual machines based on source template name
         appending the number of item.
        :type name: str
        :param os: Operating system id. If not specified, will be
         same as source.
        :type os: str
        :param bill_dept: Billing department. If not specified, will be
         same as source.
        :type bill_dept: str
        :param folder: Target folder moref. This is the logical folder
         storing the new virtual machine. If not specified, will be
         same as source.
        :type folder: str
        :param networks: list of networks moref. Network adapters are
         created based on the network index, then first item in the list
         is mapped to network adapter 1. If not specified, will be
         same as source.
        :type networks: list
        :param disks: list of disk sizes in GB. Same as networks, each
         disk item is mapped to a hard disk drive of a given size.
         If not specified, will be same as source.
         :type disks: list
        :param notes: Custom Notes in key value format to
         store in the Virtual Machine annotation as meta-data.
        :type notes: dict
        :param usage: virtual machine usage. If not specified,
         will be same as source.
        :type usage: str
        :param cpu: vCPU count. If not specified, will be same as source.
        :type cpu: int
        :param memoryGB: Memory size in GB. If not specified,
         will be same as source.
        :type memoryGB: int
        :param high_io: If set to true,VM will be created
         with a VMware Paravirtual SCSIController. If not specified,
         will be same as source.
        :type high_io: bool
        :param custom_spec: OS customization specification. Required if
         the resulting virtual machine needs to be reconfigure upon first
         boot. The current version of VMware Tools must be installed on
         the virtual machine or template to customize
         the guest operating system during cloning or deployment.
        :type custom_spec: dict
        :param kwargs:
        :return: new request object

        .. seealso:: :py:func:`get_templates` for virtual machine templates
          :py:func:`get_os` for os parameter,
          :py:func:`get_images` for image, :py:func:`get_folder` for folder,
          :py:func:`get_networks` for networks, :py:func:`get_custom_spec` for
          customization specification.

        .. note:: more information about required attributes
          available in `Virtual Machine <https://wiki.eis.utoronto.ca/x/pgCC>`_

        """
        assert self.is_vm_template(source_template).get('isTemplate'),\
            'Source is not a template'
        # get source virtual machine specification
        source_template_spec = self.get_vm_spec(source_template)
        if name:
            names = ['%s_%s' % (name, i) for i in range(1, count+1)] \
                if count > 1 else [name]
        else:
            names = ['%s_%s' % (source_template_spec['name'], i)
                     for i in range(1, count+1)]

        new_vms_spec = dict(description=description, built_from='template',
                            names=names, source_template=source_template)
        # set valid and not none params in new spec
        new_vms_spec['os'] = os if os else source_template_spec['os']
        new_vms_spec['disks'] = disks if disks \
            else source_template_spec['disks']
        new_vms_spec['cpu'] = cpu if cpu else \
            source_template_spec['cpu']
        new_vms_spec['memory'] = memoryGB if memoryGB else \
            source_template_spec['memory']
        new_vms_spec['usage'] = self.validate_usage(usage) \
            if usage else source_template_spec['usage']
        new_vms_spec['high_io'] = high_io if high_io else False
        # bill dept
        if bill_dept:
            new_vms_spec['bill_dept'] = bill_dept
        # folder
        if folder:
            self.get_folder(folder)
            new_vms_spec['folder'] = folder
        # network adapters
        if networks:
            assert [self.get_network(net) for net in networks], \
                'Invalid networks found'
            new_vms_spec['networks'] = networks
        # client notes
        if notes:
            new_vms_spec['notes'] = notes
        if custom_spec:
            new_vms_spec['custom_spec'] = custom_spec
        # creating payload
        json_payload = source_template_spec
        # overriding source spec with new vm spec
        json_payload.update(new_vms_spec)
        # update any additional k-v args
        json_payload.update(kwargs)
        json = self.request_v2('/vm', payload=json_payload, method='POST')
        return json.get('data')

    def create_vm_custom_spec(self, uuid, custom_spec, **kwargs):
        """
        Create a custom specification for a given virtual machine.

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :param custom_spec: OS customization specification. Required if
         the resulting virtual machine needs to be reconfigure upon first
         boot. The current version of VMware Tools must be installed on
         the virtual machine or template to customize
         the guest operating system during cloning or deployment.
        :type custom_spec: dict
        :param kwargs:
        :return:

        .. note:: Virtual machine must be powered on and VMware Tools must
          be installed.

        .. seealso:: :py:func:`get_custom_spec` for
          customization specification.

        """
        json = self.request_v2('/vm/{uuid}/custom_spec'.format(uuid=uuid),
                               method='POST', payload=custom_spec)
        return json.get('data')

    def get_vm_console(self, uuid):
        """
        Produces a one-time URL to Virtual Machine
        console. Virtual machine needs to be powered on
        and user must have a valid vCenter session
        (limitation in the vSphere SOAP API).

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :return: object
        """
        json = self.request_v2('/vm/{uuid}/console'.format(uuid=uuid))
        return json.get('data')

    def is_vm_template(self, uuid):
        """
        Checks if Virtual Machine is marked as template

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :return: bool
        """
        json = self.request_v2('/vm/{uuid}/template'.format(uuid=uuid))
        return json.get('data')

    def mark_vm_as_template(self, uuid, **kwargs):
        """
        Marks Virtual Machine as template to freeze changes.
        Templates cannot be modified nor powered on unless marked
        as Virtual Machine.

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time
        """
        json_payload = dict(value=True)
        json_payload.update(kwargs)
        json = self.request_v2('/vm/{uuid}/template'.format(uuid=uuid),
                               payload=json_payload, method='PUT')
        return json.get('data')

    def mark_template_as_vm(self, uuid, **kwargs):
        """
        Marks Template as Virtual Machine.

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time
        """
        json_payload = dict(value=False)
        json_payload.update(kwargs)
        json = self.request_v2('/vm/{uuid}/template'.format(uuid=uuid),
                               payload=json_payload, method='PUT')
        return json.get('data')

    def get_vm_memory(self, uuid):
        """
        Gets Virtual Machine memory information such as:

        - memoryGB
        - hotAdd
        - quickStats:

          - ballooned
          - compressed
          - consumedOverhead,
          - private
          - shared
          - swapped

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :return: object

        """
        json = self.request_v2('/vm/' + uuid + '/memory')
        return json.get('data')

    def set_vm_memory(self, uuid, sizeGB, **kwargs):
        """
        Updates Virtual Machine Memory size

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :param sizeGB: New memory size in GB
        :type sizeGB: int
        :return: change request object

        .. note:: keyword arguments include schedule to process request
         on a given date and time

        """
        payload = dict(value=int(sizeGB))
        payload.update(kwargs)
        json = self.request_v2('/vm/{uuid}/memory'.format(uuid=uuid),
                               payload=payload,
                               method='PUT')
        return json.get('data')

    def get_vm_cpu(self, uuid):
        """
        Get VM cpu information such as:

        - coresPerSocket
        - cpu
        - hotAdd
        - hotRemove
        - quickStats

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :return: change request object
        """
        json = self.request_v2('/vm/{uuid}/cpu'.format(uuid=uuid))
        return json.get('data')

    def set_vm_cpu(self, uuid, number, **kwargs):
        """
        Updates Virtual Machine CPU count

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :param number: New vCPU count
        :type number: int
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        """
        payload = dict(value=number)
        payload.update(kwargs)
        json = self.request_v2('/vm/{uuid}/cpu'.format(uuid=uuid),
                               payload=payload,
                               method='PUT')
        return json.get('data')

    # Virtual Machine devices
    def get_vm_nics(self, uuid):
        """
        Gets Virtual Machine NICs information.

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :return: list of objects
        """
        json = self.request_v2('/vm/{uuid}/nic'.format(uuid=uuid))
        nic_numbers = [nic.get('unit') for nic in json.get('data')]
        nics = list()
        for nic in nic_numbers:
            json = self.request_v2('/vm/{uuid}/nic/{nic}'.format(uuid=uuid,
                                                                 nic=nic))
            nics.append({'unit': nic,
                         'data': json['data'][0]})
        return nics

    def get_vm_nic(self, uuid, nic):
        """
        Gets Virtual Machine NIC information such as:

        - connected
        - label
        - macAddress
        - network
        - startConnected
        - type

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :param nic: nic number
        :type nic: int
        :return:
        """
        json = self.request_v2('/vm/{uuid}/nic/{nic}'.format(uuid=uuid,
                                                             nic=nic))
        return json.get('data')

    def create_vm_nic(self, uuid, network, **kwargs):
        """
        Creates Virtual Machine NIC

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :param network: Network moref to attach
        :type network: str
        :return: change request object

        """
        json_payload = dict(value=network)
        json_payload.update(kwargs)
        json = self.request_v2('/vm/{uuid}/nic'.format(uuid=uuid),
                               method='POST', payload=json_payload)
        return json.get('data')

    def delete_vm_nic(self, uuid, nic, **kwargs):
        """
        Deletes Virtual Machine NIC unit

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :param nic: Network interface card number
        :type nic: int
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        """
        json_payload = dict(attribute='state',
                            value='delete')
        json_payload.update(kwargs)
        json = self.request_v2('/vm/{uuid}/nic/{number}'.format(uuid=uuid,
                                                                number=nic),
                               method='DELETE', payload=json_payload)
        return json.get('data')

    def update_vm_nic_network(self, uuid, nic, network, **kwargs):
        """
        Updates Virtual Machine network on a given nic

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :param nic: Network interface card number
        :type nic: int
        :param network: new network moref
        :type network: str
        :return: change request object

        .. note:: keywords arguments include schedule to process request
          on a given date and time

        """
        json_payload = dict(attribute='network',
                            value=network)
        json_payload.update(kwargs)
        json = self.request_v2('/vm/{uuid}/nic/{number}'.format(uuid=uuid,
                                                                number=nic),
                               method='PUT', payload=json_payload)
        return json.get('data')

    def update_vm_nic_type(self, uuid, nic, type, **kwargs):
        """
        Updates Virtual Machine NIC type

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :param nic: Network interface card number
        :type nic: int
        :param type: new nic type (E1000e, E1000, VMXNET3, VMXNET2)
        :type type: str
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        """
        if type not in ['VMXNET2', 'VMXNET3', 'E1000', 'E1000e']:
            raise VssError('Unsupported NIC type')

        json_payload = dict(attribute='type',
                            value=type)
        json_payload.update(kwargs)
        json = self.request_v2('/vm/{uuid}/nic/{number}'.format(uuid=uuid,
                                                                number=nic),
                               method='PUT', payload=json_payload)
        return json.get('data')

    def update_vm_nic_state(self, uuid, nic, state, **kwargs):
        """
        Updates Virtual Machine NIC state

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :param nic: Network interface card number
        :type nic: int
        :param state: new nic state (connect, disconnect)
        :type state: str
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        """
        if state not in ['connect', 'disconnect']:
            raise VssError('Unsupported NIC state')

        json_payload = dict(attribute='state',
                            value=state)
        json_payload.update(kwargs)
        json = self.request_v2('/vm/{uuid}/nic/{number}'.format(uuid=uuid,
                                                                number=nic),
                               method='PUT', payload=json_payload)
        return json.get('data')

    def get_vm_floppies(self, uuid):
        """
        Returns Virtual Machine Floppy devices
        available.

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :return: list of objects
        """
        json = self.request_v2('/vm/{uuid}/floppy'.format(uuid=uuid))
        floppy_units = [fl.get('unit') for fl in json.get('data')]
        floppies = list()
        for fl in floppy_units:
            data = self.get_vm_floppy(uuid, fl)
            floppies.append({'unit': data,
                             'data': data[0]})
        return floppies

    def get_vm_floppy(self, uuid, floppy):
        """
        Returns Virtual Machine floppy unit
        information such as:

        - backing
        - connected
        - controller
        - description
        - label

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :param floppy: floppy unit number
        :type floppy: int
        :return: object
        """
        json = self.request_v2('/vm/{uuid}/floppy/{floppy}'.format(
            uuid=uuid, floppy=floppy))
        return json.get('data')

    def update_vm_floppy(self, uuid, floppy, image=None, **kwargs):
        """
        Updates given Floppy unit backing to client or image.

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :param floppy: floppy unit
        :type floppy: int
        :param image: full path to ISO
        :type image: str
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        """
        valid = self.get_floppies(path=image) if image else 'client'
        json_payload = dict(attribute='img', value=image) \
            if image else dict(attribute='client', value='')
        json_payload.update(kwargs)
        json = self.request_v2('/vm/{uuid}/floppy/{floppy}'.format(
            uuid=uuid, floppy=floppy),
            method='PUT', payload=json_payload)
        return json.get('data')

    def get_vm_cds(self, uuid):
        """
        Returns Virtual Machine CD/DVD devices
        available.

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :return: list of objects
        """
        json = self.request_v2('/vm/{uuid}/cd'.format(uuid=uuid))
        cd_units = [cd.get('unit') for cd in json.get('data')]
        cds = list()
        for cd in cd_units:
            data = self.get_vm_cd(uuid, cd)
            cds.append({'unit': cd,
                        'data': data[0]})
        return cds

    def get_vm_cd(self, uuid, cd):
        """
        Returns Virtual Machine CD/DVD unit
        information such as:

        - backing
        - connected
        - controller
        - description
        - label

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :param cd: CD/DVD unit number
        :type cd: int
        :return: object

        """
        json = self.request_v2('/vm/{uuid}/cd/{cd}'.format(uuid=uuid,
                                                           cd=cd))
        return json.get('data')

    def update_vm_cd(self, uuid, cd, iso=None, **kwargs):
        """
        Updates given CD unit backing to client or ISO.

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :param cd: CD/DVD unit
        :type cd: int
        :param iso: full path to ISO
        :type iso: str
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        """
        valid = self.get_isos(path=iso) if iso else 'client'
        json_payload = dict(attribute='iso', value=iso) \
            if iso else dict(attribute='client', value='')
        json_payload.update(kwargs)
        json = self.request_v2('/vm/{uuid}/cd/{cd}'.format(uuid=uuid,
                                                           cd=cd),
                               method='PUT', payload=json_payload)
        return json.get('data')

    def get_vm_disks(self, uuid):
        """
        Returns Virtual Machine available disks

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :return: list of objects

        """
        json = self.request_v2('/vm/{uuid}/disk'.format(uuid=uuid))
        disk_units = [disk.get('unit') for disk in json.get('data')]
        disks = list()
        for disk in disk_units:
            data = self.get_vm_disk(uuid, disk)
            disks.append({'unit': disk,
                          'data': data[0]})
        return disks

    def get_vm_disk(self, uuid, disk):
        """
        Gets Virtual Machine disk data such as:

        - capacity
        - controller
        - description
        - label
        - shares
        - filenName

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :param disk: Virtual Machine disk number
        :type disk: int
        :return: object

        """
        json = self.request_v2('/vm/{uuid}/disk/{disk}'.format(uuid=uuid,
                                                               disk=disk))
        return json.get('data')

    def create_vm_disk(self, uuid, valueGB, **kwargs):
        """
        Create new virtual disk with a given capacity

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :param valueGB: capacity in GB
        :type valueGB: int
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        """
        json_payload = dict(value=valueGB)
        json_payload.update(kwargs)
        json = self.request_v2('/vm/{uuid}/disk'.format(uuid=uuid),
                               method='POST', payload=json_payload)
        return json.get('data')

    def update_vm_disk_capacity(self, uuid, disk, valueGB, **kwargs):
        """
        Updates given Virtual Machine disk capacity

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :param disk: unit to update
        :type disk: int
        :param valueGB: New capacity in GB
        :type valueGB: int
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        """
        json_payload = dict(attribute='capacity', value=valueGB)
        json_payload.update(kwargs)
        json = self.request_v2('/vm/{uuid}/disk/{disk}'.format(uuid=uuid,
                                                               disk=disk),
                               method='PUT', payload=json_payload)
        return json.get('data')

    def delete_vm_disk(self, uuid, disk, **kwargs):
        """
        Deletes given Virtual Machine disk capacity

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :param disk: unit to delete
        :type disk: int
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        """
        json = self.request_v2('/vm/{uuid}/disk/{disk}'.format(uuid=uuid,
                                                               disk=disk),
                               method='DELETE', payload=kwargs)
        return json.get('data')

    def is_powered_on_vm(self, uuid):
        """
        Checks if given Virtual Machine is powered
        On.

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :return: bool
        """
        json = self.request_v2('/vm/{uuid}/state'.format(uuid=uuid))
        power_state = json.get('data').get('powerState')
        if power_state:
            return power_state == 'poweredOn'
        else:
            return False

    def reboot_vm(self, uuid, **kwargs):
        """
        Graceful reboot VM. This method sends a reboot signal
        via VMware Tools to the Guest Operating system,
        thus VMware Tools is required up-to-date
        and running on VM.

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        """
        json = self.update_vm_state(uuid=uuid, state='reboot', **kwargs)
        return json.get('data')

    def reset_vm(self, uuid, **kwargs):
        """
         Hard reset VM. This method resets a given Virtual Machine.
         This method is equivalent to power_off_vm and power_on_vm

         :param uuid: Virtual Machine Uuid
         :type uuid: str
         :return: change request object

         .. note:: keyword arguments include schedule to process request
           on a given date and time

         """
        json = self.update_vm_state(uuid=uuid, state='reset', **kwargs)
        return json

    def power_off_vm(self, uuid, **kwargs):
        """
        Power Off VM. This method powers Off given virtual
        machine.

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        """
        json = self.update_vm_state(uuid=uuid, state='poweredOff', **kwargs)
        return json

    def power_on_vm(self, uuid, **kwargs):
        """
        Power On VM. This method powers on given virtual
        machine.

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        """
        json = self.update_vm_state(uuid=uuid, state='poweredOn', **kwargs)
        return json

    def shutdown_vm(self, uuid, **kwargs):
        """
        Graceful shutdown VM. This method sends a shutdown signal
        via VMware Tools to the Guest Operating system,
        thus VMware Tools is required up-to-date
        and running on VM.

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        """
        json = self.update_vm_state(uuid=uuid, state='shutdown', **kwargs)
        return json

    def rename_vm(self, uuid, name, **kwargs):
        """
        Update Virtual Machine name. This do not change
        the VSS prefix ``YYMM{P|Q|D|T}-VMName``.

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :param name: New virtual machine name. Do not
         include VSS prefix.
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        """
        json_payload = dict(value=name)
        json_payload.update(kwargs)
        json = self.request_v2('/vm/{uuid}/name'.format(uuid=uuid),
                               method='PUT',
                               payload=json_payload)

        return json.get('data')

    # Virtual Machine Notes
    def get_vm_notes(self, uuid):
        """
        Get Virtual Machine client notes.
        Metadata available for users to manage.

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :return: list of key value notes
        """
        json = self.request_v2('/vm/{uuid}/note/client'.format(uuid=uuid))
        return json.get('data')

    def update_vm_notes(self, uuid, notes, **kwargs):
        """
        Update Virtual Machine client notes. Notes are
        stored as key-value metadata items.

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :param notes: New client custom notes
        :type notes: str
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        """
        json_payload = dict(value=notes)
        json_payload.update(kwargs)
        json = self.request_v2('/vm/{uuid}/note/client'.format(uuid=uuid),
                               method='PUT', payload=json_payload)
        return json.get('data')

    # Virtual Machine VSS attributes
    def get_vm_vss_description(self, uuid):
        """
        Get Virtual Machine description
        This is part of the VSS metadata added to the
        VM annotation.

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :return: dict with description
        """
        json = self.request_v2('/vm/{uuid}/vss/description'.format(
            uuid=uuid))
        return json.get('data')

    def update_vm_vss_description(self, uuid, description, **kwargs):
        """
        Update Virtual Machine description

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :param description: New virtual machine description.
        :type description: str
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time
        """
        json_payload = dict(value=description)
        json_payload.update(kwargs)
        json = self.request_v2('/vm/{uuid}/vss/description'.format(uuid=uuid),
                               method='PUT',
                               payload=json_payload)
        return json.get('data')

    def get_vm_vss_admin(self, uuid):
        """
        Get Virtual Machine administrator
        This is part of the VSS metadata added to the
        VM annotation.

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :return: dict with phone, name and email of
         vm admin

        """
        json = self.request_v2('/vm/{uuid}/vss/admin'.format(uuid=uuid))
        return json.get('data')

    def update_vm_vss_admin(self, uuid, name, phone, email, **kwargs):
        """
        Update Virtual Machine administrator contact
        info.

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :param name: Full name of VM admin
        :type name: str
        :param phone: Valid phone number of VM admin
        :type phone: str
        :param email: Valid email address of VM admin
        :type email: str
        :return: change request object

        .. note:: keyword arguments include schedule to process request
          on a given date and time
        """
        json_payload = dict(value=':'.join([name, phone, email]))
        json_payload.update(kwargs)
        json = self.request_v2('/vm/{uuid}/vss/admin'.format(uuid=uuid),
                               method='PUT',
                               payload=json_payload)
        return json.get('data')

    def get_vm_vss_ha_group(self, uuid):
        """
        Get Virtual Machine High Availability Group.
        This is part of the VSS metadata added to the
        VM annotation.

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :return: object

        """
        json = self.request_v2('/vm/{uuid}/vss/ha_group'.format(uuid=uuid))
        return json.get('data')

    def update_vm_vss_ha_group(self, uuid, vms, append=True, **kwargs):
        """
        Updates High Availability Group
        This is part of the VSS metadata added to the
        VM annotation

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :param vms: list of virtual machine Uuids
        :type vms: list
        :param append: whether to replace or append
        :type append: bool
        :return: object

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        """
        json_payload = dict(value=','.join(vms), append=append)
        json_payload.update(kwargs)
        json = self.request_v2('/vm/{uuid}/vss/ha_group'.format(uuid=uuid),
                               method='PUT', payload=json_payload)
        return json.get('data')

    def get_vm_vss_usage(self, uuid):
        """
        Get Virtual Machine Usage.
        This is part of the VSS metadata added to the
        VM annotation.

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :return: dict

        """
        json = self.request_v2('/vm/{uuid}/vss/usage'.format(uuid=uuid))
        return json.get('data')

    def get_vm_vss_client(self, uuid):
        """
        Get Virtual Machine Client.
        This is part of the VSS metadata added to the
        VM annotation.

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :return: dict

        """
        json = self.request_v2('/vm/{uuid}/vss/client'.format(uuid=uuid))
        return json.get('data')

    def update_vm_vss_client(self, uuid, client, **kwargs):
        """
        Update virtual machine client metadata.

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :param client: New VSS client
        :type client: str
        :return: change request

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        """
        json_payload = dict(value=client)
        json_payload.update(kwargs)
        json = self.request_v2('/vm/{uuid}/vss/client'.format(uuid=uuid),
                               payload=json_payload,
                               method='PUT')
        return json.get('data')

    def get_vm_vss_changelog(self, uuid):
        """
        Get Virtual Machine change log. Maximum change
        log entries are 9.
        This is part of the VSS metadata added to the
        VM annotation.

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :return: list of changelog entries as dict

        """
        json = self.request_v2('/vm/{uuid}/vss/changelog'.format(uuid=uuid))
        return json.get('data')

    def update_vm_vss_usage(self, uuid, usage, **kwargs):
        """
        Update virtual machine VSS usage or environment

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :param usage: New usage (Prod, Dev, Test or QA)
        :type usage: str
        :return: change request

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        """
        json_payload = dict(value=usage)
        json_payload.update(kwargs)
        json = self.request_v2('/vm/{uuid}/vss/usage'.format(uuid=uuid),
                               payload=json_payload,
                               method='PUT')
        return json.get('data')

    def get_vm_vss_inform(self, uuid):
        """
        Get Virtual Machine informational contacts.
        This is part of the VSS metadata added to the
        VM annotation

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :return: list of email addresses if any

        """
        json = self.request_v2('/vm/{uuid}/vss/inform'.format(uuid=uuid))
        return json.get('data')

    def update_vm_vss_inform(self, uuid, emails, append=True, **kwargs):
        """
        Updates informational contacts
        This is part of the VSS metadata added to the
        VM annotation

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :param emails: list of email(s)
        :type emails: list
        :param append: whether to replace or append
        :type append: bool
        :return: object

        .. note:: keyword arguments include schedule to process request
          on a given date and time

        """
        json_payload = dict(value=','.join(emails), append=append)
        json_payload.update(kwargs)
        json = self.request_v2('/vm/{uuid}/vss/inform'.format(uuid=uuid),
                               method='PUT', payload=json_payload)
        return json.get('data')

    def get_vm_vss_requested(self, uuid):
        """
        Get Virtual Machine requested timestamp

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :return: timestamp in str or none if unknown

        """
        json = self.request_v2('/vm/{uuid}/vss'.format(uuid=uuid))
        return json.get('data').get('requested')

    # Virtual Machine summary
    def get_vm_storage(self, uuid):
        """
        Get Virtual Machine storage summary

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :return: dict with:

        - uncommittedGB
        - provisionedGB
        - committedGB
        - unsharedGB

        """
        json = self.get_vm(uuid)
        return json.get('storage')

    def get_vm_extra_config(self, uuid):
        """
        Gets custom VM extra configuration

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :return: list of key value objects
        """
        json = self.request_v2('/vm/{uuid}/extra'.format(uuid=uuid))
        return json.get('data')

    def get_vm_permission(self, uuid):
        """
        Gets VM permission list

        :param uuid: Virtual Machine Uuid
        :type uuid: str
        :return: list of key value objects
        """
        json = self.request_v2('/vm/{uuid}/perm'.format(uuid=uuid))
        return json.get('data')

    def get_network_permission(self, moref):
        """
        Gets Network permission list

        :param moref: Network managed object reference
        :type moref: str
        :return: list of key value objects
        """
        json = self.request_v2('/network/{moref}/perm'.format(moref=moref))
        return json.get('data')

    def get_folder_permission(self, moref):
        """
        Gets Folder permission list

        :param moref: Folder managed object reference
        :type moref: str
        :return: list of key value objects
        """
        json = self.request_v2('/folder/{moref}/perm'.format(moref=moref))
        return json.get('data')

    def request_v2(self, url, headers=None, params=None, payload=None,
                   method='GET', auth=None, timeout=60):
        # update _headers
        _headers = {'Content-Type': self.content_type,
                    'User-Agent': self.user_agent}
        if headers:
            _headers.update(headers)
        # basic auth or authorization header
        if not auth and self.api_token:
            _headers['Authorization'] = 'Bearer {tk}'.format(tk=self.api_token)
        # endpoint validation
        if not url.startswith('http'):
            url = self.api_endpoint + url
        try:
            if method == 'POST':
                resp = requests.post(url, headers=_headers,
                                     timeout=timeout, auth=auth, json=payload)
                json = self.process_response(resp)
            elif method == 'DELETE':
                resp = requests.delete(url, data=json_module.dumps(params),
                                       headers=_headers,
                                       timeout=timeout, auth=auth,
                                       json=payload)
                json = self.process_response(resp)
            elif method == 'PUT':
                resp = requests.put(url, headers=_headers, params=params,
                                    timeout=timeout, auth=auth,
                                    json=payload)
                json = self.process_response(resp)
            elif method == 'GET':
                resp = requests.get(url, headers=_headers, params=params,
                                    timeout=timeout, auth=auth,
                                    json=payload)
                json = self.process_response(resp)
            elif method == 'OPTIONS':
                resp = requests.options(url, headers=_headers, params=params,
                                        timeout=timeout, auth=auth,
                                        json=payload)
                json = self.process_response(resp)
            elif method == 'PATCH':
                resp = requests.patch(url, data=json_module.dumps(params),
                                      headers=_headers,
                                      timeout=timeout, auth=auth,
                                      json=payload)
                json = self.process_response(resp)
            else:
                raise VssError('Unsupported method '
                               '{method}'.format(method=method))

        except ValueError as e:  # requests.models.json.JSONDecodeError
            raise ValueError("The API server did not "
                             "respond with a valid JSON: {}".format(e))
        except requests.RequestException as e:  # errors from requests
            raise RuntimeError(e)

        if resp.status_code not in [requests.codes.ok,
                                    requests.codes.accepted,
                                    requests.codes.no_content]:
            if json:
                if 'error' in json or 'message' in json:
                    msg = ['{}: {}'.format(k, v)
                           for k, v in json.items()]
                    if self.debug:
                        _headers = ['{}: {}'.format(k, v)
                                    for k, v in resp.headers.items()]
                        msg.extend(_headers)
                    msg = '; '.join(msg)
                    raise VssError(msg)
            resp.raise_for_status()
        return json

    def wait_for_request(self, request_url, request_attr,
                         required_status, max_tries=6):
        """
        Waits for request to be in any given status

        :param request_url: Request URL to check periodically
        :type request_url: str
        :param request_attr: Attribute to return upon completion
        :type request_attr: str
        :param required_status: Required request status.
        :type required_status: str
        :param max_tries: Maximum tries to check. Defaults to 6 and
         every try waits for 10 secs
        :type max_tries: int
        :return: False if failed or the type of attribute requested

        """
        tries = 0
        while True:
            request = self.request_v2(request_url)
            if 'data' in request:
                if 'status' in request['data']:
                    status = request['data']['status']
                    if required_status == status:
                        return request['data'][request_attr]
                    elif status in ['Pending', 'In Progress']:
                        pass
                    elif status in ['Error Retry', 'Error Processed']:
                        return False
            else:
                return False
            if tries >= max_tries:
                return False
            tries += 1
            sleep(10)

    def process_response(self, response):
        """
        Processes response codes
        :param response: request.response object
        :return: dict
        """
        _headers = dict(headers=response.headers)
        rv = dict(status=response.status_code)
        # no content status
        if response.status_code == requests.codes.no_content:
            return rv.update(_headers) if self.debug else rv
        # 400s error
        elif 500 < response.status_code > 399:
            _rv = dict(error='user error',
                       message='check request and try again')
            if 'json' in response.headers.get('Content-Type'):
                # json content type
                _r = response.json()
                if 'message' in _r:
                    _rv['message'] = _r['message']
                if 'error' in _r:
                    _rv['error'] = _r['error']
            rv.update(_rv)
        # 500+ server error
        elif response.status_code > 499:
            _rv = dict(error='server error',
                       message='api unavailable')
            if 'json' in response.headers.get('Content-Type'):
                # json content type
                _r = response.json()
                if 'message' in _r:
                    _rv['message'] = _r['message']
                if 'error' in _r:
                    _rv['error'] = _r['error']
            rv.update(_rv)
        else:
            # everything else
            if response.headers.get('Content-Disposition') \
                    and response.headers.get('Content-Type'):
                # validate if response is a file, if so, return
                # response object
                return response
            elif 'json' in response.headers.get('Content-Type'):
                # json content type
                return response.json()
            else:
                _rv = dict(error='server error',
                           message='invalid api response')
                rv.update(_rv)
        # add headers if debug
        if self.debug:
            rv.update(_headers)
        return rv

    @staticmethod
    def validate_usage(usage):
        # validate basic items
        valid_usage = [(u, a) for u, a in VALID_VM_USAGE
                       if usage.lower() in u.lower()]
        if valid_usage:
            usage = valid_usage[0][1]
        else:
            raise VssError('Usage {} not supported'.format(usage))
        return usage

    @staticmethod
    def validate_build_process(built):
        if built not in VALID_VM_BUILD_PROCESS:
            raise VssError('Built process {} not supported'.format(built))
        return built

    @staticmethod
    def get_custom_spec(hostname, domain, interfaces, dns=None):
        """
        Generates a customization specification.

        :param hostname: The network host name of the virtual machine.
        :type hostname: str
        :param domain: A DNS domain suffix such as eis.utoronto.ca.
        :type domain: str
        :param interfaces: A list of interface objects based on
         :py:func:`get_custom_spec_interface`
        :type interfaces: list
        :param dns: A list of server IP addresses to use for DNS lookup
         in a Windows guest operating system.
        :type dns: list
        :return:
        """
        custom_spec = dict(hostname=hostname,
                           domain=domain,
                           interfaces=interfaces)
        has_dhcp = False
        for interface in interfaces:
            if interface.get('dhcp') is True:
                has_dhcp = True
        # validates whether any interface has dhcp and not dns
        # but not dns and not dhcp is invalid
        if not dns and not has_dhcp:
            raise VssError('dns is required')
        # adds dns to the spec
        if dns:
            custom_spec['dns'] = dns
        return custom_spec

    @staticmethod
    def get_custom_spec_interface(dhcp, ip=None, mask=None, gateway=None):
        """
        Generates an interface object definition for a
        customization specification :py:func:`get_custom_spec`

        :param dhcp: Whether the virtual machine acquires IP config from
         DHCP. If set to true, parameters ip, subnet dns and gateway will
         be ignored.
        :type dhcp: bool
        :param ip: Specification to obtain a unique IP address
         for this virtual network adapter.
        :type ip: str
        :param mask: Subnet mask for this virtual network adapter.
        :type mask: str
        :param gateway: For a virtual network adapter with a static IP address,
         this data object type contains a list of gateways,
         in order of preference.
        :type gateway: list
        :return:
        """
        interface = dict(dhcp=dhcp)
        if not dhcp:
            fixed_ip = dict(ip=ip, mask=mask, gateway=gateway)
            interface.update(fixed_ip)
        return interface


def run_main():
    """
    Simple wrapper to execute manager functions

    Checks for `VSS_API_TOKEN` environment variable

    Example::

        python pyvss/manager.py get_vms 'summary=1&name=pm'

    """
    import sys
    import pprint
    api_token = os.environ.get('VSS_API_TOKEN')
    if not api_token:
        raise VssError('Specify environment variable VSS_API_TOKEN')
    manager = VssManager(api_token)
    fname = sys.argv[1]
    pprint.pprint(getattr(manager, fname)(*sys.argv[2:]), indent=1)


if __name__ == '__main__':
    run_main()
