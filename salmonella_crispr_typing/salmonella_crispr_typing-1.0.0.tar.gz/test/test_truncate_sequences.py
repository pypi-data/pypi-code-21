#!/usr/bin/env python3

"""
End to end tests for salmonella_crispr_typing.truncate_sequences module
"""

import os
import unittest
import filecmp

from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

from salmonella_crispr_typing import main
import salmonella_crispr_typing.truncate_sequences as tseq
from salmonella_crispr_typing.settings import LOCAL_DATA, START_CHAR, END_CHAR


class TestTruncateSequences(unittest.TestCase):
    """
    Tests for truncate_sequences.py module
    """

    def setUp(self):
        """
        Set up a sequence to work on
        """
        self.motif = "actga"
        sequence = "{0}-DR&{0}-DR&{0}".format(self.motif * 100)
        self.seq = SeqRecord(Seq(sequence), id="query", name="query")

    def test__remove_start(self):
        """
        Test for _remove_start method
        """
        sequence = tseq._remove_start(str(self.seq.seq), str(self.seq.seq).find(START_CHAR))
        expected = "[490bp]..{1}-DR&{0}-DR&{0}".format(self.motif * 100, self.motif * 2)
        self.assertEqual(sequence, expected)

    def test__remove_end(self):
        """
        Test for _remove_end method
        """
        sequence = tseq._remove_end(str(self.seq.seq), str(self.seq.seq).rfind(END_CHAR))
        expected = "{0}-DR&{0}-DR&{1}..[490bp]".format(self.motif * 100, self.motif * 2)
        self.assertEqual(sequence, expected)

    def test__is_last_from_crispr_loci(self):
        """
        Test for _is_last_from_crispr_loci
        """
        last = tseq._is_last_from_crispr_loci(str(self.seq.seq), str(self.seq.seq).rfind(END_CHAR))
        self.assertTrue(last)

    def test__remove_between(self):
        """
        Test for _remove_between method
        """
        sequence = tseq._remove_between(str(self.seq.seq))
        expected = "{0}-DR&{1}..[480bp]..{1}-DR&{0}".format(self.motif * 100, self.motif * 2)
        self.assertEqual(sequence, expected)

    def test__truncate_sequence(self):
        """
        Test for _truncate_sequence method
        """
        sequence = tseq._truncate_sequence(self.seq)
        expected = "[490bp]..{0}-DR&{0}..[480bp]..{0}-DR&{0}..[490bp]".format(self.motif * 2)
        self.assertEqual(str(sequence.seq),expected)

    def test_truncation(self):
        """
        End to end test for truncation of long genomic regions
        """
        tmp_file = 'tmp_test_trunc.output'
        input_file = os.path.dirname(__file__) + '/long_sequence.fa'
        expected_file = os.path.dirname(__file__) + '/trunc_example.test.output'
        # Open files
        with open(input_file, 'r') as file_handle:
            query = list(SeqIO.parse(file_handle, "fasta"))
        with open(LOCAL_DATA + "/spacers_Salmonella.fa", "r") as file_handle:
            spacers = list(SeqIO.parse(file_handle, "fasta"))
        res_query = [main.find_spacers(query[0], spacers)]
        res_query = tseq.truncate_sequences(res_query)
        with open(tmp_file, 'w') as file_handle:
            main.write_fasta(res_query, file_handle)
        try:
            self.assertTrue(filecmp.cmp(expected_file, tmp_file))
        finally:
            os.remove(tmp_file)