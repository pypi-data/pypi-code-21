#!/usr/bin/env python3

"""
End to end tests for salmonella_crispr_typing.extract_new module
"""

import os
import unittest
import filecmp

from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

import salmonella_crispr_typing.extract_new as extnew


class TestExtractNew(unittest.TestCase):
    """
    Tests for extract_new.py module
    """

    def setUp(self):
        """
        Set up manual sequences for extraction
        """
        self.seqs = []
        self.seqs.append(SeqRecord(Seq("aaat-DR&-SPAC&-DR&ccggg"), id="no_new", name="query1"))
        self.seqs.append(SeqRecord(Seq("aaat-DR&actgatag-DR&gtcccggg"), id="new", name="query2"))

    def test_extract_new_spacers(self):
        """
        Test main method of extract_new module
        """
        new_seqs = extnew.extract_new_spacers(self.seqs)
        self.assertEqual(str(new_seqs[0].seq), "actgatag")

    def test__extract_sequences(self):
        """
        Test for _extract_sequences method
        """
        new_seq1 = extnew._extract_sequences(self.seqs[0])
        self.assertFalse(new_seq1)
        new_seq2 = extnew._extract_sequences(self.seqs[1])
        self.assertEqual(str(new_seq2[0].seq), "actgatag")
