"""Memento support.

Memento specifies dates
https://tools.ietf.org/html/rfc7089#section-2.1.1
in terms of
https://tools.ietf.org/html/rfc1123#section-5.2.14
which is a modification of the original mail definition
https://tools.ietf.org/html/rfc822#section-5
to use 4-digit years instead of 2.

This is a subset of one of the three formats defined for HTTP Full Date in
https://tools.ietf.org/html/rfc2616#section-3.3.1
and repeated as IMF-fixdate (without reference to rfc1123) in the more recent
https://tools.ietf.org/html/rfc7231#section-7.1.1.1

Points to note:

  * Memento dates MUST be have timezone indicator "GMT" (not Z, not +0000)
  * Memento dates do not support sub-second accuracy

In Python it seems that the permissive way to parse various mail-type dates
(ie. rfc822/2822) is with email.utils.parsedate(..). However, since the
Memento version is very restrictive, it seems that datetime.datetime.strptime(..)
provides a better method, accepting only the allowed form.
"""

from datetime import datetime
try:  # Python 3
    from datetime.timezone import utc
except:  # Python 2
    from dateutil.tz import tzutc as utc


TIME_FORMAT = '%a, %d %b %Y %H:%M:%S GMT'


def memento_parse_datetime(datetime_str):
    """Parse Memento datetime_str into datetime.datetime object."""
    return datetime.strptime(datetime_str, TIME_FORMAT).replace(tzinfo=utc())


def memento_datetime_string(dt):
    """Memento datatime string from a UTC datetime.datetime object.

    N.B. Will disregard any timezone information.
    """
    return dt.strftime(TIME_FORMAT)


def links_line(context, rels, extra=None):
    """String with one link relation formatted according to RFC6690.

    Example line:

    <http://arxiv.example.net/timemap/http://a.example.org>
      ; rel="self";type="application/link-format"
      ; from="Tue, 20 Jun 2000 18:02:59 GMT"
      ; until="Wed, 09 Apr 2008 20:30:51 GMT"

    (and multiple lines are separated with commas)

    Ref: https://tools.ietf.org/html/rfc6690
    """
    s = '<' + context + '>'
    s += '\n  ;rel="' + ' '.join(rels) + '"'
    if (extra is not None):
        for (k, v) in sorted(extra.items()):
            s += '\n  ;' + k + '="' + v + '"'
    return s


class BadTimeMap(Exception):
    """Exception raised when TimeMap is not configured correctly to meet request."""

    pass


class TimeMap(object):
    """TimeMap class.

    Ref: https://tools.ietf.org/html/rfc7089#section-5
    (Seems that there is an error in the example, Figure 28, in that the "until"
    time of the TimeMap is before the date of the last Memento?)

    Possibility of paged TimeMap documents is not supported at present.

    Instance data:
        original - URI of original
        mementos - dictionary of Memento URIs indexed by datetime
        timegate - URI of TimeGate
        timemap - URI of TimeMap
        original_datetime - a datetime timestamp for the original resource
            to be used when deciding which version is best for a given
            datetime request. If not specified then the current datetime
            will be used in negotiation.
    """

    FORMATS = ['']

    # Datetime negotiation methods
    PREVIOUS = 0
    CLOSEST = 1
    LAST = 2

    def __init__(self, original=None, mementos=None, timegate=None,
                 timemap=None, original_datetime=None):
        """Initialize TimeMap."""
        self.original = original
        self.mementos = mementos if mementos else {}
        self.timegate = timegate
        self.timemap = timemap
        self.original_datetime = None

    def set_original(self, uri, datetime_str=None):
        """Set Original resource with given uri and (optional) datetime_str in map."""
        self.original = uri
        if (datetime_str is None):
            self.original_datetime = None
        else:
            self.original_datetime = memento_parse_datetime(datetime_str)

    def add_memento(self, uri, datetime_str):
        """Add Memento with given uri and datetime_str to map."""
        self.mementos[memento_parse_datetime(datetime_str)] = uri

    def serialize_link_format(self):
        """String representation in "application/link-format" format."""
        lines = []
        # MUST list the URI-R of the Original Resource that the TimeMap is
        # about;
        if (self.original is None):
            raise BadTimeMap('TimeMap MUST list the URI-R of the Original Resource')
        original_rels = ['original']
        if (self.timegate == self.original):
            original_rels.append('timegate')
        lines.append(links_line(self.original, original_rels, None))
        # MUST list the URI-M and archival datetime of each Memento for the
        # Original Resource known to the server, preferably in a single
        # document, or, alternatively in multiple documents that can be
        # gathered by following contained links with a "timemap" Relation
        # Type;
        for (datetime, uri_m) in self.mementos.items():
            lines.append(links_line(uri_m, ['memento'],
                         {'datetime': memento_datetime_string(datetime)}))
        # SHOULD list the URI-G of one or more TimeGates for the Original
        # Resource known to the responding server;
        if (self.timegate is not None and self.timegate != self.original):
            lines.append(links_line(self.timegate, ['timegate'], None))
        # SHOULD, for self-containment, list the URI-T of the TimeMap
        # itself;
        if (self.timemap is not None):
            # FIXME - add from and until
            lines.append(links_line(self.timemap, ['self'], None))
        # MUST unambiguously type listed resources as being Original
        # Resource, TimeGate, Memento, or TimeMap.
        return ',\n'.join(lines)

    def triples(self):
        """RDF representation of TimeMap as a list of triple tuples.

        Triple tuples are (s, p, o) for each triple where the values are
        string representations of the URIs, or of a literal object which
        is preced with a double-quote. These can be fed into rdflib by
        converting each URI into a rdflib.URIRef, and each literal into
        a rdflib.Literal with code like:

        from negotiator2 import TimeMap
        from rdflib import Graph, URIRef, Literal

        tm = TimeMap()
        ...
        g = Graph()
        for (s, p, o) in tm.triples():
            g.add((URIRef(s),
                   URIRef(p),
                   Literal(o.lstrip('"')) if o.startswith('"') else URIRef(o)))

        Assembly of the triples from instance data follows the same logic
        as serialize_link_format().

        (The rdflib URIRef(..) and Literal(..) conversion is not included
        in this code to avoid adding a dependency on rdflib for this one
        method, and this form would also be flexible in case another RDF
        library were used.)
        """
        triples = []
        RDF_TYPE = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'
        MEMENTO_NS = 'http://mementoweb.org/ns#'
        # MUST list the URI-R of the Original Resource that the TimeMap is
        # about;
        if (self.original is None):
            raise BadTimeMap('TimeMap MUST list the URI-R of the Original Resource')
        # MUST unambiguously type listed resources as being Original
        # Resource, TimeGate, Memento, or TimeMap.
        triples.append((self.original, RDF_TYPE, MEMENTO_NS + "Memento"))
        # SHOULD list the URI-G of one or more TimeGates for the Original
        # Resource known to the responding server;
        if (self.timegate):
            triples.append((self.timegate, RDF_TYPE, MEMENTO_NS + "TimeGate"))
            triples.append((self.original, MEMENTO_NS + "timegate", self.timegate))
        # MUST list the URI-M and archival datetime of each Memento for the
        # Original Resource known to the server, preferably in a single
        # document, or, alternatively in multiple documents that can be
        # gathered by following contained links with a "timemap" Relation
        # Type;
        for (datetime, uri_m) in self.mementos.items():
            triples.append((uri_m, RDF_TYPE, MEMENTO_NS + "Memento"))
            triples.append((uri_m, MEMENTO_NS + "memento-datetime",
                            '"' + memento_datetime_string(datetime)))
            if (self.timegate):
                triples.append((uri_m, MEMENTO_NS + "timegate", self.timegate))
        # SHOULD, for self-containment, list the URI-T of the TimeMap
        # itself;
        if (self.timemap):
            triples.append((self.timemap, RDF_TYPE, MEMENTO_NS + "TimeMap"))
            triples.append((self.original, MEMENTO_NS + "timemap", self.timemap))
            # FIXME - should there be more #timemap links from other resources, or
            # FIXME - is that just clutter?
        return triples

    def best_version(self, dt, method=None, now=None):
        """URI of the version best matching datetime dt via method.

        Methods supported are:
            TimeMap.PREVIOUS - Select the version with the last datatime before
                or equal to the given datetime (default)
            TimeMap.CLOSEST - Select the version with closest datetime
            TimeMap.LAST - Select the last version (ignoring dt)
        """
        # Make dict of combined original and mementos
        versions = dict(self.mementos)
        if (self.original is not None):
            now = datetime.utcnow() if now is None else now
            now = now.replace(tzinfo=utc())  # ensure now is sortable with memento datetimes
            original_dt = now if self.original_datetime is None else self.original_datetime
            versions[original_dt] = self.original
        if (len(versions) == 0):
            raise BadTimeMap("No versions available for negotiation.")
        dts = sorted(versions.keys())
        if (method == self.LAST):
            return(versions[dts[-1]])
        # Work through datetimes of versions in order to
        # find the best match
        last_d = None
        for d in dts:
            if (d == dt):
                return versions[d]
            elif (d > dt):
                # Have d > dt > last_d -- return last_d or d version?
                if (last_d is None):
                    return versions[d]
                elif (method == self.CLOSEST):
                    return versions[last_d if ((dt - last_d) < (d - dt)) else d]
                else:
                    return versions[last_d]
            last_d = d
        # All version datetimes are before the requested datetime,
        # return the lastest
        return versions[d]
