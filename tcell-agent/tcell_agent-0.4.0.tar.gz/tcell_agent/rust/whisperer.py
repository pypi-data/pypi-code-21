import logging
import sys
import json
import os

from ctypes import cdll, c_uint8, c_void_p, c_size_t, c_int, c_char_p, POINTER

from tcell_agent.utils.compat import to_bytes


LOGGER = logging.getLogger("tcell_agent").getChild(__name__)

version = "0.4.6"
prefix = {"win32": ""}.get(sys.platform, "lib")
extension = {"darwin": ".dylib", "win32": ".dll"}.get(sys.platform, ".so")

try:
    native_lib = cdll.LoadLibrary(os.path.abspath(os.path.join(os.path.dirname(__file__), prefix + "tcellagent-" + version + extension)))

    native_lib.cmdi_parse_sh.argtypes = [c_char_p, c_size_t, POINTER(c_uint8), c_size_t]
    """
        restype [int]: 0+ length of buffer_out answer (parsing was successful)
                       -1 general error
                       -2 buffer_out is not big enough for response
                       -3 command_str is null
    """
    native_lib.cmdi_parse_sh.restype = c_int

    native_lib.appfirewall_policy_init.argtypes = [c_char_p, c_size_t, POINTER(c_uint8), c_size_t]
    """
        restype [int]: 0+ length of buffer_out answer (parsing was successful)
                       -1 general error
                       -2 buffer_out is not big enough for response
                       -3 out is null
    """
    native_lib.appfirewall_policy_init.restype = c_int

    native_lib.appfirewall_policy_apply.argtypes = [c_void_p, c_char_p, c_size_t, POINTER(c_uint8), c_size_t]
    """
        restype [int]: 0+ length of buffer_out answer (parsing was successful)
                       -1 general error
                       -2 buffer_out is not big enough for response
                       -3 out is null
    """
    native_lib.appfirewall_policy_apply.restype = c_int

    native_lib.appfirewall_free.argtypes = [c_void_p]
    native_lib.appfirewall_free.restype = None


except Exception as ex:
    LOGGER.error("Failed to load common agent library. {e}".format(e=ex))
    LOGGER.debug(ex, exc_info=True)
    native_lib = None


def parse_cmd(cmd):
    if native_lib and cmd and cmd.strip():
        command_bytes = to_bytes(cmd)
        allocated_memory_bytes = 1024 * 8
        buf_type = c_uint8 * allocated_memory_bytes
        response = buf_type()  # allocate memory
        ans = native_lib.cmdi_parse_sh(
            command_bytes, len(command_bytes), response, allocated_memory_bytes)
        if ans >= 0:
            return json.loads("".join([chr(response_byte) for response_byte in response[:ans]]))

    return {}


def init_appfirewall(policy_str):
    if native_lib is not None and policy_str is not None:
        policy_bytes = to_bytes(policy_str)

        allocated_memory_bytes = 1024 * 8
        buf_type = c_uint8 * allocated_memory_bytes
        response = buf_type()  # allocate memory
        ans = native_lib.appfirewall_policy_init(policy_bytes,
                                                 len(policy_bytes),
                                                 response,
                                                 allocated_memory_bytes)
        if ans >= 0:
            return json.loads("".join([chr(response_byte) for response_byte in response[:ans]]))

    return {}


def apply_appfirewall(appfirewall_ptr, request_response_json_str):
    if native_lib is not None and appfirewall_ptr is not None and request_response_json_str is not None:
        request_response_bytes = to_bytes(request_response_json_str)

        allocated_memory_bytes = 1024 * 8
        buf_type = c_uint8 * allocated_memory_bytes
        response = buf_type()  # allocate memory
        ans = native_lib.appfirewall_policy_apply(appfirewall_ptr,
                                                  request_response_bytes,
                                                  len(request_response_bytes),
                                                  response,
                                                  allocated_memory_bytes)

        if ans >= 0:
            return json.loads("".join([chr(response_byte) for response_byte in response[:ans]]))

    return {}


def free_appfirewall(appfirewall_ptr):
    if native_lib is not None and appfirewall_ptr is not None:
        native_lib.appfirewall_free(appfirewall_ptr)
