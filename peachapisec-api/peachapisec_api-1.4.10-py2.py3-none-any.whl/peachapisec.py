
'''Peach API Security Python Module
Copyright (c) 2017 Peach API Security, LLC

This is a python module that provides method to call
the Peach Proxy Restful API.  This allows users
to integrate into unit-tests or custom traffic generators.
'''

from __future__ import print_function
import os, warnings, logging
import requests, json, sys
from requests import put, get, delete, post

logger = logging.getLogger(__name__)

logger.setLevel(logging.INFO)

logFormatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s] %(message)s")
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)

#fileHandler = logging.FileHandler('peachapisec.log')
#fileHandler.setFormatter(logFormatter)
#logger.addHandler(fileHandler)
class PeachInternalState:

    BEFORE_SETUP = 0
    SETUP = 1
    TEST = 2
    TEARDOWN = 3

## This code will block the use of proxies.

session = requests.Session()
session.trust_env = False

## Peach Proxy API Helper Functions

__peach_session = None
__peach_api = None
__peach_state = "Continue"
__peach_proxy = None
__peach_ca_cert = None
__peach_api_token = None
__peach_api_token_field = 'Authorization'
__peach_headers = {}
__peach_internal_state = PeachInternalState.BEFORE_SETUP
__peach_internal_state_active = False


def __goto_correct_state(goto_state):
    '''Make sure we are in correct API state
    '''

    global __peach_internal_state
    global __peach_internal_state_active

    if __peach_internal_state_active:
        return

    INTERNAL_STATE_TEST = "peach_internal_state_fix"

    try:
        __peach_internal_state_active = True

        if goto_state == PeachInternalState.SETUP:
            logger.debug("goto_state == PeachInternalState.SETUP from %s", __peach_internal_state)
            if __peach_internal_state == PeachInternalState.BEFORE_SETUP:
                return
            elif __peach_internal_state == PeachInternalState.SETUP:
                testcase(INTERNAL_STATE_TEST)
                teardown()
            elif __peach_internal_state == PeachInternalState.TEST:
                teardown()
                return
            elif __peach_internal_state == PeachInternalState.TEARDOWN:
                return

        elif goto_state == PeachInternalState.TEST:
            logger.debug("goto_state == PeachInternalState.TEST from %s", __peach_internal_state)
            if __peach_internal_state == PeachInternalState.BEFORE_SETUP:
                setup()
                return
            elif __peach_internal_state == PeachInternalState.SETUP:
                return
            elif __peach_internal_state == PeachInternalState.TEST:
                teardown()
                setup()
                return
            elif __peach_internal_state == PeachInternalState.TEARDOWN:
                setup()
                return

        elif goto_state == PeachInternalState.TEARDOWN:
            logger.debug("goto_state == PeachInternalState.TEARDOWN from %s", __peach_internal_state)
            if __peach_internal_state == PeachInternalState.BEFORE_SETUP:
                testcase(INTERNAL_STATE_TEST)
                return
            elif __peach_internal_state == PeachInternalState.SETUP:
                testcase(INTERNAL_STATE_TEST)
                return
            elif __peach_internal_state == PeachInternalState.TEST:
                return
            elif __peach_internal_state == PeachInternalState.TEARDOWN:
                setup()
                testcase(INTERNAL_STATE_TEST)
                return
    
    finally:
        __peach_internal_state = goto_state
        __peach_internal_state_active = False

def __get_error(r):
    try:
        err = r.json()

        try:
            logger.debug(str(err['FullException']).replace('\\r\\n', '\n'))
        except:
            pass
        
        msg = str(err['Message'])
        
        return msg
    except:
        pass

    return "Server responded with %s %s" % (r.status_code, r.reason)
## Setter/getter functions

def state():
    '''Current state of Peach Proxy
    '''
    global __peach_state
    return __peach_state

def session_id():
    '''Get the current sessions id
    '''
    global __peach_session
    return __peach_session['Id']

def set_session_id(session_id):
    '''Get the current sessions id
    '''
    global __peach_session
    if __peach_session == None:
        __peach_session = {}
        
    __peach_session['Id'] = session_id

def proxy_ca_cert():
    '''Get the current sessions proxy CA cert file
    '''
    global __peach_ca_cert
    return __peach_ca_cert

def set_proxy_ca_cert(filename):
    '''Set the current sessions proxy CA cert file
    '''
    global __peach_ca_cert
    __peach_ca_cert = filename

def proxy_url():
    '''Get the current sessions proxy url
    '''
    global __peach_session
    return __peach_session['ProxyUrl']

def set_proxy_url(url):
    '''Get the current sessions proxy url
    '''
    global __peach_session
    if __peach_session == None:
        __peach_session = {}

    __peach_session['ProxyUrl'] = url

def set_peach_api(api):
    '''Get the current sessions proxy url
    '''
    global __peach_api
    __peach_api = api

def get_peach_api_token():
    '''Get Peach API Token
    '''
    global __peach_api_token
    return __peach_api_token

def set_peach_api_token(token):
    '''Set Peach API token.

    This token can be found on the Settings page of the
    Peach API Security product.
    '''
    global __peach_api_token
    global __peach_api_token_field
    global __peach_headers
    
    __peach_api_token = token
    __peach_headers = { __peach_api_token_field : 'Token ' + __peach_api_token }

    
## Attempt to load from environment

arg = os.environ.get("PEACH_API", None)
if arg != None:
    set_peach_api(arg)

arg = os.environ.get("PEACH_API_TOKEN", None)
if arg != None:
    set_peach_api_token(arg)

arg = os.environ.get("PEACH_SESSIONID", None)
if arg != None:
    set_session_id(arg)

arg = os.environ.get("PEACH_PROXY", None)
if arg != None:
    set_proxy_url(arg)

arg = os.environ.get("PEACH_CA_CERT", None)
if arg != None:
    set_proxy_ca_cert(arg)

def get_jobs():
    '''Get list of job summaries
    '''

    logger.debug(">>get_jobs")

    global __peach_api
    if not __peach_api:
        logger.error("Called get_jobs() w/o a peach_api url")
        sys.exit(-1)
    
    global __peach_headers
    global __peach_api_token
    if not __peach_api_token:
        logger.error("Called get_jobs() w/o a peach_api_token")
        sys.exit(-1)

    try:
        r = session.get(
                "%s/api/jobs" % __peach_api, 
                headers=__peach_headers)
        if r.status_code != 200:
            logger.error('An error occurred while querying the job list')
            logger.error(__get_error(r))
            sys.exit(-1)

        return r.json()
        
    except requests.exceptions.RequestException as e:
        logger.error("Error communicating with Peach API Security.")
        logger.error("vvvv ERROR vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv")
        logger.error(e)
        logger.error("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        sys.exit(-1)

def stop_job(id):
    '''Stop a job

    Keyword arguments:
    id -- Job/Session id
    '''

    logger.debug(">>stop_job(%s)", id)

    try:
        orig_session_id = session_id()
    except:
        orig_session_id = None

    set_session_id(id)

    try:
        session_teardown()
    finally:
        set_session_id(orig_session_id)

def get_script_env():
    '''Return a dictionary of script
    environment for session setup.
    '''

    prefix = 'PEACH_ENV_'
    env = {}

    for key in os.environ.keys():
        key = str(key)
        if not key.startswith(prefix):
            continue
        
        env[key[len(prefix):]] = os.environ[key]
    
    return env

def get_tags():
    '''Get a list of tags from
    environment for session setup
    '''

    prefix = 'PEACH_TAG_'
    tags = []
    for key in os.environ.keys():
        key = str(key)
        if not key.startswith(prefix):
            continue

        tags.append(os.environ[key])

    return tags


def session_setup(project, profile, api, tags=[]):
    '''Notify Peach Proxy that a test session is starting.
    Called ONCE at start of testing.

    Keyword arguments:
    project -- Configuration to launch
    profile -- Name of profile within project to launch
    api -- Peach API URL, example: http://127.0.0.1:5000
    '''

    logger.debug(">>session_setup")

    global __peach_session
    global __peach_api
    if not __peach_api:
        logger.error("Called session_setup() w/o a peach_api url")
        sys.exit(-1)
    
    global __peach_headers
    global __peach_api_token
    if not __peach_api_token:
        logger.error("Called session_setup() w/o a peach_api_token")
        sys.exit(-1)

    __peach_api = api

    global __peach_state
    __peach_state = "Continue"

    global __peach_internal_state
    global __peach_internal_state_active
    __peach_internal_state = PeachInternalState.BEFORE_SETUP
    __peach_internal_state_active = False

    try:
        scriptEnv = get_script_env()
        tags.extend(get_tags())
        params = {
            'project' : project,
            'profile' : profile,
            'scriptEnvironment' : scriptEnv,
            'tags' : tags
        }

        r = session.post(
                "%s/api/sessions" % api, 
                headers=__peach_headers,
                json=params)
        if r.status_code != 201:
            logger.error('An error occurred while creating a new session')
            logger.error(__get_error(r))
            sys.exit(-1)

        __peach_session = r.json()
        
        logger.info("Peach API Security Version: %s", 
            r.headers['X-Peach-Version'])
        logger.info("Session ID: %s", session_id())
        logger.info("Proxy URL: %s", proxy_url())

        logger.info("Script Environment has %d items:" % len(scriptEnv.keys()))
        for key in scriptEnv.keys():
            logger.info("  '%s': '%s'" % (key, scriptEnv[key]))

        # If PEACH_CA_CERT is set, save proxy certificate there
        certfile = proxy_ca_cert()
        if certfile:
            with open(certfile, 'w') as f:
                f.write(__peach_session['Certificate'])
            logger.info("CA Cert: %s", certfile)

        verify_proxy_access()

    except requests.exceptions.RequestException as e:
        logger.error("Error communicating with Peach API Security.")
        logger.error("vvvv ERROR vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv")
        logger.error(e)
        logger.error("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        sys.exit(-1)


def verify_proxy_access():
    '''Make a ping request through proxy port to verify proxy access

    Verify connectivity to the Peach API Security proxy port.
    '''

    logger.debug(">>verify_proxy_access")

    global __peach_session
    if not __peach_session:
        logger.error("Called verify_proxy_access() w/o a session id")
        sys.exit(-1)
    
    try:
        r = session.get(proxy_url(),
            headers = { 'X-PeachProxy-Probe' : 'peachproxy' }
        )
        
        if r.status_code != 200:
            logger.error('Error verifying proxy port, incorrect status code via %s: %s', 
                (proxy_url(), r.status_code))
            logger.error("Please verify correct access to %s. This error is typically")
            logger.error("due to incorrect deployment of Peach API Security or network issues.")
            sys.exit(-1)
        
        try:
            data = r.json()
            if not data['ping'] == 'pong':
                raise Exception()
        except:
            logger.error('Error verifying proxy port, incorrect body returned via %s', 
                proxy_url())
            logger.error('Unexpected Body: %s', r.text)
            logger.error("Please verify correct access to %s. This error is typically", proxy_url())
            logger.error("due to incorrect deployment of Peach API Security or network issues.")
            logger.error("Verify no HTTP proxies are inbetween you and Peach API Security.")
            sys.exit(-1)
        
    except requests.exceptions.RequestException as e:
        logger.error("Error validating access to Peach API Security proxy port.")
        logger.error("Please verify correct access to %s. This error is typically")
        logger.error("due to incorrect deployment of Peach API Security or a network issue.")
        logger.error("Verify access to the port in this URL: %s", proxy_url())
        sys.exit(-1)


def session_teardown():
    '''Notify Peach Proxy that a test session is ending.

    Called ONCE at end of testing. This will cause Peach to stop.
    
    Returns:
        bool: True says failures found during testing
              False says testing completed without issue
    '''
    
    logger.debug(">>session_teardown")

    global __peach_session
    if not __peach_session:
        logger.error("Called session_teardown() w/o a session id")
        sys.exit(-1)
    
    global __peach_api
    if not __peach_api:
        logger.error("Called session_teardown() w/o a peach_api url")
        sys.exit(-1)
    
    global __peach_headers
    global __peach_api_token
    if not __peach_api_token:
        logger.error("Called session_teardown() w/o a peach_api_token")
        sys.exit(-1)
    
    try:
        r = session.delete(
                "%s/api/sessions/%s" % (__peach_api, session_id()), 
                headers = __peach_headers)
        
        if r.status_code != 200:
            logger.error("Error deleting session '%s'", session_id())
            logger.error(__get_error(r))
            sys.exit(-1)
        
        r = r.json()
        return bool(r['HasFaults'])
    except requests.exceptions.RequestException as e:
        logger.error("Error communicating with Peach API Security.")
        logger.error("vvvv ERROR vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv")
        logger.error(e)
        logger.error("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        sys.exit(-1)


def session_state():
    '''Return the job state

        - Invalid (should never be here)
        - Running - testing is in progress
        - Idle - testing has completed
        - Error - non recoverable error has occured
        - Finished - State post-session_teardown
    '''

    logger.debug(">>session_state")

    global __peach_session
    if not __peach_session:
        logger.error("Called session_state() w/o a session id")
        sys.exit(-1)

    global __peach_api
    if not __peach_api:
        logger.error("Called session_state() w/o a peach_api url")
        sys.exit(-1)

    global __peach_headers
    global __peach_api_token
    if not __peach_api_token:
        logger.error("Called session_state() w/o a peach_api_token")
        sys.exit(-1)

    try:
        r = session.get(
            "%s/api/sessions/%s" % (__peach_api, session_id()),
            headers = __peach_headers)
        
        if r.status_code != 200:
            logger.error("Error querying the state of session '%s'", session_id())
            logger.error(__get_error(r))
            sys.exit(-1)
        
        r = r.json()
        return r['State']
        
    except requests.exceptions.RequestException as e:
        logger.error("Error communicating with Peach API Security.")
        logger.error("vvvv ERROR vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv")
        logger.error(e)
        logger.error("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        sys.exit(-1)
    
def session_error_reason():
    '''Return any error message associated with job.
    '''

    logger.debug(">>session_error_reason")

    global __peach_session
    if not __peach_session:
        logger.error("Called session_error_reason() w/o a session id")
        sys.exit(-1)

    global __peach_api
    if not __peach_api:
        logger.error("Called session_error_reason() w/o a peach_api url")
        sys.exit(-1)

    global __peach_headers
    global __peach_api_token
    if not __peach_api_token:
        logger.error("Called session_error_reason() w/o a peach_api_token")
        sys.exit(-1)

    try:
        r = session.get(
            "%s/api/sessions/%s" % (__peach_api, session_id()),
            headers = __peach_headers)
        
        if r.status_code != 200:
            logger.error("Error querying the error reason of session '%s'", session_id())
            logger.error(__get_error(r))
            sys.exit(-1)
        
        r = r.json()
        return r['Reason']
        
    except requests.exceptions.RequestException as e:
        logger.error("Error communicating with Peach API Security.")
        logger.error("vvvv ERROR vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv")
        logger.error(e)
        logger.error("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        sys.exit(-1)
    

def setup():
    '''Notify Peach Proxy that setup tasks are about to run.

    This will disable fuzzing of messages so the setup tasks
    always work OK.
    '''
    
    logger.debug(">>setup()")

    __goto_correct_state(PeachInternalState.SETUP)

    global __peach_session
    if not __peach_session:
        logger.error("Called setup() w/o a session id")
        sys.exit(-1)

    global __peach_api
    if not __peach_api:
        logger.error("Called setup() w/o a peach_api url")
        sys.exit(-1)

    global __peach_headers
    global __peach_api_token
    if not __peach_api_token:
        logger.error("Called setup() w/o a peach_api_token")
        sys.exit(-1)

    try:
        r = session.post(
            "%s/api/sessions/%s/TestSetUp" % (__peach_api, session_id()),
            headers = __peach_headers)
        
        if r.status_code != 200:
            logger.error("Error calling TestSetUp for session '%s'", session_id())
            logger.error(__get_error(r))
            sys.exit(-1)
    except requests.exceptions.RequestException as e:
        logger.error("Error communicating with Peach API Security.")
        logger.error("vvvv ERROR vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv")
        logger.error(e)
        logger.error("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        sys.exit(-1)

def teardown():
    '''Notify Peach Proxy that teardown tasks are about to run.

    This will disable fuzzing of messages so the teardown tasks
    always work OK.
    
    Returns:
        str: Returns a string indicating next action
             Continue - Produce another of the current test case,
             NextTest - Move to next test case if any
             Error - Non-recoverable error has occurred. Exit.
    '''
    
    logger.debug(">>teardown")

    __goto_correct_state(PeachInternalState.TEARDOWN)

    global __peach_session
    if not __peach_session:
        logger.error("Called teardown() w/o a session id")
        sys.exit(-1)

    global __peach_api
    if not __peach_api:
        logger.error("Called teardown() w/o a peach_api url")
        sys.exit(-1)

    global __peach_headers
    global __peach_api_token
    if not __peach_api_token:
        logger.error("Called teardown() w/o a peach_api_token")
        sys.exit(-1)

    try:
        r = session.post(
            "%s/api/sessions/%s/TestTearDown" % (__peach_api, session_id()),
            headers = __peach_headers)
        
        if r.status_code != 200:
            logger.error("Error calling TestTearDown for session '%s'", session_id())
            logger.error(__get_error(r))
            sys.exit(-1)
        
        global __peach_state
        __peach_state = str(r.json())
        
        logger.debug("<<teardown: state: %s", __peach_state)
        
        return __peach_state
            
    except requests.exceptions.RequestException as e:
        logger.error("Error communicating with Peach API Security.")
        logger.error("vvvv ERROR vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv")
        logger.error(e)
        logger.error("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        sys.exit(-1)

def suite_teardown():
    '''Notify Peach that traffic generator has completed

    Normally this is called once the result of teardown() has indicate
    Peach has finished testing.  However, in the case that the
    traffic generator encounters a non-recoverable error,
    suite_teardown() will cause the Peach Job to error.
    '''
    
    logger.debug(">>suite_teardown")

    global __peach_session
    if not __peach_session:
        logger.error("Called suite_teardown() w/o a session id")
        sys.exit(-1)

    global __peach_api
    if not __peach_api:
        logger.error("Called suite_teardown() w/o a peach_api url")
        sys.exit(-1)

    global __peach_headers
    global __peach_api_token
    if not __peach_api_token:
        logger.error("Called suite_teardown() w/o a peach_api_token")
        sys.exit(-1)

    try:
        r = session.post(
            "%s/api/sessions/%s/TestSuiteTearDown" % (__peach_api, session_id()),
            headers = __peach_headers)

        if r.status_code != 200:
            logger.error("Error calling TestSuiteTearDown for session '%s'", session_id())
            logger.error(__get_error(r))
            sys.exit(-1)
            
    except requests.exceptions.RequestException as e:
        logger.error("Error communicating with Peach API Security.")
        logger.error("vvvv ERROR vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv")
        logger.error(e)
        logger.error("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        sys.exit(-1)

def testcase(name):
    '''Notify Peach Proxy that a test case is starting.
    This will enable fuzzing and group all of the following
    requests into a group.

    Keyword arguments:
    name -- Name of unit test. Shows up in metrics.
    '''
    
    logger.debug(">>testcase(%s)", name)

    __goto_correct_state(PeachInternalState.TEST)

    global __peach_session
    if not __peach_session:
        logger.error("Called testcase() w/o a session id")
        sys.exit(-1)

    global __peach_api
    if not __peach_api:
        logger.error("Called testcase() w/o a peach_api")
        sys.exit(-1)

    global __peach_headers
    global __peach_api_token
    if not __peach_api_token:
        logger.error("Called testcase() w/o a peach_api_token")
        sys.exit(-1)

    try:
        r = session.post(
            "%s/api/sessions/%s/testRun?name=%s" % (__peach_api, session_id(), name),
            headers = __peach_headers)
        
        if r.status_code != 200:
            logger.error("Error calling TestRun for session '%s'", session_id())
            logger.error(__get_error(r))
            sys.exit(-1)
    except requests.exceptions.RequestException as e:
        logger.error("Error communicating with Peach API Security.")
        logger.error("vvvv ERROR vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv")
        logger.error(e)
        logger.error("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        sys.exit(-1)

def junit_xml():
    '''Generate JUnit style XML output for use with CI integration.
    '''
        
    logger.debug(">>junit_xml")

    global __peach_session
    if not __peach_session:
        logger.error("Called junit_xml() w/o a session id")
        sys.exit(-1)

    global __peach_api
    if not __peach_api:
        logger.error("Called junit_xml() w/o a peach_api")
        sys.exit(-1)

    global __peach_headers
    global __peach_api_token
    if not __peach_api_token:
        logger.error("Called junit_xml() w/o a peach_api_token")
        sys.exit(-1)

    try:
        r = session.get(
            "%s/api/jobs/%s/junit" % (__peach_api, session_id()),
            headers = __peach_headers)
        if r.status_code != 200:
            logger.error("Error getting the junit xml for session '%s'", session_id())
            logger.error(__get_error(r))
            sys.exit(-1)
        
        return r.text
        
    except requests.exceptions.RequestException as e:
        logger.error("Error communicating with Peach API Security.")
        logger.error("vvvv ERROR vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv")
        logger.error(e)
        logger.error("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        sys.exit(-1)

def get_faults(job_id):
    '''Get list of job summaries
    '''

    logger.debug(">>get_jobs(%s)" % job_id)

    global __peach_api
    if not __peach_api:
        logger.error("Called session_setup() w/o a peach_api url")
        sys.exit(-1)
    
    global __peach_headers
    global __peach_api_token
    if not __peach_api_token:
        logger.error("Called session_setup() w/o a peach_api_token")
        sys.exit(-1)

    try:
        r = session.get(
                "%s/api/jobs/%s/faults" % (__peach_api, job_id), 
                headers=__peach_headers)
        if r.status_code != 200:
            logger.error("Error getting the faults for job '%s'", job_id)
            logger.error(__get_error(r))
            sys.exit(-1)

        return r.json()
        
    except requests.exceptions.RequestException as e:
        logger.error("Error communicating with Peach API Security.")
        logger.error("vvvv ERROR vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv")
        logger.error(e)
        logger.error("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        sys.exit(-1)


def get_fault(job_id, fault_id):
    '''Get list of job summaries
    '''

    logger.debug(">>get_jobs(%s)" % job_id)

    global __peach_api
    if not __peach_api:
        logger.error("Called session_setup() w/o a peach_api url")
        sys.exit(-1)
    
    global __peach_headers
    global __peach_api_token
    if not __peach_api_token:
        logger.error("Called session_setup() w/o a peach_api_token")
        sys.exit(-1)

    try:
        r = session.get(
                "%s/api/jobs/%s/faults/%s" % (__peach_api, job_id, fault_id), 
                headers=__peach_headers)
        if r.status_code != 200:
            logger.error("Error getting fault '%s' for job '%s'", fault_id, job_id)
            logger.error(__get_error(r))
            sys.exit(-1)

        return r.json()
        
    except requests.exceptions.RequestException as e:
        logger.error("Error communicating with Peach API Security.")
        logger.error("vvvv ERROR vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv")
        logger.error(e)
        logger.error("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        sys.exit(-1)


if __name__ == "__main__":

    print("This is a python module and should only be used by other")
    print("Python programs.  It was not intended to be run directly.")
    print("\n")
    print("For more information see the README")

# end
