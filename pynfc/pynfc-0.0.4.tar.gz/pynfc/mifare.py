from ctypes import *

STRING = c_char_p
_libraries = {}
_libraries['libnfc.so'] = CDLL('libnfc.so')


MC_STORE = 194
MC_INCREMENT = 193
MC_DECREMENT = 192
MC_TRANSFER = 176
MC_WRITE = 160
MC_READ = 48
MC_AUTH_B = 97
NBR_847 = 4
NBR_212 = 2
NBR_106 = 1
NBR_UNDEFINED = 0
NDM_PASSIVE = 1
NP_TIMEOUT_COM = 2
NP_TIMEOUT_ATR = 1
NP_HANDLE_PARITY = 4
NP_HANDLE_CRC = 3
NP_TIMEOUT_COMMAND = 0
MC_AUTH_A = 96
NP_FORCE_SPEED_106 = 14
NMT_FELICA = 7
NP_FORCE_ISO14443_B = 13
NP_FORCE_ISO14443_A = 12
NP_EASY_FRAMING = 11
NP_ACCEPT_MULTIPLE_FRAMES = 9
NP_ACCEPT_INVALID_FRAMES = 8
NP_ACTIVATE_CRYPTO1 = 6
NMT_ISO14443BI = 4
NBR_424 = 3
__codecvt_noconv = 3
__codecvt_error = 2
__codecvt_partial = 1
__codecvt_ok = 0
NDM_UNDEFINED = 0
N_INITIATOR = 1
N_TARGET = 0
NDM_ACTIVE = 2
NMT_DEP = 8
NMT_ISO14443B2CT = 6
NMT_ISO14443B2SR = 5
NMT_ISO14443B = 3
NMT_JEWEL = 2
NMT_ISO14443A = 1
NP_AUTO_ISO14443_4 = 10
NP_INFINITE_SELECT = 7
NP_ACTIVATE_FIELD = 5
class _G_fpos_t(Structure):
    pass
__off_t = c_long
class __mbstate_t(Structure):
    pass
class N11__mbstate_t3DOT_2E(Union):
    pass
N11__mbstate_t3DOT_2E._fields_ = [
    ('__wch', c_uint),
    ('__wchb', c_char * 4),
]
__mbstate_t._fields_ = [
    ('__count', c_int),
    ('__value', N11__mbstate_t3DOT_2E),
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
nfc_context._fields_ = [
]
class nfc_device(Structure):
    pass
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
int8_t = c_int8
int16_t = c_int16
int32_t = c_int32
int64_t = c_int64
uint16_t = c_uint16
uint32_t = c_uint32
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
__time_t = c_long
__useconds_t = c_uint
__suseconds_t = c_long
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
__syscall_slong_t = c_long
__syscall_ulong_t = c_ulong
__loff_t = __off64_t
__qaddr_t = POINTER(__quad_t)
__caddr_t = STRING
__intptr_t = c_long
__socklen_t = c_uint
ptrdiff_t = c_long

# values for enumeration 'mifare_cmd'
mifare_cmd = c_int # enum
class mifare_param_auth(Structure):
    pass
mifare_param_auth._fields_ = [
    ('abtKey', uint8_t * 6),
    ('abtAuthUid', uint8_t * 4),
]
class mifare_param_data(Structure):
    pass
mifare_param_data._fields_ = [
    ('abtData', uint8_t * 16),
]
class mifare_param_value(Structure):
    pass
mifare_param_value._fields_ = [
    ('abtValue', uint8_t * 4),
]
class mifare_classic_block_manufacturer(Structure):
    pass
mifare_classic_block_manufacturer._fields_ = [
    ('abtUID', uint8_t * 4),
    ('btBCC', uint8_t),
    ('btSAK', uint8_t),
    ('abtATQA', uint8_t * 2),
    ('abtManufacturer', uint8_t * 8),
]
class mifare_classic_block_data(Structure):
    pass
mifare_classic_block_data._fields_ = [
    ('abtData', uint8_t * 16),
]
class mifare_classic_block_trailer(Structure):
    pass
mifare_classic_block_trailer._fields_ = [
    ('abtKeyA', uint8_t * 6),
    ('abtAccessBits', uint8_t * 4),
    ('abtKeyB', uint8_t * 6),
]
class mifare_classic_tag(Structure):
    pass
class mifare_classic_block(Union):
    pass
mifare_classic_block._fields_ = [
    ('mbm', mifare_classic_block_manufacturer),
    ('mbd', mifare_classic_block_data),
    ('mbt', mifare_classic_block_trailer),
]
mifare_classic_tag._fields_ = [
    ('amb', mifare_classic_block * 256),
]
class mifareul_block_manufacturer(Structure):
    pass
mifareul_block_manufacturer._fields_ = [
    ('sn0', uint8_t * 3),
    ('btBCC0', uint8_t),
    ('sn1', uint8_t * 4),
    ('btBCC1', uint8_t),
    ('internal', uint8_t),
    ('lock', uint8_t * 2),
    ('otp', uint8_t * 4),
]
class mifareul_block_data(Structure):
    pass
mifareul_block_data._fields_ = [
    ('abtData', uint8_t * 16),
]
class mifareul_tag(Structure):
    pass
class mifareul_block(Union):
    pass
mifareul_block._fields_ = [
    ('mbm', mifareul_block_manufacturer),
    ('mbd', mifareul_block_data),
]
mifareul_tag._fields_ = [
    ('amb', mifareul_block * 4),
]
__all__ = ['__uint16_t', 'fseek', 'obstack_vprintf', 'nfc_property',
           '__printf_chk', '_IO_putc', 'nfc_target', 'int_fast32_t',
           'putchar_unlocked', 'FILE', '__off64_t', 'size_t',
           '__int16_t', 'fflush', 'MC_AUTH_A', 'MC_AUTH_B', '__key_t',
           'NP_HANDLE_CRC', '__uint32_t', 'NBR_106', 'open_memstream',
           'mifare_classic_block', 'uint8_t', 'fpos_t', 'MC_WRITE',
           'fwrite', 'NMT_ISO14443BI', 'fgetpos64',
           '_IO_ftrylockfile', 'NP_FORCE_ISO14443_A',
           'NP_FORCE_ISO14443_B', 'uint_least16_t', 'fputs',
           'NP_TIMEOUT_COMMAND', 'NP_AUTO_ISO14443_4',
           '__fread_unlocked_chk', 'tmpnam', '__ino64_t',
           'feof_unlocked', '__qaddr_t', 'getline', '_IO_padn',
           '__loff_t', 'intptr_t', 'off64_t', '__FILE',
           '__vprintf_chk', 'fclose', '_IO_sgetn', 'rewind',
           'NDM_PASSIVE', 'cookie_seek_function_t', 'obstack_printf',
           'sprintf', 'fpos64_t', '__asprintf_chk', 'putchar',
           'cookie_write_function_t', '__u_quad_t', '__time_t',
           'MC_DECREMENT', '__suseconds_t', 'fileno',
           'NP_INFINITE_SELECT', 'gets', 'perror', 'renameat',
           '__fgets_unlocked_chk', '_G_fpos64_t',
           'mifare_classic_tag', 'freopen64', 'remove', '_G_fpos_t',
           'uint_fast16_t', '_IO_jump_t', 'NDM_ACTIVE', 'NBR_212',
           'uint_least8_t', 'stderr', '__nlink_t', '__dprintf_chk',
           'int_fast64_t', 'ftrylockfile', 'fputc_unlocked',
           '__fsid_t', 'cookie_close_function_t', 'tempnam',
           'tmpfile', 'vsscanf', 'tmpfile64', '__ssize_t',
           '__io_close_fn', '__va_list_tag', 'pclose',
           'ferror_unlocked', '__fsword_t', 'vsnprintf', 'getdelim',
           '__fprintf_chk', 'intmax_t', 'int16_t', 'uintmax_t',
           '__codecvt_ok', 'fgets', 'ctermid', 'nfc_modulation',
           'cookie_io_functions_t', '__clockid_t', '_IO_feof', 'puts',
           'getchar_unlocked', 'vasprintf', 'uint_fast32_t',
           'fgetc_unlocked', 'nfc_driver', 'fgetpos', '__timer_t',
           '__int32_t', 'fsetpos', 'ftell', '_IO_vfprintf',
           'mifare_param_auth', 'MC_TRANSFER', 'vscanf',
           '__syscall_ulong_t', 'vdprintf', 'int_least16_t',
           '__codecvt_partial', 'N_TARGET', '__fgets_chk',
           'nfc_dep_mode', '__vfprintf_chk', 'freopen', '__overflow',
           'fputc', 'asprintf', 'ferror', '_IO_cookie_io_functions_t',
           'fwrite_unlocked', 'nfc_iso14443b2sr_info',
           '__codecvt_result', '__underflow', 'nfc_dep_info',
           'fcloseall', 'fsetpos64', '__syscall_slong_t', 'printf',
           '__blkcnt64_t', '__u_long', 'nfc_baud_rate', 'sys_nerr',
           'fseeko', '__uflow', 'NP_HANDLE_PARITY', '_IO_FILE_plus',
           'mifareul_block_manufacturer', 'setvbuf', 'popen',
           '__blkcnt_t', 'sys_errlist', '_IO_2_1_stdin_',
           'getc_unlocked', '_IO_ferror', 'ptrdiff_t',
           '__gnuc_va_list', 'NP_TIMEOUT_ATR', '__rlim64_t',
           'uint16_t', 'nfc_iso14443b_info', 'NP_TIMEOUT_COM',
           '__vsnprintf_chk', 'rename', '_IO_flockfile', '__dev_t',
           'fflush_unlocked', 'mifare_param_value', 'int32_t',
           'uint_least64_t', '__blksize_t', '__uint64_t', 'MC_STORE',
           '_IO_seekoff', '__off_t', 'fmemopen',
           'NP_ACCEPT_INVALID_FRAMES', 'fopen', '__intptr_t',
           'NMT_ISO14443B2CT', 'getchar', 'nfc_felica_info', 'putw',
           'snprintf', 'NP_FORCE_SPEED_106', '_sys_nerr', 'fdopen',
           'clearerr_unlocked', 'scanf', 'N11__mbstate_t3DOT_2E',
           'fputs_unlocked', 'mifare_classic_block_trailer',
           'nfc_context', '__daddr_t', 'tmpnam_r', '_IO_cookie_file',
           '__caddr_t', '__asprintf', 'uint_least32_t',
           'int_least64_t', 'fseeko64', '__mbstate_t', 'uintptr_t',
           'ftello64', 'putc', '__uint8_t', 'setbuffer',
           '__io_seek_fn', 'ftello', '__u_char', 'setlinebuf',
           '__fsblkcnt64_t', '__socklen_t', 'int8_t',
           '__obstack_printf_chk', 'funlockfile', 'int_fast8_t',
           '_IO_funlockfile', 'NBR_424', '_sys_errlist',
           'nfc_modulation_type', 'nfc_iso14443bi_info', 'dprintf',
           '__vdprintf_chk', 'fopencookie', '__vasprintf_chk',
           '_IO_getc', 'fscanf', 'NMT_ISO14443B2SR', 'fgetc',
           'uint_fast64_t', 'mifareul_tag', 'cuserid',
           'mifare_classic_block_data', '__fsfilcnt64_t', 'va_list',
           '_IO_FILE', '_IO_vfscanf', 'cookie_read_function_t',
           'ungetc', 'nfc_device', 'uint64_t', 'vsprintf',
           'putc_unlocked', '__gid_t', '__io_read_fn',
           'NMT_ISO14443A', 'NMT_ISO14443B', '_IO_peekc_locked',
           'sscanf', 'fileno_unlocked', 'stdout', 'NMT_FELICA',
           '_IO_2_1_stderr_', 'fread', 'nfc_jewel_info',
           'NBR_UNDEFINED', 'off_t', '__fsblkcnt_t', 'fprintf',
           '__getdelim', 'int64_t', 'int_fast16_t', 'vprintf',
           '__fread_chk', '_IO_seekpos', 'feof',
           'mifareul_block_data', 'NP_ACTIVATE_FIELD', 'NBR_847',
           'NP_ACCEPT_MULTIPLE_FRAMES', 'MC_INCREMENT', '__rlim_t',
           'clearerr', 'NMT_DEP', 'ssize_t', 'getc', '_IO_marker',
           'NMT_JEWEL', '__u_short',
           'mifare_classic_block_manufacturer', 'N_INITIATOR',
           '__mode_t', 'nfc_mode', 'vfscanf', 'int_least32_t',
           '__id_t', 'getw', 'flockfile', 'fread_unlocked', '__pid_t',
           'MC_READ', 'uint32_t', '__snprintf_chk',
           '_IO_free_backup_area', 'nfc_connstring',
           '__codecvt_error', 'fopen64', '__io_write_fn',
           '__useconds_t', '__ino_t', '__vsprintf_chk', '_IO_lock_t',
           'setbuf', '_IO_2_1_stdout_', 'obstack',
           'mifare_param_data', 'NP_ACTIVATE_CRYPTO1', 'mifare_cmd',
           'NDM_UNDEFINED', 'mifareul_block', 'NP_EASY_FRAMING',
           '__fsfilcnt_t', 'stdin', 'fgets_unlocked', '__u_int',
           '__sprintf_chk', '__quad_t', '__int64_t', 'uint_fast8_t',
           '__codecvt_noconv', 'nfc_iso14443a_info', '__clock_t',
           '__obstack_vprintf_chk', '__uid_t', 'nfc_target_info',
           '__int8_t', 'int_least8_t', 'nfc_iso14443b2ct_info',
           'vfprintf']
