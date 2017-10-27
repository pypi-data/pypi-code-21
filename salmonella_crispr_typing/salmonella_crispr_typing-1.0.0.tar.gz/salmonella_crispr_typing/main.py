#!/usr/bin/env python3

"""
Search spacers composition for a query
- obtain a spacer profile for CRISPR-1 and CRISPR-2 loci from
  concatenate sequence in 'CRISPR_concat1et2' experiment (spacers in /data)
"""

# Import -----

import argparse
import sys
import os
import re
import logging

from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.SeqIO.FastaIO import FastaWriter

from salmonella_crispr_typing import __version__
from salmonella_crispr_typing.truncate_sequences import truncate_sequences
from salmonella_crispr_typing.extract_new import extract_new_spacers
from salmonella_crispr_typing.settings import START_CHAR, END_CHAR, LOCAL_DATA, FOUND_SPAC, NEW_SPAC


# Logger -----

_LOGGER = logging.getLogger()

# Function(s) -----


def logger_level(args):
    """
    Define level of logger.
    """
    if args.debug:
        return logging.DEBUG
    elif args.verbose:
        return logging.INFO
    return logging.WARNING


def parse_arguments(args):
    """
    Define parser for salmonella_crispr tool.
    """
    parser = argparse.ArgumentParser(description='Search spacers composition for a query')
    parser.add_argument('query', type=argparse.FileType('r', encoding='UTF-8'),
                        help='input query sequence (FASTA).')
    parser.add_argument('-s', '--spacers', type=argparse.FileType('r', encoding='UTF-8'),
                        help='database of spacers (FASTA).',
                        default=LOCAL_DATA + "/spacers_Salmonella.fa")
    parser.add_argument('-o', '--outfile', help='name of output file',
                        type=argparse.FileType('w', encoding='UTF-8'),
                        default=sys.stdout)
    parser.add_argument('-t', '--truncate', help='truncate sequences with no spacers',
                        action='store_true')
    parser.add_argument('--one_line_fasta', help='write output FASTA in one line',
                        action='store_true')
    parser.add_argument('-c', '--clean_sequences', help='remove ' + END_CHAR + ' from sequences',
                        action='store_true')
    parser.add_argument('-l', '--list_spacers', help='list all spacers found', action='store_true')
    parser.add_argument('-e', '--extract_new_spacers', help='extract new found spacer sequences',
                        action='store_true')
    parser.add_argument('-v', '--verbose', help='verbose mode', action='store_true')
    parser.add_argument('--debug', help='write debug messages', action='store_true')
    parser.add_argument('--version', action='version', version=__version__,
                        help='show the version number and exit.')


    try:
        return parser.parse_args(args)
    except SystemExit:
        sys.exit()


def list_spacers(querys, spacers):
    """
    :param query: sequence where to look spacers for
    :type query: :class:`Bio.SeqRecord.SeqRecord` object.
    :param spacers: list of spacers
    :type spacers: LIST of :class:`Bio.SeqRecord.SeqRecord` object.
    :return: report to be written in a file
    :rtype: STRING
    """
    _LOGGER.info("Listing found spacers.")
    found_spacers = ""
    for query in querys:
        for spacer in spacers:
            for pos in re.finditer(str(spacer.seq.lower()), str(query.seq.lower())):
                found_spacers += "{0}\t{1}\t{2}\t{3}\n".format(query.name, pos.span()[0],
                                                               pos.span()[1], spacer.name)
    return found_spacers


def find_spacers(query, spacers):
    """
    :param query: sequence where to look spacers for
    :type query: :class:`Bio.SeqRecord.SeqRecord` object.
    :param spacers: list of spacers
    :type spacers: LIST of :class:`Bio.SeqRecord.SeqRecord` object.
    :return: query sequence with spacer sequence replaced by their names
    :rtype: :class:`Bio.SeqRecord.SeqRecord` object.
    """
    _LOGGER.info("Looking for spacers in " + query.name + ".")
    # Copy sequence of the query for modification
    seq_query = str(query.seq.lower())
    for spacer in spacers:
        seq_query = seq_query.replace(str(spacer.seq.lower()), START_CHAR + spacer.name + END_CHAR)
    res_query = SeqRecord(Seq(seq_query), id=query.id, description=query.description)
    return res_query


def clean_sequences(sequences):
    """
    This function is called if users specify it needs sequences to cleaned up..

    :param sequences: sequences with found spacers
    :type sequences: LIST of :class:`Bio.SeqRecord.SeqRecord` object.
    :return: truncated sequences
    :rtype: LIST of :class:`Bio.SeqRecord.SeqRecord` object.
    """
    _LOGGER.info("Removing " + END_CHAR + " from sequences.")
    cleaned_seq = []
    for seq in sequences:
        cleaned_seq.append(SeqRecord(Seq(str(seq.seq).replace('&', '')), id=seq.id,
                                     description=seq.description))
    return cleaned_seq
   

def write_fasta(sequence, file_handle, wrap=60):
    """
    :param sequence: sequence to write in the file
    :type sequence: :class:`Bio.SeqRecord.SeqRecord` object
    :param file_handle: output file handler
    :type file_handle: 
    """
    _LOGGER.info("Writing output to " + file_handle.name + "...")
    writer = FastaWriter(file_handle, wrap=wrap)
    writer.write_file(sequence)


def run():
    """
    Running function called by crispr command line
    """
    # Parse arguments
    args = parse_arguments(sys.argv[1:])

    # Configure logger
    logging.basicConfig(level=logger_level(args))

    # Parse query sequence(s)
    query_seqs = list(SeqIO.parse(args.query, "fasta"))
    # Parse content of spacers database
    spacers = list(SeqIO.parse(args.spacers, "fasta"))
    # First make found spacers list if asked
    if args.list_spacers:
        if args.outfile is not sys.stdout:
            spacer_file = os.path.splitext(args.outfile.name)[0] + ".bed"
        else:
            spacer_file = FOUND_SPAC
        with open(spacer_file, "w") as file_handle:
            file_handle.write(list_spacers(query_seqs, spacers))
    res_query = []
    for query in query_seqs:
        res_query.append(find_spacers(query, spacers))
    # User specified to truncate sequences with no spacers
    if args.truncate:
        res_query = truncate_sequences(res_query)
    # User specified to extract sequences from new found spacers
    if args.extract_new_spacers:
        new_seqs = extract_new_spacers(res_query)
        if new_seqs:
            with open(NEW_SPAC, "w") as handle:
                write_fasta(new_seqs, file_handle=handle, wrap=0)
        else:
            _LOGGER.warn("No new spacer has been found. " + NEW_SPAC + " will not be created.")
    # Clean up sequences to remove extra characters (END_CHAR) added
    if args.clean_sequences:
        res_query = clean_sequences(res_query)
    # Write output files
    if args.one_line_fasta:
        write_fasta(res_query, file_handle=args.outfile, wrap=0)
    else:
        write_fasta(res_query, file_handle=args.outfile)


if __name__ == "__main__":
    run()
    
