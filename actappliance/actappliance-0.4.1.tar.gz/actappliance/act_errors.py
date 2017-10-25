"""
Create an act_errors dictionary with the values being  Actifio exceptions. The use case being you can catch individual
exceptions instead of making comparisons on the caught generic exception, without requiring star imports. Also, most
users are more familiar with error codes than exception names, so referencing with a number is better.

Allows this logic:
    except act_errors[10016]:
        <handle exception>
    except act_errors[8675309]:
        <handle Jenny>

to replace this:
    except ACTError:
        if int(e.errorcode) == 10016:
            <handle exception>
        elif int(e.errorcode) == 8675309:
            <handle Jenny>
        else:
            raise

This also improves the legibility of handling several possible ACTErrors of a try block.
"""
from actappliance.misc import camelize


class ACTError(Exception):

    def __init__(self, response_obj, *args, **kwargs):
        super(ACTError, self).__init__(*args, **kwargs)
        self.errormessage = response_obj.errormessage
        self.errorcode = response_obj.errorcode
        self.msg = '{}: {}'.format(self.errorcode, self.errormessage)

    def __str__(self):
        return self.msg


_error_codes = {
    'BAD_NUMBER_FORMAT': 10001,
    'FILE_NOT_EXIST': 10002,
    'FILE_EXISTS': 10003,
    'UNKNOWN_TYPE': 10004,
    'MISSING_ARGUMENT': 10005,
    'VIOLATE_UNIQUENESS': 10006,
    'STILL_IN_USE': 10007,
    'INVALID_VALUE': 10008,
    'PROTECTED_SYSTEM_RESOURCE': 10009,
    'INVALID_NAME': 10010,
    'LOGIN_FAILURE': 10011,
    'DISABLE_SNAP': 10012,
    'DISABLE_DEDUP': 10013,
    'EXCEEDED_LIMIT': 10014,
    'CLUSTER_CONNECTION_FAILURE': 10015,
    'OBJECT_NOT_EXIST': 10016,
    'UNKNOWN_OBJECT': 10016,
    'INVALID_OPERATION': 10017,
    'INVALID_OPTION': 10018,
    'SYSTEM_RESOURCE': 10019,
    'INVALID_SESSION': 10020,
    'INVALID_FILTERVALUE': 10021,
    'CONNECTION_FAILURE': 10022,
    'OPERATION_FAILURE': 10023,
    'SECURITY_VIOLATION': 10024,
    'MDISK_OFFLINE': 10025,
    'SYSTEM_ERROR': 10026,

    'EXCEED_DED_LIMIT': 10031,
    'EXCEED_PER_LIMIT': 10032,
    'EXCEED_PRI_LIMIT': 10033,
    'EXCEED_FC_LIMIT': 10034,
    'EXCEED_RC_LIMIT': 10035,
    'EXCEED_COPY_LIMIT': 10036,
    'EXCEED_MIRROR_LIMIT': 10037,
    'EXCEED_VDISK_LIMIT': 10038,
    'PING_TIMEOUT': 10039,
    'BAD_ARGUMENT': 10040,
    'DATA_OUTOFRANGE': 10041,
    'SOCKET_TIMEOUT': 10042,
    'SLA_VIOLATION': 10043,
    'NETWORK_INTERFACE_FAILURE': 10044,
    'SAFE_DED_LIMIT': 10045,
    'SAFE_PER_LIMIT': 10046,
    'SAFE_PRI_LIMIT': 10047,
    'MIN_DED_LIMIT_XING': 10048,
    'EXCEED_MIN_DED_LIMIT': 10049,

    'SECURITY_TURNON': 10050,
    'SECURITY_TURNOFF': 10051,
    'UPDATE_IN_PROCESS': 10052,
    'OPERATION_TIMEOUT': 10053,
    'INVALID_XML': 10054,
    'REMOTE_PROTECTION_OFFLINE': 10055,
    'NODE_OFFLINE': 10056,
    'NODE_ASSERT': 10057,

    'DEDUP_DOWN': 10060,
    'DEDUP_DISABLED': 10061,
    'MULTIPLE_VMS_SAME_NAME': 10062,
    'DNS_LOOKUP_FAILED': 10063,
    'SSD_EXCEED_WEAR_LEVEL': 10064,

    'DISABLE_UDPPM_SCHEDULER': 10070,
    'INVALID_SVC_MIRROR': 10071,
    'EXCEEDING_MDL': 10072,

    'CLUSTER_INVALID_OPERATION': 10080,
    'CLUSTER_C[2]C_FAILURE': 10081,

    'LICENSE_VIOLATION': 10082,
}

# Create a dictionary of errors
act_errors = {}
for error in _error_codes:
    actifio_error = camelize(error.lower()) + 'Error'
    err_num = _error_codes[error]
    docstring = "A {0} {1} Actifio error.".format(err_num, error)
    cls_dict = {'__doc__': docstring}
    act_errors[err_num] = (type(actifio_error, (ACTError,), cls_dict))
