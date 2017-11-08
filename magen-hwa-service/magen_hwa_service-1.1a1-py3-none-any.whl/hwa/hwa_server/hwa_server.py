#! /usr/bin/python3
#
# Copyright (c) 2015 Cisco Systems, Inc. and others.  All rights reserved.
#
"""
Magen "Hello, World" Application, aka "HWA"

A simple application that uses, depends on, and shows the use of the
Magen services (identity, policy, ingestion, key).

The application, through a browser interface, maintains a toy repository
on the filesystem of its local Linux instance.
"""

import string
import argparse
import io
import sys
import os
import logging
import pkg_resources
import ssl
import time
from datetime import datetime, timedelta
from http import HTTPStatus
import base64
import json
from bs4 import BeautifulSoup

import werkzeug
import flask
from flask import request, session, Blueprint
import flask_cors
from requests import request as rq

from magen_rest_apis.magen_app import MagenApp
# If this is being run from workspace (as main module),
# import dev/magen_env.py to add workspace package directories.
src_ver = MagenApp.app_source_version(__name__)
if src_ver:
    # noinspection PyUnresolvedReferences
    import dev.magen_env
from magen_logger.logger_config import LogDefaults, initialize_logger
from magen_rest_apis.rest_server_apis import RestServerApis
from magen_rest_apis.server_urls import ServerUrls
from magen_id_client_apis.magen_client import MagenClient

from hwa.hwa_server.hwa_utils import read_dict_from_file, do_rest_call
from hwa.hwa_server.hwa_crypt import decrypt_stream

from hwa.hwa_server.hwa_urls import HwaUrls
from hwa.hwa_server.hwa_events import HwaEventSvcInitialize, HwaEventsSendEvt

__author__ = "jgdev29"
__copyright__ = "Copyright(c) 2017, Cisco Systems, Inc."
__version__ = "0.1"
__status__ = "alpha"

hwa_urls = HwaUrls()

hwaServer = flask.Flask(__name__)
flask_cors.CORS(hwaServer)
magen_client = MagenClient(hwaServer)

hwa_url_bp = Blueprint("hwa_url_bp", __name__)

# enough extensions to make the point that multiple extensions are supported
ALLOWED_EXTENSIONS=(
    'txt', 'pdf',
    'jpg', 'jpeg',
    'doc', 'docx',
    'xls', 'xlsx',
    'ppt', 'pptx')

# MAGEN ID CLIENT LIBRARY INTERFACE: START
# (see also hwa_ids_authorization() below)

# hwa_ids_clt holds interface state
# - must be created in global context since hwa_ids_clt.authorized_handler
#   is a decorator for HWA_IDS_CLT_OAUTH_CALLBACK_URL_PATH handler.
# - initialized in hwa_ids_init()
hwa_ids_clt = magen_client.register_client_app('magen_hw_agent')

def hwa_ids_is_initialized():
    return hwa_ids_clt.client_id and hwa_ids_clt.client_secret

def hwa_ids_init():
    """
    Initialize hwa_ids_clt at boot time

    - issuer: url for id svc, which app redirects to
    - args passed to issuer via redirect
      - callback_uri: uri that id svc will use to redirect back to app
      - client_id, client_secret: auth information

    Authorization based on
      - app passing client_id, client_secret
      - callback_url pre-configured into id, exactly matching value set here
    """
    hwa_urls = HwaUrls()
    server_urls = ServerUrls.get_instance()

    hwa_urls.ids_clt_oauth_callback_url_path = HWA_IDS_CLT_OAUTH_CALLBACK_URL_PATH
    hwa_ids_clt.issuer = hwa_urls.ids_issuer

    idsclt_secrets = read_dict_from_file(hwa_urls.idsclt_secret_file)
    hwa_ids_clt.client_id = idsclt_secrets.get('hwa_idsclt_client_id')
    hwa_ids_clt.client_secret = idsclt_secrets.get('hwa_idsclt_client_secret')
    if not hwa_ids_clt.client_id or not hwa_ids_clt.client_secret:
        if not os.path.exists(hwa_urls.idsclt_secret_file):
            logger.info(
                "id auth client config file (%s) missing. HWA will operate with reduced capability until correctly formatted file is provided.",
                hwa_urls.idsclt_secret_file)
            return False
        logger.error(
            "FATAL: ids client config init failed: file:%s, id:%s, secret:%s",
            hwa_urls.idsclt_secret_file,
            "Present" if hwa_ids_clt.client_id else "Missing",
            "Present" if hwa_ids_clt.client_secret else "Missing")
        assert hwa_ids_clt.client_id and hwa_ids_clt.client_secret, "id auth client config file (" + hwa_urls.idsclt_secret_file + ") contains invalid configuration"

    hwa_ids_clt.callback_uri = hwa_urls.ids_clt_oauth_callback_url

    # ids_alg='HS256'
    # ids_request_token_params = {'scope': 'email,profile'}
    # ids_scopes='openid,profile,address'

    logger.info("ID-CLIENT INIT: issuers[std:%s, redirect:%s], callback_uri:%s",
                hwa_ids_clt.issuer, hwa_urls.ids_redirect_issuer,
                hwa_ids_clt.callback_uri)

    return True

def hwa_ids_mid_token_get(request, return_url):
    """
    Return mid_token and redirect url.
    If mid_token is valid, callback_url is None, and operation can continue.
    If mid_token is None, callback_url is either authorization or error
    """
    hwa_urls = HwaUrls()

    midtoken_expired = ('magen_id_token' in session and
                        session['magen_id_token_refresh_time'] < time.time())
    if midtoken_expired:
        del session['magen_id_token']
    midtoken_valid = 'magen_id_token' in session
    logger.debug(
        "MAGEN_ID_TOKEN %sIN SESSION%s",
        "" if 'magen_id_token' in session else "NOT ",
        " BUT EXPIRED" if midtoken_expired else "")
    if midtoken_valid:
        return session['magen_id_token'], None

    # Currently, require user to click on login rather than also allowing
    # login as a side effect of other operations
    if (return_url.find('login') == -1 or
        request.method != 'GET' or len(request.args) > 0):
        logger.error("MID Token missing, url:%s, method:%s, arglen:%s, args:%s",
                     return_url, request.method, len(request.args),
                     request.args)
        msg = "Login required to use service."
        return None, flask.render_template('status_msg.html', msg=msg)

    # Unittest bypass
    if not hwa_urls.production_mode and not midtoken_valid:
        midtoken_valid = True
        magen_id_token = "1234567890"
        session['magen_id_token'] = magen_id_token
        session['magen_id_token_refresh_time'] = time.time() + 3600
        return magen_id_token, None

    assert hwa_urls.production_mode, "id svc authorize mocking not yet implemented"
    if not hwa_ids_is_initialized():
        hwa_ids_init()
        if not hwa_ids_is_initialized():
            msg = "Parameters to communicate with id service not configured"
            return None, flask.render_template('status_msg.html', msg=msg)

    session['return_url'] = return_url
    login_username = session['login_username']
    dummy_access_token = "dummy-access-token" # required by idsclt lib

    # ids_issuer and ids_redirect_issuer may differ in the case where
    # hwa and ids are local to the same host.
    # - ids_redirect_issuer needs to be meaningful to the browser
    #   - most complicated case: under aws ec2, with potentially remote browser,
    #     url authority needs to be ec2 instance global ip address,
    #     e.g. https://ec2-ww-xx-yy-zz.<aws-stuff>:5030
    # - ids_issuer needs to be meaningful for local access
    #   - most complicated case is access between two dockers, e.g.
    #     e.g. https://magen_id_service:5030
    # id client library does not currently support both these, so temporarily
    # install redirect issue latter around this call to generate a redirect.
    assert hwa_ids_clt.issuer == hwa_urls.ids_issuer
    hwa_ids_clt.issuer = hwa_urls.ids_redirect_issuer
    authorize_response = hwa_ids_clt.authorize(
        username=login_username, access_token=dummy_access_token)

    hwa_ids_clt.issuer = hwa_urls.ids_issuer
    logger.debug("Get MAGEN_ID_TOKEN by authenticating with MID service, authenticate user:%s, callback_url:%s, authorize_result:%s, return_url:%s, session:%s",
                 login_username, hwa_ids_clt.callback_uri, return_url, session)
    return None, authorize_response

def hwa_ids_mid_token_validate(mid_token):
    hwa_urls = HwaUrls()
    if not hwa_urls.production_mode:
        json_response = {
            "mc_id": "dummy-mc_id",
            "username": session['login_username']
        }
        return json_response

    assert hwa_ids_clt.issuer == hwa_urls.ids_issuer
    if not hwa_ids_is_initialized():
        msg = "Parameters to communicate with id service not configured"
        logger.error(msg)
        return None

    return(hwa_ids_clt.validate_mid_token_against_id_service(mid_token))
# MAGEN ID CLIENT LIBRARY INTERFACE: END


#
# HWA INFRASTRUCTURE ROUTINES
#
def hwa_flask_init():
    hwa_urls = HwaUrls()
    if hwa_urls.src_version: # src case: templates are relative to executable
        template_folder='../data/template'
    else:        # installed case: templates are installed with package
        template_folder=pkg_resources.resource_filename('hwa', 'data/template')
    hwaServer.template_folder = template_folder

    hwaServer.config['UPLOAD_FOLDER'] = hwa_urls.hwa_fs_dir # specific to hwa

    # for single host running hwa and id, disambiguate hwa session cookies
    # from id session cookies (browsers disambiguate by host, but not
    # by different ports in same host
    hwaServer.config['SESSION_COOKIE_NAME'] += (
        "-" + hwa_urls.hwa_app_tag + "-" + hwa_urls.local_server_port)

    flask_secrets = read_dict_from_file(hwa_urls.hwa_flask_secret_file)
    hwaServer.secret_key = flask_secrets.get('hwa_flask_secret_key', None)
    if not hwaServer.secret_key:
        logger.error("FATAL: flask config (from %s) not found",
                     hwa_urls.hwa_flask_secret_file)
        return False
    # lifetime set short (10 vs. 30) to force more interactions with id svc
    hwaServer.config['PERMANENT_SESSION_LIFETIME']=timedelta(minutes = 10)

    logger.info("FLASK INIT: session:[cookie_name:%s, lifetime:%s], static_url_path:%s, static_folder:%s, upload_folder:%s, template_folder:%s",
                 hwaServer.config['SESSION_COOKIE_NAME'],
                 hwaServer.config['PERMANENT_SESSION_LIFETIME'],
                 hwaServer.static_url_path, hwaServer.static_folder,
                 hwaServer.config['UPLOAD_FOLDER'], hwaServer.template_folder)
    return True

def hwa_logging_level_set(level_str):

    if level_str.isnumeric():
        level = int(level_str)
    else:
        level=level_str.upper()

    logger.setLevel(level=level)
    requestsLogger = logging.getLogger("requests")
    requestsLogger.setLevel(level=level)
    return True


#
# Would prefer that this output, when enabled, be interleaved
# with application logging but for the moment getting
# it to appear at all is enough progress.
#
def hwa_http_logging_set(log_dir, level):
    if level == None:
        print("http logging:disabled")
        return

    level = str(level).upper()
    werkzeugLogger = logging.getLogger("werkzeug")
    werkzeugLogger.setLevel(level=level)

    #http_logging_fname =  logger_config_instance.default_all_file
    http_logging_fname = "werkzeug.log"
    http_logging_file = os.path.join(log_dir, http_logging_fname)
    print("http logging:enabled [level:{}, logfile:{}]".format(level, http_logging_file))

    werkzeugLogger = logging.getLogger("werkzeug")
    wz_logfile_handler = logging.FileHandler(http_logging_file, "w", encoding=None, delay="true")
    wz_logfile_handler.setLevel(level)
    werkzeugLogger.addHandler(wz_logfile_handler)

def hwa_file_ingestion_allowed(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# file_name: original (pre-ingestion) name in all cases
# folder_id: folder for upload new file
# file_data: handle on new file contents
# oauth_token: box token allowing upload
# operation: {encrypt,decrypt,transparent}
def hwa_file_upload(file, ftype):
    hwa_urls = HwaUrls()
    server_urls = ServerUrls.get_instance()

    filename = werkzeug.secure_filename(file.filename)

    ufn_pfx = ""
    ufn_sfx = hwa_urls.ingest_file_suffix

    upload_filename = ufn_pfx + filename + ufn_sfx

    upload_path = os.path.join(
        hwaServer.config['UPLOAD_FOLDER'], upload_filename)
    logger.debug("Filename:%s => Directory:%s", filename, upload_path)
    if ftype == 'encrypt':

        """ CREATE byte array and seek to 0 """
        #f = open(filename, "rb")
        b = io.BytesIO()
        file.save(b)
        #for chunk in iter(lambda: f.read(4096), b''):
        #    b.write(chunk)
        #    logger.debug("bytes written from file %d", written)
        b.seek(0)

        """ SEND TO INGESTION SERVICE """
        ingestion_url = server_urls.ingestion_server_upload_url
        files = {'file': (filename, b, {'Expires': '0'})}
        logger.debug("ingesting file to %s", ingestion_url)

        """ RECEIVE BACK FROM INGESTION """
        ingest_response = rq(method="POST", url=ingestion_url, files=files)
        logger.debug('content: ')
        logger.debug(ingest_response.content)

        post_resp_json_obj = json.loads(ingest_response.content.decode("utf-8"))
        response = post_resp_json_obj.get('response')
        success = (response.get('success') == True) if response else False
        if not success:
            logger.debug("upload failed: response:%s, success:%s",
                         response, response.get('success'))
            return success, filename, upload_filename, post_resp_json_obj

        enc_file = post_resp_json_obj["response"]["container"]

        # extract for debug
        html_soup = BeautifulSoup(enc_file, 'html.parser')
        metadata_tag = html_soup.find(id="metadata")
        metadata_tag_src = metadata_tag.attrs["src"]
        metadata_b64 = metadata_tag_src.split("base64,", 1)[1]
        metadata_json = base64.b64decode(metadata_b64).decode("utf-8")
        metadata_dict = json.loads(metadata_json)
        asset_uuid = metadata_dict["asset_id"]

        f = open(upload_path, "w")
        f.write(enc_file)
        response = dict(
            asset_uuid=asset_uuid)
    else:
        file.save(upload_path)
        response = dict(
            asset_uuid="unknown")
    return True, filename, upload_filename, response

def hw_request_context_update(request, request_url=None):
    success_result = False
    html_result = None
    mid_token_result = None

    session['host_url'] = request.host_url

    # hard-coded username for now
    session['login_username'] = "wiley@acmebirdseed.com"

    # If not valid, authenticate with Magen ID Svc to get or refresh MID token
    if not request_url:
        request_url = request.path
    mid_token, ids_auth_url = hwa_ids_mid_token_get(request, request_url)
    if not mid_token:
        html_result = ids_auth_url
        # RETURN REDIRECT TO ID SVC: END OF THIS PASS THROUGH ROUTINE
        return success_result, html_result, mid_token_result

    mid_token_result = session.get('magen_id_token')
    assert mid_token_result,  "magen_id_token update error"
    success_result = True
    return success_result, html_result, mid_token_result

#
# Health check, e.g. for AWS load balancer
#
@hwa_url_bp.route('/check/', methods=["GET"])
def health_check():
    hwa_urls = HwaUrls()
    return "Check success (Magen-Hello " + hwa_urls.hwa_app_tag + ")"


@hwa_url_bp.route('/', methods=['GET', 'POST'])
def index():
    return flask.render_template('index.html')

@hwa_url_bp.route('/doc/<path:filename>')
def doc(filename):
    doc_template='doc/' + filename + '.html'
    #doc_template= filename + '.html'
    return flask.render_template(doc_template)

#
# Infrastructure API to set logging level
#
@hwa_url_bp.route('/logging_level/', methods=["GET", "POST", "PUT"])
def logging_level():
    op="logging_level"
    if request.method == 'GET':
        return RestServerApis.respond(
            HTTPStatus.OK, op,
            { "success": True, "level": logger.getEffectiveLevel()})

    level = request.json.get('level')
    logger.debug("set_logging_level: %s", level)
    if level is None:
        return RestServerApis.respond(
            HTTPStatus.NOT_FOUND, op,
            {"success": False, "cause": "missing required parameters"})

    try:
        hwa_logging_level_set(level)

        return RestServerApis.respond(
            HTTPStatus.OK, op, {
                "success": True, "cause": "level set",
                "level": logger.getEffectiveLevel()})
    except Exception as e:
        return RestServerApis.respond(
            HTTPStatus.INTERNAL_SERVER_ERROR, "set_logging_level", {
                "success": False,
                "cause": HTTPStatus.INTERNAL_SERVER_ERROR.phrase})

#
# Magen ID service oauth callback (HWA_IDS_CLT_OAUTH_CALLBACK_URL_PATH)
#
# NOTE: hwa_ids_clt.authorized_handler is called before authorized(),
#       through use of a flask within-process redirect-like mechanism.
#       [i.e. pay attention to "@hwa_ids_clt.authorized_handler" decorator]
#
# NOTE: magen id svc has a configured list of app callbacks.
#       id svc compares received callbacks against its list and
#       and rejects the oauth if exact string match (including
#       e.g. trailing '/') is not found
#       So any change to HWA_IDS_CLT_OAUTH_CALLBACK_URL_PATH below much
#       be matched by an id svc config change.
#
HWA_IDS_CLT_OAUTH_CALLBACK_URL_PATH = '/oauth/callback/'
@hwa_url_bp.route(HWA_IDS_CLT_OAUTH_CALLBACK_URL_PATH, methods=["GET"])
@hwa_ids_clt.authorized_handler
def hwa_ids_authorization(resp):
    resp = resp.json_body
    logger.debug(
        "hwa oauth callback (from id svc): resp:%s, url:%s, session:%s",
        resp, request.host_url, session)
    if resp is None:
        return 'Access denied: error=%s' % (request.args['error'])
    if 'magen_id_token' not in resp or 'expires_in' not in resp:
        msg = "No access permitted. No MID and response is " + json.dumps(resp)
        return flask.render_template('status_msg.html', msg=msg)

    magen_id_token=resp['magen_id_token'].strip()
    session['magen_id_token'] = magen_id_token
    user_client_info_json = hwa_ids_mid_token_validate(magen_id_token).json_body

    # calculate refresh time for future check and save in the session
    expires = resp.get('expires_in')
    refresh_time = int(time.time()) + expires - 10
    session['magen_id_token_refresh_time'] = refresh_time

    host_url = session['host_url']
    return_url=session['return_url']
    # ensure exactly one '/' between these two elements
    return_to = host_url.rstrip('/') + '/' + return_url.lstrip('/')

    logger.debug("Session midToken: Value:%s, Expires_in:%s, Refresh_time:%s, Return_to URI:%s, hwa ids %s uc info:%s",
                 magen_id_token, expires, refresh_time, return_to,
                 HWA_IDS_CLT_OAUTH_CALLBACK_URL_PATH,
                 user_client_info_json)

    return flask.redirect(return_to)

@hwa_url_bp.route('/login/', methods=['GET'])
def login():
    logger.info("LOGIN FLOW: START: req:%s, session:%s", request, session)
    success, html, mid_token = hw_request_context_update(request)
    if not success:
        return html

    login_username = session['login_username']
    logger.info("LOGIN FLOW: END")
    msg = "You are currently logged in as " + login_username
    return flask.render_template('status_msg.html', msg=msg)

#
# All operations on ingested files (e.g. even deletion) are done with GET
#
@hwa_url_bp.route('/hwa_repo/', defaults={'req_path': ''}, methods=['GET'])
@hwa_url_bp.route('/hwa_repo/<path:req_path>/', methods=['GET'])
def hwa_repo(req_path):
    logger.info("REPO FLOW: START: request:%s, session:%s", request, session)
    hwa_urls = HwaUrls()
    server_urls = ServerUrls.get_instance()

    success, html, mid_token = hw_request_context_update(request)
    if not success:
        return html

    # Save dynamic values that and come in the URI.
    # As the same session can be used across calls and even app
    # restart, need to overwrite old values with new values
    session['location'] = 'GetLocation' in request.args

    # restore .html (stripped below when repo file list rendered)
    ingest_file_suffix = hwa_urls.ingest_file_suffix
    file_name = req_path + (ingest_file_suffix if req_path else "")
    session['file_name'] = file_name

    for property in ['download', 'raw_view', 'raw_download', 'delete']:
        session[property] = request.args.get(property) != None


    content_header = {
        'content-type': "application/json",
        'accept': "application/json",
        'cache-control': "no-cache"
    }

    host_url = session['host_url']
    login_username = session['login_username']
    if login_username == "" or host_url is None:
        logger.error("login_username:%s, host_url:%s", login_username, host_url)
        return RestServerApis.respond(
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "errors", 'Missing login_username and/or host_url')

    user_client_info_resp = hwa_ids_mid_token_validate(mid_token)
    assert user_client_info_resp.http_status, HTTPStatus.OK
    user_client_info_json = user_client_info_resp.json_body
    logger.debug("MID user client info: %s", user_client_info_json)

    mc_id = user_client_info_json.get("mc_id", "")
    mid_username = user_client_info_json.get("username", "")

    logger.debug("HW Login Username is: %s", login_username)
    logger.debug("MID Token is: %s", mid_token)
    logger.debug("MID username is: %s", mid_username)

    if mid_username == "":
        # sync error with browser cookie, e.g. id service restarted
        del session['magen_id_token']
        return RestServerApis.respond(
            HTTPStatus.INTERNAL_SERVER_ERROR, "errors",
            'Missing MID client username')

    # these come on the viewer_call
    latitude = request.args.get('latitude', None)
    longitude = request.args.get('longitude', None)

    file_name = session['file_name']

    # Joining the base and the requested path
    abs_path = os.path.join(hwaServer.config['UPLOAD_FOLDER'], file_name)

    # Return 404 if path doesn't exist
    if not os.path.exists(abs_path):
        logger.error("%s does not exist", abs_path)
        return flask.abort(HTTPStatus.NOT_FOUND)

    # If directory, show contents, with .html stripped (see above for restore)
    if os.path.isdir(abs_path):
        repo_files = os.listdir(abs_path)
        repo_fsplits = [os.path.splitext(split) for split in repo_files]
        assets = [ asset[0] for asset in repo_fsplits if
                   asset[1] == ingest_file_suffix ]
        logger.debug("repo_files:%s, split_repo_files:%s, assets:%s",
                     repo_files, repo_fsplits, assets)
        return flask.render_template('hwa_repo.html', files=assets)

    if session['delete']:
        os.remove(abs_path)
        return flask.redirect(request.url_root + 'hwa_repo')

    ingested_file_basename = os.path.basename(os.path.normpath(abs_path))
    orig_filename = ingested_file_basename[:-len(ingest_file_suffix)]

    # Serve file
    f = open(abs_path, "rb")
    if session['raw_view'] or session['raw_download']:
        return flask.send_file(f,
                               attachment_filename=ingested_file_basename,
                               as_attachment=session['raw_download'],
                               cache_timeout = 0)

    b = io.BytesIO()
    for chunk in iter(lambda: f.read(4096), b''):
        b.write(chunk)
    b.seek(0)
    raw = b.getvalue()
    b.seek(0)
    # read file metadata to get asset id
    html_soup = BeautifulSoup(raw, 'html.parser')

    # extract asset_uuid, asset_source
    metadata_tag = html_soup.find(id="metadata")
    if not metadata_tag:
        return RestServerApis.respond(
            HTTPStatus.INTERNAL_SERVER_ERROR, "Error",
            "Not a valid ingested asset")
    metadata_tag_src = metadata_tag.attrs["src"]
    metadata_b64 = metadata_tag_src.split("base64,", 1)[1]
    metadata_json = base64.b64decode(metadata_b64).decode("utf-8")
    metadata_dict = json.loads(metadata_json)
    asset_uuid = metadata_dict["asset_id"]
    asset_source = metadata_dict.keys()
    logger.debug("asset uuid:%s, source:%s", asset_uuid, asset_source)

    # extract asset_enc for in_stream.write()
    asset_tag = html_soup.find(id="asset")
    asset_tag_src = asset_tag.attrs["src"]
    asset_b64 = asset_tag_src.split("base64,", 1)[1]
    asset_enc = base64.b64decode(asset_b64)

    iv_element = html_soup.find("p", attrs={"data-initialization-vector": True})
    iv = iv_element.get_text()

    file_size_elem = html_soup.find("p", attrs={"data-file-size": True})
    file_size = int(file_size_elem.get_text())

    event_kwgs = dict(
        action="file.open",
        application=hwa_urls.hwa_app_tag,
        client_id=mc_id,
        resource_id=asset_uuid,
        asset_name=file_name
    )

    validation_url = (
        server_urls.policy_validate_asset_access_url.format(asset_uuid) +
	              "?midToken=" + str(mid_token) +
                      "&action=" + "open" +
                      "&returnKey")
    logger.debug("policy validation:%s", validation_url)
    my_bool, flask_response, policy_request_response = do_rest_call(
        method="GET", url=validation_url, headers=content_header)
    policy_response = policy_request_response.json().get(
        'response', None) if policy_request_response else None
    if policy_response is None:
        return RestServerApis.respond(
            HTTPStatus.INTERNAL_SERVER_ERROR, "Error",
            "No policy_response returned")
    access = policy_response.get("access", None)
    if access != 'granted':
        assert access == 'denied', 'Invalid access result %s' % access
    cause = policy_response.get("cause", None)
    logger.debug("Access and cause are %s, %s", access, cause)
    if cause is None:
        cause = "not authorized to access this asset"

    allowed = my_bool and policy_request_response.status_code == 200 and access == 'granted'

    if not allowed:
        HwaEventsSendEvt(event_name='HW File View', alert='warning',
                         response = policy_response, **event_kwgs)
        # has knowledge status_msg use of <h2>
        msg = (
            "</h2><h1>Sorry, you are unable to preview the requested file.</h1>"
            "<h2>Cause: Policy failure::" + cause + "</h2>" +
            "<p>Please contact your system administrator if you have further questions.</p>")
        return flask.render_template('status_msg.html', msg=msg)

    key_b64 = policy_response.get('key').get('key')
    # key = base64.b64decode(key_b64)
    # No need to decode anymore.
    key = key_b64

    in_stream = io.BytesIO()
    in_stream.write(asset_enc)
    in_stream.seek(0, 0)

    out_stream = decrypt_stream(key, iv, file_size, in_stream=in_stream)
    out_stream.seek(0,0)

    HwaEventsSendEvt(event_name='HW File View', alert='success',
                     response=policy_response, **event_kwgs)

    return flask.send_file(out_stream, attachment_filename=orig_filename,
                           as_attachment=session['download'],
                           cache_timeout = 0)

@hwa_url_bp.route('/ingestion/', methods=['GET', 'POST'])
def ingest_file():
    logger.info("INGESTION FLOW: START: req:%s, session:%s", request, session)
    success, html, mid_token = hw_request_context_update(request)
    if not success:
        return html

    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            logger.error('No file key')
            return flask.redirect(request.url)
        file = request.files['file']
        if not file:
            logger.error('file error')
            msg = "Error: No file specified."
            return flask.render_template('status_msg.html', msg=msg)
        elif not hwa_file_ingestion_allowed(file.filename):
            logger.error('file ingestion allowed error')
            msg = "Upload not allowed for " + file.filename
            return flask.render_template('status_msg.html', msg=msg)

        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            logger.info('No selected file')
            return flask.redirect(request.url)

        ftype = 'encrypt'

        success, src_filename, upload_filename, response = hwa_file_upload(
            file, ftype)
        if not success:
            msg = "Upload failed for " + file.filename
            return flask.render_template('status_msg.html', msg=msg)

        asset_uuid = response.get("asset_uuid", "")
        policy_response=dict(
            access='granted'
        )
        event_kwgs = dict(
            action="file.create",
            application=hwa_urls.hwa_app_tag,
            client_id="N/A", # ingestion flow currently does not require session
            resource_id=asset_uuid,
            asset_name=upload_filename
        )
        HwaEventsSendEvt(event_name='HW File Ingestion', alert='success',
                         response = policy_response, **event_kwgs)
        msg = ("Your file " + src_filename +
               " has been successfully ingested into the Magen Platform as " +
               upload_filename)
        return flask.render_template('status_msg.html', msg=msg)

    return flask.render_template('ingestion_form.html')


#
# MAIN AND INITIALIZATION
#

logger = logging.getLogger(LogDefaults.default_log_name)

def main():
    hwa_urls = HwaUrls()
    hwa_urls.src_version = src_ver
    server_urls = ServerUrls.get_instance()

    #: setup parser -----------------------------------------------------------
    parser = argparse.ArgumentParser(description='HWA Test Server',
                                     usage=("\npython3 server.py "
                                            "--data-dir <dir> "
                                            "--pdp-server-ip-port <port> "
                                            "--hwa-ip-port <port> "
                                            "--log-dir <dir> "
                                            "--console-log-level {error|info|debug} "
                                            "--test "))

    parser.add_argument('--data-dir',
                        help='Set directory for log files. '
                             'Default is %s' % hwa_urls.hwa_data_dir)

    parser.add_argument('--policy-server-ip-port',
                        help='Set PDP SERVER IP and port in form <IP>:<PORT>. '
                             'Default is %s' %
                        server_urls.policy_server_url_host_port)

    parser.add_argument('--location-server-ip-port',
                        help='Set Location SERVER IP and port in form <IP>:<PORT>. '
                             'Default is %s' %
                        server_urls.location_server_url_host_port)

    parser.add_argument('--hwa-ip-port',
                        default=hwa_urls.local_server_host_port,
                        help='Set APP SERVER IP and port in form <IP>:<PORT>. '
                             'Default is %s' % hwa_urls.local_server_host_port)

    parser.add_argument('--log-dir', default=LogDefaults.default_dir,
                        help='Set directory for log files. '
                             'Default is %s' % LogDefaults.default_dir)

    parser.add_argument('--console-log-level', choices=['debug', 'info', 'error'], default='error',
                        help='Set log level for console output.'
                             'Default is %s' % 'error')

    parser.add_argument('--http-log-level', choices=['debug', 'info', 'error'],
                        help='Set log level for http output.')

    parser.add_argument('--test', action='store_true',
                        help='Run server in test mode. Used for unit tests'
                             'Default is to run in production mode)')

    #: parse CMD arguments ----------------------------------------------------
    args = parser.parse_args()

    hwa_urls.production_mode = not args.test

    if args.data_dir:
        hwa_urls.hwa_data_dir = args.data_dir

    hwa_urls.data_files_check()

    # log_level arg to initialize_logger() is not honored, so
    # also make explicit call below.
    initialize_logger(
        console_level=args.console_log_level,
        output_dir=args.log_dir,
        logger=logger)
    hwa_logging_level_set(args.console_log_level)
    hwa_http_logging_set(args.log_dir, args.http_log_level)

    logger.info("\n\n\n\n ====== STARTING HWA (MAGEN \"HELLO WORLD\" APP) SERVER  ====== \n")
    logger.info("Setting up policy server address and authorization info...")
    logger.info("[location server support currently disabled...]")
    logger.info("log level=%s, log dir=%s", args.console_log_level, args.log_dir)

    if args.policy_server_ip_port is not None:
        #server_urls.set_policy_server_url_host_port(args.policy_server_ip_port)
        logger.error("Currently unsupported operation: Policy server port override currently disabled...")

    if args.location_server_ip_port is not None:
        logger.error("Currently unsupported argument: Location server support currently disabled...")

    if not hwa_urls.production_mode:
        hwa_urls.hwa_url_scheme = "http"

    # ip and port of this micro-service
    hwa_urls.local_server_host_port = args.hwa_ip_port
    logger.info("HWA URL ELEMENTS: port:%s, scheme:%s",
                hwa_urls.local_server_host_port, hwa_urls.hwa_url_scheme)

    # Initialize flask parameters
    success = hwa_flask_init()
    if not success:
        return

    hwaServer.register_blueprint(hwa_url_bp)

    # Initialize event service client relationship
    HwaEventSvcInitialize()

    hwa_ids_init()

    if hwa_urls.hwa_url_scheme == "https" and hwa_urls.production_mode:
        logger.info("CERTIFICATE: cert:%s", hwa_urls.hwa_server_cert_crt)
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        ctx.load_cert_chain(hwa_urls.hwa_server_cert_crt,
                            hwa_urls.hwa_server_cert_pvt_key)
    elif hwa_urls.hwa_url_scheme == "http":
        ctx = None
    else:
        logger.error("FATAL: unknown url scheme:%s", hwa_urls.hwa_url_scheme)
        return

    RestServerApis.rest_api_log_all(hwaServer)

    print("Starting hwa_server...")
    sys.stdout.flush()

    hwaServer.run(
        host=hwa_urls.local_server_host, port=hwa_urls.local_server_port,
        ssl_context=ctx, threaded=True, debug=True, use_reloader=False)

if __name__ == "__main__":
    main()
else:
    pass
