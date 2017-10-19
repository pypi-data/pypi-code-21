#!/usr/bin/env python
"""
TravisCI manipulation utility class.
"""
# pylint: disable=unused-argument
from __future__ import print_function
import base64
import os
import requests
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from apikit import BackendError, retry_request, raise_from_response, raise_ise


class TravisCI(object):
    """TravisCI represents an object presenting methods to facilitate
    TravisCI interactions from Python."""

    # Module static constants.
    travis_host = "https://api.travis-ci.org"
    # User-Agent must start with the string "Travis".
    # This is not documented by Travis CI and indeed the documentation
    #  states otherwise.  Nevertheless, it appears to be true.
    travis_headers = {
        "Content-Type": "application/json",
        "Accept": "application/vnd.travis-ci.2+json",
        "User-Agent": "TravisLSSTAPI/0.1.0"
    }

    github_token = None
    travis_token = None
    public_keys = {}

    def __init__(self, github_token=None, travis_token=None):
        self.github_token = github_token
        if travis_token:
            self.travis_token = travis_token
        else:
            self.travis_token = self.exchange_token()
        self.travis_headers["Authorization"] = "token " + self.travis_token
        # Check authentication and fail if it doesn't work.
        req = requests.get(self.travis_host + "/", headers=self.travis_headers)
        raise_from_response(req)

    # pylint: disable=no-self-use
    def _debug(self, *args):
        """Super-cheesy way to get debugging output.
        """
        if os.environ.get("DEBUG"):
            print("DEBUG:", *args)

    def exchange_token(self):
        """Exchange a GitHub token for a TravisCI one.
        """
        travis_token_url = self.travis_host + "/auth/github"
        postdata = {
            "github_token": self.github_token
        }
        self._debug("Exchanging GitHub token for Travis CI token")
        req = requests.post(travis_token_url, headers=self.travis_headers,
                            json=postdata)
        raise_from_response(req)
        # pylint: disable=broad-except
        try:
            rdata = req.json()
        except Exception as exc:
            raise_ise(str(exc))
        access_token = rdata.get("access_token")
        if not access_token:
            raise BackendError(status_code=403,
                               reason="Forbidden",
                               content="Unable to get Travis CI access token")
        self._debug("Travis CI token acquired")
        return access_token

    def start_travis_sync(self):
        """Initiate a Travis <-> GH Sync"""
        sync_url = self.travis_host + "/users/sync"
        # Start sync
        req = requests.post(sync_url, headers=self.travis_headers)
        if req.status_code == 409:
            # 409 is "already syncing"; so we pretend it was ours.
            req.status_code = 200
        raise_from_response(req)
        self._debug("Travis CI <-> GitHub Sync started")

    def enable_travis_webhook(self, slug, retry_args=None):
        """Enable repository for Travis CI.

        Parameters
        ----------
        slug : `str`
            GitHub repository slug (``<org>/<repo>``).
        retry_args : `dict`, optional
            Optional dictionary of keyward arguments passed to
            `apikit.retry_request`. Use this to control the number of retries
            attempted (``'tries'`` key) or interval factor
            (``'initial_interval' key, in seconds).
        """
        self.set_travis_webhook(slug, enabled=True, retry_args=retry_args)

    def disable_travis_webhook(self, slug, retry_args=None):
        """Disable repository for Travis CI.

        Parameters
        ----------
        slug : `str`
            GitHub repository slug (``<org>/<repo>``).
        retry_args : `dict`, optional
            Optional dictionary of keyward arguments passed to
            `apikit.retry_request`. Use this to control the number of retries
            attempted (``'tries'`` key) or interval factor
            (``'initial_interval' key, in seconds).
        """
        self.set_travis_webhook(slug, enabled=False, retry_args=retry_args)

    def set_travis_webhook(self, slug, enabled=True, retry_args=None):
        """Enable/disable repository for Travis CI.

        Parameters
        ----------
        slug : `str`
            GitHub repository slug (``<org>/<repo>``).
        retry_args : `dict`, optional
            Optional dictionary of keyward arguments passed to
            `apikit.retry_request`. Use this to control the number of retries
            attempted (``'tries'`` key) or interval factor
            (``'initial_interval' key, in seconds).
        """
        # pylint: disable=too-many-locals
        if retry_args is None:
            retry_args = {}
        self.start_travis_sync()
        user_url = self.travis_host + "/repos/" + slug
        req = retry_request("get", user_url,
                            headers=self.travis_headers,
                            **retry_args)
        # Get the ID and flip the switch
        # pylint: disable=broad-except
        try:
            repo_id = req.json()["repo"]["id"]
        except Exception as exc:
            raise_ise(str(exc))
        self._debug("GitHub Repository ID: %s" % repo_id)
        hook_url = self.travis_host + "/hooks"
        hook = {
            "hook": {
                "id": repo_id,
                "active": enabled
            }
        }
        self._debug("Webhook payload:", hook)
        req = retry_request("put", hook_url, headers=self.travis_headers,
                            payload=hook,
                            **retry_args)
        raise_from_response(req)

    def get_public_key(self, repo):
        """Retrieve public key from travis repo.
        """
        if repo in self.public_keys:
            return self.public_keys[repo]
        keyurl = self.travis_host + "/repos/%s/key" % repo
        # pylint: disable=broad-except, bad-continuation
        req = retry_request("get", keyurl, headers=self.travis_headers)
        raise_from_response(req)
        try:
            keyjson = req.json()
        except Exception as exc:
            raise_ise(str(exc))
        pubkey = keyjson.get("key")
        if pubkey:
            self.public_keys[repo] = pubkey
        return pubkey

    # Adapted from https://github.com/lsst-sqre/travis-encrypt
    # Forked from https://github.com/sivel/travis-encrypt
    # Thanks to Matt Martz
    def travis_encrypt(self, public_key, data):
        """Encrypt data with supplied public key.
        """
        key = RSA.importKey(public_key)
        cipher = PKCS1_v1_5.new(key)
        self._debug("Attempting encryption of string.")
        # Python 2/3
        try:
            bdata = bytes(data, "utf8")
        except TypeError:
            bdata = bytes(data)
        retval = base64.b64encode(cipher.encrypt(bdata)).decode("utf8")
        self._debug("Encryption succeeded.")
        return retval

    def create_travis_secure_string(self, public_key, data):
        """Create encrypted entry for travis.yml from data and key.
        """
        encstring = self.travis_encrypt(public_key, data)
        return "secure: \"%s\"" % encstring

    def travis_encrypt_for_repo(self, repo, data):
        """Encrypt data with public key for supplied repo name.
        """
        pubkey = self.get_public_key(repo)
        return self.travis_encrypt(pubkey, data)

    # pylint: disable=invalid-name
    def create_travis_secure_string_for_repo(self, repo, data):
        """Create encrypted entry for travis.yml from data and repo name.
        """
        pubkey = self.get_public_key(repo)
        return self.create_travis_secure_string(pubkey, data)
