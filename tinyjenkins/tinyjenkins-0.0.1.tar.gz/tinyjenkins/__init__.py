from distutils import version
import json
import logging
import threading

import munch
from oslo_utils import units
import requests
from requests.adapters import HTTPAdapter


LOG = logging.getLogger(__name__)

_JOB_PREFIX = "/job/"
_JOB_PREFIX_LEN = len(_JOB_PREFIX)


def _format_bytes(bytes_am):
    bytes_am = max(0, bytes_am)
    mb_am = float(bytes_am) / units.M
    gb_am = float(bytes_am) / units.G
    return "%0.2fMB/%0.2fGB" % (mb_am, gb_am)


def _find_build(builds, build_num):
    for build in builds:
        tmp_build_num = int(build.get("number", -1))
        if tmp_build_num == -1:
            continue
        if tmp_build_num == build_num:
            return build
    return None


def _combine_url(base, *path_pieces, **kwargs):
    url = base
    for piece in path_pieces:
        if not piece:
            continue
        if not url.endswith("/") and not piece.startswith("/"):
            url += "/"
        url += piece
    if kwargs.get('add_api_path', False):
        if not url.endswith("/"):
            url += "/"
        url += "api/json"
    return url


class RequestError(Exception):
    def __init__(self, response):
        self.url = response.url
        self.status_code = response.status_code
        self.content = response.content
        super(RequestError, self).__init__(
            "Failed calling '%s' due to %s: %s" % (self.url,
                                                   self.status_code,
                                                   self.content))


class NotFound(RequestError):
    pass


class BuildInvokeFailure(RequestError):
    pass


class Build(object):
    def __init__(self, build_num, build_url, job, jenkins):
        self._number = build_num
        self._url = build_url
        self._job = job
        self._jenkins = jenkins
        self._data = {}
        self._polled_am = 0
        self._poll_lock = threading.Lock()

    def get_console(self):
        url = _combine_url(self._url, 'consoleText')
        resp = self._jenkins._do_request("GET", url)
        return resp.text

    def get_result(self):
        self._do_first_poll()
        return self._data['result']

    def get_eta(self):
        self._do_first_poll()
        if 'estimatedDuration' in self._data:
            eta_ms = self._data['estimatedDuration']
            eta_sec = eta_ms / 1000.0
            return max(0, eta_sec)
        else:
            return float("inf")

    def is_running(self):
        self._do_first_poll()
        return self._data['building']

    def stop(self, before_poll=False):
        if before_poll:
            self.poll()
        # Assume it is still building if we have never polled before...
        still_building = self._data.get("building", True)
        if not still_building:
            return False
        url = _combine_url(self._url, 'stop')
        resp = self._jenkins._do_request("POST", url)
        if resp.status_code not in [200, 302]:
            raise RequestError(resp)
        return True

    def poll(self):
        with self._poll_lock:
            url = _combine_url(self._url, add_api_path=True)
            resp = self._jenkins._do_request("GET", url)
            if resp.status_code != 200:
                raise RequestError(resp)
            self._data.update(resp.json())
            self._polled_am += 1

    @property
    def url(self):
        return self._url

    @property
    def number(self):
        return self._number

    def _do_first_poll(self):
        if self._polled_am < 1:
            self.poll()

    def __str__(self):
        return "Build: '%s' (%s) for '%s'" % (self._number, self._url,
                                              self._job.name)


class QueuedBuild(object):
    def __init__(self, url, job, jenkins):
        self._url = url
        self._job = job
        self._data = {}
        self._jenkins = jenkins
        self._polled_am = 0
        self._poll_lock = threading.Lock()

    @property
    def url(self):
        return self._url

    def get_build(self):
        try:
            build_num = self._data['executable']['number']
            build_url = self._data['executable']['url']
        except KeyError:
            return None
        else:
            return Build(build_num, build_url,
                         self._job, self._jenkins)

    def poll(self):
        with self._poll_lock:
            url = _combine_url(self._url, add_api_path=True)
            resp = self._jenkins._do_request("GET", url)
            if resp.status_code != 200:
                raise RequestError(resp)
            self._data.update(resp.json())
            self._polled_am += 1

    def __str__(self):
        return "QueuedBuild: url at '%s'" % (self._url)


class _CommonJob(object):
    """Common stuff shared between jobs and job folders."""

    def __init__(self, jenkins, data, parents=None, expanded=False):
        self._jenkins = jenkins
        self._data = data
        self._parents = parents
        self._expanded = expanded
        self._expand_lock = threading.RLock()

    @property
    def description(self):
        if 'description' in self._data:
            descr = self._data["description"]
        else:
            self._do_expand()
            descr = self._data.get("description")
        if not descr:
            descr = ""
        return descr

    @property
    def url(self):
        return self._data["url"]

    @property
    def name(self):
        return self._data["name"]

    @property
    def full_name(self):
        name_pieces = []
        if self._parents:
            for name in self._parents:
                if name.startswith(_JOB_PREFIX):
                    name = name[_JOB_PREFIX_LEN:]
                name_pieces.append(name)
        name_pieces.append(self._data["name"])
        return "/".join(name_pieces)

    def _do_expand(self):
        with self._expand_lock:
            if self._expanded:
                return
            url = _combine_url(self.url, add_api_path=True)
            resp = self._jenkins._do_request("GET", url)
            if resp.status_code != 200:
                raise RequestError(resp)
            self._data.update(resp.json())


class Job(_CommonJob):
    _build_request_kwargs = {
        'params': {
            'tree': 'builds[number,url]',
        },
    }
    _all_build_request_kwargs = {
        'params': {
            'tree': 'allBuilds[number,url]',
        },
    }

    def __init__(self, jenkins, data, parents=None, expanded=False):
        super(Job, self).__init__(jenkins, data,
                                  parents=parents, expanded=expanded)
        self._params = None

    def get_build(self, build_num):
        url = _combine_url(self.url, add_api_path=True)
        resp = self._jenkins._do_request(
            "GET", url, request_kwargs=self._build_request_kwargs)
        if resp.status_code != 200:
            raise RequestError(resp)
        raw_builds = resp.json().get("builds", [])
        raw_build = _find_build(raw_builds, build_num)
        if raw_build is not None:
            return Build(build_num, raw_build['url'], self, self._jenkins)
        builds_nums_seen = list(int(raw_build.get('number', -1))
                                for raw_build in raw_builds)
        builds_nums_seen = list(tmp_build_num
                                for tmp_build_num in builds_nums_seen
                                if tmp_build_num >= 1)
        builds_nums_seen = sorted(builds_nums_seen)
        self._do_expand()
        maybe_more_builds = False
        try:
            first_build_num = self._data['firstBuild']['number']
        except KeyError:
            pass
        else:
            if (not builds_nums_seen or
                    (builds_nums_seen and
                        builds_nums_seen[0] != first_build_num)):
                maybe_more_builds = True
        if maybe_more_builds:
            resp = self._jenkins._do_request(
                "GET", url, request_kwargs=self._all_build_request_kwargs)
            if resp.status_code != 200:
                raise RequestError(resp)
            raw_builds = resp.json().get("allBuilds", [])
            raw_build = _find_build(raw_builds, build_num)
            if raw_build is not None:
                return Build(build_num, raw_build['url'], self, self._jenkins)
        return None

    def get_health_report(self, refresh=True):
        if refresh or 'healthReport' not in self._data:
            self._do_expand()
        if 'healthReport' not in self._data:
            return None
        else:
            if not self._data['healthReport']:
                return None
            else:
                first_report = self._data['healthReport'][0]
                return munch.Munch({
                    'description': first_report['description'],
                    'score': first_report['score'],
                })

    @property
    def color(self):
        return self._data["color"]

    def invoke(self, build_params=None):
        if build_params and not self.has_params():
            raise ValueError("Job '%s' does support passing"
                             " any build parameters" % self.name)
        if not build_params:
            build_params = {}
        else:
            build_params = build_params.copy()
        if not self.has_params():
            build_url = _combine_url(self.url, 'build')
        else:
            build_url = _combine_url(self.url, 'buildWithParameters')
        build_params_list = []
        build_params_dct = {}
        for k in sorted(build_params.keys()):
            v = build_params[k]
            if not isinstance(v, basestring):
                v = str(v)
            if isinstance(v, unicode):
                v = v.encode("utf-8")
            build_params_list.append({
                'name': k,
                'value': v,
            })
            build_params_dct[k] = v
        request_kwargs = {
            'allow_redirects': False,
        }
        if build_params:
            request_kwargs['params'] = build_params_dct
            request_kwargs['data'] = {
                'json': json.dumps(build_params_list),
            }
        resp = self._jenkins._do_request("POST", build_url,
                                         request_kwargs=request_kwargs)
        if resp.status_code in [200, 201, 303]:
            redirect_url = resp.headers['location']
            check_url = "%s/queue/item" % self._jenkins.base_url
            if not redirect_url.startswith(check_url):
                raise ValueError("Received bad redirect url from"
                                 " jenkins to '%s'" % redirect_url)
            LOG.debug("Redirecting recieved for build url '%s' to '%s'"
                      " with build params %s", build_url,
                      redirect_url, build_params)
            return QueuedBuild(redirect_url, self, self._jenkins)
        else:
            raise BuildInvokeFailure(resp)

    def _do_expand_params(self):
        with self._expand_lock:
            if self._params is None:
                self._do_expand()
                maybe_params = []
                for prop in self._data.get("property", []):
                    if 'parameterDefinitions' in prop:
                        maybe_params.extend(prop['parameterDefinitions'])
                for action_prop in self._data.get("actions", []):
                    if 'parameterDefinitions' in action_prop:
                        maybe_params.extend(
                            action_prop['parameterDefinitions'])
                params = []
                param_names_seen = set()
                for param in maybe_params:
                    param_name = param.get("name")
                    if not param_name or param_name in param_names_seen:
                        continue
                    params.append(param)
                    param_names_seen.add(param_name)
                self._params = sorted(params, key=lambda param: param['name'])

    def get_params(self):
        self._do_expand_params()
        return tuple(self._params)

    def has_params(self):
        self._do_expand_params()
        if self._params:
            return True
        return False


class JobFolder(_CommonJob):
    """A placeholder for a (not-expanded) folder."""


class Jenkins(object):
    """A *tiny* jenkins client that does not suck."""

    _job_request_kwargs = {
        'params': {
            'tree': 'jobs[name,color,url]',
        },
    }
    _job_folder_request_kwargs = {
        'params': {
            'tree': 'jobs[name,color]',
        },
    }

    def __init__(self, base_url, username, password,
                 ssl_verify=True, timeout=None, max_retries=5):
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._ssl_verify = ssl_verify
        self._username = username
        self._password = password
        self._max_retries = max_retries
        self._data = {}

    @property
    def max_retries(self):
        return self._max_retries

    @property
    def password(self):
        return self._password

    @property
    def username(self):
        return self._username

    @property
    def ssl_verify(self):
        return self._ssl_verify

    @property
    def base_url(self):
        return self._base_url

    @property
    def timeout(self):
        return self._timeout

    def _do_extract_headers_data(self, headers):
        if not headers:
            return
        raw_ver = headers.get("X-Jenkins")
        if raw_ver:
            self._data['version'] = version.LooseVersion(raw_ver)
        raw_sess = headers.get("X-Jenkins-Session")
        if raw_sess:
            self._data['session'] = raw_sess

    def _do_request(self, meth, url, request_kwargs=None):
        if request_kwargs is None:
            request_kwargs = {}
        if self._timeout is not None:
            request_kwargs['timeout'] = self._timeout
        with requests.Session() as sess:
            sess.auth = (self._username, self._password)
            sess.verify = self._ssl_verify
            if self._max_retries is not None and self._max_retries > 0:
                for h in ['http://', 'https://']:
                    sess.mount(h, HTTPAdapter(max_retries=self._max_retries))
            resp = sess.request(meth, url, **request_kwargs)
            self._do_extract_headers_data(resp.headers)
            return resp

    def get_plugins(self):
        plugin_url = _combine_url(self._base_url,
                                  'pluginManager', add_api_path=True)
        resp = self._do_request("GET", plugin_url,
                                request_kwargs={
                                    'params': {
                                        'depth': '1',
                                    },
                                })
        if resp.status_code != 200:
            raise RequestError(resp)
        plugins = []
        resp_details = resp.json()
        for plugin in resp_details.get('plugins', []):
            tmp_plugin = munch.Munch({
                'version': plugin['version'],
                'name': plugin['shortName'],
                'url': plugin['url'],
                'active': plugin['active'],
                'long_name': plugin['longName'],
                'enabled': plugin['enabled'],
            })
            plugins.append(tmp_plugin)
        return sorted(plugins, key=lambda plugin: plugin.name)

    def perform_restart(self, safe=True):
        if safe:
            restart_url = _combine_url(self._base_url, 'safeRestart')
        else:
            restart_url = _combine_url(self._base_url, 'restart')
        resp = self._do_request("POST", restart_url)
        if resp.status_code >= 400 and resp.status_code != 503:
            raise RequestError(resp)
        if resp.status_code not in [200, 202, 503]:
            return False
        return True

    def get_nodes(self):
        master_url = _combine_url(self._base_url,
                                  'computer', add_api_path=True)
        resp = self._do_request("GET", master_url)
        if resp.status_code != 200:
            raise RequestError(resp)
        resp_details = resp.json()
        nodes = []
        for node in resp_details.get('computer', []):
            tmp_node = munch.Munch({
                'master': False,
                'name': node['displayName'],
                'offline': node['offline'],
                'offline_cause': node.get("offlineCause"),
                'idle': node['idle'],
                'launch_supported': node['launchSupported'],
            })
            if node.get("_class", '').endswith("JCloudsComputer"):
                tmp_node.dynamic = True
            else:
                tmp_node.dynamic = False
            monitors = {}
            tmp_monitors = node.get("monitorData", {})
            for monitor_name, data in tmp_monitors.items():
                if monitor_name.endswith("SwapSpaceMonitor"):
                    monitors['total_memory'] = _format_bytes(
                        data['totalPhysicalMemory'])
                    monitors['available_memory'] = _format_bytes(
                        data['availablePhysicalMemory'])
                    monitors['available_swap_space'] = _format_bytes(
                        data['availableSwapSpace'])
                elif monitor_name.endswith("ClockMonitor"):
                    drift = str(data['diff']) + "ms"
                    if data['diff'] > 0:
                        drift = "+" + drift
                    monitors['clock_drift'] = drift
                elif monitor_name.endswith("TemporarySpaceMonitor"):
                    monitors['available_disk_space'] = _format_bytes(
                        data['size'])
                elif monitor_name.endswith("ArchitectureMonitor"):
                    monitors['architecture'] = data
                elif monitor_name.endswith("ResponseTimeMonitor"):
                    monitors['response_time'] = str(data['average']) + "ms"
            tmp_node.monitors = munch.Munch(monitors)
            if tmp_node.name == 'master':
                tmp_node.master = True
            nodes.append(tmp_node)
        return sorted(nodes, key=lambda node: node.name)

    def get_session(self):
        try:
            return self._data['session']
        except KeyError:
            # Force a request to happen to populate our internal data
            # including the version...
            resp = self._do_request("GET", self._base_url)
            if resp.status_code != 200:
                raise RequestError(resp)
            return self._data.get("session")

    def get_version(self):
        try:
            return self._data['version']
        except KeyError:
            # Force a request to happen to populate our internal data
            # including the version...
            resp = self._do_request("GET", self._base_url)
            if resp.status_code != 200:
                raise RequestError(resp)
            return self._data.get("version")

    def get_job(self, job_name):
        url = _combine_url(self._base_url, '/job/%s' % job_name,
                           add_api_path=True)
        resp = self._do_request("GET", url)
        if resp.status_code in [400, 404]:
            return None
        elif resp.status_code != 200:
            raise RequestError(resp)
        else:
            job_data = resp.json()
            return Job(self, job_data, expanded=True, parents=[])

    def _iter_things_in_folder(self, folder_data,
                               curr_path, yield_folders=False):
        job_path = '/job/%s' % folder_data['name']
        next_curr_path = list(curr_path)
        next_curr_path.append(job_path)
        url = _combine_url(self._base_url, *next_curr_path,
                           add_api_path=True)
        resp = self._do_request(
            "GET", url, request_kwargs=self._job_folder_request_kwargs)
        if resp.status_code == 200:
            resp_details = resp.json()
            for job_data in resp_details.get('jobs', []):
                # Apparently this is the best way to determine if the job
                # is a multi-job/folder and not really a single job?
                if 'color' not in job_data:
                    if yield_folders:
                        yield JobFolder(self, job_data,
                                        parents=tuple(next_curr_path))
                    things_in_folder_it = self._iter_things_in_folder(
                        job_data, next_curr_path, yield_folders=yield_folders)
                    for thing in things_in_folder_it:
                        yield thing
                else:
                    next_curr_path.append("/job/%s" % (job_data['name']))
                    try:
                        job_url = _combine_url(self._base_url, *next_curr_path)
                    finally:
                        next_curr_path.pop()
                    job_data['url'] = job_url
                    yield Job(self, job_data, parents=tuple(next_curr_path))
        elif resp.status_code >= 500:
            raise RequestError(resp)

    def iter_jobs(self, expand_folders=True, yield_folders=False):
        url = _combine_url(self._base_url, add_api_path=True)
        resp = self._do_request(
            "GET", url, request_kwargs=self._job_request_kwargs)
        if resp.status_code != 200:
            raise RequestError(resp)
        resp_details = resp.json()
        for job_data in resp_details.get('jobs', []):
            # Apparently this is the best way to determine if the job
            # is a multi-job/folder and not really a single job?
            if 'color' not in job_data:
                if expand_folders:
                    if yield_folders:
                        yield JobFolder(self, job_data, parents=[])
                    things_in_folder_it = self._iter_things_in_folder(
                        job_data, [], yield_folders=yield_folders)
                    for thing in things_in_folder_it:
                        yield thing
                else:
                    if yield_folders:
                        yield JobFolder(self, job_data, parents=[])
            else:
                yield Job(self, job_data, parents=[])
