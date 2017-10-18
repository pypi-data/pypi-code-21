import re
import time

import pendulum
import requests
import singer


# By default, jobs will run for 30 minutes and be polled every 5 minutes.
JOB_TIMEOUT = 60 * 30
POLL_INTERVAL = 60 * 5

# If Corona is not supported, an error "1035" will be returned by the API.
# http://developers.marketo.com/rest-api/bulk-extract/bulk-lead-extract/#filters
NO_CORONA_CODE = "1035"

# Marketo limits REST requests to 50000 per day with a rate limit of 100
# calls per 20 seconds.
# http://developers.marketo.com/rest-api/
MAX_DAILY_CALLS = int(50000 * 0.8)
RATE_LIMIT_CALLS = 100
RATE_LIMIT_SECONDS = 20

DEFAULT_USER_AGENT = "Singer.io/tap-marketo"
DOMAIN_RE = r"([\d]{3}-[\w]{3}-[\d]{3})"


def extract_domain(url):
    result = re.search(DOMAIN_RE, url)
    if not result:
        raise ValueError("%s is not a valid Marketo URL" % url)
    return result.group()


class ApiException(Exception):
    """Indicates an error occured communicating with the Marketo API."""
    pass


class ExportFailed(Exception):
    """Indicates an error occured while attempting a bulk export."""
    pass

class Client:
    # pylint: disable=unused-argument
    def __init__(self, endpoint, client_id, client_secret,
                 max_daily_calls=MAX_DAILY_CALLS,
                 user_agent=DEFAULT_USER_AGENT,
                 job_timeout=JOB_TIMEOUT,
                 poll_interval=POLL_INTERVAL, **kwargs):

        self.domain = extract_domain(endpoint)
        self.client_id = client_id
        self.client_secret = client_secret
        self.max_daily_calls = int(max_daily_calls)
        self.user_agent = user_agent
        self.job_timeout = job_timeout
        self.poll_interval = poll_interval

        self.token_expires = None
        self.access_token = None
        self.calls_today = 0

        self._session = requests.Session()
        self._use_corona = None

    @property
    def use_corona(self):
        if getattr(self, "_use_corona", None) is None:
            self._use_corona = self.test_corona()
        return self._use_corona

    @property
    def headers(self):
        # http://developers.marketo.com/rest-api/authentication/#using_an_access_token
        if not self.token_expires or self.token_expires <= pendulum.utcnow():
            self.refresh_token()

        return {
            "Authorization": "Bearer {}".format(self.access_token),
            "User-Agent": self.user_agent,
        }

    def get_url(self, url):
        return "https://{}.mktorest.com/{}".format(self.domain, url)

    def get_bulk_endpoint(self, stream_name, action, export_id=None):
        endpoint = "bulk/v1/{}/export/".format(stream_name)
        if export_id is not None:
            endpoint += "{}/".format(export_id)
        endpoint += "{}.json".format(action)
        return endpoint

    @singer.utils.backoff((requests.exceptions.RequestException), singer.utils.exception_is_4xx)
    def refresh_token(self):
        # http://developers.marketo.com/rest-api/authentication/#creating_an_access_token
        params = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        singer.log_info("Refreshing token")

        try:
            url = self.get_url("identity/oauth/token")
            resp = requests.get(url, params=params)
            resp_time = pendulum.utcnow()
        except requests.exceptions.ConnectionError:
            raise ApiException("Connection error while refreshing token at %s.", url)

        if resp.status_code != 200:
            raise ApiException("Error refreshing token [%s]: %s", resp.status_code, resp.content)

        data = resp.json()
        if "error" in data:
            if data["error"] == "unauthorized":
                msg = "Authorization failed: "
            else:
                msg = "API returned an error: "

            msg += data.get("error_description", "No message from api")
            raise ApiException(msg)

        self.access_token = data["access_token"]
        self.token_expires = resp_time.add(seconds=data["expires_in"] - 15)
        singer.log_info("Token valid until %s", self.token_expires)

    @singer.utils.ratelimit(RATE_LIMIT_CALLS, RATE_LIMIT_SECONDS)
    @singer.utils.backoff((requests.exceptions.RequestException), singer.utils.exception_is_4xx)
    def _request(self, method, url, endpoint_name=None, stream=False, **kwargs):
        endpoint_name = endpoint_name or url
        url = self.get_url(url)
        headers = kwargs.pop("headers", {})
        headers.update(self.headers)
        req = requests.Request(method, url, headers=headers, **kwargs).prepare()
        singer.log_info("%s: %s", method, req.url)
        with singer.metrics.http_request_timer(endpoint_name):
            resp = self._session.send(req, stream=stream)

        resp.raise_for_status()
        return resp

    def update_calls_today(self):
        # http://developers.marketo.com/rest-api/endpoint-reference/lead-database-endpoint-reference/#!/Usage/getDailyUsageUsingGET
        data = self._request("GET", "rest/v1/stats/usage.json").json()
        if "result" not in data:
            raise ApiException(data)

        self.calls_today = int(data["result"][0]["total"])
        singer.log_info("Used %s of %s requests", self.calls_today, self.max_daily_calls)

    def request(self, method, url, endpoint_name=None, **kwargs):
        if self.calls_today % 250 == 0:
            self.update_calls_today()

        self.calls_today += 1
        if self.calls_today > self.max_daily_calls:
            raise ApiException("Exceeded daily quota of %s calls", self.max_daily_calls)

        resp = self._request(method, url, endpoint_name, **kwargs)
        if "stream" not in kwargs:
            if resp.content == b'':
                raise ApiException("Something went wrong and the API returned nothing.")

            data = resp.json()
            if not data["success"]:
                err = ", ".join("{code}: {message}".format(**e) for e in data["errors"])
                raise ApiException("API returned error(s): {}".format(err))

            return data
        else:
            if resp.status_code != 200:
                raise ApiException("API returned error: {0.status_code}: {0.content}".format(resp))

            return resp.iter_lines()

    def create_export(self, stream_type, fields, query):
        # http://developers.marketo.com/rest-api/bulk-extract/#creating_a_job
        payload = {
            "format": "CSV",
            "fields": fields,
            "filter": query
        }

        endpoint = self.get_bulk_endpoint(stream_type, "create")
        endpoint_name = "{}_create".format(stream_type)
        singer.log_info('Scheduling export job with query %s', query)
        data = self.request("POST", endpoint, endpoint_name=endpoint_name, json=payload)
        return data["result"][0]["exportId"]

    def enqueue_export(self, stream_type, export_id):
        # http://developers.marketo.com/rest-api/bulk-extract/#starting_a_job
        endpoint = self.get_bulk_endpoint(stream_type, "enqueue", export_id)
        endpoint_name = "{}_enqueue".format(stream_type)
        self.request("POST", endpoint, endpoint_name=endpoint_name)

    def cancel_export(self, stream_type, export_id):
        # http://developers.marketo.com/rest-api/bulk-extract/#cancelling_a_job
        endpoint = self.get_bulk_endpoint(stream_type, "cancel", export_id)
        endpoint_name = "{}_cancel".format(stream_type)
        self.request("POST", endpoint, endpoint_name=endpoint_name)

    def poll_export(self, stream_type, export_id):
        # http://developers.marketo.com/rest-api/bulk-extract/#polling_job_status
        endpoint = self.get_bulk_endpoint(stream_type, "status", export_id)
        endpoint_name = "{}_poll".format(stream_type)
        data = self.request("GET", endpoint, endpoint_name=endpoint_name)
        return data["result"][0]["status"]

    def stream_export(self, stream_type, export_id):
        # http://developers.marketo.com/rest-api/bulk-extract/#retrieving_your_data
        endpoint = self.get_bulk_endpoint(stream_type, "file", export_id)
        endpoint_name = "{}_stream".format(stream_type)
        return self.request("GET", endpoint, endpoint_name=endpoint_name, stream=True)

    def wait_for_export(self, stream_type, export_id):
        # Poll the export status until it enters a finalized state or
        # exceeds the job timeout time.
        timeout_time = pendulum.utcnow().add(seconds=self.job_timeout)
        while pendulum.utcnow() < timeout_time:
            status = self.poll_export(stream_type, export_id)
            singer.log_info("export %s status is %s", export_id, status)

            if status == "Created":
                # If the status is created, the export has been made but
                # not started, so enqueue the export.
                self.enqueue_export(stream_type, export_id)

            elif status in ["Cancelled", "Failed"]:
                # Cancelled and failed exports fail the current sync.
                raise ExportFailed(status)

            elif status == "Completed":
                return True

            time.sleep(self.poll_interval)

        raise ExportFailed("Timed out")

    def test_corona(self):
        # http://developers.marketo.com/rest-api/bulk-extract/#limits
        # Corona allows us to do bulk queries for Leads using updatedAt
        # as a filter. Clients without Corona (should only be clients
        # with < 50,000 Leads) must do a full bulk export every sync.
        # We test for Corona by requesting a one-second export of leads
        # using the updatedAt filter.
        singer.log_info("Testing for Corona support")
        start_pen = pendulum.utcnow().subtract(days=1).replace(microsecond=0)
        end_pen = start_pen.add(seconds=1)
        payload = {
            "format": "CSV",
            "fields": ["id"],
            "filter": {
                "updatedAt": {
                    "startAt": start_pen.isoformat(),
                    "endAt": end_pen.isoformat(),
                },
            },
        }
        endpoint = self.get_bulk_endpoint("leads", "create")
        data = self._request("POST", endpoint, endpoint_name="leads_create", json=payload).json()

        # If the error code indicating no Corona support is present,
        # Corona is not supported. If we don't get that error code,
        # Corona is supported and we need to clean up by cancelling the
        # test export we requested.
        err_codes = set(err["code"] for err in data.get("errors", []))
        if NO_CORONA_CODE in err_codes:
            singer.log_info("Corona not supported.")
            return False
        else:
            singer.log_info("Corona is supported.")
            self.cancel_export("leads", data["result"][0]["exportId"])
            return True
