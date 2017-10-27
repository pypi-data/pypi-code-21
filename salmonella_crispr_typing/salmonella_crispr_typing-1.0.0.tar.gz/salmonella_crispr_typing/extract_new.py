#!/usr/bin/env python3

"""
Methods to extract new spacer sequences.
"""

import logging

from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

from salmonella_crispr_typing.settings import START_CHAR, END_CHAR, SPACER_MAX

_LOGGER = logging.getLogger(__name__)


def _extract_sequences(sequence):
    """
    Extract a sequence between spacers if < SPACER_MAX length

    :param sequence: sequence to be truncated
    :type sequence: :class:`Bio.SeqRecord.SeqRecord` object
    :return: new spacer sequences
    :rtype: LIST of :class:`Bio.SeqRecord.SeqRecord` object.
    """
    _LOGGER.debug("Extracting new spacer sequence from " + sequence.id + ".")
    new_sequences = []
    num_spacer = 1
    for motif in str(sequence.seq).split(END_CHAR)[1:-1]:
        # new spacer can only be at the begining of the motif
        if len(motif) < (SPACER_MAX + 10) and motif[0] != '-':
            new_seq = motif.split(START_CHAR)[0]
            _LOGGER.debug("New spacer found: " + new_seq)
            new_sequences.append(SeqRecord(Seq(new_seq), id="new_spacer_" + str(num_spacer),
                                           description=sequence.description))
            num_spacer += 1
    # Return list of sequences
    return new_sequences


def extract_new_spacers(sequences):
    """
    This function is called if users specify it needs to extract sequences of new spacers.

    :param sequences: sequences with found spacers
    :type sequences: LIST of :class:`Bio.SeqRecord.SeqRecord` object.
    :return: new spacer sequences
    :rtype: LIST of :class:`Bio.SeqRecord.SeqRecord` object.
    """
    _LOGGER.info("Extracting new spacer sequences.")
    new_sequences = []
    for sequence in sequences:
        if sequence.seq.find(START_CHAR) != -1:  # It means there is at least one spacer
            for new_seq in _extract_sequences(sequence):
                new_sequences.append(new_seq)
    return new_sequences
