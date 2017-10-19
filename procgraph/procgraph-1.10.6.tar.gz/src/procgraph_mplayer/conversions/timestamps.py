from contracts import contract
import datetime
import time

TIMESTAMP_FIELD = 'timestamp'  


@contract(timestamp='float', returns='str')
def iso_from_timestamp(timestamp):
    dt = datetime.datetime.fromtimestamp(timestamp)
    iso = str(dt)
    iso = iso.replace(' ', 'T')
    return iso

@contract(iso='str', returns='float')
def timestamp_from_iso(iso):
    """ Returns a timestamp in double """
    import dateutil.parser
    d = dateutil.parser.parse(iso)  # datetime
    s = time.mktime(d.timetuple()) + 0.001 * 0.001 * d.microsecond
    return s
 
