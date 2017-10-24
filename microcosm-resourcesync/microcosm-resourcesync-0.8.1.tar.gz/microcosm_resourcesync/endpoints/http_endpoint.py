"""
HTTP endpoint.

"""
from os.path import commonprefix
from six.moves.urllib.parse import urlparse, urlunparse
from sys import stderr

from click import echo, progressbar
from requests import Session
from requests.exceptions import ConnectionError, HTTPError

from microcosm_resourcesync.batching import batched
from microcosm_resourcesync.endpoints.base import Endpoint
from microcosm_resourcesync.formatters import Formatters


class BatchingNotSupported(Exception):
    pass


class HTTPEndpoint(Endpoint):
    """
    Read and write resources for an HTTP URI.

    """
    def __init__(self, uri):
        self.uri = uri
        self.session = Session()
        self.allowed_methods_cache = dict()

    def __repr__(self):
        return "{}('{}')".format(
            self.__class__.__name__,
            self.uri,
        )

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.uri == other.uri

    @property
    def default_formatter(self):
        return Formatters.JSON.name

    def read(self, schema_cls, follow_mode, **kwargs):
        """
        Read all YAML documents from the file.

        """
        deque, seen = [self.uri], set()

        while deque:
            uri = deque.pop()
            if uri in seen:
                continue

            resource_data = self.read_resource_data(uri, **kwargs)
            for resource in self.iter_resources(resource_data, schema_cls):
                try:
                    resource.id
                    if resource.uri not in seen:
                        yield resource
                        seen.add(resource.uri)
                except Exception:
                    # ignore resources that do not have identifiers (e.g. collections)
                    pass

                # expand resource links, preferring pagination because it returns batches
                page_links = [
                    link.uri
                    for link in resource.links(follow_mode)
                    if link.uri not in seen and link.relation in ("prev", "next")
                ]
                other_links = [
                    link.uri
                    for link in resource.links(follow_mode)
                    if link.uri not in seen and link.relation not in ("prev", "next")
                ]
                deque = other_links + deque + page_links

            # done processing this uri (in paginated cases, this uri won't match any resource.uri)
            seen.add(uri)

    def read_resource_data(self, uri, verbose, limit, auth=None, **kwargs):
        """
        Read resource data from a URI.

        """
        if verbose:
            echo("Fetching resource(s) from: {}".format(uri), err=True)

        response = self.session.get(
            uri,
            headers={
                "X-Request-Limit": str(limit),
            },
            auth=auth,
        )
        # NB: if resources have broken hyperlinks, we can get a 404 here
        if verbose and response.status_code >= 400:
            echo("Failed fetching resource(s) from: {}: {}".format(uri, response.text))
        response.raise_for_status()
        content_type = response.headers["Content-Type"]
        formatter = Formatters.for_content_type(content_type).value
        return formatter.load(response.text)

    def write(self, resources, **kwargs):
        """
        Write resources as YAML to an HTTP endpoint.

        """
        with progressbar(length=len(resources), file=stderr) as progress_bar:
            for resource_batch in batched(resources, **kwargs):
                self.write_resources(resource_batch, **kwargs)
                progress_bar.update(len(resource_batch))

    def write_resources(self, resource_batch, **kwargs):
        """
        Write several resources.

        """
        try:
            # attempt to write resources in a batch
            if len(resource_batch) > 1:
                self.write_resource_batch(resource_batch, **kwargs)
                return
        except BatchingNotSupported:
            # fall through
            pass

        # write resources once at a time
        for resource in resource_batch:
            self.write_resource(resource, **kwargs)

    def write_resource_batch(self, resource_batch, formatter, max_attempts=2, verbose=False, auth=None, **kwargs):
        """
        Write resources in a batch.

        Uses the microcosm `BatchUpdate` convention to PATCH the base collection URI.

        """
        uri = commonprefix([
            self.join_uri(resource.uri)
            for resource in resource_batch
        ]).rstrip("/")

        allowed_methods = self.get_allowed_methods(uri)

        if "PATCH" not in allowed_methods:
            raise BatchingNotSupported()

        if verbose:
            echo("Batch updating resource(s) for: {}".format(uri), err=True)

        data = formatter.value.dump(dict(
            items=resource_batch,
        ))

        response = self.retry(
            self.session.patch,
            uri=uri,
            auth=auth,
            data=data,
            headers={
                "Content-Type": formatter.value.preferred_mime_type,
            },
            max_attempts=max_attempts,
        )
        response.raise_for_status()

    def get_allowed_methods(self, uri):
        """
        Use an OPTIONS query to compute the allowed methods for a URI.

        Cache these results locally to avoid extra requests when batching is not supported.

        """
        if uri in self.allowed_methods_cache:
            return self.allowed_methods_cache[uri]
        response = self.session.options(uri)
        allowed_methods = response.headers.get("Allow", [])
        self.allowed_methods_cache[uri] = allowed_methods
        return allowed_methods

    def write_resource(self, resource, formatter, max_attempts, auth=None, **kwargs):
        """
        Write a single resource via Replace conntetion (PUT).

        """
        uri = self.join_uri(resource.uri)
        data = formatter.value.dump(resource)

        # NB: verbose logging the message content is obnoxius and interferes with the
        # progressbar; if we need more information here, we probably need more levels
        # of verbosity and a more traditional progress bar

        response = self.retry(
            self.session.put,
            uri=uri,
            auth=auth,
            data=data,
            headers={
                "Content-Type": formatter.value.preferred_mime_type,
            },
            max_attempts=max_attempts,
        )
        response.raise_for_status()

    def join_uri(self, uri):
        """
        Construct a URL using the configured base URL's scheme and netloc and the remainder of the resource's URI.

        This is what `urljoin` ought to do...

        """
        parsed_base_uri = urlparse(self.uri)
        parsed_uri = urlparse(uri)
        return urlunparse(parsed_uri._replace(
            scheme=parsed_base_uri.scheme,
            netloc=parsed_base_uri.netloc,
        ))

    def iter_resources(self, resource_data, schema_cls):
        """
        Iterate over resources in a resource.

        """
        resource = schema_cls(resource_data)

        yield resource

        # process embedded resources (e.g. collections)
        for embedded_resource in resource.embedded:
            yield schema_cls(embedded_resource)

    def retry(self, func, uri, max_attempts, **kwargs):
        """
        Retry HTTP operations on connection failures.

        """
        last_error = None
        for attempt in range(max_attempts):
            try:
                return func(uri, **kwargs)
            except ConnectionError as error:
                echo("Connection error for uri: {}: {}".format(uri, error), err=True)
                last_error = error
                continue
            except HTTPError as error:
                if error.response.status_code in (504, 502):
                    echo("HTTP error for uri: {}: {}".format(uri, error), err=True)
                    last_error = error
                    continue
                raise
            else:
                break
        else:
            # If we reached here, all attempts were unsuccessful - raise last error encountered
            raise last_error
