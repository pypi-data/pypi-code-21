import sys, os
from . import fasta


def chunkseq (seq, length):
    return (seq[0+i:length+i] for i in range(0, len(seq), length))


def sanitize_fasta (ifile, ofile = None,
                    replace_with = None, truncate_at = None, block_width = 80):    
    with open(ifile, 'r', encoding=fasta.defaultencoding) as ifo:
        try:
            if ofile:
                ofo = open(ofile, 'w', encoding='ascii')
                # only ascii chars will be left after sanitizing
            else:
                ofo = sys.stdout
            for identifier, seq in fasta.FastaReader(ifo).sequences():
                if truncate_at:
                    index = identifier.find(truncate_at)
                    if index == -1:
                        index = None
                    identifier = identifier[:index]
                # write sanitized identifier line
                ofo.write('>')
                ofo.write(fasta.sanitize_id(
                    identifier.encode(fasta.defaultencoding),
                    replace_with)
                          )
                ofo.write('\n')
                # write sanitized sequence block
                for subseq in chunkseq(seq, block_width):
                    ofo.write(subseq)
                    ofo.write('\n')
        finally:
            if ofo is not sys.stdout:
                try:
                    ofo.close()
                except:
                    pass


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(usage = argparse.SUPPRESS,
                                     formatter_class = argparse.RawDescriptionHelpFormatter,
                                     description = """

Sanitize file formats to ensure compatibility with MiModD.

Currently, works on fasta files only replacing illegal characters
in sequence titles and ensuring uniform wrapping of all sequence lines.
""")
    parser.add_argument('ifile', metavar='input file', help='the file the contents of which should be sanitized')
    parser.add_argument('-o', '--ofile', metavar='OFILE', default=argparse.SUPPRESS, help='redirect the output to the specified file (default: stdout)')
    parser.add_argument('-r', '--replace-with', metavar='STRING', default=argparse.SUPPRESS, help='use this string to replace any invalid character in any sequence title (default: replace invalid characters with their hexadecimal percent encoding)')
    parser.add_argument('-t', '--truncate-at', metavar='STRING', default=argparse.SUPPRESS, help='truncate sequence titles at the first occurence of the given string (invalid characters in the remaining part of the title will still get replaced)')
    parser.add_argument('-b', '--block-width', metavar='WIDTH', type=int, default=argparse.SUPPRESS, help='wrap each sequence to the specified number of nucleotides per line (default: 80 bases per line)')
    args = vars(parser.parse_args())
    if 'replace_with' in args and \
       any(not fasta.is_valid_char(c) for c in args['replace_with']):
        raise RuntimeError('A replacement string cannot itself contain non-ASCII, whitespace, non-printable characters nor any of the illegal characters ({0}).'
                              .format(fasta.ILLEGAL_ID_CHARS))
    print()
    print('sanitizing', args['ifile'], '...')
    sanitize_fasta(**args)


