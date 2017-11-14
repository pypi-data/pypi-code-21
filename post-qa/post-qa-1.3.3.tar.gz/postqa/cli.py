"""Command line interface / runner."""

from __future__ import (division, absolute_import, print_function,
                        unicode_literals)
from builtins import *  # NOQA
from future.standard_library import install_aliases
install_aliases()  # NOQA

import sys
import argparse
import json

import requests

from . import jsonshim
from . import lsstsw
from . import jenkinsenv
from .schemas import load_schema, validate


def run_post_qa():
    """CLI entrypoint for the ``post-qa`` command."""
    args = parse_args()

    registered_metrics = load_registered_metrics(api_url=args.api_url)

    metric_json, job_json = build_json_docs(args.qa_json_path,
                                            args.lsstsw_dirname,
                                            args.probe_git,
                                            registered_metrics)
    if not args.test:
        if metric_json:
            upload_json_doc(metric_json, api_url=args.api_url,
                            api_endpoint='metrics',
                            api_user=args.api_user,
                            api_password=args.api_password)

        upload_json_doc(job_json, api_url=args.api_url,
                        api_endpoint='jobs',
                        api_user=args.api_user,
                        api_password=args.api_password)
    else:
        print(json.dumps(metric_json, indent=2, sort_keys=True))
        print(json.dumps(job_json, indent=2, sort_keys=True))


def parse_args():
    parser = argparse.ArgumentParser(
        description="""Upload JSON from validate_drp to the SQuaSH API

This script is meant to be run from a Jenkins CI environment
and uses the following environment variables:

- ``BUILD_ID`` : ID in the ci system
- ``BUILD_URL``: ci page with information about the build
- ``PRODUCT``: the name of the product built, in this case 'validate_drp'
- ``dataset``: the name of the dataset processed by validate_drp
- ``label`` : the name of the platform where it runs
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        '--lsstsw',
        dest='lsstsw_dirname',
        required=True,
        help='Path of lsstsw directory')
    parser.add_argument(
        '--qa-json',
        dest='qa_json_path',
        required=True,
        help='Filename of QA JSON output file')
    parser.add_argument(
        '--api-url',
        dest='api_url',
        required=True,
        help='URL of SQuaSH API')
    parser.add_argument(
        '--api-user',
        dest='api_user',
        required=True,
        help='Username for SQuaSH API')
    parser.add_argument(
        '--api-password',
        dest='api_password',
        required=True,
        help='Password for SQuaSH API')
    parser.add_argument(
        '--test',
        default=False,
        action='store_true',
        help='Print the shimmed JSON rather than uploading it')

    feature_parser = parser.add_mutually_exclusive_group(required=False)
    feature_parser.add_argument(
        '--probe-git',
        dest='probe_git',
        action='store_true')
    feature_parser.add_argument(
        '--no-probe-git',
        dest='probe_git',
        action='store_false')
    parser.set_defaults(probe_git=True)
    return parser.parse_args()


def build_json_docs(
        qa_json_path,
        lsstsw_dirname,
        probe_git=True,
        registered_metrics=[]):
    """Build a json message for SQUASH's /api/jobs endpoint from
    validate_drp-type JSON data.
    """
    # Shim validate_drp's JSON to SQuaSH measurements format
    with open(qa_json_path) as f:
        qa_json = json.load(f, encoding='utf-8')
    metric_json, job_json = jsonshim.shim_validate_drp(qa_json,
                                                       registered_metrics)

    # Add 'packages' sub-document
    lsstsw_install = lsstsw.Lsstsw(
            dirname=lsstsw_dirname,
            probe_git=probe_git)
    job_json.update(lsstsw_install.json)

    # Add metadata from the CI environment
    jenkins = jenkinsenv.JenkinsEnv()
    job_json.update(jenkins.json)

    # Validate
    metric_schema = load_schema(schema='metric')
    validate(metric_json, metric_schema)

    job_schema = load_schema(schema='job')
    validate(job_json, job_schema)

    return metric_json, job_json


# memoizing the return from this method made a mess of testing; need some sort
# of resetable memoization in order to enable proper testing.
def get_endpoint_urls(api_url):
    """Lookup endpoint URL.
    """

    try:
        r = requests.get(api_url)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)

    return r.json()


def load_registered_metrics(api_url):
    """Return list of metrics registered in SQuaSH.
    """
    metric_endpoint_url = get_endpoint_urls(api_url)['metrics']

    try:
        r = requests.get(metric_endpoint_url)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)

    registered_metrics = [m['metric'] for m in r.json()['results']]

    return registered_metrics


def upload_json_doc(json_doc, api_url, api_endpoint,
                    api_user=None, api_password=None):
    """Upload json document to SQuaSH through a POST request to the
    API endpoint.
    """

    api_endpoint_url = get_endpoint_urls(api_url)[api_endpoint]

    try:
        # disable redirect following for POST as requests will turn a POST into
        # a GET when following a redirect
        # https://github.com/kennethreitz/requests/commit/95a03532c36f1afd38c395f7160c7f7086557b7b
        r = requests.post(api_endpoint_url,
                          auth=(api_user, api_password),
                          json=json_doc,
                          allow_redirects=False)
        print('POST {0} status: {1}'.format(api_endpoint_url, r.status_code))
        r.raise_for_status()

        # be pedantic about return status. requests#status_code will not error
        # on 3xx codes
        if r.status_code != 201:
            print('Expected 201 -- Got:', r.status_code, r.reason)
            sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(json.dumps(json_doc))
        print(e)
        sys.exit(1)
