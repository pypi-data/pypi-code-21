"""cubicweb-datacat test utilities"""

from cubicweb import Binary


def create_file(cnx, data, data_name=None, **kwargs):
    """Create a File entity"""
    data_name = data_name or data.decode('utf-8')
    kwargs.setdefault('data_format', u'text/plain')
    return cnx.create_entity('File', data=Binary(data),
                             data_name=data_name,
                             **kwargs)


def produce_file(cnx, resourcefeed, inputfile):
    """Simulate the production of `inputfile` by resource feed `resourcefeed`"""
    tseq = resourcefeed.transformation_script[0].transformation_sequence
    # Build a transformation process "by hand".
    with cnx.security_enabled(write=False):
        process = cnx.create_entity(
            'DataTransformationProcess',
            process_input_file=inputfile,
            process_for_resourcefeed=resourcefeed,
            transformation_sequence=tseq)
        cnx.commit()  # transformation triggered in a hook.
    return process.reverse_produced_by[0]


def mediatypes_scheme(cnx, *labels):
    """Build a "dummy" media-types concept scheme to satisfy hooks on
    distribution/file media type conformance. Return concepts corresponding to
    requested `labels`.
    """
    scheme = cnx.create_entity(
        'ConceptScheme',
        cwuri=u'http://www.iana.org/assignments/media-types/media-types.xml')
    return [scheme.add_concept(label) for label in labels]
