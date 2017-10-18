import sys
import os
import unittest
import shutil
from io import StringIO
sys.path.append(".")
from mock_gff3 import Create_generator
import annogesiclib.merge_sRNA as ms


class TestMergesRNA(unittest.TestCase):

    def setUp(self):
        self.example = Example()
        self.test_folder = "test_folder"
        if (not os.path.exists(self.test_folder)):
            os.mkdir(self.test_folder)

    def tearDown(self):
        if os.path.exists(self.test_folder):
            shutil.rmtree(self.test_folder)


class Example(object):
    tss_dict = [{"seq_id": "aaa", "source": "Refseq", "feature": "TSS", "start": 3,
                 "end": 3, "phase": ".", "strand": "+", "score": "."},
                {"seq_id": "aaa", "source": "Refseq", "feature": "TSS", "start": 16,
                 "end": 16, "phase": ".", "strand": "-", "score": "."},
                {"seq_id": "aaa", "source": "Refseq", "feature": "TSS", "start": 54,
                 "end": 54, "phase": ".", "strand": "+", "score": "."}]
    attributes_tss = [{"ID": "CDS0", "Name": "CDS_0", "type": "Primary", "associated_gene": "AAA_00001", "UTR_length": "Primary_25"},
                      {"ID": "CDS1", "Name": "CDS_1", "type": "Internal", "associated_gene": "AAA_00002", "UTR_length": "Internal_NA"},
                      {"ID": "CDS2", "Name": "CDS_2", "type": "Primary&Antisense",
                       "associated_gene": "AAA_00004&AAA_00006", "UTR_length": "Primary_25&Internal_NA"}]
    tss2_dict = [{"seq_id": "aaa", "source": "Refseq", "feature": "TSS", "start": 3,
                  "end": 3, "phase": ".", "strand": "+", "score": "."},
                 {"seq_id": "aaa", "source": "Refseq", "feature": "TSS", "start": 18,
                  "end": 18, "phase": ".", "strand": "-", "score": "."},
                 {"seq_id": "aaa", "source": "Refseq", "feature": "TSS", "start": 23,
                  "end": 23, "phase": ".", "strand": "+", "score": "."}]
    attributes_tss2 = [{"ID": "CDS0", "Name": "CDS_0", "type": "Primary", "associated_gene": "AAA_00001", "UTR_length": "Primary_25"},
                       {"ID": "CDS1", "Name": "CDS_1", "type": "Internal", "associated_gene": "AAA_00002", "UTR_length": "Internal_NA"},
                       {"ID": "CDS2", "Name": "CDS_2", "type": "Primary&Antisense",
                        "associated_gene": "AAA_00004&AAA_00006", "UTR_length": "Primary_25&Internal_NA"}]
    gff_dict = [{"start": 6, "end": 15, "phase": ".",
                 "strand": "+", "seq_id": "aaa", "score": ".",
                 "source": "Refseq", "feature": "gene"},
                {"start": 1258, "end": 2234, "phase": ".",
                 "strand": "+", "seq_id": "aaa", "score": ".",
                 "source": "Refseq", "feature": "gene"},
                {"start": 3544, "end": 6517, "phase": ".",
                 "strand": "-", "seq_id": "aaa", "score": ".",
                 "source": "Refseq", "feature": "gene"}]
    attributes_gff = [{"ID": "gene0", "Name": "gene_0", "locus_tag": "AAA_00001"},
                      {"ID": "gene0", "Name": "gene_1", "locus_tag": "AAA_00002"},
                      {"ID": "gene1", "Name": "gene_2", "locus_tag": "AAA_00003"}]
    tsss = []
    tsss2 = []
    genes = []
    for index in range(0, 3):
        tsss.append(Create_generator(tss_dict[index], attributes_tss[index], "gff"))
        tsss2.append(Create_generator(tss2_dict[index], attributes_tss2[index], "gff"))
        genes.append(Create_generator(gff_dict[index], attributes_gff[index], "gff"))

if __name__ == "__main__":
    unittest.main()

