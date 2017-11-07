from ctypes import *

_libraries = {}
_libraries['libfreefare.so'] = CDLL('libfreefare.so')
STRING = c_char_p
_libraries['libnfc.so'] = CDLL('libnfc.so')
WSTRING = c_wchar_p


__codecvt_ok = 0
NMT_ISO14443B2SR = 5
NP_ACTIVATE_FIELD = 5
MDFT_BACKUP_DATA_FILE = 1
N_INITIATOR = 1
N_TARGET = 0
NDM_ACTIVE = 2
NP_INFINITE_SELECT = 7
ULTRALIGHT = 0
P_PID = 1
P_PGID = 2
ITIMER_VIRTUAL = 1
NP_EASY_FRAMING = 11
DESFIRE = 4
NP_ACCEPT_INVALID_FRAMES = 8
NP_ACTIVATE_CRYPTO1 = 6
NP_TIMEOUT_ATR = 1
AS_NEW = 1
NP_HANDLE_PARITY = 4
P_ALL = 0
MDFT_VALUE_FILE_WITH_BACKUP = 2
NP_TIMEOUT_COMMAND = 0
NMT_DEP = 8
ITIMER_REAL = 0
NMT_FELICA = 7
NP_AUTO_ISO14443_4 = 10
NMT_ISO14443BI = 4
ULTRALIGHT_C = 1
MDFT_STANDARD_DATA_FILE = 0
MFC_KEY_B = 1
NP_FORCE_SPEED_106 = 14
MDFT_CYCLIC_RECORD_FILE_WITH_BACKUP = 4
NP_FORCE_ISO14443_A = 12
NP_HANDLE_CRC = 3
NDM_PASSIVE = 1
MFC_KEY_A = 0
T_3K3DES = 2
NMT_ISO14443B = 3
NBR_106 = 1
NP_FORCE_ISO14443_B = 13
NBR_847 = 4
__codecvt_noconv = 3
NBR_424 = 3
NBR_212 = 2
NBR_UNDEFINED = 0
AS_LEGACY = 0
T_DES = 0
ITIMER_PROF = 2
__codecvt_error = 2
MDFT_LINEAR_RECORD_FILE_WITH_BACKUP = 3
NDM_UNDEFINED = 0
NP_TIMEOUT_COM = 2
__codecvt_partial = 1
UIT_BOOLEAN = 3
CLASSIC_1K = 2
NP_ACCEPT_MULTIPLE_FRAMES = 9
UIT_INFO = 4
NMT_ISO14443B2CT = 6
CLASSIC_4K = 3
NMT_JEWEL = 2
NMT_ISO14443A = 1
T_AES = 3
T_3DES = 1
UIT_ERROR = 5
UIT_VERIFY = 2
UIT_PROMPT = 1
UIT_NONE = 0
class _G_fpos_t(Structure):
    pass
__off_t = c_long
class __mbstate_t(Structure):
    pass
class N11__mbstate_t4DOT_22E(Union):
    pass
N11__mbstate_t4DOT_22E._fields_ = [
    ('__wch', c_uint),
    ('__wchb', c_char * 4),
]
__mbstate_t._fields_ = [
    ('__count', c_int),
    ('__value', N11__mbstate_t4DOT_22E),
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

# values for enumeration 'mifare_tag_type'
mifare_tag_type = c_int # enum
class mifare_tag(Structure):
    pass
MifareTag = POINTER(mifare_tag)
class mifare_desfire_key(Structure):
    pass
MifareDESFireKey = POINTER(mifare_desfire_key)
uint8_t = c_uint8
MifareUltralightPageNumber = uint8_t
MifareUltralightPage = c_ubyte * 4
class nfc_device(Structure):
    pass
freefare_get_tags = _libraries['libfreefare.so'].freefare_get_tags
freefare_get_tags.restype = POINTER(MifareTag)
freefare_get_tags.argtypes = [POINTER(nfc_device)]
class nfc_iso14443a_info(Structure):
    pass
size_t = c_ulong
nfc_iso14443a_info._pack_ = 1
nfc_iso14443a_info._fields_ = [
    ('abtAtqa', uint8_t * 2),
    ('btSak', uint8_t),
    ('szUidLen', size_t),
    ('abtUid', uint8_t * 10),
    ('szAtsLen', size_t),
    ('abtAts', uint8_t * 254),
]
freefare_tag_new = _libraries['libfreefare.so'].freefare_tag_new
freefare_tag_new.restype = MifareTag
freefare_tag_new.argtypes = [POINTER(nfc_device), nfc_iso14443a_info]
freefare_get_tag_type = _libraries['libfreefare.so'].freefare_get_tag_type
freefare_get_tag_type.restype = mifare_tag_type
freefare_get_tag_type.argtypes = [MifareTag]
freefare_get_tag_friendly_name = _libraries['libfreefare.so'].freefare_get_tag_friendly_name
freefare_get_tag_friendly_name.restype = STRING
freefare_get_tag_friendly_name.argtypes = [MifareTag]
freefare_get_tag_uid = _libraries['libfreefare.so'].freefare_get_tag_uid
freefare_get_tag_uid.restype = STRING
freefare_get_tag_uid.argtypes = [MifareTag]
freefare_free_tag = _libraries['libfreefare.so'].freefare_free_tag
freefare_free_tag.restype = None
freefare_free_tag.argtypes = [MifareTag]
freefare_free_tags = _libraries['libfreefare.so'].freefare_free_tags
freefare_free_tags.restype = None
freefare_free_tags.argtypes = [POINTER(MifareTag)]
freefare_strerror = _libraries['libfreefare.so'].freefare_strerror
freefare_strerror.restype = STRING
freefare_strerror.argtypes = [MifareTag]
freefare_strerror_r = _libraries['libfreefare.so'].freefare_strerror_r
freefare_strerror_r.restype = c_int
freefare_strerror_r.argtypes = [MifareTag, STRING, size_t]
freefare_perror = _libraries['libfreefare.so'].freefare_perror
freefare_perror.restype = None
freefare_perror.argtypes = [MifareTag, STRING]
mifare_ultralight_connect = _libraries['libfreefare.so'].mifare_ultralight_connect
mifare_ultralight_connect.restype = c_int
mifare_ultralight_connect.argtypes = [MifareTag]
mifare_ultralight_disconnect = _libraries['libfreefare.so'].mifare_ultralight_disconnect
mifare_ultralight_disconnect.restype = c_int
mifare_ultralight_disconnect.argtypes = [MifareTag]
mifare_ultralight_read = _libraries['libfreefare.so'].mifare_ultralight_read
mifare_ultralight_read.restype = c_int
mifare_ultralight_read.argtypes = [MifareTag, MifareUltralightPageNumber, POINTER(MifareUltralightPage)]
mifare_ultralight_write = _libraries['libfreefare.so'].mifare_ultralight_write
mifare_ultralight_write.restype = c_int
mifare_ultralight_write.argtypes = [MifareTag, MifareUltralightPageNumber, POINTER(c_ubyte)]
mifare_ultralightc_authenticate = _libraries['libfreefare.so'].mifare_ultralightc_authenticate
mifare_ultralightc_authenticate.restype = c_int
mifare_ultralightc_authenticate.argtypes = [MifareTag, MifareDESFireKey]
is_mifare_ultralightc_on_reader = _libraries['libfreefare.so'].is_mifare_ultralightc_on_reader
is_mifare_ultralightc_on_reader.restype = c_bool
is_mifare_ultralightc_on_reader.argtypes = [POINTER(nfc_device), nfc_iso14443a_info]
MifareClassicBlock = c_ubyte * 16
MifareClassicSectorNumber = uint8_t
MifareClassicBlockNumber = c_ubyte

# values for enumeration 'MifareClassicKeyType'
MifareClassicKeyType = c_int # enum
MifareClassicKey = c_ubyte * 6
mifare_classic_nfcforum_public_key_a = (MifareClassicKey).in_dll(_libraries['libfreefare.so'], 'mifare_classic_nfcforum_public_key_a')
mifare_classic_connect = _libraries['libfreefare.so'].mifare_classic_connect
mifare_classic_connect.restype = c_int
mifare_classic_connect.argtypes = [MifareTag]
mifare_classic_disconnect = _libraries['libfreefare.so'].mifare_classic_disconnect
mifare_classic_disconnect.restype = c_int
mifare_classic_disconnect.argtypes = [MifareTag]
mifare_classic_authenticate = _libraries['libfreefare.so'].mifare_classic_authenticate
mifare_classic_authenticate.restype = c_int
mifare_classic_authenticate.argtypes = [MifareTag, MifareClassicBlockNumber, POINTER(c_ubyte), MifareClassicKeyType]
mifare_classic_read = _libraries['libfreefare.so'].mifare_classic_read
mifare_classic_read.restype = c_int
mifare_classic_read.argtypes = [MifareTag, MifareClassicBlockNumber, POINTER(MifareClassicBlock)]
int32_t = c_int32
mifare_classic_init_value = _libraries['libfreefare.so'].mifare_classic_init_value
mifare_classic_init_value.restype = c_int
mifare_classic_init_value.argtypes = [MifareTag, MifareClassicBlockNumber, int32_t, MifareClassicBlockNumber]
mifare_classic_read_value = _libraries['libfreefare.so'].mifare_classic_read_value
mifare_classic_read_value.restype = c_int
mifare_classic_read_value.argtypes = [MifareTag, MifareClassicBlockNumber, POINTER(int32_t), POINTER(MifareClassicBlockNumber)]
mifare_classic_write = _libraries['libfreefare.so'].mifare_classic_write
mifare_classic_write.restype = c_int
mifare_classic_write.argtypes = [MifareTag, MifareClassicBlockNumber, POINTER(c_ubyte)]
uint32_t = c_uint32
mifare_classic_increment = _libraries['libfreefare.so'].mifare_classic_increment
mifare_classic_increment.restype = c_int
mifare_classic_increment.argtypes = [MifareTag, MifareClassicBlockNumber, uint32_t]
mifare_classic_decrement = _libraries['libfreefare.so'].mifare_classic_decrement
mifare_classic_decrement.restype = c_int
mifare_classic_decrement.argtypes = [MifareTag, MifareClassicBlockNumber, uint32_t]
mifare_classic_restore = _libraries['libfreefare.so'].mifare_classic_restore
mifare_classic_restore.restype = c_int
mifare_classic_restore.argtypes = [MifareTag, MifareClassicBlockNumber]
mifare_classic_transfer = _libraries['libfreefare.so'].mifare_classic_transfer
mifare_classic_transfer.restype = c_int
mifare_classic_transfer.argtypes = [MifareTag, MifareClassicBlockNumber]
uint16_t = c_uint16
mifare_classic_get_trailer_block_permission = _libraries['libfreefare.so'].mifare_classic_get_trailer_block_permission
mifare_classic_get_trailer_block_permission.restype = c_int
mifare_classic_get_trailer_block_permission.argtypes = [MifareTag, MifareClassicBlockNumber, uint16_t, MifareClassicKeyType]
mifare_classic_get_data_block_permission = _libraries['libfreefare.so'].mifare_classic_get_data_block_permission
mifare_classic_get_data_block_permission.restype = c_int
mifare_classic_get_data_block_permission.argtypes = [MifareTag, MifareClassicBlockNumber, c_ubyte, MifareClassicKeyType]
mifare_classic_format_sector = _libraries['libfreefare.so'].mifare_classic_format_sector
mifare_classic_format_sector.restype = c_int
mifare_classic_format_sector.argtypes = [MifareTag, MifareClassicSectorNumber]
mifare_classic_trailer_block = _libraries['libfreefare.so'].mifare_classic_trailer_block
mifare_classic_trailer_block.restype = None
mifare_classic_trailer_block.argtypes = [POINTER(MifareClassicBlock), POINTER(c_ubyte), uint8_t, uint8_t, uint8_t, uint8_t, uint8_t, POINTER(c_ubyte)]
mifare_classic_block_sector = _libraries['libfreefare.so'].mifare_classic_block_sector
mifare_classic_block_sector.restype = MifareClassicSectorNumber
mifare_classic_block_sector.argtypes = [MifareClassicBlockNumber]
mifare_classic_sector_first_block = _libraries['libfreefare.so'].mifare_classic_sector_first_block
mifare_classic_sector_first_block.restype = MifareClassicBlockNumber
mifare_classic_sector_first_block.argtypes = [MifareClassicSectorNumber]
mifare_classic_sector_block_count = _libraries['libfreefare.so'].mifare_classic_sector_block_count
mifare_classic_sector_block_count.restype = size_t
mifare_classic_sector_block_count.argtypes = [MifareClassicSectorNumber]
mifare_classic_sector_last_block = _libraries['libfreefare.so'].mifare_classic_sector_last_block
mifare_classic_sector_last_block.restype = MifareClassicBlockNumber
mifare_classic_sector_last_block.argtypes = [MifareClassicSectorNumber]
class mad_aid(Structure):
    pass
mad_aid._fields_ = [
    ('application_code', uint8_t),
    ('function_cluster_code', uint8_t),
]
MadAid = mad_aid
class mad(Structure):
    pass
mad._fields_ = [
]
Mad = POINTER(mad)
mad_public_key_a = (MifareClassicKey).in_dll(_libraries['libfreefare.so'], 'mad_public_key_a')
mad_free_aid = (MadAid).in_dll(_libraries['libfreefare.so'], 'mad_free_aid')
mad_defect_aid = (MadAid).in_dll(_libraries['libfreefare.so'], 'mad_defect_aid')
mad_reserved_aid = (MadAid).in_dll(_libraries['libfreefare.so'], 'mad_reserved_aid')
mad_card_holder_aid = (MadAid).in_dll(_libraries['libfreefare.so'], 'mad_card_holder_aid')
mad_not_applicable_aid = (MadAid).in_dll(_libraries['libfreefare.so'], 'mad_not_applicable_aid')
mad_nfcforum_aid = (MadAid).in_dll(_libraries['libfreefare.so'], 'mad_nfcforum_aid')
mad_new = _libraries['libfreefare.so'].mad_new
mad_new.restype = Mad
mad_new.argtypes = [uint8_t]
mad_read = _libraries['libfreefare.so'].mad_read
mad_read.restype = Mad
mad_read.argtypes = [MifareTag]
mad_write = _libraries['libfreefare.so'].mad_write
mad_write.restype = c_int
mad_write.argtypes = [MifareTag, Mad, POINTER(c_ubyte), POINTER(c_ubyte)]
mad_get_version = _libraries['libfreefare.so'].mad_get_version
mad_get_version.restype = c_int
mad_get_version.argtypes = [Mad]
mad_set_version = _libraries['libfreefare.so'].mad_set_version
mad_set_version.restype = None
mad_set_version.argtypes = [Mad, uint8_t]
mad_get_card_publisher_sector = _libraries['libfreefare.so'].mad_get_card_publisher_sector
mad_get_card_publisher_sector.restype = MifareClassicSectorNumber
mad_get_card_publisher_sector.argtypes = [Mad]
mad_set_card_publisher_sector = _libraries['libfreefare.so'].mad_set_card_publisher_sector
mad_set_card_publisher_sector.restype = c_int
mad_set_card_publisher_sector.argtypes = [Mad, MifareClassicSectorNumber]
mad_get_aid = _libraries['libfreefare.so'].mad_get_aid
mad_get_aid.restype = c_int
mad_get_aid.argtypes = [Mad, MifareClassicSectorNumber, POINTER(MadAid)]
mad_set_aid = _libraries['libfreefare.so'].mad_set_aid
mad_set_aid.restype = c_int
mad_set_aid.argtypes = [Mad, MifareClassicSectorNumber, MadAid]
mad_sector_reserved = _libraries['libfreefare.so'].mad_sector_reserved
mad_sector_reserved.restype = c_bool
mad_sector_reserved.argtypes = [MifareClassicSectorNumber]
mad_free = _libraries['libfreefare.so'].mad_free
mad_free.restype = None
mad_free.argtypes = [Mad]
mifare_application_alloc = _libraries['libfreefare.so'].mifare_application_alloc
mifare_application_alloc.restype = POINTER(MifareClassicSectorNumber)
mifare_application_alloc.argtypes = [Mad, MadAid, size_t]
__ssize_t = c_long
ssize_t = __ssize_t
mifare_application_read = _libraries['libfreefare.so'].mifare_application_read
mifare_application_read.restype = ssize_t
mifare_application_read.argtypes = [MifareTag, Mad, MadAid, c_void_p, size_t, POINTER(c_ubyte), MifareClassicKeyType]
mifare_application_write = _libraries['libfreefare.so'].mifare_application_write
mifare_application_write.restype = ssize_t
mifare_application_write.argtypes = [MifareTag, Mad, MadAid, c_void_p, size_t, POINTER(c_ubyte), MifareClassicKeyType]
mifare_application_free = _libraries['libfreefare.so'].mifare_application_free
mifare_application_free.restype = None
mifare_application_free.argtypes = [Mad, MadAid]
mifare_application_find = _libraries['libfreefare.so'].mifare_application_find
mifare_application_find.restype = POINTER(MifareClassicSectorNumber)
mifare_application_find.argtypes = [Mad, MadAid]

# values for enumeration 'mifare_desfire_file_types'
mifare_desfire_file_types = c_int # enum
class mifare_desfire_aid(Structure):
    pass
MifareDESFireAID = POINTER(mifare_desfire_aid)
class mifare_desfire_df(Structure):
    pass
mifare_desfire_df._fields_ = [
    ('aid', uint32_t),
    ('fid', uint16_t),
    ('df_name', uint8_t * 16),
    ('df_name_len', size_t),
]
MifareDESFireDF = mifare_desfire_df
mifare_desfire_aid_new = _libraries['libfreefare.so'].mifare_desfire_aid_new
mifare_desfire_aid_new.restype = MifareDESFireAID
mifare_desfire_aid_new.argtypes = [uint32_t]
mifare_desfire_aid_new_with_mad_aid = _libraries['libfreefare.so'].mifare_desfire_aid_new_with_mad_aid
mifare_desfire_aid_new_with_mad_aid.restype = MifareDESFireAID
mifare_desfire_aid_new_with_mad_aid.argtypes = [MadAid, uint8_t]
mifare_desfire_aid_get_aid = _libraries['libfreefare.so'].mifare_desfire_aid_get_aid
mifare_desfire_aid_get_aid.restype = uint32_t
mifare_desfire_aid_get_aid.argtypes = [MifareDESFireAID]
mifare_desfire_last_pcd_error = _libraries['libfreefare.so'].mifare_desfire_last_pcd_error
mifare_desfire_last_pcd_error.restype = uint8_t
mifare_desfire_last_pcd_error.argtypes = [MifareTag]
mifare_desfire_last_picc_error = _libraries['libfreefare.so'].mifare_desfire_last_picc_error
mifare_desfire_last_picc_error.restype = uint8_t
mifare_desfire_last_picc_error.argtypes = [MifareTag]
class mifare_desfire_version_info(Structure):
    pass
class N27mifare_desfire_version_info4DOT_44E(Structure):
    pass
N27mifare_desfire_version_info4DOT_44E._fields_ = [
    ('vendor_id', uint8_t),
    ('type', uint8_t),
    ('subtype', uint8_t),
    ('version_major', uint8_t),
    ('version_minor', uint8_t),
    ('storage_size', uint8_t),
    ('protocol', uint8_t),
]
class N27mifare_desfire_version_info4DOT_45E(Structure):
    pass
N27mifare_desfire_version_info4DOT_45E._fields_ = [
    ('vendor_id', uint8_t),
    ('type', uint8_t),
    ('subtype', uint8_t),
    ('version_major', uint8_t),
    ('version_minor', uint8_t),
    ('storage_size', uint8_t),
    ('protocol', uint8_t),
]
mifare_desfire_version_info._fields_ = [
    ('hardware', N27mifare_desfire_version_info4DOT_44E),
    ('software', N27mifare_desfire_version_info4DOT_45E),
    ('uid', uint8_t * 7),
    ('batch_number', uint8_t * 5),
    ('production_week', uint8_t),
    ('production_year', uint8_t),
]
class mifare_desfire_file_settings(Structure):
    pass
class N28mifare_desfire_file_settings4DOT_46E(Union):
    pass
class N28mifare_desfire_file_settings4DOT_464DOT_47E(Structure):
    pass
N28mifare_desfire_file_settings4DOT_464DOT_47E._fields_ = [
    ('file_size', uint32_t),
]
class N28mifare_desfire_file_settings4DOT_464DOT_48E(Structure):
    pass
N28mifare_desfire_file_settings4DOT_464DOT_48E._fields_ = [
    ('lower_limit', int32_t),
    ('upper_limit', int32_t),
    ('limited_credit_value', int32_t),
    ('limited_credit_enabled', uint8_t),
]
class N28mifare_desfire_file_settings4DOT_464DOT_49E(Structure):
    pass
N28mifare_desfire_file_settings4DOT_464DOT_49E._fields_ = [
    ('record_size', uint32_t),
    ('max_number_of_records', uint32_t),
    ('current_number_of_records', uint32_t),
]
N28mifare_desfire_file_settings4DOT_46E._fields_ = [
    ('standard_file', N28mifare_desfire_file_settings4DOT_464DOT_47E),
    ('value_file', N28mifare_desfire_file_settings4DOT_464DOT_48E),
    ('linear_record_file', N28mifare_desfire_file_settings4DOT_464DOT_49E),
]
mifare_desfire_file_settings._fields_ = [
    ('file_type', uint8_t),
    ('communication_settings', uint8_t),
    ('access_rights', uint16_t),
    ('settings', N28mifare_desfire_file_settings4DOT_46E),
]
mifare_desfire_connect = _libraries['libfreefare.so'].mifare_desfire_connect
mifare_desfire_connect.restype = c_int
mifare_desfire_connect.argtypes = [MifareTag]
mifare_desfire_disconnect = _libraries['libfreefare.so'].mifare_desfire_disconnect
mifare_desfire_disconnect.restype = c_int
mifare_desfire_disconnect.argtypes = [MifareTag]
mifare_desfire_authenticate = _libraries['libfreefare.so'].mifare_desfire_authenticate
mifare_desfire_authenticate.restype = c_int
mifare_desfire_authenticate.argtypes = [MifareTag, uint8_t, MifareDESFireKey]
mifare_desfire_authenticate_iso = _libraries['libfreefare.so'].mifare_desfire_authenticate_iso
mifare_desfire_authenticate_iso.restype = c_int
mifare_desfire_authenticate_iso.argtypes = [MifareTag, uint8_t, MifareDESFireKey]
mifare_desfire_authenticate_aes = _libraries['libfreefare.so'].mifare_desfire_authenticate_aes
mifare_desfire_authenticate_aes.restype = c_int
mifare_desfire_authenticate_aes.argtypes = [MifareTag, uint8_t, MifareDESFireKey]
mifare_desfire_change_key_settings = _libraries['libfreefare.so'].mifare_desfire_change_key_settings
mifare_desfire_change_key_settings.restype = c_int
mifare_desfire_change_key_settings.argtypes = [MifareTag, uint8_t]
mifare_desfire_get_key_settings = _libraries['libfreefare.so'].mifare_desfire_get_key_settings
mifare_desfire_get_key_settings.restype = c_int
mifare_desfire_get_key_settings.argtypes = [MifareTag, POINTER(uint8_t), POINTER(uint8_t)]
mifare_desfire_change_key = _libraries['libfreefare.so'].mifare_desfire_change_key
mifare_desfire_change_key.restype = c_int
mifare_desfire_change_key.argtypes = [MifareTag, uint8_t, MifareDESFireKey, MifareDESFireKey]
mifare_desfire_get_key_version = _libraries['libfreefare.so'].mifare_desfire_get_key_version
mifare_desfire_get_key_version.restype = c_int
mifare_desfire_get_key_version.argtypes = [MifareTag, uint8_t, POINTER(uint8_t)]
mifare_desfire_create_application = _libraries['libfreefare.so'].mifare_desfire_create_application
mifare_desfire_create_application.restype = c_int
mifare_desfire_create_application.argtypes = [MifareTag, MifareDESFireAID, uint8_t, uint8_t]
mifare_desfire_create_application_3k3des = _libraries['libfreefare.so'].mifare_desfire_create_application_3k3des
mifare_desfire_create_application_3k3des.restype = c_int
mifare_desfire_create_application_3k3des.argtypes = [MifareTag, MifareDESFireAID, uint8_t, uint8_t]
mifare_desfire_create_application_aes = _libraries['libfreefare.so'].mifare_desfire_create_application_aes
mifare_desfire_create_application_aes.restype = c_int
mifare_desfire_create_application_aes.argtypes = [MifareTag, MifareDESFireAID, uint8_t, uint8_t]
mifare_desfire_create_application_iso = _libraries['libfreefare.so'].mifare_desfire_create_application_iso
mifare_desfire_create_application_iso.restype = c_int
mifare_desfire_create_application_iso.argtypes = [MifareTag, MifareDESFireAID, uint8_t, uint8_t, c_int, uint16_t, POINTER(uint8_t), size_t]
mifare_desfire_create_application_3k3des_iso = _libraries['libfreefare.so'].mifare_desfire_create_application_3k3des_iso
mifare_desfire_create_application_3k3des_iso.restype = c_int
mifare_desfire_create_application_3k3des_iso.argtypes = [MifareTag, MifareDESFireAID, uint8_t, uint8_t, c_int, uint16_t, POINTER(uint8_t), size_t]
mifare_desfire_create_application_aes_iso = _libraries['libfreefare.so'].mifare_desfire_create_application_aes_iso
mifare_desfire_create_application_aes_iso.restype = c_int
mifare_desfire_create_application_aes_iso.argtypes = [MifareTag, MifareDESFireAID, uint8_t, uint8_t, c_int, uint16_t, POINTER(uint8_t), size_t]
mifare_desfire_delete_application = _libraries['libfreefare.so'].mifare_desfire_delete_application
mifare_desfire_delete_application.restype = c_int
mifare_desfire_delete_application.argtypes = [MifareTag, MifareDESFireAID]
mifare_desfire_get_application_ids = _libraries['libfreefare.so'].mifare_desfire_get_application_ids
mifare_desfire_get_application_ids.restype = c_int
mifare_desfire_get_application_ids.argtypes = [MifareTag, POINTER(POINTER(MifareDESFireAID)), POINTER(size_t)]
mifare_desfire_get_df_names = _libraries['libfreefare.so'].mifare_desfire_get_df_names
mifare_desfire_get_df_names.restype = c_int
mifare_desfire_get_df_names.argtypes = [MifareTag, POINTER(POINTER(MifareDESFireDF)), POINTER(size_t)]
mifare_desfire_free_application_ids = _libraries['libfreefare.so'].mifare_desfire_free_application_ids
mifare_desfire_free_application_ids.restype = None
mifare_desfire_free_application_ids.argtypes = [POINTER(MifareDESFireAID)]
mifare_desfire_select_application = _libraries['libfreefare.so'].mifare_desfire_select_application
mifare_desfire_select_application.restype = c_int
mifare_desfire_select_application.argtypes = [MifareTag, MifareDESFireAID]
mifare_desfire_format_picc = _libraries['libfreefare.so'].mifare_desfire_format_picc
mifare_desfire_format_picc.restype = c_int
mifare_desfire_format_picc.argtypes = [MifareTag]
mifare_desfire_get_version = _libraries['libfreefare.so'].mifare_desfire_get_version
mifare_desfire_get_version.restype = c_int
mifare_desfire_get_version.argtypes = [MifareTag, POINTER(mifare_desfire_version_info)]
mifare_desfire_free_mem = _libraries['libfreefare.so'].mifare_desfire_free_mem
mifare_desfire_free_mem.restype = c_int
mifare_desfire_free_mem.argtypes = [MifareTag, POINTER(uint32_t)]
mifare_desfire_set_configuration = _libraries['libfreefare.so'].mifare_desfire_set_configuration
mifare_desfire_set_configuration.restype = c_int
mifare_desfire_set_configuration.argtypes = [MifareTag, c_bool, c_bool]
mifare_desfire_set_default_key = _libraries['libfreefare.so'].mifare_desfire_set_default_key
mifare_desfire_set_default_key.restype = c_int
mifare_desfire_set_default_key.argtypes = [MifareTag, MifareDESFireKey]
mifare_desfire_set_ats = _libraries['libfreefare.so'].mifare_desfire_set_ats
mifare_desfire_set_ats.restype = c_int
mifare_desfire_set_ats.argtypes = [MifareTag, POINTER(uint8_t)]
mifare_desfire_get_card_uid = _libraries['libfreefare.so'].mifare_desfire_get_card_uid
mifare_desfire_get_card_uid.restype = c_int
mifare_desfire_get_card_uid.argtypes = [MifareTag, POINTER(STRING)]
mifare_desfire_get_file_ids = _libraries['libfreefare.so'].mifare_desfire_get_file_ids
mifare_desfire_get_file_ids.restype = c_int
mifare_desfire_get_file_ids.argtypes = [MifareTag, POINTER(POINTER(uint8_t)), POINTER(size_t)]
mifare_desfire_get_iso_file_ids = _libraries['libfreefare.so'].mifare_desfire_get_iso_file_ids
mifare_desfire_get_iso_file_ids.restype = c_int
mifare_desfire_get_iso_file_ids.argtypes = [MifareTag, POINTER(POINTER(uint16_t)), POINTER(size_t)]
mifare_desfire_get_file_settings = _libraries['libfreefare.so'].mifare_desfire_get_file_settings
mifare_desfire_get_file_settings.restype = c_int
mifare_desfire_get_file_settings.argtypes = [MifareTag, uint8_t, POINTER(mifare_desfire_file_settings)]
mifare_desfire_change_file_settings = _libraries['libfreefare.so'].mifare_desfire_change_file_settings
mifare_desfire_change_file_settings.restype = c_int
mifare_desfire_change_file_settings.argtypes = [MifareTag, uint8_t, uint8_t, uint16_t]
mifare_desfire_create_std_data_file = _libraries['libfreefare.so'].mifare_desfire_create_std_data_file
mifare_desfire_create_std_data_file.restype = c_int
mifare_desfire_create_std_data_file.argtypes = [MifareTag, uint8_t, uint8_t, uint16_t, uint32_t]
mifare_desfire_create_std_data_file_iso = _libraries['libfreefare.so'].mifare_desfire_create_std_data_file_iso
mifare_desfire_create_std_data_file_iso.restype = c_int
mifare_desfire_create_std_data_file_iso.argtypes = [MifareTag, uint8_t, uint8_t, uint16_t, uint32_t, uint16_t]
mifare_desfire_create_backup_data_file = _libraries['libfreefare.so'].mifare_desfire_create_backup_data_file
mifare_desfire_create_backup_data_file.restype = c_int
mifare_desfire_create_backup_data_file.argtypes = [MifareTag, uint8_t, uint8_t, uint16_t, uint32_t]
mifare_desfire_create_backup_data_file_iso = _libraries['libfreefare.so'].mifare_desfire_create_backup_data_file_iso
mifare_desfire_create_backup_data_file_iso.restype = c_int
mifare_desfire_create_backup_data_file_iso.argtypes = [MifareTag, uint8_t, uint8_t, uint16_t, uint32_t, uint16_t]
mifare_desfire_create_value_file = _libraries['libfreefare.so'].mifare_desfire_create_value_file
mifare_desfire_create_value_file.restype = c_int
mifare_desfire_create_value_file.argtypes = [MifareTag, uint8_t, uint8_t, uint16_t, int32_t, int32_t, int32_t, uint8_t]
mifare_desfire_create_linear_record_file = _libraries['libfreefare.so'].mifare_desfire_create_linear_record_file
mifare_desfire_create_linear_record_file.restype = c_int
mifare_desfire_create_linear_record_file.argtypes = [MifareTag, uint8_t, uint8_t, uint16_t, uint32_t, uint32_t]
mifare_desfire_create_linear_record_file_iso = _libraries['libfreefare.so'].mifare_desfire_create_linear_record_file_iso
mifare_desfire_create_linear_record_file_iso.restype = c_int
mifare_desfire_create_linear_record_file_iso.argtypes = [MifareTag, uint8_t, uint8_t, uint16_t, uint32_t, uint32_t, uint16_t]
mifare_desfire_create_cyclic_record_file = _libraries['libfreefare.so'].mifare_desfire_create_cyclic_record_file
mifare_desfire_create_cyclic_record_file.restype = c_int
mifare_desfire_create_cyclic_record_file.argtypes = [MifareTag, uint8_t, uint8_t, uint16_t, uint32_t, uint32_t]
mifare_desfire_create_cyclic_record_file_iso = _libraries['libfreefare.so'].mifare_desfire_create_cyclic_record_file_iso
mifare_desfire_create_cyclic_record_file_iso.restype = c_int
mifare_desfire_create_cyclic_record_file_iso.argtypes = [MifareTag, uint8_t, uint8_t, uint16_t, uint32_t, uint32_t, uint16_t]
mifare_desfire_delete_file = _libraries['libfreefare.so'].mifare_desfire_delete_file
mifare_desfire_delete_file.restype = c_int
mifare_desfire_delete_file.argtypes = [MifareTag, uint8_t]
off_t = __off_t
mifare_desfire_read_data = _libraries['libfreefare.so'].mifare_desfire_read_data
mifare_desfire_read_data.restype = ssize_t
mifare_desfire_read_data.argtypes = [MifareTag, uint8_t, off_t, size_t, c_void_p]
mifare_desfire_read_data_ex = _libraries['libfreefare.so'].mifare_desfire_read_data_ex
mifare_desfire_read_data_ex.restype = ssize_t
mifare_desfire_read_data_ex.argtypes = [MifareTag, uint8_t, off_t, size_t, c_void_p, c_int]
mifare_desfire_write_data = _libraries['libfreefare.so'].mifare_desfire_write_data
mifare_desfire_write_data.restype = ssize_t
mifare_desfire_write_data.argtypes = [MifareTag, uint8_t, off_t, size_t, c_void_p]
mifare_desfire_write_data_ex = _libraries['libfreefare.so'].mifare_desfire_write_data_ex
mifare_desfire_write_data_ex.restype = ssize_t
mifare_desfire_write_data_ex.argtypes = [MifareTag, uint8_t, off_t, size_t, c_void_p, c_int]
mifare_desfire_get_value = _libraries['libfreefare.so'].mifare_desfire_get_value
mifare_desfire_get_value.restype = c_int
mifare_desfire_get_value.argtypes = [MifareTag, uint8_t, POINTER(int32_t)]
mifare_desfire_get_value_ex = _libraries['libfreefare.so'].mifare_desfire_get_value_ex
mifare_desfire_get_value_ex.restype = c_int
mifare_desfire_get_value_ex.argtypes = [MifareTag, uint8_t, POINTER(int32_t), c_int]
mifare_desfire_credit = _libraries['libfreefare.so'].mifare_desfire_credit
mifare_desfire_credit.restype = c_int
mifare_desfire_credit.argtypes = [MifareTag, uint8_t, int32_t]
mifare_desfire_credit_ex = _libraries['libfreefare.so'].mifare_desfire_credit_ex
mifare_desfire_credit_ex.restype = c_int
mifare_desfire_credit_ex.argtypes = [MifareTag, uint8_t, int32_t, c_int]
mifare_desfire_debit = _libraries['libfreefare.so'].mifare_desfire_debit
mifare_desfire_debit.restype = c_int
mifare_desfire_debit.argtypes = [MifareTag, uint8_t, int32_t]
mifare_desfire_debit_ex = _libraries['libfreefare.so'].mifare_desfire_debit_ex
mifare_desfire_debit_ex.restype = c_int
mifare_desfire_debit_ex.argtypes = [MifareTag, uint8_t, int32_t, c_int]
mifare_desfire_limited_credit = _libraries['libfreefare.so'].mifare_desfire_limited_credit
mifare_desfire_limited_credit.restype = c_int
mifare_desfire_limited_credit.argtypes = [MifareTag, uint8_t, int32_t]
mifare_desfire_limited_credit_ex = _libraries['libfreefare.so'].mifare_desfire_limited_credit_ex
mifare_desfire_limited_credit_ex.restype = c_int
mifare_desfire_limited_credit_ex.argtypes = [MifareTag, uint8_t, int32_t, c_int]
mifare_desfire_write_record = _libraries['libfreefare.so'].mifare_desfire_write_record
mifare_desfire_write_record.restype = ssize_t
mifare_desfire_write_record.argtypes = [MifareTag, uint8_t, off_t, size_t, c_void_p]
mifare_desfire_write_record_ex = _libraries['libfreefare.so'].mifare_desfire_write_record_ex
mifare_desfire_write_record_ex.restype = ssize_t
mifare_desfire_write_record_ex.argtypes = [MifareTag, uint8_t, off_t, size_t, c_void_p, c_int]
mifare_desfire_read_records = _libraries['libfreefare.so'].mifare_desfire_read_records
mifare_desfire_read_records.restype = ssize_t
mifare_desfire_read_records.argtypes = [MifareTag, uint8_t, off_t, size_t, c_void_p]
mifare_desfire_read_records_ex = _libraries['libfreefare.so'].mifare_desfire_read_records_ex
mifare_desfire_read_records_ex.restype = ssize_t
mifare_desfire_read_records_ex.argtypes = [MifareTag, uint8_t, off_t, size_t, c_void_p, c_int]
mifare_desfire_clear_record_file = _libraries['libfreefare.so'].mifare_desfire_clear_record_file
mifare_desfire_clear_record_file.restype = c_int
mifare_desfire_clear_record_file.argtypes = [MifareTag, uint8_t]
mifare_desfire_commit_transaction = _libraries['libfreefare.so'].mifare_desfire_commit_transaction
mifare_desfire_commit_transaction.restype = c_int
mifare_desfire_commit_transaction.argtypes = [MifareTag]
mifare_desfire_abort_transaction = _libraries['libfreefare.so'].mifare_desfire_abort_transaction
mifare_desfire_abort_transaction.restype = c_int
mifare_desfire_abort_transaction.argtypes = [MifareTag]
mifare_desfire_des_key_new = _libraries['libfreefare.so'].mifare_desfire_des_key_new
mifare_desfire_des_key_new.restype = MifareDESFireKey
mifare_desfire_des_key_new.argtypes = [POINTER(uint8_t)]
mifare_desfire_3des_key_new = _libraries['libfreefare.so'].mifare_desfire_3des_key_new
mifare_desfire_3des_key_new.restype = MifareDESFireKey
mifare_desfire_3des_key_new.argtypes = [POINTER(uint8_t)]
mifare_desfire_des_key_new_with_version = _libraries['libfreefare.so'].mifare_desfire_des_key_new_with_version
mifare_desfire_des_key_new_with_version.restype = MifareDESFireKey
mifare_desfire_des_key_new_with_version.argtypes = [POINTER(uint8_t)]
mifare_desfire_3des_key_new_with_version = _libraries['libfreefare.so'].mifare_desfire_3des_key_new_with_version
mifare_desfire_3des_key_new_with_version.restype = MifareDESFireKey
mifare_desfire_3des_key_new_with_version.argtypes = [POINTER(uint8_t)]
mifare_desfire_3k3des_key_new = _libraries['libfreefare.so'].mifare_desfire_3k3des_key_new
mifare_desfire_3k3des_key_new.restype = MifareDESFireKey
mifare_desfire_3k3des_key_new.argtypes = [POINTER(uint8_t)]
mifare_desfire_3k3des_key_new_with_version = _libraries['libfreefare.so'].mifare_desfire_3k3des_key_new_with_version
mifare_desfire_3k3des_key_new_with_version.restype = MifareDESFireKey
mifare_desfire_3k3des_key_new_with_version.argtypes = [POINTER(uint8_t)]
mifare_desfire_aes_key_new = _libraries['libfreefare.so'].mifare_desfire_aes_key_new
mifare_desfire_aes_key_new.restype = MifareDESFireKey
mifare_desfire_aes_key_new.argtypes = [POINTER(uint8_t)]
mifare_desfire_aes_key_new_with_version = _libraries['libfreefare.so'].mifare_desfire_aes_key_new_with_version
mifare_desfire_aes_key_new_with_version.restype = MifareDESFireKey
mifare_desfire_aes_key_new_with_version.argtypes = [POINTER(uint8_t), uint8_t]
mifare_desfire_key_get_version = _libraries['libfreefare.so'].mifare_desfire_key_get_version
mifare_desfire_key_get_version.restype = uint8_t
mifare_desfire_key_get_version.argtypes = [MifareDESFireKey]
mifare_desfire_key_set_version = _libraries['libfreefare.so'].mifare_desfire_key_set_version
mifare_desfire_key_set_version.restype = None
mifare_desfire_key_set_version.argtypes = [MifareDESFireKey, uint8_t]
mifare_desfire_key_free = _libraries['libfreefare.so'].mifare_desfire_key_free
mifare_desfire_key_free.restype = None
mifare_desfire_key_free.argtypes = [MifareDESFireKey]
tlv_encode = _libraries['libfreefare.so'].tlv_encode
tlv_encode.restype = POINTER(uint8_t)
tlv_encode.argtypes = [uint8_t, POINTER(uint8_t), uint16_t, POINTER(size_t)]
tlv_decode = _libraries['libfreefare.so'].tlv_decode
tlv_decode.restype = POINTER(uint8_t)
tlv_decode.argtypes = [POINTER(uint8_t), POINTER(uint8_t), POINTER(uint16_t)]
tlv_record_length = _libraries['libfreefare.so'].tlv_record_length
tlv_record_length.restype = size_t
tlv_record_length.argtypes = [POINTER(uint8_t), POINTER(size_t), POINTER(size_t)]
tlv_append = _libraries['libfreefare.so'].tlv_append
tlv_append.restype = POINTER(uint8_t)
tlv_append.argtypes = [POINTER(uint8_t), POINTER(uint8_t)]
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
nfc_context._fields_ = [
]
nfc_device._fields_ = [
]
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
class openssl_item_st(Structure):
    pass
openssl_item_st._fields_ = [
    ('code', c_int),
    ('value', c_void_p),
    ('value_size', size_t),
    ('value_length', POINTER(size_t)),
]
OPENSSL_ITEM = openssl_item_st
class CRYPTO_dynlock_value(Structure):
    pass
CRYPTO_dynlock_value._fields_ = [
]
class CRYPTO_dynlock(Structure):
    pass
CRYPTO_dynlock._fields_ = [
    ('references', c_int),
    ('data', POINTER(CRYPTO_dynlock_value)),
]
class bio_st(Structure):
    pass
bio_st._fields_ = [
]
BIO_dummy = bio_st
class crypto_ex_data_st(Structure):
    pass
class stack_st_void(Structure):
    pass
crypto_ex_data_st._fields_ = [
    ('sk', POINTER(stack_st_void)),
    ('dummy', c_int),
]
class stack_st(Structure):
    pass
stack_st._fields_ = [
    ('num', c_int),
    ('data', POINTER(STRING)),
    ('sorted', c_int),
    ('num_alloc', c_int),
    ('comp', CFUNCTYPE(c_int, c_void_p, c_void_p)),
]
_STACK = stack_st
stack_st_void._fields_ = [
    ('stack', _STACK),
]
class crypto_ex_data_func_st(Structure):
    pass
CRYPTO_EX_DATA = crypto_ex_data_st
CRYPTO_EX_new = CFUNCTYPE(c_int, c_void_p, c_void_p, POINTER(CRYPTO_EX_DATA), c_int, c_long, c_void_p)
CRYPTO_EX_free = CFUNCTYPE(None, c_void_p, c_void_p, POINTER(CRYPTO_EX_DATA), c_int, c_long, c_void_p)
CRYPTO_EX_dup = CFUNCTYPE(c_int, POINTER(CRYPTO_EX_DATA), POINTER(CRYPTO_EX_DATA), c_void_p, c_int, c_long, c_void_p)
crypto_ex_data_func_st._fields_ = [
    ('argl', c_long),
    ('argp', c_void_p),
    ('new_func', POINTER(CRYPTO_EX_new)),
    ('free_func', POINTER(CRYPTO_EX_free)),
    ('dup_func', POINTER(CRYPTO_EX_dup)),
]
CRYPTO_EX_DATA_FUNCS = crypto_ex_data_func_st
class stack_st_CRYPTO_EX_DATA_FUNCS(Structure):
    pass
stack_st_CRYPTO_EX_DATA_FUNCS._fields_ = [
    ('stack', _STACK),
]
CRYPTO_mem_ctrl = _libraries['libfreefare.so'].CRYPTO_mem_ctrl
CRYPTO_mem_ctrl.restype = c_int
CRYPTO_mem_ctrl.argtypes = [c_int]
CRYPTO_is_mem_check_on = _libraries['libfreefare.so'].CRYPTO_is_mem_check_on
CRYPTO_is_mem_check_on.restype = c_int
CRYPTO_is_mem_check_on.argtypes = []
SSLeay_version = _libraries['libfreefare.so'].SSLeay_version
SSLeay_version.restype = STRING
SSLeay_version.argtypes = [c_int]
SSLeay = _libraries['libfreefare.so'].SSLeay
SSLeay.restype = c_ulong
SSLeay.argtypes = []
OPENSSL_issetugid = _libraries['libfreefare.so'].OPENSSL_issetugid
OPENSSL_issetugid.restype = c_int
OPENSSL_issetugid.argtypes = []
class st_CRYPTO_EX_DATA_IMPL(Structure):
    pass
CRYPTO_EX_DATA_IMPL = st_CRYPTO_EX_DATA_IMPL
st_CRYPTO_EX_DATA_IMPL._fields_ = [
]
CRYPTO_get_ex_data_implementation = _libraries['libfreefare.so'].CRYPTO_get_ex_data_implementation
CRYPTO_get_ex_data_implementation.restype = POINTER(CRYPTO_EX_DATA_IMPL)
CRYPTO_get_ex_data_implementation.argtypes = []
CRYPTO_set_ex_data_implementation = _libraries['libfreefare.so'].CRYPTO_set_ex_data_implementation
CRYPTO_set_ex_data_implementation.restype = c_int
CRYPTO_set_ex_data_implementation.argtypes = [POINTER(CRYPTO_EX_DATA_IMPL)]
CRYPTO_ex_data_new_class = _libraries['libfreefare.so'].CRYPTO_ex_data_new_class
CRYPTO_ex_data_new_class.restype = c_int
CRYPTO_ex_data_new_class.argtypes = []
CRYPTO_get_ex_new_index = _libraries['libfreefare.so'].CRYPTO_get_ex_new_index
CRYPTO_get_ex_new_index.restype = c_int
CRYPTO_get_ex_new_index.argtypes = [c_int, c_long, c_void_p, POINTER(CRYPTO_EX_new), POINTER(CRYPTO_EX_dup), POINTER(CRYPTO_EX_free)]
CRYPTO_new_ex_data = _libraries['libfreefare.so'].CRYPTO_new_ex_data
CRYPTO_new_ex_data.restype = c_int
CRYPTO_new_ex_data.argtypes = [c_int, c_void_p, POINTER(CRYPTO_EX_DATA)]
CRYPTO_dup_ex_data = _libraries['libfreefare.so'].CRYPTO_dup_ex_data
CRYPTO_dup_ex_data.restype = c_int
CRYPTO_dup_ex_data.argtypes = [c_int, POINTER(CRYPTO_EX_DATA), POINTER(CRYPTO_EX_DATA)]
CRYPTO_free_ex_data = _libraries['libfreefare.so'].CRYPTO_free_ex_data
CRYPTO_free_ex_data.restype = None
CRYPTO_free_ex_data.argtypes = [c_int, c_void_p, POINTER(CRYPTO_EX_DATA)]
CRYPTO_set_ex_data = _libraries['libfreefare.so'].CRYPTO_set_ex_data
CRYPTO_set_ex_data.restype = c_int
CRYPTO_set_ex_data.argtypes = [POINTER(CRYPTO_EX_DATA), c_int, c_void_p]
CRYPTO_get_ex_data = _libraries['libfreefare.so'].CRYPTO_get_ex_data
CRYPTO_get_ex_data.restype = c_void_p
CRYPTO_get_ex_data.argtypes = [POINTER(CRYPTO_EX_DATA), c_int]
CRYPTO_cleanup_all_ex_data = _libraries['libfreefare.so'].CRYPTO_cleanup_all_ex_data
CRYPTO_cleanup_all_ex_data.restype = None
CRYPTO_cleanup_all_ex_data.argtypes = []
CRYPTO_get_new_lockid = _libraries['libfreefare.so'].CRYPTO_get_new_lockid
CRYPTO_get_new_lockid.restype = c_int
CRYPTO_get_new_lockid.argtypes = [STRING]
CRYPTO_num_locks = _libraries['libfreefare.so'].CRYPTO_num_locks
CRYPTO_num_locks.restype = c_int
CRYPTO_num_locks.argtypes = []
CRYPTO_lock = _libraries['libfreefare.so'].CRYPTO_lock
CRYPTO_lock.restype = None
CRYPTO_lock.argtypes = [c_int, c_int, STRING, c_int]
CRYPTO_set_locking_callback = _libraries['libfreefare.so'].CRYPTO_set_locking_callback
CRYPTO_set_locking_callback.restype = None
CRYPTO_set_locking_callback.argtypes = [CFUNCTYPE(None, c_int, c_int, STRING, c_int)]
CRYPTO_get_locking_callback = _libraries['libfreefare.so'].CRYPTO_get_locking_callback
CRYPTO_get_locking_callback.restype = CFUNCTYPE(None, c_int, c_int, STRING, c_int)
CRYPTO_get_locking_callback.argtypes = []
CRYPTO_set_add_lock_callback = _libraries['libfreefare.so'].CRYPTO_set_add_lock_callback
CRYPTO_set_add_lock_callback.restype = None
CRYPTO_set_add_lock_callback.argtypes = [CFUNCTYPE(c_int, POINTER(c_int), c_int, c_int, STRING, c_int)]
CRYPTO_get_add_lock_callback = _libraries['libfreefare.so'].CRYPTO_get_add_lock_callback
CRYPTO_get_add_lock_callback.restype = CFUNCTYPE(c_int, POINTER(c_int), c_int, c_int, STRING, c_int)
CRYPTO_get_add_lock_callback.argtypes = []
class crypto_threadid_st(Structure):
    pass
crypto_threadid_st._fields_ = [
    ('ptr', c_void_p),
    ('val', c_ulong),
]
CRYPTO_THREADID = crypto_threadid_st
CRYPTO_THREADID_set_numeric = _libraries['libfreefare.so'].CRYPTO_THREADID_set_numeric
CRYPTO_THREADID_set_numeric.restype = None
CRYPTO_THREADID_set_numeric.argtypes = [POINTER(CRYPTO_THREADID), c_ulong]
CRYPTO_THREADID_set_pointer = _libraries['libfreefare.so'].CRYPTO_THREADID_set_pointer
CRYPTO_THREADID_set_pointer.restype = None
CRYPTO_THREADID_set_pointer.argtypes = [POINTER(CRYPTO_THREADID), c_void_p]
CRYPTO_THREADID_set_callback = _libraries['libfreefare.so'].CRYPTO_THREADID_set_callback
CRYPTO_THREADID_set_callback.restype = c_int
CRYPTO_THREADID_set_callback.argtypes = [CFUNCTYPE(None, POINTER(CRYPTO_THREADID))]
CRYPTO_THREADID_get_callback = _libraries['libfreefare.so'].CRYPTO_THREADID_get_callback
CRYPTO_THREADID_get_callback.restype = CFUNCTYPE(None, POINTER(CRYPTO_THREADID))
CRYPTO_THREADID_get_callback.argtypes = []
CRYPTO_THREADID_current = _libraries['libfreefare.so'].CRYPTO_THREADID_current
CRYPTO_THREADID_current.restype = None
CRYPTO_THREADID_current.argtypes = [POINTER(CRYPTO_THREADID)]
CRYPTO_THREADID_cmp = _libraries['libfreefare.so'].CRYPTO_THREADID_cmp
CRYPTO_THREADID_cmp.restype = c_int
CRYPTO_THREADID_cmp.argtypes = [POINTER(CRYPTO_THREADID), POINTER(CRYPTO_THREADID)]
CRYPTO_THREADID_cpy = _libraries['libfreefare.so'].CRYPTO_THREADID_cpy
CRYPTO_THREADID_cpy.restype = None
CRYPTO_THREADID_cpy.argtypes = [POINTER(CRYPTO_THREADID), POINTER(CRYPTO_THREADID)]
CRYPTO_THREADID_hash = _libraries['libfreefare.so'].CRYPTO_THREADID_hash
CRYPTO_THREADID_hash.restype = c_ulong
CRYPTO_THREADID_hash.argtypes = [POINTER(CRYPTO_THREADID)]
CRYPTO_set_id_callback = _libraries['libfreefare.so'].CRYPTO_set_id_callback
CRYPTO_set_id_callback.restype = None
CRYPTO_set_id_callback.argtypes = [CFUNCTYPE(c_ulong)]
CRYPTO_get_id_callback = _libraries['libfreefare.so'].CRYPTO_get_id_callback
CRYPTO_get_id_callback.restype = CFUNCTYPE(c_ulong)
CRYPTO_get_id_callback.argtypes = []
CRYPTO_thread_id = _libraries['libfreefare.so'].CRYPTO_thread_id
CRYPTO_thread_id.restype = c_ulong
CRYPTO_thread_id.argtypes = []
CRYPTO_get_lock_name = _libraries['libfreefare.so'].CRYPTO_get_lock_name
CRYPTO_get_lock_name.restype = STRING
CRYPTO_get_lock_name.argtypes = [c_int]
CRYPTO_add_lock = _libraries['libfreefare.so'].CRYPTO_add_lock
CRYPTO_add_lock.restype = c_int
CRYPTO_add_lock.argtypes = [POINTER(c_int), c_int, c_int, STRING, c_int]
CRYPTO_get_new_dynlockid = _libraries['libfreefare.so'].CRYPTO_get_new_dynlockid
CRYPTO_get_new_dynlockid.restype = c_int
CRYPTO_get_new_dynlockid.argtypes = []
CRYPTO_destroy_dynlockid = _libraries['libfreefare.so'].CRYPTO_destroy_dynlockid
CRYPTO_destroy_dynlockid.restype = None
CRYPTO_destroy_dynlockid.argtypes = [c_int]
CRYPTO_get_dynlock_value = _libraries['libfreefare.so'].CRYPTO_get_dynlock_value
CRYPTO_get_dynlock_value.restype = POINTER(CRYPTO_dynlock_value)
CRYPTO_get_dynlock_value.argtypes = [c_int]
CRYPTO_set_dynlock_create_callback = _libraries['libfreefare.so'].CRYPTO_set_dynlock_create_callback
CRYPTO_set_dynlock_create_callback.restype = None
CRYPTO_set_dynlock_create_callback.argtypes = [CFUNCTYPE(POINTER(CRYPTO_dynlock_value), STRING, c_int)]
CRYPTO_set_dynlock_lock_callback = _libraries['libfreefare.so'].CRYPTO_set_dynlock_lock_callback
CRYPTO_set_dynlock_lock_callback.restype = None
CRYPTO_set_dynlock_lock_callback.argtypes = [CFUNCTYPE(None, c_int, POINTER(CRYPTO_dynlock_value), STRING, c_int)]
CRYPTO_set_dynlock_destroy_callback = _libraries['libfreefare.so'].CRYPTO_set_dynlock_destroy_callback
CRYPTO_set_dynlock_destroy_callback.restype = None
CRYPTO_set_dynlock_destroy_callback.argtypes = [CFUNCTYPE(None, POINTER(CRYPTO_dynlock_value), STRING, c_int)]
CRYPTO_get_dynlock_create_callback = _libraries['libfreefare.so'].CRYPTO_get_dynlock_create_callback
CRYPTO_get_dynlock_create_callback.restype = CFUNCTYPE(POINTER(CRYPTO_dynlock_value), STRING, c_int)
CRYPTO_get_dynlock_create_callback.argtypes = []
CRYPTO_get_dynlock_lock_callback = _libraries['libfreefare.so'].CRYPTO_get_dynlock_lock_callback
CRYPTO_get_dynlock_lock_callback.restype = CFUNCTYPE(None, c_int, POINTER(CRYPTO_dynlock_value), STRING, c_int)
CRYPTO_get_dynlock_lock_callback.argtypes = []
CRYPTO_get_dynlock_destroy_callback = _libraries['libfreefare.so'].CRYPTO_get_dynlock_destroy_callback
CRYPTO_get_dynlock_destroy_callback.restype = CFUNCTYPE(None, POINTER(CRYPTO_dynlock_value), STRING, c_int)
CRYPTO_get_dynlock_destroy_callback.argtypes = []
CRYPTO_set_mem_functions = _libraries['libfreefare.so'].CRYPTO_set_mem_functions
CRYPTO_set_mem_functions.restype = c_int
CRYPTO_set_mem_functions.argtypes = [CFUNCTYPE(c_void_p, size_t), CFUNCTYPE(c_void_p, c_void_p, size_t), CFUNCTYPE(None, c_void_p)]
CRYPTO_set_locked_mem_functions = _libraries['libfreefare.so'].CRYPTO_set_locked_mem_functions
CRYPTO_set_locked_mem_functions.restype = c_int
CRYPTO_set_locked_mem_functions.argtypes = [CFUNCTYPE(c_void_p, size_t), CFUNCTYPE(None, c_void_p)]
CRYPTO_set_mem_ex_functions = _libraries['libfreefare.so'].CRYPTO_set_mem_ex_functions
CRYPTO_set_mem_ex_functions.restype = c_int
CRYPTO_set_mem_ex_functions.argtypes = [CFUNCTYPE(c_void_p, size_t, STRING, c_int), CFUNCTYPE(c_void_p, c_void_p, size_t, STRING, c_int), CFUNCTYPE(None, c_void_p)]
CRYPTO_set_locked_mem_ex_functions = _libraries['libfreefare.so'].CRYPTO_set_locked_mem_ex_functions
CRYPTO_set_locked_mem_ex_functions.restype = c_int
CRYPTO_set_locked_mem_ex_functions.argtypes = [CFUNCTYPE(c_void_p, size_t, STRING, c_int), CFUNCTYPE(None, c_void_p)]
CRYPTO_set_mem_debug_functions = _libraries['libfreefare.so'].CRYPTO_set_mem_debug_functions
CRYPTO_set_mem_debug_functions.restype = c_int
CRYPTO_set_mem_debug_functions.argtypes = [CFUNCTYPE(None, c_void_p, c_int, STRING, c_int, c_int), CFUNCTYPE(None, c_void_p, c_void_p, c_int, STRING, c_int, c_int), CFUNCTYPE(None, c_void_p, c_int), CFUNCTYPE(None, c_long), CFUNCTYPE(c_long)]
CRYPTO_get_mem_functions = _libraries['libfreefare.so'].CRYPTO_get_mem_functions
CRYPTO_get_mem_functions.restype = None
CRYPTO_get_mem_functions.argtypes = [CFUNCTYPE(c_void_p, size_t), CFUNCTYPE(c_void_p, c_void_p, size_t), CFUNCTYPE(None, c_void_p)]
CRYPTO_get_locked_mem_functions = _libraries['libfreefare.so'].CRYPTO_get_locked_mem_functions
CRYPTO_get_locked_mem_functions.restype = None
CRYPTO_get_locked_mem_functions.argtypes = [CFUNCTYPE(c_void_p, size_t), CFUNCTYPE(None, c_void_p)]
CRYPTO_get_mem_ex_functions = _libraries['libfreefare.so'].CRYPTO_get_mem_ex_functions
CRYPTO_get_mem_ex_functions.restype = None
CRYPTO_get_mem_ex_functions.argtypes = [CFUNCTYPE(c_void_p, size_t, STRING, c_int), CFUNCTYPE(c_void_p, c_void_p, size_t, STRING, c_int), CFUNCTYPE(None, c_void_p)]
CRYPTO_get_locked_mem_ex_functions = _libraries['libfreefare.so'].CRYPTO_get_locked_mem_ex_functions
CRYPTO_get_locked_mem_ex_functions.restype = None
CRYPTO_get_locked_mem_ex_functions.argtypes = [CFUNCTYPE(c_void_p, size_t, STRING, c_int), CFUNCTYPE(None, c_void_p)]
CRYPTO_get_mem_debug_functions = _libraries['libfreefare.so'].CRYPTO_get_mem_debug_functions
CRYPTO_get_mem_debug_functions.restype = None
CRYPTO_get_mem_debug_functions.argtypes = [CFUNCTYPE(None, c_void_p, c_int, STRING, c_int, c_int), CFUNCTYPE(None, c_void_p, c_void_p, c_int, STRING, c_int, c_int), CFUNCTYPE(None, c_void_p, c_int), CFUNCTYPE(None, c_long), CFUNCTYPE(c_long)]
CRYPTO_malloc_locked = _libraries['libfreefare.so'].CRYPTO_malloc_locked
CRYPTO_malloc_locked.restype = c_void_p
CRYPTO_malloc_locked.argtypes = [c_int, STRING, c_int]
CRYPTO_free_locked = _libraries['libfreefare.so'].CRYPTO_free_locked
CRYPTO_free_locked.restype = None
CRYPTO_free_locked.argtypes = [c_void_p]
CRYPTO_malloc = _libraries['libfreefare.so'].CRYPTO_malloc
CRYPTO_malloc.restype = c_void_p
CRYPTO_malloc.argtypes = [c_int, STRING, c_int]
CRYPTO_strdup = _libraries['libfreefare.so'].CRYPTO_strdup
CRYPTO_strdup.restype = STRING
CRYPTO_strdup.argtypes = [STRING, STRING, c_int]
CRYPTO_free = _libraries['libfreefare.so'].CRYPTO_free
CRYPTO_free.restype = None
CRYPTO_free.argtypes = [c_void_p]
CRYPTO_realloc = _libraries['libfreefare.so'].CRYPTO_realloc
CRYPTO_realloc.restype = c_void_p
CRYPTO_realloc.argtypes = [c_void_p, c_int, STRING, c_int]
CRYPTO_realloc_clean = _libraries['libfreefare.so'].CRYPTO_realloc_clean
CRYPTO_realloc_clean.restype = c_void_p
CRYPTO_realloc_clean.argtypes = [c_void_p, c_int, c_int, STRING, c_int]
CRYPTO_remalloc = _libraries['libfreefare.so'].CRYPTO_remalloc
CRYPTO_remalloc.restype = c_void_p
CRYPTO_remalloc.argtypes = [c_void_p, c_int, STRING, c_int]
OPENSSL_cleanse = _libraries['libfreefare.so'].OPENSSL_cleanse
OPENSSL_cleanse.restype = None
OPENSSL_cleanse.argtypes = [c_void_p, size_t]
CRYPTO_set_mem_debug_options = _libraries['libfreefare.so'].CRYPTO_set_mem_debug_options
CRYPTO_set_mem_debug_options.restype = None
CRYPTO_set_mem_debug_options.argtypes = [c_long]
CRYPTO_get_mem_debug_options = _libraries['libfreefare.so'].CRYPTO_get_mem_debug_options
CRYPTO_get_mem_debug_options.restype = c_long
CRYPTO_get_mem_debug_options.argtypes = []
CRYPTO_push_info_ = _libraries['libfreefare.so'].CRYPTO_push_info_
CRYPTO_push_info_.restype = c_int
CRYPTO_push_info_.argtypes = [STRING, STRING, c_int]
CRYPTO_pop_info = _libraries['libfreefare.so'].CRYPTO_pop_info
CRYPTO_pop_info.restype = c_int
CRYPTO_pop_info.argtypes = []
CRYPTO_remove_all_info = _libraries['libfreefare.so'].CRYPTO_remove_all_info
CRYPTO_remove_all_info.restype = c_int
CRYPTO_remove_all_info.argtypes = []
CRYPTO_dbg_malloc = _libraries['libfreefare.so'].CRYPTO_dbg_malloc
CRYPTO_dbg_malloc.restype = None
CRYPTO_dbg_malloc.argtypes = [c_void_p, c_int, STRING, c_int, c_int]
CRYPTO_dbg_realloc = _libraries['libfreefare.so'].CRYPTO_dbg_realloc
CRYPTO_dbg_realloc.restype = None
CRYPTO_dbg_realloc.argtypes = [c_void_p, c_void_p, c_int, STRING, c_int, c_int]
CRYPTO_dbg_free = _libraries['libfreefare.so'].CRYPTO_dbg_free
CRYPTO_dbg_free.restype = None
CRYPTO_dbg_free.argtypes = [c_void_p, c_int]
CRYPTO_dbg_set_options = _libraries['libfreefare.so'].CRYPTO_dbg_set_options
CRYPTO_dbg_set_options.restype = None
CRYPTO_dbg_set_options.argtypes = [c_long]
CRYPTO_dbg_get_options = _libraries['libfreefare.so'].CRYPTO_dbg_get_options
CRYPTO_dbg_get_options.restype = c_long
CRYPTO_dbg_get_options.argtypes = []
FILE = _IO_FILE
CRYPTO_mem_leaks_fp = _libraries['libfreefare.so'].CRYPTO_mem_leaks_fp
CRYPTO_mem_leaks_fp.restype = None
CRYPTO_mem_leaks_fp.argtypes = [POINTER(FILE)]
CRYPTO_mem_leaks = _libraries['libfreefare.so'].CRYPTO_mem_leaks
CRYPTO_mem_leaks.restype = None
CRYPTO_mem_leaks.argtypes = [POINTER(bio_st)]
CRYPTO_MEM_LEAK_CB = CFUNCTYPE(c_void_p, c_ulong, STRING, c_int, c_int, c_void_p)
CRYPTO_mem_leaks_cb = _libraries['libfreefare.so'].CRYPTO_mem_leaks_cb
CRYPTO_mem_leaks_cb.restype = None
CRYPTO_mem_leaks_cb.argtypes = [POINTER(CRYPTO_MEM_LEAK_CB)]
OpenSSLDie = _libraries['libfreefare.so'].OpenSSLDie
OpenSSLDie.restype = None
OpenSSLDie.argtypes = [STRING, c_int, STRING]
OPENSSL_ia32cap_loc = _libraries['libfreefare.so'].OPENSSL_ia32cap_loc
OPENSSL_ia32cap_loc.restype = POINTER(c_ulong)
OPENSSL_ia32cap_loc.argtypes = []
OPENSSL_isservice = _libraries['libfreefare.so'].OPENSSL_isservice
OPENSSL_isservice.restype = c_int
OPENSSL_isservice.argtypes = []
FIPS_mode = _libraries['libfreefare.so'].FIPS_mode
FIPS_mode.restype = c_int
FIPS_mode.argtypes = []
FIPS_mode_set = _libraries['libfreefare.so'].FIPS_mode_set
FIPS_mode_set.restype = c_int
FIPS_mode_set.argtypes = [c_int]
OPENSSL_init = _libraries['libfreefare.so'].OPENSSL_init
OPENSSL_init.restype = None
OPENSSL_init.argtypes = []
CRYPTO_memcmp = _libraries['libfreefare.so'].CRYPTO_memcmp
CRYPTO_memcmp.restype = c_int
CRYPTO_memcmp.argtypes = [c_void_p, c_void_p, size_t]
ERR_load_CRYPTO_strings = _libraries['libfreefare.so'].ERR_load_CRYPTO_strings
ERR_load_CRYPTO_strings.restype = None
ERR_load_CRYPTO_strings.argtypes = []
DES_cblock = c_ubyte * 8
const_DES_cblock = c_ubyte * 8
class DES_ks(Structure):
    pass
class N6DES_ks3DOT_0E(Union):
    pass
N6DES_ks3DOT_0E._fields_ = [
    ('cblock', DES_cblock),
    ('deslong', c_uint * 2),
]
DES_ks._fields_ = [
    ('ks', N6DES_ks3DOT_0E * 16),
]
DES_key_schedule = DES_ks
_shadow_DES_check_key = (c_int).in_dll(_libraries['libfreefare.so'], '_shadow_DES_check_key')
_shadow_DES_rw_mode = (c_int).in_dll(_libraries['libfreefare.so'], '_shadow_DES_rw_mode')
DES_options = _libraries['libfreefare.so'].DES_options
DES_options.restype = STRING
DES_options.argtypes = []
DES_ecb3_encrypt = _libraries['libfreefare.so'].DES_ecb3_encrypt
DES_ecb3_encrypt.restype = None
DES_ecb3_encrypt.argtypes = [POINTER(const_DES_cblock), POINTER(DES_cblock), POINTER(DES_key_schedule), POINTER(DES_key_schedule), POINTER(DES_key_schedule), c_int]
DES_cbc_cksum = _libraries['libfreefare.so'].DES_cbc_cksum
DES_cbc_cksum.restype = c_uint
DES_cbc_cksum.argtypes = [POINTER(c_ubyte), POINTER(DES_cblock), c_long, POINTER(DES_key_schedule), POINTER(const_DES_cblock)]
DES_cbc_encrypt = _libraries['libfreefare.so'].DES_cbc_encrypt
DES_cbc_encrypt.restype = None
DES_cbc_encrypt.argtypes = [POINTER(c_ubyte), POINTER(c_ubyte), c_long, POINTER(DES_key_schedule), POINTER(DES_cblock), c_int]
DES_ncbc_encrypt = _libraries['libfreefare.so'].DES_ncbc_encrypt
DES_ncbc_encrypt.restype = None
DES_ncbc_encrypt.argtypes = [POINTER(c_ubyte), POINTER(c_ubyte), c_long, POINTER(DES_key_schedule), POINTER(DES_cblock), c_int]
DES_xcbc_encrypt = _libraries['libfreefare.so'].DES_xcbc_encrypt
DES_xcbc_encrypt.restype = None
DES_xcbc_encrypt.argtypes = [POINTER(c_ubyte), POINTER(c_ubyte), c_long, POINTER(DES_key_schedule), POINTER(DES_cblock), POINTER(const_DES_cblock), POINTER(const_DES_cblock), c_int]
DES_cfb_encrypt = _libraries['libfreefare.so'].DES_cfb_encrypt
DES_cfb_encrypt.restype = None
DES_cfb_encrypt.argtypes = [POINTER(c_ubyte), POINTER(c_ubyte), c_int, c_long, POINTER(DES_key_schedule), POINTER(DES_cblock), c_int]
DES_ecb_encrypt = _libraries['libfreefare.so'].DES_ecb_encrypt
DES_ecb_encrypt.restype = None
DES_ecb_encrypt.argtypes = [POINTER(const_DES_cblock), POINTER(DES_cblock), POINTER(DES_key_schedule), c_int]
DES_encrypt1 = _libraries['libfreefare.so'].DES_encrypt1
DES_encrypt1.restype = None
DES_encrypt1.argtypes = [POINTER(c_uint), POINTER(DES_key_schedule), c_int]
DES_encrypt2 = _libraries['libfreefare.so'].DES_encrypt2
DES_encrypt2.restype = None
DES_encrypt2.argtypes = [POINTER(c_uint), POINTER(DES_key_schedule), c_int]
DES_encrypt3 = _libraries['libfreefare.so'].DES_encrypt3
DES_encrypt3.restype = None
DES_encrypt3.argtypes = [POINTER(c_uint), POINTER(DES_key_schedule), POINTER(DES_key_schedule), POINTER(DES_key_schedule)]
DES_decrypt3 = _libraries['libfreefare.so'].DES_decrypt3
DES_decrypt3.restype = None
DES_decrypt3.argtypes = [POINTER(c_uint), POINTER(DES_key_schedule), POINTER(DES_key_schedule), POINTER(DES_key_schedule)]
DES_ede3_cbc_encrypt = _libraries['libfreefare.so'].DES_ede3_cbc_encrypt
DES_ede3_cbc_encrypt.restype = None
DES_ede3_cbc_encrypt.argtypes = [POINTER(c_ubyte), POINTER(c_ubyte), c_long, POINTER(DES_key_schedule), POINTER(DES_key_schedule), POINTER(DES_key_schedule), POINTER(DES_cblock), c_int]
DES_ede3_cbcm_encrypt = _libraries['libfreefare.so'].DES_ede3_cbcm_encrypt
DES_ede3_cbcm_encrypt.restype = None
DES_ede3_cbcm_encrypt.argtypes = [POINTER(c_ubyte), POINTER(c_ubyte), c_long, POINTER(DES_key_schedule), POINTER(DES_key_schedule), POINTER(DES_key_schedule), POINTER(DES_cblock), POINTER(DES_cblock), c_int]
DES_ede3_cfb64_encrypt = _libraries['libfreefare.so'].DES_ede3_cfb64_encrypt
DES_ede3_cfb64_encrypt.restype = None
DES_ede3_cfb64_encrypt.argtypes = [POINTER(c_ubyte), POINTER(c_ubyte), c_long, POINTER(DES_key_schedule), POINTER(DES_key_schedule), POINTER(DES_key_schedule), POINTER(DES_cblock), POINTER(c_int), c_int]
DES_ede3_cfb_encrypt = _libraries['libfreefare.so'].DES_ede3_cfb_encrypt
DES_ede3_cfb_encrypt.restype = None
DES_ede3_cfb_encrypt.argtypes = [POINTER(c_ubyte), POINTER(c_ubyte), c_int, c_long, POINTER(DES_key_schedule), POINTER(DES_key_schedule), POINTER(DES_key_schedule), POINTER(DES_cblock), c_int]
DES_ede3_ofb64_encrypt = _libraries['libfreefare.so'].DES_ede3_ofb64_encrypt
DES_ede3_ofb64_encrypt.restype = None
DES_ede3_ofb64_encrypt.argtypes = [POINTER(c_ubyte), POINTER(c_ubyte), c_long, POINTER(DES_key_schedule), POINTER(DES_key_schedule), POINTER(DES_key_schedule), POINTER(DES_cblock), POINTER(c_int)]
DES_enc_read = _libraries['libfreefare.so'].DES_enc_read
DES_enc_read.restype = c_int
DES_enc_read.argtypes = [c_int, c_void_p, c_int, POINTER(DES_key_schedule), POINTER(DES_cblock)]
DES_enc_write = _libraries['libfreefare.so'].DES_enc_write
DES_enc_write.restype = c_int
DES_enc_write.argtypes = [c_int, c_void_p, c_int, POINTER(DES_key_schedule), POINTER(DES_cblock)]
DES_fcrypt = _libraries['libfreefare.so'].DES_fcrypt
DES_fcrypt.restype = STRING
DES_fcrypt.argtypes = [STRING, STRING, STRING]
DES_crypt = _libraries['libfreefare.so'].DES_crypt
DES_crypt.restype = STRING
DES_crypt.argtypes = [STRING, STRING]
DES_ofb_encrypt = _libraries['libfreefare.so'].DES_ofb_encrypt
DES_ofb_encrypt.restype = None
DES_ofb_encrypt.argtypes = [POINTER(c_ubyte), POINTER(c_ubyte), c_int, c_long, POINTER(DES_key_schedule), POINTER(DES_cblock)]
DES_pcbc_encrypt = _libraries['libfreefare.so'].DES_pcbc_encrypt
DES_pcbc_encrypt.restype = None
DES_pcbc_encrypt.argtypes = [POINTER(c_ubyte), POINTER(c_ubyte), c_long, POINTER(DES_key_schedule), POINTER(DES_cblock), c_int]
DES_quad_cksum = _libraries['libfreefare.so'].DES_quad_cksum
DES_quad_cksum.restype = c_uint
DES_quad_cksum.argtypes = [POINTER(c_ubyte), POINTER(DES_cblock), c_long, c_int, POINTER(DES_cblock)]
DES_random_key = _libraries['libfreefare.so'].DES_random_key
DES_random_key.restype = c_int
DES_random_key.argtypes = [POINTER(DES_cblock)]
DES_set_odd_parity = _libraries['libfreefare.so'].DES_set_odd_parity
DES_set_odd_parity.restype = None
DES_set_odd_parity.argtypes = [POINTER(DES_cblock)]
DES_check_key_parity = _libraries['libfreefare.so'].DES_check_key_parity
DES_check_key_parity.restype = c_int
DES_check_key_parity.argtypes = [POINTER(const_DES_cblock)]
DES_is_weak_key = _libraries['libfreefare.so'].DES_is_weak_key
DES_is_weak_key.restype = c_int
DES_is_weak_key.argtypes = [POINTER(const_DES_cblock)]
DES_set_key = _libraries['libfreefare.so'].DES_set_key
DES_set_key.restype = c_int
DES_set_key.argtypes = [POINTER(const_DES_cblock), POINTER(DES_key_schedule)]
DES_key_sched = _libraries['libfreefare.so'].DES_key_sched
DES_key_sched.restype = c_int
DES_key_sched.argtypes = [POINTER(const_DES_cblock), POINTER(DES_key_schedule)]
DES_set_key_checked = _libraries['libfreefare.so'].DES_set_key_checked
DES_set_key_checked.restype = c_int
DES_set_key_checked.argtypes = [POINTER(const_DES_cblock), POINTER(DES_key_schedule)]
DES_set_key_unchecked = _libraries['libfreefare.so'].DES_set_key_unchecked
DES_set_key_unchecked.restype = None
DES_set_key_unchecked.argtypes = [POINTER(const_DES_cblock), POINTER(DES_key_schedule)]
DES_string_to_key = _libraries['libfreefare.so'].DES_string_to_key
DES_string_to_key.restype = None
DES_string_to_key.argtypes = [STRING, POINTER(DES_cblock)]
DES_string_to_2keys = _libraries['libfreefare.so'].DES_string_to_2keys
DES_string_to_2keys.restype = None
DES_string_to_2keys.argtypes = [STRING, POINTER(DES_cblock), POINTER(DES_cblock)]
DES_cfb64_encrypt = _libraries['libfreefare.so'].DES_cfb64_encrypt
DES_cfb64_encrypt.restype = None
DES_cfb64_encrypt.argtypes = [POINTER(c_ubyte), POINTER(c_ubyte), c_long, POINTER(DES_key_schedule), POINTER(DES_cblock), POINTER(c_int), c_int]
DES_ofb64_encrypt = _libraries['libfreefare.so'].DES_ofb64_encrypt
DES_ofb64_encrypt.restype = None
DES_ofb64_encrypt.argtypes = [POINTER(c_ubyte), POINTER(c_ubyte), c_long, POINTER(DES_key_schedule), POINTER(DES_cblock), POINTER(c_int)]
DES_read_password = _libraries['libfreefare.so'].DES_read_password
DES_read_password.restype = c_int
DES_read_password.argtypes = [POINTER(DES_cblock), STRING, c_int]
DES_read_2passwords = _libraries['libfreefare.so'].DES_read_2passwords
DES_read_2passwords.restype = c_int
DES_read_2passwords.argtypes = [POINTER(DES_cblock), POINTER(DES_cblock), STRING, c_int]
_ossl_old_des_cblock = c_ubyte * 8
class _ossl_old_des_ks_struct(Structure):
    pass
class N23_ossl_old_des_ks_struct3DOT_1E(Union):
    pass
N23_ossl_old_des_ks_struct3DOT_1E._fields_ = [
    ('_', _ossl_old_des_cblock),
    ('pad', c_uint * 2),
]
_ossl_old_des_ks_struct._fields_ = [
    ('ks', N23_ossl_old_des_ks_struct3DOT_1E),
]
_ossl_old_des_key_schedule = _ossl_old_des_ks_struct * 16
_ossl_old_des_options = _libraries['libfreefare.so']._ossl_old_des_options
_ossl_old_des_options.restype = STRING
_ossl_old_des_options.argtypes = []
_ossl_old_des_ecb3_encrypt = _libraries['libfreefare.so']._ossl_old_des_ecb3_encrypt
_ossl_old_des_ecb3_encrypt.restype = None
_ossl_old_des_ecb3_encrypt.argtypes = [POINTER(_ossl_old_des_cblock), POINTER(_ossl_old_des_cblock), POINTER(_ossl_old_des_ks_struct), POINTER(_ossl_old_des_ks_struct), POINTER(_ossl_old_des_ks_struct), c_int]
_ossl_old_des_cbc_cksum = _libraries['libfreefare.so']._ossl_old_des_cbc_cksum
_ossl_old_des_cbc_cksum.restype = c_uint
_ossl_old_des_cbc_cksum.argtypes = [POINTER(_ossl_old_des_cblock), POINTER(_ossl_old_des_cblock), c_long, POINTER(_ossl_old_des_ks_struct), POINTER(_ossl_old_des_cblock)]
_ossl_old_des_cbc_encrypt = _libraries['libfreefare.so']._ossl_old_des_cbc_encrypt
_ossl_old_des_cbc_encrypt.restype = None
_ossl_old_des_cbc_encrypt.argtypes = [POINTER(_ossl_old_des_cblock), POINTER(_ossl_old_des_cblock), c_long, POINTER(_ossl_old_des_ks_struct), POINTER(_ossl_old_des_cblock), c_int]
_ossl_old_des_ncbc_encrypt = _libraries['libfreefare.so']._ossl_old_des_ncbc_encrypt
_ossl_old_des_ncbc_encrypt.restype = None
_ossl_old_des_ncbc_encrypt.argtypes = [POINTER(_ossl_old_des_cblock), POINTER(_ossl_old_des_cblock), c_long, POINTER(_ossl_old_des_ks_struct), POINTER(_ossl_old_des_cblock), c_int]
_ossl_old_des_xcbc_encrypt = _libraries['libfreefare.so']._ossl_old_des_xcbc_encrypt
_ossl_old_des_xcbc_encrypt.restype = None
_ossl_old_des_xcbc_encrypt.argtypes = [POINTER(_ossl_old_des_cblock), POINTER(_ossl_old_des_cblock), c_long, POINTER(_ossl_old_des_ks_struct), POINTER(_ossl_old_des_cblock), POINTER(_ossl_old_des_cblock), POINTER(_ossl_old_des_cblock), c_int]
_ossl_old_des_cfb_encrypt = _libraries['libfreefare.so']._ossl_old_des_cfb_encrypt
_ossl_old_des_cfb_encrypt.restype = None
_ossl_old_des_cfb_encrypt.argtypes = [POINTER(c_ubyte), POINTER(c_ubyte), c_int, c_long, POINTER(_ossl_old_des_ks_struct), POINTER(_ossl_old_des_cblock), c_int]
_ossl_old_des_ecb_encrypt = _libraries['libfreefare.so']._ossl_old_des_ecb_encrypt
_ossl_old_des_ecb_encrypt.restype = None
_ossl_old_des_ecb_encrypt.argtypes = [POINTER(_ossl_old_des_cblock), POINTER(_ossl_old_des_cblock), POINTER(_ossl_old_des_ks_struct), c_int]
_ossl_old_des_encrypt = _libraries['libfreefare.so']._ossl_old_des_encrypt
_ossl_old_des_encrypt.restype = None
_ossl_old_des_encrypt.argtypes = [POINTER(c_uint), POINTER(_ossl_old_des_ks_struct), c_int]
_ossl_old_des_encrypt2 = _libraries['libfreefare.so']._ossl_old_des_encrypt2
_ossl_old_des_encrypt2.restype = None
_ossl_old_des_encrypt2.argtypes = [POINTER(c_uint), POINTER(_ossl_old_des_ks_struct), c_int]
_ossl_old_des_encrypt3 = _libraries['libfreefare.so']._ossl_old_des_encrypt3
_ossl_old_des_encrypt3.restype = None
_ossl_old_des_encrypt3.argtypes = [POINTER(c_uint), POINTER(_ossl_old_des_ks_struct), POINTER(_ossl_old_des_ks_struct), POINTER(_ossl_old_des_ks_struct)]
_ossl_old_des_decrypt3 = _libraries['libfreefare.so']._ossl_old_des_decrypt3
_ossl_old_des_decrypt3.restype = None
_ossl_old_des_decrypt3.argtypes = [POINTER(c_uint), POINTER(_ossl_old_des_ks_struct), POINTER(_ossl_old_des_ks_struct), POINTER(_ossl_old_des_ks_struct)]
_ossl_old_des_ede3_cbc_encrypt = _libraries['libfreefare.so']._ossl_old_des_ede3_cbc_encrypt
_ossl_old_des_ede3_cbc_encrypt.restype = None
_ossl_old_des_ede3_cbc_encrypt.argtypes = [POINTER(_ossl_old_des_cblock), POINTER(_ossl_old_des_cblock), c_long, POINTER(_ossl_old_des_ks_struct), POINTER(_ossl_old_des_ks_struct), POINTER(_ossl_old_des_ks_struct), POINTER(_ossl_old_des_cblock), c_int]
_ossl_old_des_ede3_cfb64_encrypt = _libraries['libfreefare.so']._ossl_old_des_ede3_cfb64_encrypt
_ossl_old_des_ede3_cfb64_encrypt.restype = None
_ossl_old_des_ede3_cfb64_encrypt.argtypes = [POINTER(c_ubyte), POINTER(c_ubyte), c_long, POINTER(_ossl_old_des_ks_struct), POINTER(_ossl_old_des_ks_struct), POINTER(_ossl_old_des_ks_struct), POINTER(_ossl_old_des_cblock), POINTER(c_int), c_int]
_ossl_old_des_ede3_ofb64_encrypt = _libraries['libfreefare.so']._ossl_old_des_ede3_ofb64_encrypt
_ossl_old_des_ede3_ofb64_encrypt.restype = None
_ossl_old_des_ede3_ofb64_encrypt.argtypes = [POINTER(c_ubyte), POINTER(c_ubyte), c_long, POINTER(_ossl_old_des_ks_struct), POINTER(_ossl_old_des_ks_struct), POINTER(_ossl_old_des_ks_struct), POINTER(_ossl_old_des_cblock), POINTER(c_int)]
_ossl_old_des_enc_read = _libraries['libfreefare.so']._ossl_old_des_enc_read
_ossl_old_des_enc_read.restype = c_int
_ossl_old_des_enc_read.argtypes = [c_int, STRING, c_int, POINTER(_ossl_old_des_ks_struct), POINTER(_ossl_old_des_cblock)]
_ossl_old_des_enc_write = _libraries['libfreefare.so']._ossl_old_des_enc_write
_ossl_old_des_enc_write.restype = c_int
_ossl_old_des_enc_write.argtypes = [c_int, STRING, c_int, POINTER(_ossl_old_des_ks_struct), POINTER(_ossl_old_des_cblock)]
_ossl_old_des_fcrypt = _libraries['libfreefare.so']._ossl_old_des_fcrypt
_ossl_old_des_fcrypt.restype = STRING
_ossl_old_des_fcrypt.argtypes = [STRING, STRING, STRING]
_ossl_old_des_crypt = _libraries['libfreefare.so']._ossl_old_des_crypt
_ossl_old_des_crypt.restype = STRING
_ossl_old_des_crypt.argtypes = [STRING, STRING]
_ossl_old_crypt = _libraries['libfreefare.so']._ossl_old_crypt
_ossl_old_crypt.restype = STRING
_ossl_old_crypt.argtypes = [STRING, STRING]
_ossl_old_des_ofb_encrypt = _libraries['libfreefare.so']._ossl_old_des_ofb_encrypt
_ossl_old_des_ofb_encrypt.restype = None
_ossl_old_des_ofb_encrypt.argtypes = [POINTER(c_ubyte), POINTER(c_ubyte), c_int, c_long, POINTER(_ossl_old_des_ks_struct), POINTER(_ossl_old_des_cblock)]
_ossl_old_des_pcbc_encrypt = _libraries['libfreefare.so']._ossl_old_des_pcbc_encrypt
_ossl_old_des_pcbc_encrypt.restype = None
_ossl_old_des_pcbc_encrypt.argtypes = [POINTER(_ossl_old_des_cblock), POINTER(_ossl_old_des_cblock), c_long, POINTER(_ossl_old_des_ks_struct), POINTER(_ossl_old_des_cblock), c_int]
_ossl_old_des_quad_cksum = _libraries['libfreefare.so']._ossl_old_des_quad_cksum
_ossl_old_des_quad_cksum.restype = c_uint
_ossl_old_des_quad_cksum.argtypes = [POINTER(_ossl_old_des_cblock), POINTER(_ossl_old_des_cblock), c_long, c_int, POINTER(_ossl_old_des_cblock)]
_ossl_old_des_random_seed = _libraries['libfreefare.so']._ossl_old_des_random_seed
_ossl_old_des_random_seed.restype = None
_ossl_old_des_random_seed.argtypes = [POINTER(c_ubyte)]
_ossl_old_des_random_key = _libraries['libfreefare.so']._ossl_old_des_random_key
_ossl_old_des_random_key.restype = None
_ossl_old_des_random_key.argtypes = [POINTER(c_ubyte)]
_ossl_old_des_read_password = _libraries['libfreefare.so']._ossl_old_des_read_password
_ossl_old_des_read_password.restype = c_int
_ossl_old_des_read_password.argtypes = [POINTER(_ossl_old_des_cblock), STRING, c_int]
_ossl_old_des_read_2passwords = _libraries['libfreefare.so']._ossl_old_des_read_2passwords
_ossl_old_des_read_2passwords.restype = c_int
_ossl_old_des_read_2passwords.argtypes = [POINTER(_ossl_old_des_cblock), POINTER(_ossl_old_des_cblock), STRING, c_int]
_ossl_old_des_set_odd_parity = _libraries['libfreefare.so']._ossl_old_des_set_odd_parity
_ossl_old_des_set_odd_parity.restype = None
_ossl_old_des_set_odd_parity.argtypes = [POINTER(_ossl_old_des_cblock)]
_ossl_old_des_is_weak_key = _libraries['libfreefare.so']._ossl_old_des_is_weak_key
_ossl_old_des_is_weak_key.restype = c_int
_ossl_old_des_is_weak_key.argtypes = [POINTER(_ossl_old_des_cblock)]
_ossl_old_des_set_key = _libraries['libfreefare.so']._ossl_old_des_set_key
_ossl_old_des_set_key.restype = c_int
_ossl_old_des_set_key.argtypes = [POINTER(_ossl_old_des_cblock), POINTER(_ossl_old_des_ks_struct)]
_ossl_old_des_key_sched = _libraries['libfreefare.so']._ossl_old_des_key_sched
_ossl_old_des_key_sched.restype = c_int
_ossl_old_des_key_sched.argtypes = [POINTER(_ossl_old_des_cblock), POINTER(_ossl_old_des_ks_struct)]
_ossl_old_des_string_to_key = _libraries['libfreefare.so']._ossl_old_des_string_to_key
_ossl_old_des_string_to_key.restype = None
_ossl_old_des_string_to_key.argtypes = [STRING, POINTER(_ossl_old_des_cblock)]
_ossl_old_des_string_to_2keys = _libraries['libfreefare.so']._ossl_old_des_string_to_2keys
_ossl_old_des_string_to_2keys.restype = None
_ossl_old_des_string_to_2keys.argtypes = [STRING, POINTER(_ossl_old_des_cblock), POINTER(_ossl_old_des_cblock)]
_ossl_old_des_cfb64_encrypt = _libraries['libfreefare.so']._ossl_old_des_cfb64_encrypt
_ossl_old_des_cfb64_encrypt.restype = None
_ossl_old_des_cfb64_encrypt.argtypes = [POINTER(c_ubyte), POINTER(c_ubyte), c_long, POINTER(_ossl_old_des_ks_struct), POINTER(_ossl_old_des_cblock), POINTER(c_int), c_int]
_ossl_old_des_ofb64_encrypt = _libraries['libfreefare.so']._ossl_old_des_ofb64_encrypt
_ossl_old_des_ofb64_encrypt.restype = None
_ossl_old_des_ofb64_encrypt.argtypes = [POINTER(c_ubyte), POINTER(c_ubyte), c_long, POINTER(_ossl_old_des_ks_struct), POINTER(_ossl_old_des_cblock), POINTER(c_int)]
_ossl_096_des_random_seed = _libraries['libfreefare.so']._ossl_096_des_random_seed
_ossl_096_des_random_seed.restype = None
_ossl_096_des_random_seed.argtypes = [POINTER(DES_cblock)]
class asn1_string_st(Structure):
    pass
ASN1_INTEGER = asn1_string_st
asn1_string_st._fields_ = [
]
ASN1_ENUMERATED = asn1_string_st
ASN1_BIT_STRING = asn1_string_st
ASN1_OCTET_STRING = asn1_string_st
ASN1_PRINTABLESTRING = asn1_string_st
ASN1_T61STRING = asn1_string_st
ASN1_IA5STRING = asn1_string_st
ASN1_GENERALSTRING = asn1_string_st
ASN1_UNIVERSALSTRING = asn1_string_st
ASN1_BMPSTRING = asn1_string_st
ASN1_UTCTIME = asn1_string_st
ASN1_TIME = asn1_string_st
ASN1_GENERALIZEDTIME = asn1_string_st
ASN1_VISIBLESTRING = asn1_string_st
ASN1_UTF8STRING = asn1_string_st
ASN1_STRING = asn1_string_st
ASN1_BOOLEAN = c_int
ASN1_NULL = c_int
class ASN1_ITEM_st(Structure):
    pass
ASN1_ITEM = ASN1_ITEM_st
ASN1_ITEM_st._fields_ = [
]
class asn1_pctx_st(Structure):
    pass
asn1_pctx_st._fields_ = [
]
ASN1_PCTX = asn1_pctx_st
class bignum_st(Structure):
    pass
bignum_st._fields_ = [
]
BIGNUM = bignum_st
class bignum_ctx(Structure):
    pass
bignum_ctx._fields_ = [
]
BN_CTX = bignum_ctx
class bn_blinding_st(Structure):
    pass
bn_blinding_st._fields_ = [
]
BN_BLINDING = bn_blinding_st
class bn_mont_ctx_st(Structure):
    pass
BN_MONT_CTX = bn_mont_ctx_st
bn_mont_ctx_st._fields_ = [
]
class bn_recp_ctx_st(Structure):
    pass
bn_recp_ctx_st._fields_ = [
]
BN_RECP_CTX = bn_recp_ctx_st
class bn_gencb_st(Structure):
    pass
bn_gencb_st._fields_ = [
]
BN_GENCB = bn_gencb_st
class buf_mem_st(Structure):
    pass
BUF_MEM = buf_mem_st
buf_mem_st._fields_ = [
]
class evp_cipher_st(Structure):
    pass
evp_cipher_st._fields_ = [
]
EVP_CIPHER = evp_cipher_st
class evp_cipher_ctx_st(Structure):
    pass
EVP_CIPHER_CTX = evp_cipher_ctx_st
evp_cipher_ctx_st._fields_ = [
]
class env_md_st(Structure):
    pass
EVP_MD = env_md_st
env_md_st._fields_ = [
]
class env_md_ctx_st(Structure):
    pass
EVP_MD_CTX = env_md_ctx_st
env_md_ctx_st._fields_ = [
]
class evp_pkey_st(Structure):
    pass
EVP_PKEY = evp_pkey_st
evp_pkey_st._fields_ = [
]
class evp_pkey_asn1_method_st(Structure):
    pass
evp_pkey_asn1_method_st._fields_ = [
]
EVP_PKEY_ASN1_METHOD = evp_pkey_asn1_method_st
class evp_pkey_method_st(Structure):
    pass
EVP_PKEY_METHOD = evp_pkey_method_st
evp_pkey_method_st._fields_ = [
]
class evp_pkey_ctx_st(Structure):
    pass
EVP_PKEY_CTX = evp_pkey_ctx_st
evp_pkey_ctx_st._fields_ = [
]
class dh_st(Structure):
    pass
dh_st._fields_ = [
]
DH = dh_st
class dh_method(Structure):
    pass
DH_METHOD = dh_method
dh_method._fields_ = [
]
class dsa_st(Structure):
    pass
DSA = dsa_st
dsa_st._fields_ = [
]
class dsa_method(Structure):
    pass
DSA_METHOD = dsa_method
dsa_method._fields_ = [
]
class rsa_st(Structure):
    pass
rsa_st._fields_ = [
]
RSA = rsa_st
class rsa_meth_st(Structure):
    pass
rsa_meth_st._fields_ = [
]
RSA_METHOD = rsa_meth_st
class rand_meth_st(Structure):
    pass
RAND_METHOD = rand_meth_st
rand_meth_st._fields_ = [
]
class ecdh_method(Structure):
    pass
ECDH_METHOD = ecdh_method
ecdh_method._fields_ = [
]
class ecdsa_method(Structure):
    pass
ECDSA_METHOD = ecdsa_method
ecdsa_method._fields_ = [
]
class x509_st(Structure):
    pass
x509_st._fields_ = [
]
X509 = x509_st
class X509_algor_st(Structure):
    pass
X509_ALGOR = X509_algor_st
X509_algor_st._fields_ = [
]
class X509_crl_st(Structure):
    pass
X509_CRL = X509_crl_st
X509_crl_st._fields_ = [
]
class x509_crl_method_st(Structure):
    pass
X509_CRL_METHOD = x509_crl_method_st
x509_crl_method_st._fields_ = [
]
class x509_revoked_st(Structure):
    pass
X509_REVOKED = x509_revoked_st
x509_revoked_st._fields_ = [
]
class X509_name_st(Structure):
    pass
X509_NAME = X509_name_st
X509_name_st._fields_ = [
]
class X509_pubkey_st(Structure):
    pass
X509_PUBKEY = X509_pubkey_st
X509_pubkey_st._fields_ = [
]
class x509_store_st(Structure):
    pass
X509_STORE = x509_store_st
x509_store_st._fields_ = [
]
class x509_store_ctx_st(Structure):
    pass
X509_STORE_CTX = x509_store_ctx_st
x509_store_ctx_st._fields_ = [
]
class pkcs8_priv_key_info_st(Structure):
    pass
PKCS8_PRIV_KEY_INFO = pkcs8_priv_key_info_st
pkcs8_priv_key_info_st._fields_ = [
]
class v3_ext_ctx(Structure):
    pass
X509V3_CTX = v3_ext_ctx
v3_ext_ctx._fields_ = [
]
class conf_st(Structure):
    pass
conf_st._fields_ = [
]
CONF = conf_st
class store_st(Structure):
    pass
store_st._fields_ = [
]
STORE = store_st
class store_method_st(Structure):
    pass
store_method_st._fields_ = [
]
STORE_METHOD = store_method_st
class ui_st(Structure):
    pass
ui_st._fields_ = [
]
UI = ui_st
class ui_method_st(Structure):
    pass
UI_METHOD = ui_method_st
ui_method_st._fields_ = [
]
class st_ERR_FNS(Structure):
    pass
st_ERR_FNS._fields_ = [
]
ERR_FNS = st_ERR_FNS
class engine_st(Structure):
    pass
engine_st._fields_ = [
]
ENGINE = engine_st
class ssl_st(Structure):
    pass
ssl_st._fields_ = [
]
SSL = ssl_st
class ssl_ctx_st(Structure):
    pass
ssl_ctx_st._fields_ = [
]
SSL_CTX = ssl_ctx_st
class X509_POLICY_NODE_st(Structure):
    pass
X509_POLICY_NODE = X509_POLICY_NODE_st
X509_POLICY_NODE_st._fields_ = [
]
class X509_POLICY_LEVEL_st(Structure):
    pass
X509_POLICY_LEVEL = X509_POLICY_LEVEL_st
X509_POLICY_LEVEL_st._fields_ = [
]
class X509_POLICY_TREE_st(Structure):
    pass
X509_POLICY_TREE_st._fields_ = [
]
X509_POLICY_TREE = X509_POLICY_TREE_st
class X509_POLICY_CACHE_st(Structure):
    pass
X509_POLICY_CACHE = X509_POLICY_CACHE_st
X509_POLICY_CACHE_st._fields_ = [
]
class AUTHORITY_KEYID_st(Structure):
    pass
AUTHORITY_KEYID = AUTHORITY_KEYID_st
AUTHORITY_KEYID_st._fields_ = [
]
class DIST_POINT_st(Structure):
    pass
DIST_POINT_st._fields_ = [
]
DIST_POINT = DIST_POINT_st
class ISSUING_DIST_POINT_st(Structure):
    pass
ISSUING_DIST_POINT = ISSUING_DIST_POINT_st
ISSUING_DIST_POINT_st._fields_ = [
]
class NAME_CONSTRAINTS_st(Structure):
    pass
NAME_CONSTRAINTS = NAME_CONSTRAINTS_st
NAME_CONSTRAINTS_st._fields_ = [
]
class ocsp_req_ctx_st(Structure):
    pass
ocsp_req_ctx_st._fields_ = [
]
OCSP_REQ_CTX = ocsp_req_ctx_st
class ocsp_response_st(Structure):
    pass
ocsp_response_st._fields_ = [
]
OCSP_RESPONSE = ocsp_response_st
class ocsp_responder_id_st(Structure):
    pass
OCSP_RESPID = ocsp_responder_id_st
ocsp_responder_id_st._fields_ = [
]
OPENSSL_STRING = STRING
OPENSSL_CSTRING = STRING
class stack_st_OPENSSL_STRING(Structure):
    pass
stack_st_OPENSSL_STRING._fields_ = [
    ('stack', _STACK),
]
OPENSSL_BLOCK = c_void_p
class stack_st_OPENSSL_BLOCK(Structure):
    pass
stack_st_OPENSSL_BLOCK._fields_ = [
    ('stack', _STACK),
]
sk_num = _libraries['libfreefare.so'].sk_num
sk_num.restype = c_int
sk_num.argtypes = [POINTER(_STACK)]
sk_value = _libraries['libfreefare.so'].sk_value
sk_value.restype = c_void_p
sk_value.argtypes = [POINTER(_STACK), c_int]
sk_set = _libraries['libfreefare.so'].sk_set
sk_set.restype = c_void_p
sk_set.argtypes = [POINTER(_STACK), c_int, c_void_p]
sk_new = _libraries['libfreefare.so'].sk_new
sk_new.restype = POINTER(_STACK)
sk_new.argtypes = [CFUNCTYPE(c_int, c_void_p, c_void_p)]
sk_new_null = _libraries['libfreefare.so'].sk_new_null
sk_new_null.restype = POINTER(_STACK)
sk_new_null.argtypes = []
sk_free = _libraries['libfreefare.so'].sk_free
sk_free.restype = None
sk_free.argtypes = [POINTER(_STACK)]
sk_pop_free = _libraries['libfreefare.so'].sk_pop_free
sk_pop_free.restype = None
sk_pop_free.argtypes = [POINTER(_STACK), CFUNCTYPE(None, c_void_p)]
sk_insert = _libraries['libfreefare.so'].sk_insert
sk_insert.restype = c_int
sk_insert.argtypes = [POINTER(_STACK), c_void_p, c_int]
sk_delete = _libraries['libfreefare.so'].sk_delete
sk_delete.restype = c_void_p
sk_delete.argtypes = [POINTER(_STACK), c_int]
sk_delete_ptr = _libraries['libfreefare.so'].sk_delete_ptr
sk_delete_ptr.restype = c_void_p
sk_delete_ptr.argtypes = [POINTER(_STACK), c_void_p]
sk_find = _libraries['libfreefare.so'].sk_find
sk_find.restype = c_int
sk_find.argtypes = [POINTER(_STACK), c_void_p]
sk_find_ex = _libraries['libfreefare.so'].sk_find_ex
sk_find_ex.restype = c_int
sk_find_ex.argtypes = [POINTER(_STACK), c_void_p]
sk_push = _libraries['libfreefare.so'].sk_push
sk_push.restype = c_int
sk_push.argtypes = [POINTER(_STACK), c_void_p]
sk_unshift = _libraries['libfreefare.so'].sk_unshift
sk_unshift.restype = c_int
sk_unshift.argtypes = [POINTER(_STACK), c_void_p]
sk_shift = _libraries['libfreefare.so'].sk_shift
sk_shift.restype = c_void_p
sk_shift.argtypes = [POINTER(_STACK)]
sk_pop = _libraries['libfreefare.so'].sk_pop
sk_pop.restype = c_void_p
sk_pop.argtypes = [POINTER(_STACK)]
sk_zero = _libraries['libfreefare.so'].sk_zero
sk_zero.restype = None
sk_zero.argtypes = [POINTER(_STACK)]
sk_set_cmp_func = _libraries['libfreefare.so'].sk_set_cmp_func
sk_set_cmp_func.restype = CFUNCTYPE(c_int, c_void_p, c_void_p)
sk_set_cmp_func.argtypes = [POINTER(_STACK), CFUNCTYPE(c_int, c_void_p, c_void_p)]
sk_dup = _libraries['libfreefare.so'].sk_dup
sk_dup.restype = POINTER(_STACK)
sk_dup.argtypes = [POINTER(_STACK)]
sk_sort = _libraries['libfreefare.so'].sk_sort
sk_sort.restype = None
sk_sort.argtypes = [POINTER(_STACK)]
sk_is_sorted = _libraries['libfreefare.so'].sk_is_sorted
sk_is_sorted.restype = c_int
sk_is_sorted.argtypes = [POINTER(_STACK)]
UI_new = _libraries['libfreefare.so'].UI_new
UI_new.restype = POINTER(UI)
UI_new.argtypes = []
UI_new_method = _libraries['libfreefare.so'].UI_new_method
UI_new_method.restype = POINTER(UI)
UI_new_method.argtypes = [POINTER(UI_METHOD)]
UI_free = _libraries['libfreefare.so'].UI_free
UI_free.restype = None
UI_free.argtypes = [POINTER(UI)]
UI_add_input_string = _libraries['libfreefare.so'].UI_add_input_string
UI_add_input_string.restype = c_int
UI_add_input_string.argtypes = [POINTER(UI), STRING, c_int, STRING, c_int, c_int]
UI_dup_input_string = _libraries['libfreefare.so'].UI_dup_input_string
UI_dup_input_string.restype = c_int
UI_dup_input_string.argtypes = [POINTER(UI), STRING, c_int, STRING, c_int, c_int]
UI_add_verify_string = _libraries['libfreefare.so'].UI_add_verify_string
UI_add_verify_string.restype = c_int
UI_add_verify_string.argtypes = [POINTER(UI), STRING, c_int, STRING, c_int, c_int, STRING]
UI_dup_verify_string = _libraries['libfreefare.so'].UI_dup_verify_string
UI_dup_verify_string.restype = c_int
UI_dup_verify_string.argtypes = [POINTER(UI), STRING, c_int, STRING, c_int, c_int, STRING]
UI_add_input_boolean = _libraries['libfreefare.so'].UI_add_input_boolean
UI_add_input_boolean.restype = c_int
UI_add_input_boolean.argtypes = [POINTER(UI), STRING, STRING, STRING, STRING, c_int, STRING]
UI_dup_input_boolean = _libraries['libfreefare.so'].UI_dup_input_boolean
UI_dup_input_boolean.restype = c_int
UI_dup_input_boolean.argtypes = [POINTER(UI), STRING, STRING, STRING, STRING, c_int, STRING]
UI_add_info_string = _libraries['libfreefare.so'].UI_add_info_string
UI_add_info_string.restype = c_int
UI_add_info_string.argtypes = [POINTER(UI), STRING]
UI_dup_info_string = _libraries['libfreefare.so'].UI_dup_info_string
UI_dup_info_string.restype = c_int
UI_dup_info_string.argtypes = [POINTER(UI), STRING]
UI_add_error_string = _libraries['libfreefare.so'].UI_add_error_string
UI_add_error_string.restype = c_int
UI_add_error_string.argtypes = [POINTER(UI), STRING]
UI_dup_error_string = _libraries['libfreefare.so'].UI_dup_error_string
UI_dup_error_string.restype = c_int
UI_dup_error_string.argtypes = [POINTER(UI), STRING]
UI_construct_prompt = _libraries['libfreefare.so'].UI_construct_prompt
UI_construct_prompt.restype = STRING
UI_construct_prompt.argtypes = [POINTER(UI), STRING, STRING]
UI_add_user_data = _libraries['libfreefare.so'].UI_add_user_data
UI_add_user_data.restype = c_void_p
UI_add_user_data.argtypes = [POINTER(UI), c_void_p]
UI_get0_user_data = _libraries['libfreefare.so'].UI_get0_user_data
UI_get0_user_data.restype = c_void_p
UI_get0_user_data.argtypes = [POINTER(UI)]
UI_get0_result = _libraries['libfreefare.so'].UI_get0_result
UI_get0_result.restype = STRING
UI_get0_result.argtypes = [POINTER(UI), c_int]
UI_process = _libraries['libfreefare.so'].UI_process
UI_process.restype = c_int
UI_process.argtypes = [POINTER(UI)]
UI_ctrl = _libraries['libfreefare.so'].UI_ctrl
UI_ctrl.restype = c_int
UI_ctrl.argtypes = [POINTER(UI), c_int, c_long, c_void_p, CFUNCTYPE(None)]
UI_get_ex_new_index = _libraries['libfreefare.so'].UI_get_ex_new_index
UI_get_ex_new_index.restype = c_int
UI_get_ex_new_index.argtypes = [c_long, c_void_p, POINTER(CRYPTO_EX_new), POINTER(CRYPTO_EX_dup), POINTER(CRYPTO_EX_free)]
UI_set_ex_data = _libraries['libfreefare.so'].UI_set_ex_data
UI_set_ex_data.restype = c_int
UI_set_ex_data.argtypes = [POINTER(UI), c_int, c_void_p]
UI_get_ex_data = _libraries['libfreefare.so'].UI_get_ex_data
UI_get_ex_data.restype = c_void_p
UI_get_ex_data.argtypes = [POINTER(UI), c_int]
UI_set_default_method = _libraries['libfreefare.so'].UI_set_default_method
UI_set_default_method.restype = None
UI_set_default_method.argtypes = [POINTER(UI_METHOD)]
UI_get_default_method = _libraries['libfreefare.so'].UI_get_default_method
UI_get_default_method.restype = POINTER(UI_METHOD)
UI_get_default_method.argtypes = []
UI_get_method = _libraries['libfreefare.so'].UI_get_method
UI_get_method.restype = POINTER(UI_METHOD)
UI_get_method.argtypes = [POINTER(UI)]
UI_set_method = _libraries['libfreefare.so'].UI_set_method
UI_set_method.restype = POINTER(UI_METHOD)
UI_set_method.argtypes = [POINTER(UI), POINTER(UI_METHOD)]
UI_OpenSSL = _libraries['libfreefare.so'].UI_OpenSSL
UI_OpenSSL.restype = POINTER(UI_METHOD)
UI_OpenSSL.argtypes = []
class ui_string_st(Structure):
    pass
ui_string_st._fields_ = [
]
UI_STRING = ui_string_st
class stack_st_UI_STRING(Structure):
    pass
stack_st_UI_STRING._fields_ = [
    ('stack', _STACK),
]

# values for enumeration 'UI_string_types'
UI_string_types = c_int # enum
UI_create_method = _libraries['libfreefare.so'].UI_create_method
UI_create_method.restype = POINTER(UI_METHOD)
UI_create_method.argtypes = [STRING]
UI_destroy_method = _libraries['libfreefare.so'].UI_destroy_method
UI_destroy_method.restype = None
UI_destroy_method.argtypes = [POINTER(UI_METHOD)]
UI_method_set_opener = _libraries['libfreefare.so'].UI_method_set_opener
UI_method_set_opener.restype = c_int
UI_method_set_opener.argtypes = [POINTER(UI_METHOD), CFUNCTYPE(c_int, POINTER(UI))]
UI_method_set_writer = _libraries['libfreefare.so'].UI_method_set_writer
UI_method_set_writer.restype = c_int
UI_method_set_writer.argtypes = [POINTER(UI_METHOD), CFUNCTYPE(c_int, POINTER(UI), POINTER(UI_STRING))]
UI_method_set_flusher = _libraries['libfreefare.so'].UI_method_set_flusher
UI_method_set_flusher.restype = c_int
UI_method_set_flusher.argtypes = [POINTER(UI_METHOD), CFUNCTYPE(c_int, POINTER(UI))]
UI_method_set_reader = _libraries['libfreefare.so'].UI_method_set_reader
UI_method_set_reader.restype = c_int
UI_method_set_reader.argtypes = [POINTER(UI_METHOD), CFUNCTYPE(c_int, POINTER(UI), POINTER(UI_STRING))]
UI_method_set_closer = _libraries['libfreefare.so'].UI_method_set_closer
UI_method_set_closer.restype = c_int
UI_method_set_closer.argtypes = [POINTER(UI_METHOD), CFUNCTYPE(c_int, POINTER(UI))]
UI_method_set_prompt_constructor = _libraries['libfreefare.so'].UI_method_set_prompt_constructor
UI_method_set_prompt_constructor.restype = c_int
UI_method_set_prompt_constructor.argtypes = [POINTER(UI_METHOD), CFUNCTYPE(STRING, POINTER(UI), STRING, STRING)]
UI_method_get_opener = _libraries['libfreefare.so'].UI_method_get_opener
UI_method_get_opener.restype = CFUNCTYPE(c_int, POINTER(UI))
UI_method_get_opener.argtypes = [POINTER(UI_METHOD)]
UI_method_get_writer = _libraries['libfreefare.so'].UI_method_get_writer
UI_method_get_writer.restype = CFUNCTYPE(c_int, POINTER(UI), POINTER(UI_STRING))
UI_method_get_writer.argtypes = [POINTER(UI_METHOD)]
UI_method_get_flusher = _libraries['libfreefare.so'].UI_method_get_flusher
UI_method_get_flusher.restype = CFUNCTYPE(c_int, POINTER(UI))
UI_method_get_flusher.argtypes = [POINTER(UI_METHOD)]
UI_method_get_reader = _libraries['libfreefare.so'].UI_method_get_reader
UI_method_get_reader.restype = CFUNCTYPE(c_int, POINTER(UI), POINTER(UI_STRING))
UI_method_get_reader.argtypes = [POINTER(UI_METHOD)]
UI_method_get_closer = _libraries['libfreefare.so'].UI_method_get_closer
UI_method_get_closer.restype = CFUNCTYPE(c_int, POINTER(UI))
UI_method_get_closer.argtypes = [POINTER(UI_METHOD)]
UI_method_get_prompt_constructor = _libraries['libfreefare.so'].UI_method_get_prompt_constructor
UI_method_get_prompt_constructor.restype = CFUNCTYPE(STRING, POINTER(UI), STRING, STRING)
UI_method_get_prompt_constructor.argtypes = [POINTER(UI_METHOD)]
UI_get_string_type = _libraries['libfreefare.so'].UI_get_string_type
UI_get_string_type.restype = UI_string_types
UI_get_string_type.argtypes = [POINTER(UI_STRING)]
UI_get_input_flags = _libraries['libfreefare.so'].UI_get_input_flags
UI_get_input_flags.restype = c_int
UI_get_input_flags.argtypes = [POINTER(UI_STRING)]
UI_get0_output_string = _libraries['libfreefare.so'].UI_get0_output_string
UI_get0_output_string.restype = STRING
UI_get0_output_string.argtypes = [POINTER(UI_STRING)]
UI_get0_action_string = _libraries['libfreefare.so'].UI_get0_action_string
UI_get0_action_string.restype = STRING
UI_get0_action_string.argtypes = [POINTER(UI_STRING)]
UI_get0_result_string = _libraries['libfreefare.so'].UI_get0_result_string
UI_get0_result_string.restype = STRING
UI_get0_result_string.argtypes = [POINTER(UI_STRING)]
UI_get0_test_string = _libraries['libfreefare.so'].UI_get0_test_string
UI_get0_test_string.restype = STRING
UI_get0_test_string.argtypes = [POINTER(UI_STRING)]
UI_get_result_minsize = _libraries['libfreefare.so'].UI_get_result_minsize
UI_get_result_minsize.restype = c_int
UI_get_result_minsize.argtypes = [POINTER(UI_STRING)]
UI_get_result_maxsize = _libraries['libfreefare.so'].UI_get_result_maxsize
UI_get_result_maxsize.restype = c_int
UI_get_result_maxsize.argtypes = [POINTER(UI_STRING)]
UI_set_result = _libraries['libfreefare.so'].UI_set_result
UI_set_result.restype = c_int
UI_set_result.argtypes = [POINTER(UI), POINTER(UI_STRING), STRING]
UI_UTIL_read_pw_string = _libraries['libfreefare.so'].UI_UTIL_read_pw_string
UI_UTIL_read_pw_string.restype = c_int
UI_UTIL_read_pw_string.argtypes = [STRING, c_int, STRING, c_int]
UI_UTIL_read_pw = _libraries['libfreefare.so'].UI_UTIL_read_pw
UI_UTIL_read_pw.restype = c_int
UI_UTIL_read_pw.argtypes = [STRING, STRING, c_int, STRING, c_int]
ERR_load_UI_strings = _libraries['libfreefare.so'].ERR_load_UI_strings
ERR_load_UI_strings.restype = None
ERR_load_UI_strings.argtypes = []
_ossl_old_des_read_pw_string = _libraries['libfreefare.so']._ossl_old_des_read_pw_string
_ossl_old_des_read_pw_string.restype = c_int
_ossl_old_des_read_pw_string.argtypes = [STRING, c_int, STRING, c_int]
_ossl_old_des_read_pw = _libraries['libfreefare.so']._ossl_old_des_read_pw
_ossl_old_des_read_pw.restype = c_int
_ossl_old_des_read_pw.argtypes = [STRING, STRING, c_int, STRING, c_int]
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
__FILE = _IO_FILE
__va_list_tag._fields_ = [
]
__gnuc_va_list = __va_list_tag * 1
va_list = __gnuc_va_list
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
class div_t(Structure):
    pass
div_t._fields_ = [
    ('quot', c_int),
    ('rem', c_int),
]
class ldiv_t(Structure):
    pass
ldiv_t._fields_ = [
    ('quot', c_long),
    ('rem', c_long),
]
class lldiv_t(Structure):
    pass
lldiv_t._fields_ = [
    ('quot', c_longlong),
    ('rem', c_longlong),
]
__ctype_get_mb_cur_max = _libraries['libnfc.so'].__ctype_get_mb_cur_max
__ctype_get_mb_cur_max.restype = size_t
__ctype_get_mb_cur_max.argtypes = []
strtod = _libraries['libnfc.so'].strtod
strtod.restype = c_double
strtod.argtypes = [STRING, POINTER(STRING)]
strtof = _libraries['libnfc.so'].strtof
strtof.restype = c_float
strtof.argtypes = [STRING, POINTER(STRING)]
strtold = _libraries['libnfc.so'].strtold
strtold.restype = c_longdouble
strtold.argtypes = [STRING, POINTER(STRING)]
strtol = _libraries['libnfc.so'].strtol
strtol.restype = c_long
strtol.argtypes = [STRING, POINTER(STRING), c_int]
strtoul = _libraries['libnfc.so'].strtoul
strtoul.restype = c_ulong
strtoul.argtypes = [STRING, POINTER(STRING), c_int]
strtoq = _libraries['libnfc.so'].strtoq
strtoq.restype = c_longlong
strtoq.argtypes = [STRING, POINTER(STRING), c_int]
strtouq = _libraries['libnfc.so'].strtouq
strtouq.restype = c_ulonglong
strtouq.argtypes = [STRING, POINTER(STRING), c_int]
strtoll = _libraries['libnfc.so'].strtoll
strtoll.restype = c_longlong
strtoll.argtypes = [STRING, POINTER(STRING), c_int]
strtoull = _libraries['libnfc.so'].strtoull
strtoull.restype = c_ulonglong
strtoull.argtypes = [STRING, POINTER(STRING), c_int]
class __locale_struct(Structure):
    pass
__locale_t = POINTER(__locale_struct)
strtol_l = _libraries['libnfc.so'].strtol_l
strtol_l.restype = c_long
strtol_l.argtypes = [STRING, POINTER(STRING), c_int, __locale_t]
strtoul_l = _libraries['libnfc.so'].strtoul_l
strtoul_l.restype = c_ulong
strtoul_l.argtypes = [STRING, POINTER(STRING), c_int, __locale_t]
strtoll_l = _libraries['libnfc.so'].strtoll_l
strtoll_l.restype = c_longlong
strtoll_l.argtypes = [STRING, POINTER(STRING), c_int, __locale_t]
strtoull_l = _libraries['libnfc.so'].strtoull_l
strtoull_l.restype = c_ulonglong
strtoull_l.argtypes = [STRING, POINTER(STRING), c_int, __locale_t]
strtod_l = _libraries['libnfc.so'].strtod_l
strtod_l.restype = c_double
strtod_l.argtypes = [STRING, POINTER(STRING), __locale_t]
strtof_l = _libraries['libnfc.so'].strtof_l
strtof_l.restype = c_float
strtof_l.argtypes = [STRING, POINTER(STRING), __locale_t]
strtold_l = _libraries['libnfc.so'].strtold_l
strtold_l.restype = c_longdouble
strtold_l.argtypes = [STRING, POINTER(STRING), __locale_t]
atoi = _libraries['libnfc.so'].atoi
atoi.restype = c_int
atoi.argtypes = [STRING]
atol = _libraries['libnfc.so'].atol
atol.restype = c_long
atol.argtypes = [STRING]
atoll = _libraries['libnfc.so'].atoll
atoll.restype = c_longlong
atoll.argtypes = [STRING]
l64a = _libraries['libnfc.so'].l64a
l64a.restype = STRING
l64a.argtypes = [c_long]
a64l = _libraries['libnfc.so'].a64l
a64l.restype = c_long
a64l.argtypes = [STRING]
random = _libraries['libnfc.so'].random
random.restype = c_long
random.argtypes = []
srandom = _libraries['libnfc.so'].srandom
srandom.restype = None
srandom.argtypes = [c_uint]
initstate = _libraries['libnfc.so'].initstate
initstate.restype = STRING
initstate.argtypes = [c_uint, STRING, size_t]
setstate = _libraries['libnfc.so'].setstate
setstate.restype = STRING
setstate.argtypes = [STRING]
class random_data(Structure):
    pass
random_data._fields_ = [
    ('fptr', POINTER(int32_t)),
    ('rptr', POINTER(int32_t)),
    ('state', POINTER(int32_t)),
    ('rand_type', c_int),
    ('rand_deg', c_int),
    ('rand_sep', c_int),
    ('end_ptr', POINTER(int32_t)),
]
random_r = _libraries['libnfc.so'].random_r
random_r.restype = c_int
random_r.argtypes = [POINTER(random_data), POINTER(int32_t)]
srandom_r = _libraries['libnfc.so'].srandom_r
srandom_r.restype = c_int
srandom_r.argtypes = [c_uint, POINTER(random_data)]
initstate_r = _libraries['libnfc.so'].initstate_r
initstate_r.restype = c_int
initstate_r.argtypes = [c_uint, STRING, size_t, POINTER(random_data)]
setstate_r = _libraries['libnfc.so'].setstate_r
setstate_r.restype = c_int
setstate_r.argtypes = [STRING, POINTER(random_data)]
rand = _libraries['libnfc.so'].rand
rand.restype = c_int
rand.argtypes = []
srand = _libraries['libnfc.so'].srand
srand.restype = None
srand.argtypes = [c_uint]
rand_r = _libraries['libnfc.so'].rand_r
rand_r.restype = c_int
rand_r.argtypes = [POINTER(c_uint)]
drand48 = _libraries['libnfc.so'].drand48
drand48.restype = c_double
drand48.argtypes = []
erand48 = _libraries['libnfc.so'].erand48
erand48.restype = c_double
erand48.argtypes = [POINTER(c_ushort)]
lrand48 = _libraries['libnfc.so'].lrand48
lrand48.restype = c_long
lrand48.argtypes = []
nrand48 = _libraries['libnfc.so'].nrand48
nrand48.restype = c_long
nrand48.argtypes = [POINTER(c_ushort)]
mrand48 = _libraries['libnfc.so'].mrand48
mrand48.restype = c_long
mrand48.argtypes = []
jrand48 = _libraries['libnfc.so'].jrand48
jrand48.restype = c_long
jrand48.argtypes = [POINTER(c_ushort)]
srand48 = _libraries['libnfc.so'].srand48
srand48.restype = None
srand48.argtypes = [c_long]
seed48 = _libraries['libnfc.so'].seed48
seed48.restype = POINTER(c_ushort)
seed48.argtypes = [POINTER(c_ushort)]
lcong48 = _libraries['libnfc.so'].lcong48
lcong48.restype = None
lcong48.argtypes = [POINTER(c_ushort)]
class drand48_data(Structure):
    pass
drand48_data._fields_ = [
    ('__x', c_ushort * 3),
    ('__old_x', c_ushort * 3),
    ('__c', c_ushort),
    ('__init', c_ushort),
    ('__a', c_ulonglong),
]
drand48_r = _libraries['libnfc.so'].drand48_r
drand48_r.restype = c_int
drand48_r.argtypes = [POINTER(drand48_data), POINTER(c_double)]
erand48_r = _libraries['libnfc.so'].erand48_r
erand48_r.restype = c_int
erand48_r.argtypes = [POINTER(c_ushort), POINTER(drand48_data), POINTER(c_double)]
lrand48_r = _libraries['libnfc.so'].lrand48_r
lrand48_r.restype = c_int
lrand48_r.argtypes = [POINTER(drand48_data), POINTER(c_long)]
nrand48_r = _libraries['libnfc.so'].nrand48_r
nrand48_r.restype = c_int
nrand48_r.argtypes = [POINTER(c_ushort), POINTER(drand48_data), POINTER(c_long)]
mrand48_r = _libraries['libnfc.so'].mrand48_r
mrand48_r.restype = c_int
mrand48_r.argtypes = [POINTER(drand48_data), POINTER(c_long)]
jrand48_r = _libraries['libnfc.so'].jrand48_r
jrand48_r.restype = c_int
jrand48_r.argtypes = [POINTER(c_ushort), POINTER(drand48_data), POINTER(c_long)]
srand48_r = _libraries['libnfc.so'].srand48_r
srand48_r.restype = c_int
srand48_r.argtypes = [c_long, POINTER(drand48_data)]
seed48_r = _libraries['libnfc.so'].seed48_r
seed48_r.restype = c_int
seed48_r.argtypes = [POINTER(c_ushort), POINTER(drand48_data)]
lcong48_r = _libraries['libnfc.so'].lcong48_r
lcong48_r.restype = c_int
lcong48_r.argtypes = [POINTER(c_ushort), POINTER(drand48_data)]
malloc = _libraries['libnfc.so'].malloc
malloc.restype = c_void_p
malloc.argtypes = [size_t]
calloc = _libraries['libnfc.so'].calloc
calloc.restype = c_void_p
calloc.argtypes = [size_t, size_t]
realloc = _libraries['libnfc.so'].realloc
realloc.restype = c_void_p
realloc.argtypes = [c_void_p, size_t]
free = _libraries['libnfc.so'].free
free.restype = None
free.argtypes = [c_void_p]
cfree = _libraries['libnfc.so'].cfree
cfree.restype = None
cfree.argtypes = [c_void_p]
valloc = _libraries['libnfc.so'].valloc
valloc.restype = c_void_p
valloc.argtypes = [size_t]
posix_memalign = _libraries['libnfc.so'].posix_memalign
posix_memalign.restype = c_int
posix_memalign.argtypes = [POINTER(c_void_p), size_t, size_t]
aligned_alloc = _libraries['libnfc.so'].aligned_alloc
aligned_alloc.restype = c_void_p
aligned_alloc.argtypes = [size_t, size_t]
abort = _libraries['libnfc.so'].abort
abort.restype = None
abort.argtypes = []
on_exit = _libraries['libnfc.so'].on_exit
on_exit.restype = c_int
on_exit.argtypes = [CFUNCTYPE(None, c_int, c_void_p), c_void_p]
exit = _libraries['libnfc.so'].exit
exit.restype = None
exit.argtypes = [c_int]
quick_exit = _libraries['libnfc.so'].quick_exit
quick_exit.restype = None
quick_exit.argtypes = [c_int]
_Exit = _libraries['libnfc.so']._Exit
_Exit.restype = None
_Exit.argtypes = [c_int]
getenv = _libraries['libnfc.so'].getenv
getenv.restype = STRING
getenv.argtypes = [STRING]
secure_getenv = _libraries['libnfc.so'].secure_getenv
secure_getenv.restype = STRING
secure_getenv.argtypes = [STRING]
putenv = _libraries['libnfc.so'].putenv
putenv.restype = c_int
putenv.argtypes = [STRING]
setenv = _libraries['libnfc.so'].setenv
setenv.restype = c_int
setenv.argtypes = [STRING, STRING, c_int]
unsetenv = _libraries['libnfc.so'].unsetenv
unsetenv.restype = c_int
unsetenv.argtypes = [STRING]
clearenv = _libraries['libnfc.so'].clearenv
clearenv.restype = c_int
clearenv.argtypes = []
mktemp = _libraries['libnfc.so'].mktemp
mktemp.restype = STRING
mktemp.argtypes = [STRING]
mkstemp = _libraries['libnfc.so'].mkstemp
mkstemp.restype = c_int
mkstemp.argtypes = [STRING]
mkstemp64 = _libraries['libnfc.so'].mkstemp64
mkstemp64.restype = c_int
mkstemp64.argtypes = [STRING]
mkstemps = _libraries['libnfc.so'].mkstemps
mkstemps.restype = c_int
mkstemps.argtypes = [STRING, c_int]
mkstemps64 = _libraries['libnfc.so'].mkstemps64
mkstemps64.restype = c_int
mkstemps64.argtypes = [STRING, c_int]
mkdtemp = _libraries['libnfc.so'].mkdtemp
mkdtemp.restype = STRING
mkdtemp.argtypes = [STRING]
mkostemp = _libraries['libnfc.so'].mkostemp
mkostemp.restype = c_int
mkostemp.argtypes = [STRING, c_int]
mkostemp64 = _libraries['libnfc.so'].mkostemp64
mkostemp64.restype = c_int
mkostemp64.argtypes = [STRING, c_int]
mkostemps = _libraries['libnfc.so'].mkostemps
mkostemps.restype = c_int
mkostemps.argtypes = [STRING, c_int, c_int]
mkostemps64 = _libraries['libnfc.so'].mkostemps64
mkostemps64.restype = c_int
mkostemps64.argtypes = [STRING, c_int, c_int]
system = _libraries['libnfc.so'].system
system.restype = c_int
system.argtypes = [STRING]
canonicalize_file_name = _libraries['libnfc.so'].canonicalize_file_name
canonicalize_file_name.restype = STRING
canonicalize_file_name.argtypes = [STRING]
__compar_fn_t = CFUNCTYPE(c_int, c_void_p, c_void_p)
comparison_fn_t = __compar_fn_t
__compar_d_fn_t = CFUNCTYPE(c_int, c_void_p, c_void_p, c_void_p)
qsort = _libraries['libnfc.so'].qsort
qsort.restype = None
qsort.argtypes = [c_void_p, size_t, size_t, __compar_fn_t]
qsort_r = _libraries['libnfc.so'].qsort_r
qsort_r.restype = None
qsort_r.argtypes = [c_void_p, size_t, size_t, __compar_d_fn_t, c_void_p]
abs = _libraries['libnfc.so'].abs
abs.restype = c_int
abs.argtypes = [c_int]
labs = _libraries['libnfc.so'].labs
labs.restype = c_long
labs.argtypes = [c_long]
llabs = _libraries['libnfc.so'].llabs
llabs.restype = c_longlong
llabs.argtypes = [c_longlong]
div = _libraries['libnfc.so'].div
div.restype = div_t
div.argtypes = [c_int, c_int]
ldiv = _libraries['libnfc.so'].ldiv
ldiv.restype = ldiv_t
ldiv.argtypes = [c_long, c_long]
lldiv = _libraries['libnfc.so'].lldiv
lldiv.restype = lldiv_t
lldiv.argtypes = [c_longlong, c_longlong]
ecvt = _libraries['libnfc.so'].ecvt
ecvt.restype = STRING
ecvt.argtypes = [c_double, c_int, POINTER(c_int), POINTER(c_int)]
fcvt = _libraries['libnfc.so'].fcvt
fcvt.restype = STRING
fcvt.argtypes = [c_double, c_int, POINTER(c_int), POINTER(c_int)]
gcvt = _libraries['libnfc.so'].gcvt
gcvt.restype = STRING
gcvt.argtypes = [c_double, c_int, STRING]
qecvt = _libraries['libnfc.so'].qecvt
qecvt.restype = STRING
qecvt.argtypes = [c_longdouble, c_int, POINTER(c_int), POINTER(c_int)]
qfcvt = _libraries['libnfc.so'].qfcvt
qfcvt.restype = STRING
qfcvt.argtypes = [c_longdouble, c_int, POINTER(c_int), POINTER(c_int)]
qgcvt = _libraries['libnfc.so'].qgcvt
qgcvt.restype = STRING
qgcvt.argtypes = [c_longdouble, c_int, STRING]
ecvt_r = _libraries['libnfc.so'].ecvt_r
ecvt_r.restype = c_int
ecvt_r.argtypes = [c_double, c_int, POINTER(c_int), POINTER(c_int), STRING, size_t]
fcvt_r = _libraries['libnfc.so'].fcvt_r
fcvt_r.restype = c_int
fcvt_r.argtypes = [c_double, c_int, POINTER(c_int), POINTER(c_int), STRING, size_t]
qecvt_r = _libraries['libnfc.so'].qecvt_r
qecvt_r.restype = c_int
qecvt_r.argtypes = [c_longdouble, c_int, POINTER(c_int), POINTER(c_int), STRING, size_t]
qfcvt_r = _libraries['libnfc.so'].qfcvt_r
qfcvt_r.restype = c_int
qfcvt_r.argtypes = [c_longdouble, c_int, POINTER(c_int), POINTER(c_int), STRING, size_t]
mblen = _libraries['libnfc.so'].mblen
mblen.restype = c_int
mblen.argtypes = [STRING, size_t]
mbtowc = _libraries['libnfc.so'].mbtowc
mbtowc.restype = c_int
mbtowc.argtypes = [WSTRING, STRING, size_t]
rpmatch = _libraries['libnfc.so'].rpmatch
rpmatch.restype = c_int
rpmatch.argtypes = [STRING]
getsubopt = _libraries['libnfc.so'].getsubopt
getsubopt.restype = c_int
getsubopt.argtypes = [POINTER(STRING), POINTER(STRING), POINTER(STRING)]
posix_openpt = _libraries['libnfc.so'].posix_openpt
posix_openpt.restype = c_int
posix_openpt.argtypes = [c_int]
grantpt = _libraries['libnfc.so'].grantpt
grantpt.restype = c_int
grantpt.argtypes = [c_int]
unlockpt = _libraries['libnfc.so'].unlockpt
unlockpt.restype = c_int
unlockpt.argtypes = [c_int]
ptsname = _libraries['libnfc.so'].ptsname
ptsname.restype = STRING
ptsname.argtypes = [c_int]
getpt = _libraries['libnfc.so'].getpt
getpt.restype = c_int
getpt.argtypes = []
getloadavg = _libraries['libnfc.so'].getloadavg
getloadavg.restype = c_int
getloadavg.argtypes = [POINTER(c_double), c_int]
__clock_t = c_long
clock_t = __clock_t
__time_t = c_long
time_t = __time_t
__clockid_t = c_int
clockid_t = __clockid_t
__timer_t = c_void_p
timer_t = __timer_t
class timespec(Structure):
    pass
__syscall_slong_t = c_long
timespec._fields_ = [
    ('tv_sec', __time_t),
    ('tv_nsec', __syscall_slong_t),
]
pthread_t = c_ulong
class pthread_attr_t(Union):
    pass
class __pthread_internal_list(Structure):
    pass
__pthread_internal_list._fields_ = [
    ('__prev', POINTER(__pthread_internal_list)),
    ('__next', POINTER(__pthread_internal_list)),
]
__pthread_list_t = __pthread_internal_list
class __pthread_mutex_s(Structure):
    pass
__pthread_mutex_s._fields_ = [
    ('__lock', c_int),
    ('__count', c_uint),
    ('__owner', c_int),
    ('__nusers', c_uint),
    ('__kind', c_int),
    ('__spins', c_short),
    ('__elision', c_short),
    ('__list', __pthread_list_t),
]
class N14pthread_cond_t4DOT_14E(Structure):
    pass
N14pthread_cond_t4DOT_14E._fields_ = [
    ('__lock', c_int),
    ('__futex', c_uint),
    ('__total_seq', c_ulonglong),
    ('__wakeup_seq', c_ulonglong),
    ('__woken_seq', c_ulonglong),
    ('__mutex', c_void_p),
    ('__nwaiters', c_uint),
    ('__broadcast_seq', c_uint),
]
pthread_key_t = c_uint
pthread_once_t = c_int
class N16pthread_rwlock_t4DOT_17E(Structure):
    pass
N16pthread_rwlock_t4DOT_17E._fields_ = [
    ('__lock', c_int),
    ('__nr_readers', c_uint),
    ('__readers_wakeup', c_uint),
    ('__writer_wakeup', c_uint),
    ('__nr_readers_queued', c_uint),
    ('__nr_writers_queued', c_uint),
    ('__writer', c_int),
    ('__shared', c_int),
    ('__pad1', c_ulong),
    ('__pad2', c_ulong),
    ('__flags', c_uint),
]
pthread_spinlock_t = c_int
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
bsearch = _libraries['libnfc.so'].bsearch
bsearch.restype = c_void_p
bsearch.argtypes = [c_void_p, c_void_p, size_t, size_t, __compar_fn_t]
atof = _libraries['libnfc.so'].atof
atof.restype = c_double
atof.argtypes = [STRING]
__realpath_chk = _libraries['libnfc.so'].__realpath_chk
__realpath_chk.restype = STRING
__realpath_chk.argtypes = [STRING, STRING, size_t]
realpath = _libraries['libnfc.so'].realpath
realpath.restype = STRING
realpath.argtypes = [STRING, STRING]
__ptsname_r_chk = _libraries['libnfc.so'].__ptsname_r_chk
__ptsname_r_chk.restype = c_int
__ptsname_r_chk.argtypes = [c_int, STRING, size_t, size_t]
ptsname_r = _libraries['libnfc.so'].ptsname_r
ptsname_r.restype = c_int
ptsname_r.argtypes = [c_int, STRING, size_t]
__wctomb_chk = _libraries['libnfc.so'].__wctomb_chk
__wctomb_chk.restype = c_int
__wctomb_chk.argtypes = [STRING, c_wchar, size_t]
wctomb = _libraries['libnfc.so'].wctomb
wctomb.restype = c_int
wctomb.argtypes = [STRING, c_wchar]
__mbstowcs_chk = _libraries['libnfc.so'].__mbstowcs_chk
__mbstowcs_chk.restype = size_t
__mbstowcs_chk.argtypes = [WSTRING, STRING, size_t, size_t]
mbstowcs = _libraries['libnfc.so'].mbstowcs
mbstowcs.restype = size_t
mbstowcs.argtypes = [WSTRING, STRING, size_t]
__wcstombs_chk = _libraries['libnfc.so'].__wcstombs_chk
__wcstombs_chk.restype = size_t
__wcstombs_chk.argtypes = [STRING, WSTRING, size_t, size_t]
wcstombs = _libraries['libnfc.so'].wcstombs
wcstombs.restype = size_t
wcstombs.argtypes = [STRING, WSTRING, size_t]
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
__rlim_t = c_ulong
__rlim64_t = c_ulong
__id_t = c_uint
__useconds_t = c_uint
__daddr_t = c_int
__key_t = c_int
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

# values for enumeration 'idtype_t'
idtype_t = c_int # enum
class N4wait3DOT_4E(Structure):
    pass
N4wait3DOT_4E._fields_ = [
    ('__w_termsig', c_uint, 7),
    ('__w_coredump', c_uint, 1),
    ('__w_retcode', c_uint, 8),
    ('', c_uint, 16),
]
class N4wait3DOT_5E(Structure):
    pass
N4wait3DOT_5E._fields_ = [
    ('__w_stopval', c_uint, 8),
    ('__w_stopsig', c_uint, 8),
    ('', c_uint, 16),
]
sigset_t = __sigset_t
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
gnu_dev_major = _libraries['libnfc.so'].gnu_dev_major
gnu_dev_major.restype = c_uint
gnu_dev_major.argtypes = [c_ulonglong]
gnu_dev_minor = _libraries['libnfc.so'].gnu_dev_minor
gnu_dev_minor.restype = c_uint
gnu_dev_minor.argtypes = [c_ulonglong]
gnu_dev_makedev = _libraries['libnfc.so'].gnu_dev_makedev
gnu_dev_makedev.restype = c_ulonglong
gnu_dev_makedev.argtypes = [c_uint, c_uint]
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
u_char = __u_char
u_short = __u_short
u_int = __u_int
u_long = __u_long
quad_t = __quad_t
u_quad_t = __u_quad_t
fsid_t = __fsid_t
loff_t = __loff_t
ino_t = __ino_t
ino64_t = __ino64_t
dev_t = __dev_t
gid_t = __gid_t
mode_t = __mode_t
nlink_t = __nlink_t
uid_t = __uid_t
off64_t = __off64_t
pid_t = __pid_t
id_t = __id_t
daddr_t = __daddr_t
caddr_t = __caddr_t
key_t = __key_t
useconds_t = __useconds_t
suseconds_t = __suseconds_t
ulong = c_ulong
ushort = c_ushort
uint = c_uint
int8_t = c_int8
int16_t = c_int16
int64_t = c_int64
u_int8_t = c_ubyte
u_int16_t = c_ushort
u_int32_t = c_uint
u_int64_t = c_ulong
register_t = c_long
blksize_t = __blksize_t
blkcnt_t = __blkcnt_t
fsblkcnt_t = __fsblkcnt_t
fsfilcnt_t = __fsfilcnt_t
blkcnt64_t = __blkcnt64_t
fsblkcnt64_t = __fsblkcnt64_t
fsfilcnt64_t = __fsfilcnt64_t
class __locale_data(Structure):
    pass
__locale_struct._fields_ = [
    ('__locales', POINTER(__locale_data) * 13),
    ('__ctype_b', POINTER(c_ushort)),
    ('__ctype_tolower', POINTER(c_int)),
    ('__ctype_toupper', POINTER(c_int)),
    ('__names', STRING * 13),
]
__locale_data._fields_ = [
]
locale_t = __locale_t
ptrdiff_t = c_long
class supported_tag(Structure):
    pass
supported_tag._fields_ = [
    ('type', mifare_tag_type),
    ('friendly_name', STRING),
    ('SAK', uint8_t),
    ('ATS_min_length', uint8_t),
    ('ATS_compare_length', uint8_t),
    ('ATS', uint8_t * 5),
    ('check_tag_on_reader', CFUNCTYPE(c_bool, POINTER(nfc_device), nfc_iso14443a_info)),
]
mifare_tag._fields_ = [
    ('device', POINTER(nfc_device)),
    ('info', nfc_iso14443a_info),
    ('tag_info', POINTER(supported_tag)),
    ('active', c_int),
]
class mifare_classic_tag(Structure):
    pass
class N18mifare_classic_tag4DOT_50E(Structure):
    pass
N18mifare_classic_tag4DOT_50E._fields_ = [
    ('sector_trailer_block_number', int16_t),
    ('sector_access_bits', uint16_t),
    ('block_number', int16_t),
    ('block_access_bits', uint8_t),
]
mifare_classic_tag._fields_ = [
    ('__tag', mifare_tag),
    ('last_authentication_key_type', MifareClassicKeyType),
    ('cached_access_bits', N18mifare_classic_tag4DOT_50E),
]
mifare_desfire_aid._fields_ = [
    ('data', uint8_t * 3),
]

# values for unnamed enumeration
mifare_desfire_key._fields_ = [
    ('data', uint8_t * 24),
    ('type', c_int),
    ('ks1', DES_key_schedule),
    ('ks2', DES_key_schedule),
    ('ks3', DES_key_schedule),
    ('cmac_sk1', uint8_t * 24),
    ('cmac_sk2', uint8_t * 24),
    ('aes_version', uint8_t),
]
class mifare_desfire_tag(Structure):
    pass

# values for unnamed enumeration
mifare_desfire_tag._fields_ = [
    ('__tag', mifare_tag),
    ('last_picc_error', uint8_t),
    ('last_internal_error', uint8_t),
    ('last_pcd_error', uint8_t),
    ('session_key', MifareDESFireKey),
    ('authentication_scheme', c_int),
    ('authenticated_key_no', uint8_t),
    ('ivect', uint8_t * 16),
    ('cmac', uint8_t * 16),
    ('crypto_buffer', POINTER(uint8_t)),
    ('crypto_buffer_size', size_t),
    ('selected_application', uint32_t),
]
mifare_desfire_session_key_new = _libraries['libfreefare.so'].mifare_desfire_session_key_new
mifare_desfire_session_key_new.restype = MifareDESFireKey
mifare_desfire_session_key_new.argtypes = [POINTER(uint8_t), POINTER(uint8_t), MifareDESFireKey]
mifare_desfire_error_lookup = _libraries['libfreefare.so'].mifare_desfire_error_lookup
mifare_desfire_error_lookup.restype = STRING
mifare_desfire_error_lookup.argtypes = [uint8_t]
class mifare_ultralight_tag(Structure):
    pass
mifare_ultralight_tag._fields_ = [
    ('__tag', mifare_tag),
    ('cache', MifareUltralightPage * 51),
    ('cached_pages', uint8_t * 48),
]
pthread_attr_t._fields_ = [
    ('__size', c_char * 56),
    ('__align', c_long),
]
__all__ = ['__uint16_t', '__int16_t', 'nfc_property',
           'CRYPTO_THREADID_get_callback', 'X509_REVOKED',
           'mad_sector_reserved', 'wctomb', 'SSL_CTX', 'UIT_BOOLEAN',
           'ASN1_VISIBLESTRING', 'UI_free', 'u_short',
           'mifare_classic_authenticate', 'mifare_application_alloc',
           '__off64_t', 'obstack_vprintf', 'fsetpos',
           'DES_ede3_cbc_encrypt',
           'MDFT_LINEAR_RECORD_FILE_WITH_BACKUP',
           'mifare_desfire_write_data', 'canonicalize_file_name',
           'nfc_device_get_name', '__fsblkcnt_t', 'ASN1_STRING',
           'uint8_t', 'fpos_t', 'X509', 'CRYPTO_get_dynlock_value',
           'qecvt', 'CRYPTO_set_dynlock_destroy_callback',
           '_ossl_old_des_ede3_cbc_encrypt', '_ossl_old_des_encrypt',
           'CRYPTO_get_id_callback', 'getline', '__realpath_chk',
           'rand_r', 'getpt', '__FILE', 'UI_get0_output_string',
           'DES_ede3_cfb64_encrypt', 'DIST_POINT', 'getloadavg',
           'fopencookie', 'mifare_application_read', 'mad_new',
           'CRYPTO_free_ex_data', 'dh_method', '__suseconds_t',
           '_ossl_old_des_ofb64_encrypt', 'X509_algor_st',
           'CRYPTO_push_info_', 'ocsp_req_ctx_st', 'mbstowcs',
           'pid_t', 'freefare_strerror_r', 'int_fast32_t',
           'uint_fast16_t', 'mifare_application_write',
           'mifare_desfire_authenticate_aes', 'CRYPTO_get_ex_data',
           'va_list', 'uint_least8_t',
           'mifare_desfire_change_file_settings', 'ASN1_IA5STRING',
           '__ptsname_r_chk', 'div', 'int64_t',
           'mifare_desfire_create_application', 'gnu_dev_makedev',
           'fputc_unlocked', 'mad_set_card_publisher_sector',
           'renameat', 'str_nfc_baud_rate', '__uint64_t', 'sk_sort',
           'ecvt', '__va_list_tag', 'buf_mem_st', '__u_long',
           'nfc_initiator_select_passive_target',
           'nfc_device_set_property_bool', 'CRYPTO_set_mem_functions',
           'strtod', '__ctype_get_mb_cur_max', '__vfprintf_chk',
           'N16pthread_rwlock_t4DOT_17E', 'UI_get_result_maxsize',
           'nfc_modulation', 'sk_value', '__clockid_t',
           'mifare_desfire_write_data_ex', 'CRYPTO_mem_ctrl',
           'ECDSA_METHOD', 'CRYPTO_THREADID_hash', 'UI_add_user_data',
           '_ossl_old_des_ks_struct',
           'CRYPTO_set_mem_debug_functions', 'abs', 'N4wait3DOT_5E',
           'id_t', 'ASN1_BIT_STRING', 'sk_shift', '_G_fpos_t',
           'evp_pkey_ctx_st', 'mifare_classic_trailer_block',
           'N4wait3DOT_4E', '_ossl_old_des_read_password',
           'N28mifare_desfire_file_settings4DOT_464DOT_49E',
           'mifare_desfire_key_free', 'DSA_METHOD',
           'CRYPTO_ex_data_new_class', 'fputc',
           'mifare_desfire_clear_record_file', 'DES_encrypt2',
           '_ossl_old_des_ofb_encrypt', 'pthread_key_t',
           '__underflow', 'open_memstream', 'setstate_r', 'SSLeay',
           'getchar', 'CRYPTO_realloc', 'UI_get0_action_string',
           'nrand48_r', '_ossl_old_des_cbc_encrypt',
           'CRYPTO_new_ex_data', 'sk_is_sorted',
           'CRYPTO_set_locked_mem_functions',
           '_ossl_old_des_read_pw_string',
           'iso14443a_locate_historical_bytes', 'UIT_NONE',
           'stack_st_CRYPTO_EX_DATA_FUNCS', 'popen',
           'DES_ecb3_encrypt', 'X509_POLICY_NODE', 'rename',
           'evp_pkey_method_st', '_IO_ferror',
           '_ossl_old_des_string_to_2keys', 'X509_CRL_METHOD',
           'mifare_ultralight_tag', 'nfc_dep_info', 'strtof',
           'uint_fast8_t', 'UI_STRING', 'freefare_strerror',
           'ecdsa_method', 'fcloseall', 'UI_add_input_boolean',
           'mifare_classic_get_data_block_permission', 'realloc',
           'mad_reserved_aid', 'DES_check_key_parity',
           'mifare_desfire_get_key_settings',
           'CRYPTO_get_ex_new_index',
           'N27mifare_desfire_version_info4DOT_45E',
           'UI_add_info_string', '__off_t', 'unlockpt', 'MFC_KEY_A',
           'MFC_KEY_B', 'DES_fcrypt', 'NMT_ISO14443B2CT',
           'mifare_desfire_create_application_3k3des',
           'nfc_iso14443b2sr_info', 'sk_delete', '__vdprintf_chk',
           'NP_FORCE_SPEED_106', 'nfc_target_receive_bytes', 'stdout',
           'fsfilcnt64_t', 'fputs_unlocked', 'x509_store_st',
           'lrand48_r', 'ui_string_st', '_ossl_old_des_cfb64_encrypt',
           'nfc_target_send_bytes', 'clock_t', 'CRYPTO_thread_id',
           'int_least64_t', 'mifare_ultralightc_authenticate',
           'engine_st', 'ftello64', 'CRYPTO_EX_DATA', 'qsort',
           'ferror_unlocked', 'qgcvt', 'AUTHORITY_KEYID_st',
           'sk_push', 'sk_delete_ptr', 'X509_POLICY_LEVEL_st',
           'mifare_desfire_credit', 'uintmax_t',
           'CRYPTO_get_new_dynlockid', 'DES_enc_write', 'CLASSIC_4K',
           'CRYPTO_THREADID', 'evp_pkey_asn1_method_st',
           'mifare_desfire_set_configuration', 'erand48_r',
           'EVP_CIPHER_CTX', '_ossl_old_des_random_seed',
           'bn_gencb_st', 'MifareClassicSectorNumber', 'strtold',
           'RSA_METHOD', 'timer_t', 'ftrylockfile',
           'CRYPTO_THREADID_cmp', 'fmemopen', 'mkostemps', 'strtoq',
           '__fsfilcnt64_t',
           'mifare_classic_get_trailer_block_permission', '_IO_FILE',
           'env_md_ctx_st', 'fprintf', 'nfc_device', 'asn1_string_st',
           'sk_pop', 'ui_st', 'X509_PUBKEY', '__locale_struct',
           '__io_read_fn', '__loff_t', 'ASN1_ITEM_st',
           'nfc_jewel_info', 'off_t', 'mad_set_version',
           'ui_method_st', 'MifareClassicBlockNumber', 'abort',
           'DES_random_key', 'UI_ctrl', 'crypto_ex_data_st',
           'freefare_get_tag_friendly_name', 'strtoll', 'ECDH_METHOD',
           'feof', 'DES_quad_cksum', 'NP_ACTIVATE_FIELD', 'locale_t',
           'str_nfc_modulation_type', '__locale_t', 'clearerr',
           'CRYPTO_EX_dup', 'freefare_free_tags', 'OCSP_RESPID',
           'OPENSSL_BLOCK', 'lrand48',
           'mifare_classic_sector_first_block',
           'mifare_desfire_change_key_settings',
           'UI_method_set_reader', 'mifare_classic_decrement',
           'nfc_list_devices', '_ossl_old_des_options',
           'freefare_get_tag_type', 'UI', '__mode_t', 'UI_new',
           'UI_get_input_flags', 'bsearch', 'ASN1_NULL',
           'mifare_desfire_get_version', 'DESFIRE',
           'stack_st_OPENSSL_BLOCK', 'UI_get_default_method',
           '_IO_free_backup_area', 'unsetenv', 'OPENSSL_issetugid',
           'mrand48_r', 'str_nfc_target', '__pthread_internal_list',
           'CRYPTO_malloc', 'CRYPTO_EX_DATA_FUNCS', 'key_t',
           'random_r', 'freefare_free_tag', 'on_exit', 'mad',
           'valloc', 'nfc_strerror', 'ITIMER_PROF', 'ITIMER_VIRTUAL',
           'NDM_UNDEFINED', 'T_3K3DES', 'mifare_tag', 'mad_set_aid',
           'bn_blinding_st',
           'mifare_desfire_create_cyclic_record_file', '__u_int',
           '__sprintf_chk', 'srand48_r', 'AS_NEW',
           'nfc_initiator_init_secure_element', '__clock_t',
           'DES_crypt', 'UI_dup_error_string', 'CRYPTO_dup_ex_data',
           'UI_method_set_writer', 'MDFT_VALUE_FILE_WITH_BACKUP',
           'DES_ede3_cfb_encrypt', 'UI_UTIL_read_pw_string',
           'strtouq', 'nfc_version', 'nfc_target', 'T_DES',
           'UI_get0_result', 'CRYPTO_malloc_locked',
           'DES_set_key_unchecked', 'nfc_device_set_property_int',
           'mifare_desfire_create_linear_record_file', 'size_t',
           'ASN1_GENERALSTRING',
           'mifare_desfire_create_backup_data_file_iso',
           'CRYPTO_get_ex_data_implementation', '_ossl_old_des_crypt',
           '_ossl_old_des_ede3_cfb64_encrypt', 'CRYPTO_MEM_LEAK_CB',
           'NMT_ISO14443BI', 'X509_NAME', '_IO_ftrylockfile',
           'NP_FORCE_ISO14443_A', 'NP_FORCE_ISO14443_B',
           'N23_ossl_old_des_ks_struct3DOT_1E', 'uint_least16_t',
           '__syscall_slong_t', 'UI_get0_test_string',
           'nfc_initiator_poll_target', 'mifare_ultralight_connect',
           'mkostemps64', 'BN_BLINDING', 'feof_unlocked', '__qaddr_t',
           'mifare_classic_init_value',
           'mifare_desfire_write_record_ex', 'UI_dup_verify_string',
           'CRYPTO_get_locked_mem_ex_functions', 'DES_key_schedule',
           'mifare_desfire_disconnect', 'rewind', 'u_char',
           'fpos64_t', '__asprintf_chk', '__itimer_which_t',
           'cookie_write_function_t', 'perror',
           'CRYPTO_get_lock_name', 'SSL', 'X509_POLICY_NODE_st',
           '__vprintf_chk', 'NP_INFINITE_SELECT', 'AS_LEGACY',
           'sigset_t', 'conf_st', 'gcvt', 'getdelim', 'sk_dup',
           'CRYPTO_set_dynlock_lock_callback', 'mad_card_holder_aid',
           'UI_add_error_string', '__int32_t', 'UI_METHOD',
           'UIT_PROMPT', 'vsprintf', '_ossl_old_des_cfb_encrypt',
           'setstate', 'mifare_ultralight_read', 'snprintf',
           'pthread_spinlock_t', 'flockfile',
           'st_CRYPTO_EX_DATA_IMPL',
           'CRYPTO_get_dynlock_destroy_callback',
           '_ossl_old_des_encrypt3',
           'MDFT_CYCLIC_RECORD_FILE_WITH_BACKUP', 'sk_zero',
           'UI_method_set_flusher', 'fsblkcnt64_t', '__fsword_t',
           '__fd_mask', 'mad_nfcforum_aid',
           'mifare_desfire_write_record',
           'nfc_initiator_list_passive_targets',
           '_ossl_old_des_xcbc_encrypt',
           'mifare_desfire_session_key_new', 'int_fast64_t',
           'initstate_r', 'CRYPTO_get_add_lock_callback',
           '__useconds_t', 'DES_ncbc_encrypt', 'uint_fast32_t',
           'mifare_desfire_create_application_3k3des_iso',
           'nfc_driver', 'CRYPTO_EX_new', 'openssl_item_st',
           '_ossl_old_des_pcbc_encrypt', 'sk_unshift',
           '_ossl_old_des_ede3_ofb64_encrypt', 'sprintf', 'vscanf',
           '_ossl_old_des_enc_read', 'CRYPTO_memcmp', '__fgets_chk',
           'CRYPTO_dbg_set_options', 'BIGNUM', 'iso14443a_crc_append',
           'DES_key_sched', 'mifare_desfire_limited_credit_ex',
           'asprintf', 'nfc_exit', 'UI_create_method',
           '_IO_cookie_io_functions_t', 'free', 'labs',
           '_ossl_old_des_decrypt3', '__gnuc_va_list',
           'CRYPTO_mem_leaks_fp', 'UI_set_result', 'qsort_r',
           'BN_CTX', 'nfc_baud_rate', 'ERR_FNS',
           'UI_set_default_method', 'fseeko', '__uflow',
           'NP_HANDLE_PARITY', '__dev_t', 'DIST_POINT_st',
           '__pthread_list_t', 'nfc_register_driver',
           'OPENSSL_ia32cap_loc', 'pthread_attr_t',
           'UI_add_input_string', 'EVP_MD', 'uint', 'NP_TIMEOUT_ATR',
           '__rlim64_t', 'ino_t', 'strtoll_l', 'bignum_st',
           'mifare_desfire_last_pcd_error', 'nfc_idle',
           'nfc_device_get_connstring', '_shadow_DES_check_key',
           'N28mifare_desfire_file_settings4DOT_464DOT_47E',
           '__getdelim', 'DES_options', 'system', 'ASN1_OCTET_STRING',
           'calloc', '__blksize_t', 'sk_num', '_IO_seekoff',
           'nfc_close', 'ecdh_method', 'DES_cbc_cksum', 'fsblkcnt_t',
           'x509_store_ctx_st', 'mkdtemp', 'strtoull_l',
           'mifare_classic_disconnect', 'UI_construct_prompt',
           'UI_dup_info_string', 'nfc_device_get_supported_baud_rate',
           'bn_mont_ctx_st', 'stderr', '_sys_nerr', 'scanf',
           'OCSP_REQ_CTX', 'mifare_desfire_read_records_ex', 'fclose',
           'DH_METHOD', 'DES_read_password', 'comparison_fn_t',
           'MifareDESFireKey', 'ino64_t', 'tlv_record_length',
           '__asprintf', 'dprintf', 'DES_ede3_ofb64_encrypt',
           '_ossl_old_des_cbc_cksum', 'mkstemp64', 'ecvt_r',
           '__mbstate_t', '__quad_t', 'DES_cfb_encrypt', 'nfc_init',
           'CRYPTO_is_mem_check_on', 'BUF_MEM', 'setbuffer',
           'itimerval', '__u_char', 'CRYPTO_free', '__caddr_t',
           'strtod_l', 'funlockfile', 'mkostemp',
           'nfc_target_receive_bits', 'CRYPTO_add_lock', 'UIT_ERROR',
           '_Exit', 'ULTRALIGHT_C', 'stack_st',
           'mifare_desfire_get_file_ids', 'RAND_METHOD',
           'ERR_load_UI_strings', 'nfc_open', 'UIT_VERIFY', 'fscanf',
           'ASN1_BOOLEAN', 'quad_t', 'X509V3_CTX',
           'mifare_desfire_abort_transaction', 'rsa_st',
           'UI_method_get_prompt_constructor',
           '_ossl_old_des_read_2passwords', 'int16_t',
           'ASN1_UNIVERSALSTRING', 'uint64_t', 'putc_unlocked',
           'nfc_initiator_transceive_bits',
           'CRYPTO_get_dynlock_lock_callback',
           'nfc_initiator_transceive_bytes', '_IO_peekc_locked',
           'N6DES_ks3DOT_0E', 'DH', 'nfc_context',
           'CRYPTO_get_mem_debug_options', 'x509_crl_method_st',
           'RSA', 'UI_method_get_closer', 'vprintf', '__fread_chk',
           '__rlim_t', 'sys_nerr',
           'mifare_desfire_commit_transaction',
           'NP_ACCEPT_MULTIPLE_FRAMES', 'mad_public_key_a', 'nlink_t',
           'secure_getenv', 'UI_dup_input_string', 'fseek',
           'obstack_printf', 'printf',
           'mifare_desfire_create_std_data_file', '__io_seek_fn',
           'UI_string_types', 'ptrdiff_t', 'BIO_dummy', 'ssl_ctx_st',
           '_ossl_old_des_ecb_encrypt', 'UI_get_ex_new_index',
           'mktemp', 'ssize_t', 'ulong', 'nfc_connstring', 'fopen64',
           'freefare_perror', 'is_mifare_ultralightc_on_reader',
           'timespec', 'int8_t', 'mad_write', 'getchar_unlocked',
           'asn1_pctx_st', 'STORE', '_ossl_old_des_random_key',
           'mifare_desfire_create_application_aes_iso',
           'X509_POLICY_CACHE', 'srand48', 'PKCS8_PRIV_KEY_INFO',
           'X509_CRL', '__fsfilcnt_t', 'fgets_unlocked',
           '__obstack_printf_chk', 'suseconds_t',
           'mifare_desfire_connect', 'atoi', 'x509_st', 'fseeko64',
           '__obstack_vprintf_chk', '__uid_t', 'setlinebuf',
           'useconds_t', 'N14pthread_cond_t4DOT_14E',
           'nfc_iso14443b2ct_info', 'mifare_desfire_limited_credit',
           'ENGINE', '__pthread_mutex_s', 'fgetpos', 'T_3DES',
           'mifare_desfire_aes_key_new', 'UI_method_get_reader',
           '__printf_chk', 'a64l', 'mifare_desfire_authenticate',
           'random', '_IO_putc', 'settimeofday', 'NMT_ISO14443A',
           'mifare_desfire_free_mem', '__uint8_t',
           'UI_get_result_minsize', 'mode_t', 'MifareClassicKeyType',
           'strtoull', 'time_t', 'strtol', 'UI_dup_input_boolean',
           'NBR_106', 'timeval', 'stack_st_UI_STRING',
           '_IO_2_1_stdin_', 'mifare_desfire_get_iso_file_ids',
           'nfc_iso14443b_info', 'putw', 'mkstemps', 'EVP_PKEY',
           'timezone', 'fputs', 'NP_AUTO_ISO14443_4',
           'CRYPTO_EX_free', 'strtof_l', 'FIPS_mode',
           '_ossl_old_des_cblock', 'MifareTag',
           'mifare_ultralight_write', 'NAME_CONSTRAINTS_st',
           'freefare_get_tag_uid', 'mifare_desfire_read_data_ex',
           'intptr_t', 'l64a', 'mifare_ultralight_disconnect',
           'UIT_INFO', 'int_fast8_t', 'MadAid', 'env_md_st',
           'N28mifare_desfire_file_settings4DOT_464DOT_48E',
           'erand48', 'tlv_encode', 'ptsname_r',
           'ASN1_PRINTABLESTRING', 'mifare_desfire_3k3des_key_new',
           'ldiv_t', 'N18mifare_classic_tag4DOT_50E', 'fileno',
           'ASN1_GENERALIZEDTIME', 'mifare_classic_sector_last_block',
           'ERR_load_CRYPTO_strings', 'UI_get0_user_data', 'vfscanf',
           'CRYPTO_lock', 'remove', '__codecvt_partial',
           'nfc_device_get_information_about', 'NDM_ACTIVE',
           'NBR_212', 'mifare_desfire_key_get_version', 'fd_mask',
           'MifareDESFireDF', 'blkcnt_t',
           'mifare_desfire_3k3des_key_new_with_version', '__fsid_t',
           'cookie_close_function_t',
           'mifare_desfire_delete_application', 'mbtowc', 'FILE',
           '__ssize_t', 'CRYPTO_set_locking_callback',
           'mifare_desfire_select_application',
           'pkcs8_priv_key_info_st', 'nfc_device_get_last_error',
           'mifare_desfire_debit_ex', 'OPENSSL_STRING', 'grantpt',
           'OPENSSL_ITEM', 'X509_POLICY_CACHE_st', 'quick_exit',
           'UI_set_method', 'mad_defect_aid', 'BN_GENCB',
           'mifare_desfire_create_linear_record_file_iso', 'lcong48',
           'jrand48', 'mifare_desfire_get_value_ex', '__sigset_t',
           'nfc_initiator_target_is_present', 'X509_STORE',
           'OPENSSL_CSTRING', 'strtoul', 'CRYPTO_set_ex_data',
           'UI_method_get_flusher', 'posix_memalign', '_IO_padn',
           'X509_STORE_CTX', 'UI_set_ex_data', 'vdprintf',
           'mifare_desfire_create_application_aes', 'setitimer',
           '_sys_errlist', 'ASN1_TIME', 'nfc_dep_mode',
           'DES_read_2passwords', '__overflow',
           'MDFT_BACKUP_DATA_FILE', 'mifare_desfire_aid', 'sk_insert',
           'int_least32_t', 'UI_get_method', 'UI_destroy_method',
           'strtol_l', 'mifare_classic_increment',
           'mifare_desfire_free_application_ids', '__blkcnt64_t',
           'P_PID', 'tmpnam_r', 'x509_revoked_st', 'futimesat',
           'CRYPTO_num_locks', 'nfc_modulation_type', '_IO_FILE_plus',
           'mad_get_aid', 'lcong48_r', 'ushort', '__fdelt_chk',
           '__blkcnt_t', 'clockid_t', 'fwrite', 'BN_RECP_CTX',
           'OpenSSLDie', 'mifare_desfire_change_key', 'uint16_t',
           'ISSUING_DIST_POINT', 'ASN1_BMPSTRING', 'srandom',
           '__vsnprintf_chk', '_IO_flockfile', 'CRYPTO_dbg_free',
           'fflush_unlocked', 'vasprintf',
           'mifare_desfire_key_set_version', 'int32_t', 'fsetpos64',
           'N11__mbstate_t4DOT_22E', 'CRYPTO_realloc_clean',
           'crypto_threadid_st', 'nfc_initiator_init',
           'DES_ecb_encrypt', 'tmpfile64', 'getc_unlocked',
           'DES_string_to_key', 'qecvt_r', '__intptr_t',
           'UI_new_method', 'nfc_felica_info',
           'CRYPTO_get_mem_functions', 'mad_free_aid', 'DES_decrypt3',
           'UI_get_ex_data', '__compar_d_fn_t',
           'MifareUltralightPage', 'ssl_st', 'UI_UTIL_read_pw',
           'CRYPTO_THREADID_set_callback', 'gnu_dev_major',
           'UI_method_set_prompt_constructor', 'putc',
           '_ossl_old_des_set_key', 'CRYPTO_get_locked_mem_functions',
           'DSA', '_ossl_old_des_key_sched',
           'mifare_desfire_create_value_file', 'fcvt_r', 'mad_free',
           'seed48_r', 'fread', 'dh_st', '__int64_t', 'ftello',
           'UI_method_get_writer', '__ino64_t',
           'CRYPTO_set_dynlock_create_callback', 'adjtime',
           'stack_st_void', 'NBR_424', 'ASN1_UTCTIME',
           'mifare_classic_read', '_STACK', 'DES_xcbc_encrypt',
           'u_int8_t', 'NAME_CONSTRAINTS', 'T_AES', 'drand48',
           'crypto_ex_data_func_st', 'pselect',
           '_ossl_old_des_enc_write', 'jrand48_r',
           'mifare_classic_transfer',
           'mifare_desfire_get_key_version', 'fgetc', '__dprintf_chk',
           'u_long', 'nfc_initiator_select_dep_target',
           'DES_cbc_encrypt', 'qfcvt', 'EVP_CIPHER',
           'CRYPTO_destroy_dynlockid', 'ocsp_response_st', 'clearenv',
           '_ossl_old_des_set_odd_parity',
           'mifare_desfire_aid_new_with_mad_aid', 'NMT_ISO14443B',
           'UI_OpenSSL', 'cfree', 'srand', 'EVP_PKEY_METHOD',
           'lutimes', 'wcstombs', 'nfc_abort_command', 'int_fast16_t',
           'mifare_classic_connect', 'ASN1_INTEGER', 'pthread_t',
           'mifare_desfire_3des_key_new_with_version',
           'DES_set_odd_parity', 'drand48_data', 'blksize_t',
           'freefare_tag_new', 'DES_set_key', 'DES_ofb_encrypt',
           'qfcvt_r', '_ossl_old_des_key_schedule', 'DES_is_weak_key',
           'nfc_strerror_r', 'NMT_JEWEL', 'v3_ext_ctx',
           'MifareClassicBlock', '__fsblkcnt64_t', 'NBR_847',
           'nfc_initiator_deselect_target', 'fsfilcnt_t', 'getw',
           'vsnprintf', 'UI_method_set_opener', 'ldiv',
           '__snprintf_chk', '__io_write_fn', 'caddr_t', '__ino_t',
           'mifare_desfire_get_df_names', 'CRYPTO_dbg_get_options',
           '_IO_lock_t', 'setbuf', '_IO_2_1_stdout_', 'u_quad_t',
           'stdin', 'NP_ACTIVATE_CRYPTO1', 'idtype_t',
           'nfc_device_get_supported_modulation', 'sk_set',
           'uint_fast64_t', 'mifare_tag_type',
           'cookie_seek_function_t', 'drand48_r',
           'MDFT_STANDARD_DATA_FILE', 'DES_pcbc_encrypt', 'nrand48',
           'tlv_decode', 'sk_find_ex', 'mifare_desfire_credit_ex',
           'uint32_t', 'nfc_iso14443a_info',
           'mifare_desfire_create_std_data_file_iso',
           'ocsp_responder_id_st', 'nfc_target_info', 'rand_meth_st',
           'getc', 'mifare_application_free',
           'CRYPTO_remove_all_info', 'uid_t', 'CRYPTO_dynlock',
           '__mbstowcs_chk', 'mifare_desfire_aid_new',
           'CRYPTO_EX_DATA_IMPL', '_IO_marker', 'mkstemps64',
           'select', 'mifare_desfire_3des_key_new',
           'mifare_desfire_get_value', '__timer_t', 'CONF',
           'mifare_desfire_des_key_new', '__wcstombs_chk', 'fflush',
           'random_data', 'CRYPTO_get_locking_callback', 'nfc_perror',
           'atoll', 'DES_string_to_2keys', 'NP_HANDLE_CRC',
           '__uint32_t', 'mifare_desfire_last_picc_error',
           '__compar_fn_t', '__fprintf_chk', 'P_PGID', 'DES_cblock',
           'ptsname', 'nfc_iso14443bi_info', 'rsa_meth_st',
           'fgetpos64', 'NP_TIMEOUT_COMMAND',
           'mifare_desfire_get_application_ids', 'X509_crl_st',
           'tmpnam', 'ASN1_PCTX', 'vfprintf', 'UI_add_verify_string',
           'ASN1_UTF8STRING', 'store_method_st', '__u_short',
           'loff_t', 'mifare_desfire_read_records', 'off64_t',
           'CRYPTO_set_id_callback', 'nfc_target_send_bits',
           '_IO_sgetn', 'NDM_PASSIVE', 'srandom_r',
           '__fread_unlocked_chk',
           'mifare_desfire_des_key_new_with_version',
           'ISSUING_DIST_POINT_st', 'u_int32_t', 'putchar',
           'bignum_ctx', 'mifare_desfire_file_types', 'gnu_dev_minor',
           'register_t', 'mkstemp', 'DES_cfb64_encrypt',
           'CRYPTO_pop_info', 'ctermid', 'CRYPTO_THREADID_cpy',
           'CRYPTO_strdup', '__fgets_unlocked_chk', '_G_fpos64_t',
           'futimes', 'mifare_classic_tag',
           'mifare_desfire_error_lookup', 'mblen', '_IO_vfprintf',
           'freopen', '_ossl_old_des_is_weak_key', 'bn_recp_ctx_st',
           'fread_unlocked', 'CRYPTO_dbg_malloc', 'st_ERR_FNS',
           'tempnam', 'tmpfile', '__syscall_ulong_t',
           'mifare_classic_format_sector', 'fd_set', 'rpmatch',
           '__io_close_fn', 'sk_pop_free', 'pclose',
           'DES_ofb64_encrypt', '__fdelt_warn', 'llabs', 'seed48',
           'OCSP_RESPONSE', 'mifare_classic_sector_block_count',
           'evp_cipher_ctx_st', '__itimer_which', '__codecvt_ok',
           'fgets', 'fwrite_unlocked', 'X509_ALGOR',
           'mad_get_version', '__id_t', 'nfc_mode',
           'UI_method_set_closer', 'const_DES_cblock', '_IO_feof',
           'dsa_st', 'UI_process', 'gid_t',
           'CRYPTO_set_ex_data_implementation', 'nfc_target_init',
           'mifare_desfire_version_info',
           'mifare_desfire_create_cyclic_record_file_iso',
           'AUTHORITY_KEYID', 'ULTRALIGHT',
           'mifare_classic_nfcforum_public_key_a', 'ftell',
           'OPENSSL_init', 'exit', '__time_t', 'u_int16_t',
           'mifare_desfire_read_data', 'iso14443a_crc',
           'CRYPTO_free_locked', 'int_least16_t', 'EVP_PKEY_CTX',
           'N_TARGET', 'OPENSSL_isservice', 'mad_aid',
           'mad_get_card_publisher_sector', 'UI_get_string_type',
           'getitimer', 'sk_new_null', 'DES_enc_read',
           'CRYPTO_remalloc', 'nfc_free', 'DES_encrypt3',
           'CRYPTO_set_add_lock_callback', 'DES_encrypt1',
           '__nlink_t', '__codecvt_result', '__vasprintf_chk',
           'mifare_desfire_file_settings', '_shadow_DES_rw_mode',
           'SSLeay_version', 'X509_POLICY_TREE_st', 'getsubopt',
           'putchar_unlocked', 'CRYPTO_set_mem_ex_functions',
           'mifare_desfire_set_default_key', 'tlv_append',
           'mifare_application_find', 'X509_pubkey_st', 'rand',
           'puts', '_ossl_old_des_fcrypt', 'STORE_METHOD',
           'OPENSSL_cleanse', 'CRYPTO_mem_leaks', 'malloc',
           'UI_method_get_opener', 'sys_errlist', 'BN_MONT_CTX',
           'mifare_desfire_get_file_settings', 'clearerr_unlocked',
           'obstack', 'NP_TIMEOUT_COM', 'fcvt',
           'CRYPTO_dynlock_value', 'realpath', 'aligned_alloc',
           'UI_get0_result_string', '__vsprintf_chk',
           'CRYPTO_cleanup_all_ex_data', 'ferror', 'uint_least64_t',
           'mkostemp64', 'vsscanf', '_ossl_old_des_quad_cksum',
           'mad_not_applicable_aid', 'CRYPTO_mem_leaks_cb', 'dev_t',
           'lldiv', 'NP_ACCEPT_INVALID_FRAMES', 'fopen', 'sk_free',
           'CRYPTO_set_mem_debug_options', '__gid_t',
           'mifare_classic_block_sector', 'CRYPTO_dbg_realloc',
           'putenv', 'fdopen', '_ossl_old_des_encrypt2',
           'mifare_desfire_authenticate_iso', 'u_int64_t',
           'mifare_desfire_aes_key_new_with_version', '__daddr_t',
           'MifareDESFireAID', '_IO_cookie_file', '__sig_atomic_t',
           'CRYPTO_get_mem_ex_functions', 'uintptr_t', 'mrand48',
           '_ossl_old_crypt', 'mifare_desfire_key',
           'CRYPTO_THREADID_set_numeric', 'freefare_get_tags',
           'mifare_classic_restore', '_ossl_old_des_read_pw', 'u_int',
           'getenv', 'ASN1_T61STRING', 'evp_pkey_st',
           'CRYPTO_set_locked_mem_ex_functions', '_IO_funlockfile',
           'atol', 'N27mifare_desfire_version_info4DOT_44E',
           'N28mifare_desfire_file_settings4DOT_46E',
           'mifare_classic_read_value', 'atof', 'uint_least32_t',
           'ASN1_ITEM', 'ASN1_ENUMERATED', '__timezone_ptr_t',
           '_IO_getc', 'mifare_desfire_delete_file',
           'mifare_desfire_tag', 'CRYPTO_THREADID_set_pointer',
           'DES_set_key_checked', 'intmax_t', 'cuserid',
           'pthread_once_t', '_ossl_old_des_string_to_key',
           '_IO_vfscanf', 'cookie_read_function_t', 'ungetc',
           'CRYPTO_THREADID_current', 'blkcnt64_t',
           'X509_POLICY_LEVEL', 'sscanf', 'fileno_unlocked',
           'EVP_PKEY_ASN1_METHOD', 'NMT_FELICA', '_IO_2_1_stderr_',
           '_ossl_old_des_ecb3_encrypt', 'ITIMER_REAL',
           'NBR_UNDEFINED', 'DES_ks', 'mad_read', 'initstate',
           'freopen64', 'dsa_method', 'DES_ede3_cbcm_encrypt',
           'mifare_desfire_create_backup_data_file', 'bio_st',
           '_IO_seekpos', 'sk_set_cmp_func', 'mifare_classic_write',
           'NMT_ISO14443B2SR', 'posix_openpt', 'CLASSIC_1K',
           'lldiv_t', 'NMT_DEP', 'FIPS_mode_set',
           'mifare_desfire_get_card_uid', 'strtold_l',
           'mifare_desfire_format_picc', 'daddr_t', 'EVP_MD_CTX',
           'setenv', '__u_quad_t', 'Mad', 'N_INITIATOR',
           'nfc_initiator_transceive_bytes_timed', 'evp_cipher_st',
           'cookie_io_functions_t', 'X509_name_st', '__int8_t',
           'supported_tag', '__key_t', 'mifare_desfire_debit',
           'fsid_t', '__pid_t', '_ossl_old_des_ncbc_encrypt',
           '_ossl_096_des_random_seed', '_IO_jump_t',
           'stack_st_OPENSSL_STRING', '__codecvt_error',
           'mifare_desfire_set_ats', '__wctomb_chk', '__locale_data',
           'X509_POLICY_TREE', 'CRYPTO_get_dynlock_create_callback',
           'store_st', 'mifare_desfire_aid_get_aid',
           'mifare_desfire_df', 'gets', 'sk_new', 'strtoul_l',
           'utimes', 'nfc_initiator_transceive_bits_timed',
           'NP_EASY_FRAMING', '__socklen_t',
           'mifare_desfire_create_application_iso', 'gettimeofday',
           'CRYPTO_get_new_lockid', 'P_ALL',
           'CRYPTO_get_mem_debug_functions', 'setvbuf',
           '__codecvt_noconv', 'fgetc_unlocked',
           'MifareUltralightPageNumber',
           'nfc_initiator_poll_dep_target', 'MifareClassicKey',
           'int_least8_t', 'div_t', 'sk_find']
