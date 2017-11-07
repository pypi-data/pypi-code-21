from ctypes import *

STRING = c_char_p
_libraries = {}
_libraries['libnfc.so'] = CDLL('libnfc.so')


__codecvt_ok = 0
NBR_106 = 1
NMT_DEP = 8
NMT_FELICA = 7
NMT_ISO14443B2CT = 6
NMT_ISO14443B2SR = 5
NMT_ISO14443BI = 4
NMT_ISO14443B = 3
NMT_JEWEL = 2
NMT_ISO14443A = 1
__codecvt_error = 2
__codecvt_partial = 1
__codecvt_noconv = 3
N_INITIATOR = 1
N_TARGET = 0
ITIMER_REAL = 0
ITIMER_PROF = 2
NP_FORCE_SPEED_106 = 14
NP_FORCE_ISO14443_B = 13
NP_FORCE_ISO14443_A = 12
NP_EASY_FRAMING = 11
NP_AUTO_ISO14443_4 = 10
NP_ACCEPT_MULTIPLE_FRAMES = 9
NP_ACCEPT_INVALID_FRAMES = 8
NP_INFINITE_SELECT = 7
NP_ACTIVATE_CRYPTO1 = 6
NP_ACTIVATE_FIELD = 5
NP_HANDLE_PARITY = 4
NP_HANDLE_CRC = 3
NP_TIMEOUT_COM = 2
NP_TIMEOUT_ATR = 1
NP_TIMEOUT_COMMAND = 0
NBR_847 = 4
NBR_424 = 3
NBR_212 = 2
NBR_UNDEFINED = 0
NDM_ACTIVE = 2
ITIMER_VIRTUAL = 1
NDM_UNDEFINED = 0
NDM_PASSIVE = 1
class _G_fpos_t(Structure):
    pass
__off_t = c_long
class __mbstate_t(Structure):
    pass
class N11__mbstate_t3DOT_4E(Union):
    pass
N11__mbstate_t3DOT_4E._fields_ = [
    ('__wch', c_uint),
    ('__wchb', c_char * 4),
]
__mbstate_t._fields_ = [
    ('__count', c_int),
    ('__value', N11__mbstate_t3DOT_4E),
]
_G_fpos_t._fields_ = [
    ('__pos', __off_t),
    ('__state', __mbstate_t),
]
class _G_fpos64_t(Structure):
    pass
__off64_t = c_long
_G_fpos64_t._fields_ = [
    ('__pos', __off64_t),
    ('__state', __mbstate_t),
]
class _IO_jump_t(Structure):
    pass
_IO_jump_t._fields_ = [
]
_IO_lock_t = None
class _IO_marker(Structure):
    pass
class _IO_FILE(Structure):
    pass
_IO_marker._fields_ = [
    ('_next', POINTER(_IO_marker)),
    ('_sbuf', POINTER(_IO_FILE)),
    ('_pos', c_int),
]

# values for enumeration '__codecvt_result'
__codecvt_result = c_int # enum
size_t = c_ulong
_IO_FILE._fields_ = [
    ('_flags', c_int),
    ('_IO_read_ptr', STRING),
    ('_IO_read_end', STRING),
    ('_IO_read_base', STRING),
    ('_IO_write_base', STRING),
    ('_IO_write_ptr', STRING),
    ('_IO_write_end', STRING),
    ('_IO_buf_base', STRING),
    ('_IO_buf_end', STRING),
    ('_IO_save_base', STRING),
    ('_IO_backup_base', STRING),
    ('_IO_save_end', STRING),
    ('_markers', POINTER(_IO_marker)),
    ('_chain', POINTER(_IO_FILE)),
    ('_fileno', c_int),
    ('_flags2', c_int),
    ('_old_offset', __off_t),
    ('_cur_column', c_ushort),
    ('_vtable_offset', c_byte),
    ('_shortbuf', c_char * 1),
    ('_lock', POINTER(_IO_lock_t)),
    ('_offset', __off64_t),
    ('__pad1', c_void_p),
    ('__pad2', c_void_p),
    ('__pad3', c_void_p),
    ('__pad4', c_void_p),
    ('__pad5', size_t),
    ('_mode', c_int),
    ('_unused2', c_char * 20),
]
class _IO_FILE_plus(Structure):
    pass
_IO_FILE_plus._fields_ = [
]
_IO_2_1_stdin_ = (_IO_FILE_plus).in_dll(_libraries['libnfc.so'], '_IO_2_1_stdin_')
_IO_2_1_stdout_ = (_IO_FILE_plus).in_dll(_libraries['libnfc.so'], '_IO_2_1_stdout_')
_IO_2_1_stderr_ = (_IO_FILE_plus).in_dll(_libraries['libnfc.so'], '_IO_2_1_stderr_')
__ssize_t = c_long
__io_read_fn = CFUNCTYPE(__ssize_t, c_void_p, STRING, size_t)
__io_write_fn = CFUNCTYPE(__ssize_t, c_void_p, STRING, size_t)
__io_seek_fn = CFUNCTYPE(c_int, c_void_p, POINTER(__off64_t), c_int)
__io_close_fn = CFUNCTYPE(c_int, c_void_p)
cookie_read_function_t = __io_read_fn
cookie_write_function_t = __io_write_fn
cookie_seek_function_t = __io_seek_fn
cookie_close_function_t = __io_close_fn
class _IO_cookie_io_functions_t(Structure):
    pass
_IO_cookie_io_functions_t._fields_ = [
    ('read', POINTER(__io_read_fn)),
    ('write', POINTER(__io_write_fn)),
    ('seek', POINTER(__io_seek_fn)),
    ('close', POINTER(__io_close_fn)),
]
cookie_io_functions_t = _IO_cookie_io_functions_t
class _IO_cookie_file(Structure):
    pass
_IO_cookie_file._fields_ = [
]
__underflow = _libraries['libnfc.so'].__underflow
__underflow.restype = c_int
__underflow.argtypes = [POINTER(_IO_FILE)]
__uflow = _libraries['libnfc.so'].__uflow
__uflow.restype = c_int
__uflow.argtypes = [POINTER(_IO_FILE)]
__overflow = _libraries['libnfc.so'].__overflow
__overflow.restype = c_int
__overflow.argtypes = [POINTER(_IO_FILE), c_int]
_IO_getc = _libraries['libnfc.so']._IO_getc
_IO_getc.restype = c_int
_IO_getc.argtypes = [POINTER(_IO_FILE)]
_IO_putc = _libraries['libnfc.so']._IO_putc
_IO_putc.restype = c_int
_IO_putc.argtypes = [c_int, POINTER(_IO_FILE)]
_IO_feof = _libraries['libnfc.so']._IO_feof
_IO_feof.restype = c_int
_IO_feof.argtypes = [POINTER(_IO_FILE)]
_IO_ferror = _libraries['libnfc.so']._IO_ferror
_IO_ferror.restype = c_int
_IO_ferror.argtypes = [POINTER(_IO_FILE)]
_IO_peekc_locked = _libraries['libnfc.so']._IO_peekc_locked
_IO_peekc_locked.restype = c_int
_IO_peekc_locked.argtypes = [POINTER(_IO_FILE)]
_IO_flockfile = _libraries['libnfc.so']._IO_flockfile
_IO_flockfile.restype = None
_IO_flockfile.argtypes = [POINTER(_IO_FILE)]
_IO_funlockfile = _libraries['libnfc.so']._IO_funlockfile
_IO_funlockfile.restype = None
_IO_funlockfile.argtypes = [POINTER(_IO_FILE)]
_IO_ftrylockfile = _libraries['libnfc.so']._IO_ftrylockfile
_IO_ftrylockfile.restype = c_int
_IO_ftrylockfile.argtypes = [POINTER(_IO_FILE)]
class __va_list_tag(Structure):
    pass
_IO_vfscanf = _libraries['libnfc.so']._IO_vfscanf
_IO_vfscanf.restype = c_int
_IO_vfscanf.argtypes = [POINTER(_IO_FILE), STRING, POINTER(__va_list_tag), POINTER(c_int)]
_IO_vfprintf = _libraries['libnfc.so']._IO_vfprintf
_IO_vfprintf.restype = c_int
_IO_vfprintf.argtypes = [POINTER(_IO_FILE), STRING, POINTER(__va_list_tag)]
_IO_padn = _libraries['libnfc.so']._IO_padn
_IO_padn.restype = __ssize_t
_IO_padn.argtypes = [POINTER(_IO_FILE), c_int, __ssize_t]
_IO_sgetn = _libraries['libnfc.so']._IO_sgetn
_IO_sgetn.restype = size_t
_IO_sgetn.argtypes = [POINTER(_IO_FILE), c_void_p, size_t]
_IO_seekoff = _libraries['libnfc.so']._IO_seekoff
_IO_seekoff.restype = __off64_t
_IO_seekoff.argtypes = [POINTER(_IO_FILE), __off64_t, c_int, c_int]
_IO_seekpos = _libraries['libnfc.so']._IO_seekpos
_IO_seekpos.restype = __off64_t
_IO_seekpos.argtypes = [POINTER(_IO_FILE), __off64_t, c_int]
_IO_free_backup_area = _libraries['libnfc.so']._IO_free_backup_area
_IO_free_backup_area.restype = None
_IO_free_backup_area.argtypes = [POINTER(_IO_FILE)]
class nfc_context(Structure):
    pass
class nfc_device(Structure):
    pass
class nfc_driver(Structure):
    pass
nfc_driver._fields_ = [
]
nfc_connstring = c_char * 1024

# values for enumeration 'nfc_property'
nfc_property = c_int # enum

# values for enumeration 'nfc_dep_mode'
nfc_dep_mode = c_int # enum
class nfc_dep_info(Structure):
    pass
uint8_t = c_uint8
nfc_dep_info._pack_ = 1
nfc_dep_info._fields_ = [
    ('abtNFCID3', uint8_t * 10),
    ('btDID', uint8_t),
    ('btBS', uint8_t),
    ('btBR', uint8_t),
    ('btTO', uint8_t),
    ('btPP', uint8_t),
    ('abtGB', uint8_t * 48),
    ('szGB', size_t),
    ('ndm', nfc_dep_mode),
]
class nfc_iso14443a_info(Structure):
    pass
nfc_iso14443a_info._pack_ = 1
nfc_iso14443a_info._fields_ = [
    ('abtAtqa', uint8_t * 2),
    ('btSak', uint8_t),
    ('szUidLen', size_t),
    ('abtUid', uint8_t * 10),
    ('szAtsLen', size_t),
    ('abtAts', uint8_t * 254),
]
class nfc_felica_info(Structure):
    pass
nfc_felica_info._pack_ = 1
nfc_felica_info._fields_ = [
    ('szLen', size_t),
    ('btResCode', uint8_t),
    ('abtId', uint8_t * 8),
    ('abtPad', uint8_t * 8),
    ('abtSysCode', uint8_t * 2),
]
class nfc_iso14443b_info(Structure):
    pass
nfc_iso14443b_info._fields_ = [
    ('abtPupi', uint8_t * 4),
    ('abtApplicationData', uint8_t * 4),
    ('abtProtocolInfo', uint8_t * 3),
    ('ui8CardIdentifier', uint8_t),
]
class nfc_iso14443bi_info(Structure):
    pass
nfc_iso14443bi_info._pack_ = 1
nfc_iso14443bi_info._fields_ = [
    ('abtDIV', uint8_t * 4),
    ('btVerLog', uint8_t),
    ('btConfig', uint8_t),
    ('szAtrLen', size_t),
    ('abtAtr', uint8_t * 33),
]
class nfc_iso14443b2sr_info(Structure):
    pass
nfc_iso14443b2sr_info._fields_ = [
    ('abtUID', uint8_t * 8),
]
class nfc_iso14443b2ct_info(Structure):
    pass
nfc_iso14443b2ct_info._fields_ = [
    ('abtUID', uint8_t * 4),
    ('btProdCode', uint8_t),
    ('btFabCode', uint8_t),
]
class nfc_jewel_info(Structure):
    pass
nfc_jewel_info._fields_ = [
    ('btSensRes', uint8_t * 2),
    ('btId', uint8_t * 4),
]

# values for enumeration 'nfc_baud_rate'
nfc_baud_rate = c_int # enum

# values for enumeration 'nfc_modulation_type'
nfc_modulation_type = c_int # enum

# values for enumeration 'nfc_mode'
nfc_mode = c_int # enum
class nfc_modulation(Structure):
    pass
nfc_modulation._pack_ = 1
nfc_modulation._fields_ = [
    ('nmt', nfc_modulation_type),
    ('nbr', nfc_baud_rate),
]
class nfc_target(Structure):
    pass
class nfc_target_info(Union):
    pass
nfc_target_info._fields_ = [
    ('nai', nfc_iso14443a_info),
    ('nfi', nfc_felica_info),
    ('nbi', nfc_iso14443b_info),
    ('nii', nfc_iso14443bi_info),
    ('nsi', nfc_iso14443b2sr_info),
    ('nci', nfc_iso14443b2ct_info),
    ('nji', nfc_jewel_info),
    ('ndi', nfc_dep_info),
]
nfc_target._fields_ = [
    ('nti', nfc_target_info),
    ('nm', nfc_modulation),
]
nfc_init = _libraries['libnfc.so'].nfc_init
nfc_init.restype = None
nfc_init.argtypes = [POINTER(POINTER(nfc_context))]
nfc_exit = _libraries['libnfc.so'].nfc_exit
nfc_exit.restype = None
nfc_exit.argtypes = [POINTER(nfc_context)]
nfc_register_driver = _libraries['libnfc.so'].nfc_register_driver
nfc_register_driver.restype = c_int
nfc_register_driver.argtypes = [POINTER(nfc_driver)]
nfc_open = _libraries['libnfc.so'].nfc_open
nfc_open.restype = POINTER(nfc_device)
nfc_open.argtypes = [POINTER(nfc_context), STRING]
nfc_close = _libraries['libnfc.so'].nfc_close
nfc_close.restype = None
nfc_close.argtypes = [POINTER(nfc_device)]
nfc_abort_command = _libraries['libnfc.so'].nfc_abort_command
nfc_abort_command.restype = c_int
nfc_abort_command.argtypes = [POINTER(nfc_device)]
nfc_list_devices = _libraries['libnfc.so'].nfc_list_devices
nfc_list_devices.restype = size_t
nfc_list_devices.argtypes = [POINTER(nfc_context), POINTER(nfc_connstring), size_t]
nfc_idle = _libraries['libnfc.so'].nfc_idle
nfc_idle.restype = c_int
nfc_idle.argtypes = [POINTER(nfc_device)]
nfc_initiator_init = _libraries['libnfc.so'].nfc_initiator_init
nfc_initiator_init.restype = c_int
nfc_initiator_init.argtypes = [POINTER(nfc_device)]
nfc_initiator_init_secure_element = _libraries['libnfc.so'].nfc_initiator_init_secure_element
nfc_initiator_init_secure_element.restype = c_int
nfc_initiator_init_secure_element.argtypes = [POINTER(nfc_device)]
nfc_initiator_select_passive_target = _libraries['libnfc.so'].nfc_initiator_select_passive_target
nfc_initiator_select_passive_target.restype = c_int
nfc_initiator_select_passive_target.argtypes = [POINTER(nfc_device), nfc_modulation, POINTER(uint8_t), size_t, POINTER(nfc_target)]
nfc_initiator_list_passive_targets = _libraries['libnfc.so'].nfc_initiator_list_passive_targets
nfc_initiator_list_passive_targets.restype = c_int
nfc_initiator_list_passive_targets.argtypes = [POINTER(nfc_device), nfc_modulation, POINTER(nfc_target), size_t]
nfc_initiator_poll_target = _libraries['libnfc.so'].nfc_initiator_poll_target
nfc_initiator_poll_target.restype = c_int
nfc_initiator_poll_target.argtypes = [POINTER(nfc_device), POINTER(nfc_modulation), size_t, uint8_t, uint8_t, POINTER(nfc_target)]
nfc_initiator_select_dep_target = _libraries['libnfc.so'].nfc_initiator_select_dep_target
nfc_initiator_select_dep_target.restype = c_int
nfc_initiator_select_dep_target.argtypes = [POINTER(nfc_device), nfc_dep_mode, nfc_baud_rate, POINTER(nfc_dep_info), POINTER(nfc_target), c_int]
nfc_initiator_poll_dep_target = _libraries['libnfc.so'].nfc_initiator_poll_dep_target
nfc_initiator_poll_dep_target.restype = c_int
nfc_initiator_poll_dep_target.argtypes = [POINTER(nfc_device), nfc_dep_mode, nfc_baud_rate, POINTER(nfc_dep_info), POINTER(nfc_target), c_int]
nfc_initiator_deselect_target = _libraries['libnfc.so'].nfc_initiator_deselect_target
nfc_initiator_deselect_target.restype = c_int
nfc_initiator_deselect_target.argtypes = [POINTER(nfc_device)]
nfc_initiator_transceive_bytes = _libraries['libnfc.so'].nfc_initiator_transceive_bytes
nfc_initiator_transceive_bytes.restype = c_int
nfc_initiator_transceive_bytes.argtypes = [POINTER(nfc_device), POINTER(uint8_t), size_t, POINTER(uint8_t), size_t, c_int]
nfc_initiator_transceive_bits = _libraries['libnfc.so'].nfc_initiator_transceive_bits
nfc_initiator_transceive_bits.restype = c_int
nfc_initiator_transceive_bits.argtypes = [POINTER(nfc_device), POINTER(uint8_t), size_t, POINTER(uint8_t), POINTER(uint8_t), size_t, POINTER(uint8_t)]
uint32_t = c_uint32
nfc_initiator_transceive_bytes_timed = _libraries['libnfc.so'].nfc_initiator_transceive_bytes_timed
nfc_initiator_transceive_bytes_timed.restype = c_int
nfc_initiator_transceive_bytes_timed.argtypes = [POINTER(nfc_device), POINTER(uint8_t), size_t, POINTER(uint8_t), size_t, POINTER(uint32_t)]
nfc_initiator_transceive_bits_timed = _libraries['libnfc.so'].nfc_initiator_transceive_bits_timed
nfc_initiator_transceive_bits_timed.restype = c_int
nfc_initiator_transceive_bits_timed.argtypes = [POINTER(nfc_device), POINTER(uint8_t), size_t, POINTER(uint8_t), POINTER(uint8_t), size_t, POINTER(uint8_t), POINTER(uint32_t)]
nfc_initiator_target_is_present = _libraries['libnfc.so'].nfc_initiator_target_is_present
nfc_initiator_target_is_present.restype = c_int
nfc_initiator_target_is_present.argtypes = [POINTER(nfc_device), POINTER(nfc_target)]
nfc_target_init = _libraries['libnfc.so'].nfc_target_init
nfc_target_init.restype = c_int
nfc_target_init.argtypes = [POINTER(nfc_device), POINTER(nfc_target), POINTER(uint8_t), size_t, c_int]
nfc_target_send_bytes = _libraries['libnfc.so'].nfc_target_send_bytes
nfc_target_send_bytes.restype = c_int
nfc_target_send_bytes.argtypes = [POINTER(nfc_device), POINTER(uint8_t), size_t, c_int]
nfc_target_receive_bytes = _libraries['libnfc.so'].nfc_target_receive_bytes
nfc_target_receive_bytes.restype = c_int
nfc_target_receive_bytes.argtypes = [POINTER(nfc_device), POINTER(uint8_t), size_t, c_int]
nfc_target_send_bits = _libraries['libnfc.so'].nfc_target_send_bits
nfc_target_send_bits.restype = c_int
nfc_target_send_bits.argtypes = [POINTER(nfc_device), POINTER(uint8_t), size_t, POINTER(uint8_t)]
nfc_target_receive_bits = _libraries['libnfc.so'].nfc_target_receive_bits
nfc_target_receive_bits.restype = c_int
nfc_target_receive_bits.argtypes = [POINTER(nfc_device), POINTER(uint8_t), size_t, POINTER(uint8_t)]
nfc_strerror = _libraries['libnfc.so'].nfc_strerror
nfc_strerror.restype = STRING
nfc_strerror.argtypes = [POINTER(nfc_device)]
nfc_strerror_r = _libraries['libnfc.so'].nfc_strerror_r
nfc_strerror_r.restype = c_int
nfc_strerror_r.argtypes = [POINTER(nfc_device), STRING, size_t]
nfc_perror = _libraries['libnfc.so'].nfc_perror
nfc_perror.restype = None
nfc_perror.argtypes = [POINTER(nfc_device), STRING]
nfc_device_get_last_error = _libraries['libnfc.so'].nfc_device_get_last_error
nfc_device_get_last_error.restype = c_int
nfc_device_get_last_error.argtypes = [POINTER(nfc_device)]
nfc_device_get_name = _libraries['libnfc.so'].nfc_device_get_name
nfc_device_get_name.restype = STRING
nfc_device_get_name.argtypes = [POINTER(nfc_device)]
nfc_device_get_connstring = _libraries['libnfc.so'].nfc_device_get_connstring
nfc_device_get_connstring.restype = STRING
nfc_device_get_connstring.argtypes = [POINTER(nfc_device)]
nfc_device_get_supported_modulation = _libraries['libnfc.so'].nfc_device_get_supported_modulation
nfc_device_get_supported_modulation.restype = c_int
nfc_device_get_supported_modulation.argtypes = [POINTER(nfc_device), nfc_mode, POINTER(POINTER(nfc_modulation_type))]
nfc_device_get_supported_baud_rate = _libraries['libnfc.so'].nfc_device_get_supported_baud_rate
nfc_device_get_supported_baud_rate.restype = c_int
nfc_device_get_supported_baud_rate.argtypes = [POINTER(nfc_device), nfc_modulation_type, POINTER(POINTER(nfc_baud_rate))]
nfc_device_set_property_int = _libraries['libnfc.so'].nfc_device_set_property_int
nfc_device_set_property_int.restype = c_int
nfc_device_set_property_int.argtypes = [POINTER(nfc_device), nfc_property, c_int]
nfc_device_set_property_bool = _libraries['libnfc.so'].nfc_device_set_property_bool
nfc_device_set_property_bool.restype = c_int
nfc_device_set_property_bool.argtypes = [POINTER(nfc_device), nfc_property, c_bool]
iso14443a_crc = _libraries['libnfc.so'].iso14443a_crc
iso14443a_crc.restype = None
iso14443a_crc.argtypes = [POINTER(uint8_t), size_t, POINTER(uint8_t)]
iso14443a_crc_append = _libraries['libnfc.so'].iso14443a_crc_append
iso14443a_crc_append.restype = None
iso14443a_crc_append.argtypes = [POINTER(uint8_t), size_t]
iso14443a_locate_historical_bytes = _libraries['libnfc.so'].iso14443a_locate_historical_bytes
iso14443a_locate_historical_bytes.restype = POINTER(uint8_t)
iso14443a_locate_historical_bytes.argtypes = [POINTER(uint8_t), size_t, POINTER(size_t)]
nfc_free = _libraries['libnfc.so'].nfc_free
nfc_free.restype = None
nfc_free.argtypes = [c_void_p]
nfc_version = _libraries['libnfc.so'].nfc_version
nfc_version.restype = STRING
nfc_version.argtypes = []
nfc_device_get_information_about = _libraries['libnfc.so'].nfc_device_get_information_about
nfc_device_get_information_about.restype = c_int
nfc_device_get_information_about.argtypes = [POINTER(nfc_device), POINTER(STRING)]
str_nfc_modulation_type = _libraries['libnfc.so'].str_nfc_modulation_type
str_nfc_modulation_type.restype = STRING
str_nfc_modulation_type.argtypes = [nfc_modulation_type]
str_nfc_baud_rate = _libraries['libnfc.so'].str_nfc_baud_rate
str_nfc_baud_rate.restype = STRING
str_nfc_baud_rate.argtypes = [nfc_baud_rate]
str_nfc_target = _libraries['libnfc.so'].str_nfc_target
str_nfc_target.restype = c_int
str_nfc_target.argtypes = [POINTER(STRING), POINTER(nfc_target), c_bool]
int8_t = c_int8
int16_t = c_int16
int32_t = c_int32
int64_t = c_int64
uint16_t = c_uint16
uint64_t = c_uint64
int_least8_t = c_byte
int_least16_t = c_short
int_least32_t = c_int
int_least64_t = c_long
uint_least8_t = c_ubyte
uint_least16_t = c_ushort
uint_least32_t = c_uint
uint_least64_t = c_ulong
int_fast8_t = c_byte
int_fast16_t = c_long
int_fast32_t = c_long
int_fast64_t = c_long
uint_fast8_t = c_ubyte
uint_fast16_t = c_ulong
uint_fast32_t = c_ulong
uint_fast64_t = c_ulong
intptr_t = c_long
uintptr_t = c_ulong
intmax_t = c_long
uintmax_t = c_ulong
FILE = _IO_FILE
__FILE = _IO_FILE
__va_list_tag._fields_ = [
]
__gnuc_va_list = __va_list_tag * 1
va_list = __gnuc_va_list
off_t = __off_t
off64_t = __off64_t
ssize_t = __ssize_t
fpos_t = _G_fpos_t
fpos64_t = _G_fpos64_t
stdin = (POINTER(_IO_FILE)).in_dll(_libraries['libnfc.so'], 'stdin')
stdout = (POINTER(_IO_FILE)).in_dll(_libraries['libnfc.so'], 'stdout')
stderr = (POINTER(_IO_FILE)).in_dll(_libraries['libnfc.so'], 'stderr')
remove = _libraries['libnfc.so'].remove
remove.restype = c_int
remove.argtypes = [STRING]
rename = _libraries['libnfc.so'].rename
rename.restype = c_int
rename.argtypes = [STRING, STRING]
renameat = _libraries['libnfc.so'].renameat
renameat.restype = c_int
renameat.argtypes = [c_int, STRING, c_int, STRING]
tmpfile = _libraries['libnfc.so'].tmpfile
tmpfile.restype = POINTER(FILE)
tmpfile.argtypes = []
tmpfile64 = _libraries['libnfc.so'].tmpfile64
tmpfile64.restype = POINTER(FILE)
tmpfile64.argtypes = []
tmpnam = _libraries['libnfc.so'].tmpnam
tmpnam.restype = STRING
tmpnam.argtypes = [STRING]
tmpnam_r = _libraries['libnfc.so'].tmpnam_r
tmpnam_r.restype = STRING
tmpnam_r.argtypes = [STRING]
tempnam = _libraries['libnfc.so'].tempnam
tempnam.restype = STRING
tempnam.argtypes = [STRING, STRING]
fclose = _libraries['libnfc.so'].fclose
fclose.restype = c_int
fclose.argtypes = [POINTER(FILE)]
fflush = _libraries['libnfc.so'].fflush
fflush.restype = c_int
fflush.argtypes = [POINTER(FILE)]
fflush_unlocked = _libraries['libnfc.so'].fflush_unlocked
fflush_unlocked.restype = c_int
fflush_unlocked.argtypes = [POINTER(FILE)]
fcloseall = _libraries['libnfc.so'].fcloseall
fcloseall.restype = c_int
fcloseall.argtypes = []
fopen = _libraries['libnfc.so'].fopen
fopen.restype = POINTER(FILE)
fopen.argtypes = [STRING, STRING]
freopen = _libraries['libnfc.so'].freopen
freopen.restype = POINTER(FILE)
freopen.argtypes = [STRING, STRING, POINTER(FILE)]
fopen64 = _libraries['libnfc.so'].fopen64
fopen64.restype = POINTER(FILE)
fopen64.argtypes = [STRING, STRING]
freopen64 = _libraries['libnfc.so'].freopen64
freopen64.restype = POINTER(FILE)
freopen64.argtypes = [STRING, STRING, POINTER(FILE)]
fdopen = _libraries['libnfc.so'].fdopen
fdopen.restype = POINTER(FILE)
fdopen.argtypes = [c_int, STRING]
fopencookie = _libraries['libnfc.so'].fopencookie
fopencookie.restype = POINTER(FILE)
fopencookie.argtypes = [c_void_p, STRING, _IO_cookie_io_functions_t]
fmemopen = _libraries['libnfc.so'].fmemopen
fmemopen.restype = POINTER(FILE)
fmemopen.argtypes = [c_void_p, size_t, STRING]
open_memstream = _libraries['libnfc.so'].open_memstream
open_memstream.restype = POINTER(FILE)
open_memstream.argtypes = [POINTER(STRING), POINTER(size_t)]
setbuf = _libraries['libnfc.so'].setbuf
setbuf.restype = None
setbuf.argtypes = [POINTER(FILE), STRING]
setvbuf = _libraries['libnfc.so'].setvbuf
setvbuf.restype = c_int
setvbuf.argtypes = [POINTER(FILE), STRING, c_int, size_t]
setbuffer = _libraries['libnfc.so'].setbuffer
setbuffer.restype = None
setbuffer.argtypes = [POINTER(FILE), STRING, size_t]
setlinebuf = _libraries['libnfc.so'].setlinebuf
setlinebuf.restype = None
setlinebuf.argtypes = [POINTER(FILE)]
fscanf = _libraries['libnfc.so'].fscanf
fscanf.restype = c_int
fscanf.argtypes = [POINTER(FILE), STRING]
scanf = _libraries['libnfc.so'].scanf
scanf.restype = c_int
scanf.argtypes = [STRING]
sscanf = _libraries['libnfc.so'].sscanf
sscanf.restype = c_int
sscanf.argtypes = [STRING, STRING]
vfscanf = _libraries['libnfc.so'].vfscanf
vfscanf.restype = c_int
vfscanf.argtypes = [POINTER(FILE), STRING, POINTER(__va_list_tag)]
vscanf = _libraries['libnfc.so'].vscanf
vscanf.restype = c_int
vscanf.argtypes = [STRING, POINTER(__va_list_tag)]
vsscanf = _libraries['libnfc.so'].vsscanf
vsscanf.restype = c_int
vsscanf.argtypes = [STRING, STRING, POINTER(__va_list_tag)]
fgetc = _libraries['libnfc.so'].fgetc
fgetc.restype = c_int
fgetc.argtypes = [POINTER(FILE)]
getc = _libraries['libnfc.so'].getc
getc.restype = c_int
getc.argtypes = [POINTER(FILE)]
fputc = _libraries['libnfc.so'].fputc
fputc.restype = c_int
fputc.argtypes = [c_int, POINTER(FILE)]
putc = _libraries['libnfc.so'].putc
putc.restype = c_int
putc.argtypes = [c_int, POINTER(FILE)]
getw = _libraries['libnfc.so'].getw
getw.restype = c_int
getw.argtypes = [POINTER(FILE)]
putw = _libraries['libnfc.so'].putw
putw.restype = c_int
putw.argtypes = [c_int, POINTER(FILE)]
gets = _libraries['libnfc.so'].gets
gets.restype = STRING
gets.argtypes = [STRING]
__getdelim = _libraries['libnfc.so'].__getdelim
__getdelim.restype = __ssize_t
__getdelim.argtypes = [POINTER(STRING), POINTER(size_t), c_int, POINTER(FILE)]
getdelim = _libraries['libnfc.so'].getdelim
getdelim.restype = __ssize_t
getdelim.argtypes = [POINTER(STRING), POINTER(size_t), c_int, POINTER(FILE)]
fputs = _libraries['libnfc.so'].fputs
fputs.restype = c_int
fputs.argtypes = [STRING, POINTER(FILE)]
puts = _libraries['libnfc.so'].puts
puts.restype = c_int
puts.argtypes = [STRING]
ungetc = _libraries['libnfc.so'].ungetc
ungetc.restype = c_int
ungetc.argtypes = [c_int, POINTER(FILE)]
fwrite = _libraries['libnfc.so'].fwrite
fwrite.restype = size_t
fwrite.argtypes = [c_void_p, size_t, size_t, POINTER(FILE)]
fputs_unlocked = _libraries['libnfc.so'].fputs_unlocked
fputs_unlocked.restype = c_int
fputs_unlocked.argtypes = [STRING, POINTER(FILE)]
fwrite_unlocked = _libraries['libnfc.so'].fwrite_unlocked
fwrite_unlocked.restype = size_t
fwrite_unlocked.argtypes = [c_void_p, size_t, size_t, POINTER(FILE)]
fseek = _libraries['libnfc.so'].fseek
fseek.restype = c_int
fseek.argtypes = [POINTER(FILE), c_long, c_int]
ftell = _libraries['libnfc.so'].ftell
ftell.restype = c_long
ftell.argtypes = [POINTER(FILE)]
rewind = _libraries['libnfc.so'].rewind
rewind.restype = None
rewind.argtypes = [POINTER(FILE)]
fseeko = _libraries['libnfc.so'].fseeko
fseeko.restype = c_int
fseeko.argtypes = [POINTER(FILE), __off_t, c_int]
ftello = _libraries['libnfc.so'].ftello
ftello.restype = __off_t
ftello.argtypes = [POINTER(FILE)]
fgetpos = _libraries['libnfc.so'].fgetpos
fgetpos.restype = c_int
fgetpos.argtypes = [POINTER(FILE), POINTER(fpos_t)]
fsetpos = _libraries['libnfc.so'].fsetpos
fsetpos.restype = c_int
fsetpos.argtypes = [POINTER(FILE), POINTER(fpos_t)]
fseeko64 = _libraries['libnfc.so'].fseeko64
fseeko64.restype = c_int
fseeko64.argtypes = [POINTER(FILE), __off64_t, c_int]
ftello64 = _libraries['libnfc.so'].ftello64
ftello64.restype = __off64_t
ftello64.argtypes = [POINTER(FILE)]
fgetpos64 = _libraries['libnfc.so'].fgetpos64
fgetpos64.restype = c_int
fgetpos64.argtypes = [POINTER(FILE), POINTER(fpos64_t)]
fsetpos64 = _libraries['libnfc.so'].fsetpos64
fsetpos64.restype = c_int
fsetpos64.argtypes = [POINTER(FILE), POINTER(fpos64_t)]
clearerr = _libraries['libnfc.so'].clearerr
clearerr.restype = None
clearerr.argtypes = [POINTER(FILE)]
feof = _libraries['libnfc.so'].feof
feof.restype = c_int
feof.argtypes = [POINTER(FILE)]
ferror = _libraries['libnfc.so'].ferror
ferror.restype = c_int
ferror.argtypes = [POINTER(FILE)]
clearerr_unlocked = _libraries['libnfc.so'].clearerr_unlocked
clearerr_unlocked.restype = None
clearerr_unlocked.argtypes = [POINTER(FILE)]
perror = _libraries['libnfc.so'].perror
perror.restype = None
perror.argtypes = [STRING]
fileno = _libraries['libnfc.so'].fileno
fileno.restype = c_int
fileno.argtypes = [POINTER(FILE)]
fileno_unlocked = _libraries['libnfc.so'].fileno_unlocked
fileno_unlocked.restype = c_int
fileno_unlocked.argtypes = [POINTER(FILE)]
popen = _libraries['libnfc.so'].popen
popen.restype = POINTER(FILE)
popen.argtypes = [STRING, STRING]
pclose = _libraries['libnfc.so'].pclose
pclose.restype = c_int
pclose.argtypes = [POINTER(FILE)]
ctermid = _libraries['libnfc.so'].ctermid
ctermid.restype = STRING
ctermid.argtypes = [STRING]
cuserid = _libraries['libnfc.so'].cuserid
cuserid.restype = STRING
cuserid.argtypes = [STRING]
class obstack(Structure):
    pass
obstack._fields_ = [
]
flockfile = _libraries['libnfc.so'].flockfile
flockfile.restype = None
flockfile.argtypes = [POINTER(FILE)]
ftrylockfile = _libraries['libnfc.so'].ftrylockfile
ftrylockfile.restype = c_int
ftrylockfile.argtypes = [POINTER(FILE)]
funlockfile = _libraries['libnfc.so'].funlockfile
funlockfile.restype = None
funlockfile.argtypes = [POINTER(FILE)]
__time_t = c_long
time_t = __time_t
class timespec(Structure):
    pass
__syscall_slong_t = c_long
timespec._fields_ = [
    ('tv_sec', __time_t),
    ('tv_nsec', __syscall_slong_t),
]
__fdelt_chk = _libraries['libnfc.so'].__fdelt_chk
__fdelt_chk.restype = c_long
__fdelt_chk.argtypes = [c_long]
__fdelt_warn = _libraries['libnfc.so'].__fdelt_warn
__fdelt_warn.restype = c_long
__fdelt_warn.argtypes = [c_long]
__sig_atomic_t = c_int
class __sigset_t(Structure):
    pass
__sigset_t._fields_ = [
    ('__val', c_ulong * 16),
]
getchar = _libraries['libnfc.so'].getchar
getchar.restype = c_int
getchar.argtypes = []
fgetc_unlocked = _libraries['libnfc.so'].fgetc_unlocked
fgetc_unlocked.restype = c_int
fgetc_unlocked.argtypes = [POINTER(FILE)]
getc_unlocked = _libraries['libnfc.so'].getc_unlocked
getc_unlocked.restype = c_int
getc_unlocked.argtypes = [POINTER(FILE)]
getchar_unlocked = _libraries['libnfc.so'].getchar_unlocked
getchar_unlocked.restype = c_int
getchar_unlocked.argtypes = []
putchar = _libraries['libnfc.so'].putchar
putchar.restype = c_int
putchar.argtypes = [c_int]
fputc_unlocked = _libraries['libnfc.so'].fputc_unlocked
fputc_unlocked.restype = c_int
fputc_unlocked.argtypes = [c_int, POINTER(FILE)]
putc_unlocked = _libraries['libnfc.so'].putc_unlocked
putc_unlocked.restype = c_int
putc_unlocked.argtypes = [c_int, POINTER(FILE)]
putchar_unlocked = _libraries['libnfc.so'].putchar_unlocked
putchar_unlocked.restype = c_int
putchar_unlocked.argtypes = [c_int]
getline = _libraries['libnfc.so'].getline
getline.restype = __ssize_t
getline.argtypes = [POINTER(STRING), POINTER(size_t), POINTER(FILE)]
feof_unlocked = _libraries['libnfc.so'].feof_unlocked
feof_unlocked.restype = c_int
feof_unlocked.argtypes = [POINTER(FILE)]
ferror_unlocked = _libraries['libnfc.so'].ferror_unlocked
ferror_unlocked.restype = c_int
ferror_unlocked.argtypes = [POINTER(FILE)]
__sprintf_chk = _libraries['libnfc.so'].__sprintf_chk
__sprintf_chk.restype = c_int
__sprintf_chk.argtypes = [STRING, c_int, size_t, STRING]
__vsprintf_chk = _libraries['libnfc.so'].__vsprintf_chk
__vsprintf_chk.restype = c_int
__vsprintf_chk.argtypes = [STRING, c_int, size_t, STRING, POINTER(__va_list_tag)]
sprintf = _libraries['libnfc.so'].sprintf
sprintf.restype = c_int
sprintf.argtypes = [STRING, STRING]
vsprintf = _libraries['libnfc.so'].vsprintf
vsprintf.restype = c_int
vsprintf.argtypes = [STRING, STRING, POINTER(__va_list_tag)]
__snprintf_chk = _libraries['libnfc.so'].__snprintf_chk
__snprintf_chk.restype = c_int
__snprintf_chk.argtypes = [STRING, size_t, c_int, size_t, STRING]
__vsnprintf_chk = _libraries['libnfc.so'].__vsnprintf_chk
__vsnprintf_chk.restype = c_int
__vsnprintf_chk.argtypes = [STRING, size_t, c_int, size_t, STRING, POINTER(__va_list_tag)]
snprintf = _libraries['libnfc.so'].snprintf
snprintf.restype = c_int
snprintf.argtypes = [STRING, size_t, STRING]
vsnprintf = _libraries['libnfc.so'].vsnprintf
vsnprintf.restype = c_int
vsnprintf.argtypes = [STRING, size_t, STRING, POINTER(__va_list_tag)]
__fprintf_chk = _libraries['libnfc.so'].__fprintf_chk
__fprintf_chk.restype = c_int
__fprintf_chk.argtypes = [POINTER(FILE), c_int, STRING]
__printf_chk = _libraries['libnfc.so'].__printf_chk
__printf_chk.restype = c_int
__printf_chk.argtypes = [c_int, STRING]
__vfprintf_chk = _libraries['libnfc.so'].__vfprintf_chk
__vfprintf_chk.restype = c_int
__vfprintf_chk.argtypes = [POINTER(FILE), c_int, STRING, POINTER(__va_list_tag)]
__vprintf_chk = _libraries['libnfc.so'].__vprintf_chk
__vprintf_chk.restype = c_int
__vprintf_chk.argtypes = [c_int, STRING, POINTER(__va_list_tag)]
fprintf = _libraries['libnfc.so'].fprintf
fprintf.restype = c_int
fprintf.argtypes = [POINTER(FILE), STRING]
printf = _libraries['libnfc.so'].printf
printf.restype = c_int
printf.argtypes = [STRING]
vprintf = _libraries['libnfc.so'].vprintf
vprintf.restype = c_int
vprintf.argtypes = [STRING, POINTER(__va_list_tag)]
vfprintf = _libraries['libnfc.so'].vfprintf
vfprintf.restype = c_int
vfprintf.argtypes = [POINTER(FILE), STRING, POINTER(__va_list_tag)]
__dprintf_chk = _libraries['libnfc.so'].__dprintf_chk
__dprintf_chk.restype = c_int
__dprintf_chk.argtypes = [c_int, c_int, STRING]
__vdprintf_chk = _libraries['libnfc.so'].__vdprintf_chk
__vdprintf_chk.restype = c_int
__vdprintf_chk.argtypes = [c_int, c_int, STRING, POINTER(__va_list_tag)]
dprintf = _libraries['libnfc.so'].dprintf
dprintf.restype = c_int
dprintf.argtypes = [c_int, STRING]
vdprintf = _libraries['libnfc.so'].vdprintf
vdprintf.restype = c_int
vdprintf.argtypes = [c_int, STRING, POINTER(__va_list_tag)]
__asprintf_chk = _libraries['libnfc.so'].__asprintf_chk
__asprintf_chk.restype = c_int
__asprintf_chk.argtypes = [POINTER(STRING), c_int, STRING]
__vasprintf_chk = _libraries['libnfc.so'].__vasprintf_chk
__vasprintf_chk.restype = c_int
__vasprintf_chk.argtypes = [POINTER(STRING), c_int, STRING, POINTER(__va_list_tag)]
__obstack_printf_chk = _libraries['libnfc.so'].__obstack_printf_chk
__obstack_printf_chk.restype = c_int
__obstack_printf_chk.argtypes = [POINTER(obstack), c_int, STRING]
__obstack_vprintf_chk = _libraries['libnfc.so'].__obstack_vprintf_chk
__obstack_vprintf_chk.restype = c_int
__obstack_vprintf_chk.argtypes = [POINTER(obstack), c_int, STRING, POINTER(__va_list_tag)]
asprintf = _libraries['libnfc.so'].asprintf
asprintf.restype = c_int
asprintf.argtypes = [POINTER(STRING), STRING]
__asprintf = _libraries['libnfc.so'].__asprintf
__asprintf.restype = c_int
__asprintf.argtypes = [POINTER(STRING), STRING]
obstack_printf = _libraries['libnfc.so'].obstack_printf
obstack_printf.restype = c_int
obstack_printf.argtypes = [POINTER(obstack), STRING]
vasprintf = _libraries['libnfc.so'].vasprintf
vasprintf.restype = c_int
vasprintf.argtypes = [POINTER(STRING), STRING, POINTER(__va_list_tag)]
obstack_vprintf = _libraries['libnfc.so'].obstack_vprintf
obstack_vprintf.restype = c_int
obstack_vprintf.argtypes = [POINTER(obstack), STRING, POINTER(__va_list_tag)]
__fgets_chk = _libraries['libnfc.so'].__fgets_chk
__fgets_chk.restype = STRING
__fgets_chk.argtypes = [STRING, size_t, c_int, POINTER(FILE)]
fgets = _libraries['libnfc.so'].fgets
fgets.restype = STRING
fgets.argtypes = [STRING, c_int, POINTER(FILE)]
__fread_chk = _libraries['libnfc.so'].__fread_chk
__fread_chk.restype = size_t
__fread_chk.argtypes = [c_void_p, size_t, size_t, size_t, POINTER(FILE)]
fread = _libraries['libnfc.so'].fread
fread.restype = size_t
fread.argtypes = [c_void_p, size_t, size_t, POINTER(FILE)]
__fgets_unlocked_chk = _libraries['libnfc.so'].__fgets_unlocked_chk
__fgets_unlocked_chk.restype = STRING
__fgets_unlocked_chk.argtypes = [STRING, size_t, c_int, POINTER(FILE)]
fgets_unlocked = _libraries['libnfc.so'].fgets_unlocked
fgets_unlocked.restype = STRING
fgets_unlocked.argtypes = [STRING, c_int, POINTER(FILE)]
__fread_unlocked_chk = _libraries['libnfc.so'].__fread_unlocked_chk
__fread_unlocked_chk.restype = size_t
__fread_unlocked_chk.argtypes = [c_void_p, size_t, size_t, size_t, POINTER(FILE)]
fread_unlocked = _libraries['libnfc.so'].fread_unlocked
fread_unlocked.restype = size_t
fread_unlocked.argtypes = [c_void_p, size_t, size_t, POINTER(FILE)]
sys_nerr = (c_int).in_dll(_libraries['libnfc.so'], 'sys_nerr')
sys_errlist = (STRING * 0).in_dll(_libraries['libnfc.so'], 'sys_errlist')
_sys_nerr = (c_int).in_dll(_libraries['libnfc.so'], '_sys_nerr')
_sys_errlist = (STRING * 0).in_dll(_libraries['libnfc.so'], '_sys_errlist')
class timeval(Structure):
    pass
__suseconds_t = c_long
timeval._fields_ = [
    ('tv_sec', __time_t),
    ('tv_usec', __suseconds_t),
]
__u_char = c_ubyte
__u_short = c_ushort
__u_int = c_uint
__u_long = c_ulong
__int8_t = c_byte
__uint8_t = c_ubyte
__int16_t = c_short
__uint16_t = c_ushort
__int32_t = c_int
__uint32_t = c_uint
__int64_t = c_long
__uint64_t = c_ulong
__quad_t = c_long
__u_quad_t = c_ulong
__dev_t = c_ulong
__uid_t = c_uint
__gid_t = c_uint
__ino_t = c_ulong
__ino64_t = c_ulong
__mode_t = c_uint
__nlink_t = c_ulong
__pid_t = c_int
class __fsid_t(Structure):
    pass
__fsid_t._fields_ = [
    ('__val', c_int * 2),
]
__clock_t = c_long
__rlim_t = c_ulong
__rlim64_t = c_ulong
__id_t = c_uint
__useconds_t = c_uint
__daddr_t = c_int
__key_t = c_int
__clockid_t = c_int
__timer_t = c_void_p
__blksize_t = c_long
__blkcnt_t = c_long
__blkcnt64_t = c_long
__fsblkcnt_t = c_ulong
__fsblkcnt64_t = c_ulong
__fsfilcnt_t = c_ulong
__fsfilcnt64_t = c_ulong
__fsword_t = c_long
__syscall_ulong_t = c_ulong
__loff_t = __off64_t
__qaddr_t = POINTER(__quad_t)
__caddr_t = STRING
__intptr_t = c_long
__socklen_t = c_uint
sigset_t = __sigset_t
suseconds_t = __suseconds_t
__fd_mask = c_long
class fd_set(Structure):
    pass
fd_set._fields_ = [
    ('fds_bits', __fd_mask * 16),
]
fd_mask = __fd_mask
select = _libraries['libnfc.so'].select
select.restype = c_int
select.argtypes = [c_int, POINTER(fd_set), POINTER(fd_set), POINTER(fd_set), POINTER(timeval)]
pselect = _libraries['libnfc.so'].pselect
pselect.restype = c_int
pselect.argtypes = [c_int, POINTER(fd_set), POINTER(fd_set), POINTER(fd_set), POINTER(timespec), POINTER(__sigset_t)]
class timezone(Structure):
    pass
timezone._fields_ = [
    ('tz_minuteswest', c_int),
    ('tz_dsttime', c_int),
]
__timezone_ptr_t = POINTER(timezone)
gettimeofday = _libraries['libnfc.so'].gettimeofday
gettimeofday.restype = c_int
gettimeofday.argtypes = [POINTER(timeval), __timezone_ptr_t]
settimeofday = _libraries['libnfc.so'].settimeofday
settimeofday.restype = c_int
settimeofday.argtypes = [POINTER(timeval), POINTER(timezone)]
adjtime = _libraries['libnfc.so'].adjtime
adjtime.restype = c_int
adjtime.argtypes = [POINTER(timeval), POINTER(timeval)]

# values for enumeration '__itimer_which'
__itimer_which = c_int # enum
class itimerval(Structure):
    pass
itimerval._fields_ = [
    ('it_interval', timeval),
    ('it_value', timeval),
]
__itimer_which_t = c_int
getitimer = _libraries['libnfc.so'].getitimer
getitimer.restype = c_int
getitimer.argtypes = [__itimer_which_t, POINTER(itimerval)]
setitimer = _libraries['libnfc.so'].setitimer
setitimer.restype = c_int
setitimer.argtypes = [__itimer_which_t, POINTER(itimerval), POINTER(itimerval)]
utimes = _libraries['libnfc.so'].utimes
utimes.restype = c_int
utimes.argtypes = [STRING, POINTER(timeval)]
lutimes = _libraries['libnfc.so'].lutimes
lutimes.restype = c_int
lutimes.argtypes = [STRING, POINTER(timeval)]
futimes = _libraries['libnfc.so'].futimes
futimes.restype = c_int
futimes.argtypes = [c_int, POINTER(timeval)]
futimesat = _libraries['libnfc.so'].futimesat
futimesat.restype = c_int
futimesat.argtypes = [c_int, STRING, POINTER(timeval)]
ptrdiff_t = c_long
class nfc_user_defined_device(Structure):
    pass
nfc_user_defined_device._fields_ = [
    ('name', c_char * 256),
    ('connstring', nfc_connstring),
    ('optional', c_bool),
]
nfc_context._fields_ = [
    ('allow_autoscan', c_bool),
    ('allow_intrusive_scan', c_bool),
    ('log_level', uint32_t),
    ('user_defined_devices', nfc_user_defined_device * 4),
    ('user_defined_device_count', c_uint),
]
nfc_device._fields_ = [
    ('context', POINTER(nfc_context)),
    ('driver', POINTER(nfc_driver)),
    ('driver_data', c_void_p),
    ('chip_data', c_void_p),
    ('name', c_char * 256),
    ('connstring', nfc_connstring),
    ('bCrc', c_bool),
    ('bPar', c_bool),
    ('bEasyFraming', c_bool),
    ('bInfiniteSelect', c_bool),
    ('bAutoIso14443_4', c_bool),
    ('btSupportByte', uint8_t),
    ('last_error', c_int),
]
__all__ = ['__int16_t', 'nfc_property', 'getc_unlocked',
           'int_fast32_t', '__off64_t', 'nfc_device_get_name',
           'uint8_t', 'fpos_t', 'getline', '__FILE', 'fclose',
           '__time_t', 'freopen64', 'uint_fast16_t', '_IO_jump_t',
           'iso14443a_crc_append', 'fputc_unlocked',
           'str_nfc_baud_rate', '__uint64_t', 'timespec',
           '__va_list_tag', 'nfc_initiator_select_passive_target',
           'nfc_device_set_property_bool', 'nfc_modulation',
           '__clockid_t', 'getchar_unlocked', 'N11__mbstate_t3DOT_4E',
           '_G_fpos_t', 'settimeofday', '__underflow',
           'open_memstream', 'fsetpos64', '__u_long',
           'iso14443a_locate_historical_bytes', 'popen', '_IO_ferror',
           'uint_fast8_t', '__mode_t', 'printf', 'fmemopen',
           'NMT_ISO14443B2CT', 'getchar', 'nfc_iso14443b2sr_info',
           'NP_FORCE_SPEED_106', 'nfc_target_receive_bytes',
           'fputs_unlocked', 'nfc_target_send_bytes',
           'uint_least32_t', 'int_least64_t', 'ftello64', '__int8_t',
           '__fsblkcnt64_t', 'gettimeofday', 'fwrite_unlocked',
           '__uflow', 'fopencookie', 'ftrylockfile', '__fsfilcnt64_t',
           '_IO_FILE', 'nfc_device', '__io_read_fn', 'nfc_jewel_info',
           'off_t', 'fprintf', '__fsblkcnt_t', 'feof',
           'NP_ACTIVATE_FIELD', 'str_nfc_modulation_type', 'clearerr',
           'nfc_list_devices', 'rewind', 'putc_unlocked', 'flockfile',
           'vasprintf', '_IO_free_backup_area', 'str_nfc_target',
           'nfc_strerror', 'ITIMER_PROF', 'ITIMER_VIRTUAL',
           'funlockfile', 'stdin', '__u_int', '__sprintf_chk',
           'ssize_t', '__clock_t', '__fsfilcnt_t', 'nfc_exit',
           'nfc_version', 'nfc_target', 'nfc_device_set_property_int',
           'ferror_unlocked', 'size_t', 'fwrite', 'NMT_ISO14443BI',
           '_IO_ftrylockfile', 'NP_FORCE_ISO14443_A',
           'NP_FORCE_ISO14443_B', 'uint_least16_t',
           '__syscall_slong_t', 'nfc_initiator_poll_target',
           'feof_unlocked', '__qaddr_t', 'fpos64_t', '__asprintf_chk',
           'cookie_write_function_t', '__vprintf_chk',
           'NP_INFINITE_SELECT', 'sigset_t', 'getdelim',
           '__itimer_which', '__int32_t', 'vsscanf', '__fsword_t',
           '__fd_mask', 'fileno_unlocked',
           'nfc_initiator_list_passive_targets', 'int_fast64_t',
           '__useconds_t', 'nfc_initiator_deselect_target',
           'uint_fast32_t', 'nfc_driver', 'sprintf', 'vscanf',
           'uint_least8_t', 'stderr', 'asprintf', '__printf_chk',
           '_IO_cookie_io_functions_t', '__gnuc_va_list',
           'nfc_baud_rate', 'fseeko', 'putchar', 'NP_HANDLE_PARITY',
           'nfc_register_driver', 'NP_TIMEOUT_ATR', '__rlim64_t',
           'nfc_idle', '__blksize_t', '_IO_seekoff', 'nfc_close',
           'nfc_device_get_supported_baud_rate', 'snprintf',
           '_sys_nerr', 'scanf', '__asprintf', 'dprintf',
           '__mbstate_t', 'nfc_init', '__uint8_t', 'setbuffer',
           '__u_char', '__caddr_t', '__obstack_printf_chk',
           'NDM_UNDEFINED', 'nfc_target_receive_bits',
           'nfc_device_get_connstring', '__vdprintf_chk', 'nfc_open',
           'fscanf', 'va_list', 'uint64_t',
           'nfc_initiator_transceive_bits', 'vsnprintf',
           'nfc_initiator_transceive_bytes', '_IO_peekc_locked',
           'nfc_context', 'pselect', '__fread_chk', '__rlim_t',
           'NP_ACCEPT_MULTIPLE_FRAMES', 'fseek', 'timeval',
           'nfc_initiator_init_secure_element', 'nfc_connstring',
           'nfc_iso14443a_info', '__fdelt_chk', '__quad_t',
           '__blkcnt64_t', '__key_t', 'fseeko64',
           '__obstack_vprintf_chk', '__uid_t', 'setlinebuf',
           'setvbuf', 'vfprintf', '__uint16_t', 'obstack_vprintf',
           '_IO_putc', 'putchar_unlocked', 'fputc', 'NBR_106',
           '_IO_2_1_stdin_', 'nfc_iso14443b_info', 'fgetpos64',
           'fputs', 'NP_AUTO_ISO14443_4', '__loff_t', 'intptr_t',
           'int_fast8_t', 'cookie_seek_function_t',
           '__itimer_which_t', 'fileno', 'perror', 'remove',
           '__codecvt_partial', 'nfc_device_get_information_about',
           'NDM_ACTIVE', 'NBR_212', '__fgets_chk', 'fd_mask',
           '__timer_t', 'cookie_close_function_t', 'FILE',
           '__ssize_t', '__getdelim', 'nfc_device_get_last_error',
           'itimerval', '__fprintf_chk', 'int16_t', '__sigset_t',
           'nfc_initiator_target_is_present', '_sys_errlist',
           'fgetpos', '_IO_padn', 'vdprintf', 'nfc_dep_mode',
           '__overflow', '__intptr_t', 'tmpnam_r', 'futimesat',
           'nfc_modulation_type', '_IO_FILE_plus', '__blkcnt_t',
           'uint16_t', '__vsnprintf_chk', '_IO_flockfile',
           'fflush_unlocked', 'int32_t', 'off64_t',
           'nfc_initiator_init', 'tmpfile64', 'sys_nerr',
           'nfc_felica_info', 'putw', 'puts', 'clearerr_unlocked',
           'obstack', 'putc', 'ftello', 'adjtime', '__dev_t',
           'NBR_424', '__suseconds_t', 'NMT_ISO14443B2SR',
           '__dprintf_chk', 'nfc_initiator_select_dep_target',
           'vsprintf', 'rename', 'NMT_ISO14443A', 'NMT_ISO14443B',
           'stdout', 'uintmax_t', 'lutimes', 'nfc_abort_command',
           'int_fast16_t', 'time_t', 'getc', 'nfc_strerror_r',
           'NMT_JEWEL', 'gets', 'int_least32_t', 'getw',
           '__snprintf_chk', '__io_write_fn', '__ino_t',
           '__vsprintf_chk', '_IO_lock_t', 'setbuf',
           '_IO_2_1_stdout_', 'NP_ACTIVATE_CRYPTO1',
           'nfc_device_get_supported_modulation', 'uint_fast64_t',
           'setitimer', '__timezone_ptr_t', '__int64_t', 'uint32_t',
           'fopen64', 'nfc_target_info', 'suseconds_t', '_IO_marker',
           '__fsid_t', 'fflush', 'nfc_perror', 'NP_HANDLE_CRC',
           '__uint32_t', 'fd_set', 'nfc_iso14443bi_info',
           'NP_TIMEOUT_COMMAND', 'tmpnam', '__ino64_t',
           'nfc_target_send_bits', '_IO_sgetn', 'NDM_PASSIVE',
           '__fread_unlocked_chk', 'renameat', '__fgets_unlocked_chk',
           '_G_fpos64_t', 'futimes', '_IO_vfprintf', 'freopen',
           '__nlink_t', 'fread_unlocked', 'tempnam', 'tmpfile',
           '__syscall_ulong_t', '__io_close_fn', 'fgetc', 'pclose',
           '__off_t', '__fdelt_warn', 'nfc_user_defined_device',
           'intmax_t', '__codecvt_ok', 'fgets', 'ctermid', '__id_t',
           'cookie_io_functions_t', '_IO_feof', 'nfc_target_init',
           'int_least8_t', 'fsetpos', 'ftell', 'select',
           'iso14443a_crc', 'int_least16_t', 'N_TARGET',
           '__vfprintf_chk', 'getitimer', 'nfc_free',
           '__codecvt_result', '__vasprintf_chk', 'nfc_dep_info',
           'fcloseall', 'sys_errlist', 'ptrdiff_t', 'NP_TIMEOUT_COM',
           'obstack_printf', 'ferror', 'uint_least64_t',
           'fgets_unlocked', 'NP_ACCEPT_INVALID_FRAMES', 'fopen',
           '__gid_t', 'fdopen', '__daddr_t', '_IO_cookie_file',
           '__sig_atomic_t', 'uintptr_t', 'vprintf', '__io_seek_fn',
           'int8_t', '_IO_funlockfile', '_IO_getc', 'cuserid',
           '_IO_vfscanf', 'cookie_read_function_t', 'ungetc',
           'sscanf', 'NMT_FELICA', '_IO_2_1_stderr_', 'fread',
           'ITIMER_REAL', 'NBR_UNDEFINED', 'int64_t', 'timezone',
           '_IO_seekpos', 'NBR_847', 'NMT_DEP', '__u_quad_t',
           '__u_short', 'N_INITIATOR',
           'nfc_initiator_transceive_bytes_timed', 'nfc_mode',
           'vfscanf', '__pid_t', '__codecvt_error', 'utimes',
           'nfc_initiator_transceive_bits_timed', 'NP_EASY_FRAMING',
           '__socklen_t', 'nfc_iso14443b2ct_info', '__codecvt_noconv',
           'fgetc_unlocked', 'nfc_initiator_poll_dep_target']
