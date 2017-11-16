"""
pyrkube.hosts
~~~~~~~~~~~~~~

Kubernetes hostname classes for pyrkube.

:copyright: (c) 2017 by Joe Black.
:license: Apache2.
"""

import socket

from . import config


def lookup_addr(fqdn):
    """Lookup an IP Address by hostname."""
    socket.setdefaulttimeout()
    try:
        return socket.gethostbyname(fqdn)
    except socket.gaierror:
        pass


def get_hostname(obj, domain=None):
    """Return a Hostname object depending on the type of object passed."""
    domain = domain or config.DOMAIN

    if isinstance(obj, str):
        length = len(obj.split('.'))
        if length == 6:
            return StatefulPodHostname(obj, domain)
        elif length == 5:
            return PodHostname(obj, domain)
        else:
            raise RuntimeError('Not sure how to process host for %s', obj)
    else:
        owner = obj.owner
        if owner:
            if owner.kind == 'StatefulSet':
                return StatefulPodHostname(obj, domain)
        return PodHostname(obj, domain)


class PodHostnameBase:
    """Base class for PodHostnames."""
    def __init__(self, obj, domain='cluster.local'):
        self.domain = domain
        if isinstance(obj, str):
            self.fqdn = obj
        else:
            self._init_from_pod(obj)

    @property
    def fqdn(self):
        """Returns a calculated FQDN for the hostname."""
        parts = self._parts + ('namespace', 'domain')
        args = [getattr(self, p) for p in parts]
        return self._join_fqdn(*args)

    @fqdn.setter
    def fqdn(self, fqdn):
        """"Allows a new kube hostname object to be set by manipulating the
        FQDN.
        """
        self._init_from_fqdn(fqdn)

    def __repr__(self):
        return '%s(%r)' % (
            type(self).__name__,
            self.fqdn
        )

    def __str__(self):
        return self.fqdn

    def _join_fqdn(self, *args):
        return '.'.join(args[:-1] + (self.type, args[-1]))

    def __lt__(self, other):
        return self.hostname < other.hostname


class PodHostname(PodHostnameBase):
    """Represents a kubernetes 'Pod' hostname.

    A Kubernetes hostname where individual parts can be manipulated and the
    hostname is updated.  str(host) will return the hostname as a string.
    """

    type = 'pod'
    _parts = ('hostname',)

    def _init_from_pod(self, pod):
        self.ip = pod.status.podIP
        self.hostname = self.ip.replace('.', '-')
        self.namespace = pod.metadata.namespace

    def _init_from_fqdn(self, fqdn):
        self.hostname, self.namespace, _, self.domain = fqdn.split('.', 3)
        self.ip = self.hostname.replace('-', '.')

    def clone(self):
        """Clone's a copy of the current KubeHostname object.

        Options include requesting the KubeHostname for the master or by
        passing an index.
        """
        return type(self)(self.fqdn)


class StatefulPodHostname(PodHostnameBase):
    """Represents a kubernetes 'StatefulSet' hostname.

    A Kubernetes hostname where individual parts can be manipulated and the
    hostname is updated.  str(host) will return the hostname as a string.
    """

    type = 'svc'
    _parts = ('hostname', 'subdomain')

    @staticmethod
    def _get_hostname(pod):
        return (
            pod.metadata.get('hostname') or
            pod.metadata.annotations.get('pod.beta.kubernetes.io/hostname')
        )

    @staticmethod
    def _get_subdomain(pod):
        return (
            pod.metadata.get('subdomain') or
            pod.metadata.annotations.get('pod.beta.kubernetes.io/subdomain')
        )

    def _init_from_pod(self, pod):
        self.ip = pod.status.podIP
        self.hostname = self._get_hostname(pod)
        self.subdomain = self._get_subdomain(pod)
        self.namespace = pod.metadata.namespace

    def _init_from_fqdn(self, fqdn):
        # self.ip = lookup_addr(fqdn)

        self.hostname, self.subdomain, self.namespace, _, self.domain = (
            fqdn.split('.', 4)
        )

    @property
    def hostname(self):
        """Retrieves the first part of the kubernetes hostname.
        Example: `couchdb-0`
        """
        return '%s-%s' % (self.statefulset, self.index)

    @hostname.setter
    def hostname(self, hostname):
        """Allows the first part of the kubernetes hostname to be set and a
        new hostname object recalculated.
        """
        self.statefulset, index = hostname.split('-')
        self.index = int(index)

    @property
    def is_master(self):
        """Determines whether the index is 0 for when the master of a
        StatefulSet needs to be determined."""
        return self.index == 0

    def clone(self, master=False, index=None):
        """Clone's a copy of the current KubeHostname object.

        Options include requesting the KubeHostname for the master or by
        passing an index.
        """
        new = type(self)(self.fqdn)
        if index:
            new.index = index
        elif master:
            new.index = 0
        return new
