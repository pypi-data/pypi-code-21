import hashlib
from .iterx import SepIter

from . import FormatParseError

from .encoding_base import DEFAULTENCODING, FALLBACKENCODING

defaultencoding = DEFAULTENCODING
ILLEGAL_ID_CHARS = set('<>[]*;=,')


def is_valid_char (c):
    return 32 < ord(c) < 127 and c not in ILLEGAL_ID_CHARS


def is_valid_id (identifier):
    return all(32 < ord(c) < 127 and c not in ILLEGAL_ID_CHARS
               for c in identifier)


def assert_valid_ids (identifiers):
    for title in identifiers:
        if not is_valid_id(title):
            raise FormatParseError(
                'Invalid reference genome file {token}: Some sequence names contain characters that are not allowed in MiModD.',
                token='', # to be filled in by caller
                help='non-ASCII, whitespace, non-printable characters and any of the characters "{0}" are disallowed in sequence names.\nYou may manually clean up the file or run "python3 -m MiModD.sanitize" to replace invalid characters automatically.'
                     .format(''.join(sorted(ILLEGAL_ID_CHARS)))
                )
    

def sanitize_id (identifier_bytes, replacement_str = None):
    try:
        identifier = identifier_bytes.decode(DEFAULTENCODING)
    except UnicodeDecodeError:
        identifier = identifier_bytes.decode(FALLBACKENCODING)
    amended_chars = []
    for c in identifier:
        if is_valid_char(c):
            amended_chars.append(c)
        elif replacement_str:
            # a fixed replacement string has been specified
            # => use it to replace any invalid character
            amended_chars.append(replacement_str)
        else:
            # use the capitalized percent encoding of the UTF-8
            # representation of the invalid character
            utf_bytes=c.encode('utf-8')
            for byte_val in utf_bytes:
                amended_chars.append('%')
                amended_chars.append(hex(byte_val)[2:].upper().zfill(2))
    return ''.join(amended_chars)


class FastaReader (SepIter):
    RECORD_SEP = '>'
    
    def __init__ (self, iterable):
        self.super = super(FastaReader, self) # set this for fast access by next()
        self.super.__init__(iterable, self.RECORD_SEP)
        
    def __iter__ (self):
        first_header, first_seq_iter = next(self.i)
        if first_header is None:
            raise FormatParseError(
                'Input does not seem to be in fasta format '
                '(expected ">" at start of file).'
                )
        yield first_header, first_seq_iter
        for record in self.i:
            yield record
    
    def identifiers (self):
        for header, seq_iter in self:
            yield header
            
    def sequences (self):
        for header, seq_iter in self:
            yield (header, ''.join(s.strip().replace(' ', '') for s in seq_iter))

    def md5sums (self):
        for header, seq_iter in self:
            md5 = hashlib.md5()
            for seqline in seq_iter:
                md5.update(seqline.strip().replace(' ', '').upper().encode())
            yield (header, md5.hexdigest())


def get_fasta_info (ifile, calculate_md5sums=True):
    dna_strings = 'ACGTNKSYMWRBDHV'
    dna_strings += dna_strings.lower()
    IUPAC_DNA_codes = set(dna_strings)

    seqinfo = []
    with open(ifile, 'r', encoding=FALLBACKENCODING) as ifo:
        for header, seq_iter in FastaReader(ifo):
            seqlen = 0
            if calculate_md5sums:
                md5 = hashlib.md5()
                for seqline in seq_iter:
                    seqline = seqline.strip().replace(' ', '').upper()
                    if any(c not in IUPAC_DNA_codes for c in seqline):
                        raise FormatParseError(
                            'Invalid nucleotide code in sequence ' + header
                            )
                    seqlen += len(seqline)
                    if calculate_md5sums:
                        md5.update(seqline.encode())
            if seqlen == 0:
                raise FormatParseError(
                    'No nucleotide information found for sequence ' + header
                    )
            seqinfo.append(
                {'SN': header,
                 'LN': seqlen,
                 'M5': md5.hexdigest() if calculate_md5sums else None}
                )
    if not seqinfo:
        raise FormatParseError('Empty input.')
    return seqinfo
