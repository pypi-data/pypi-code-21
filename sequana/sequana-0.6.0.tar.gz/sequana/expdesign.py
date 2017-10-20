# -*- coding: utf-8 -*-
#
#  This file is part of Sequana software
#
#  Copyright (c) 2016 - Sequana Development Team
#
#  File author(s):
#      Thomas Cokelaer <thomas.cokelaer@pasteur.fr>
#      Dimitri Desvillechabrol <dimitri.desvillechabrol@pasteur.fr>,
#          <d.desvillechabrol@gmail.com>
#
#  Distributed under the terms of the 3-clause BSD license.
#  The full license is in the LICENSE file, distributed with this software.
#
#  website: https://github.com/sequana/sequana
#  documentation: http://sequana.readthedocs.io
#
##############################################################################
"""Module to handle experimental design files (adapters)


Sequencers or experimentalists create so-called design files to
store information about the sequencing experiment. For example the
name of the samples, the sample well, and the index sequences.

The format used to store the design information may vary from one sequencing
platform to another. The design file can be used for many different purposes.
Currently, we only use them to retrieve information about adapters.

Since there are different formats possible, we decided on a minimal and common
set of information. For now, this is a CSV file with the following minimal header::

    Sample_ID, Index1_Seq

or, for double-indexing::

    Sample_ID, Index1_Seq, Index2_Seq


Users should only use the :class:`ExpDesignAdapter` class, which understands
the different formats. Currently, the design file created by MiSeq Illumina
machine


"""
import shlex
import io

from sequana.lazy import pandas as pd


__all__ = ["ExpDesignAdapter", "ExpDesignMiSeq", "ExpDesignHiSeq",
           "ExpDesignBase"]


class ExpDesignAdapter(object):
    """Generic Experimental design class

    This class is used to store the mapping between sample ID and adapter
    used.

    The design information is stored as a dataframe in the attribute
    :attr:`df`.

    The input format is not unique. There are currently 3 different inputs
    possible as defined in

    - :class:`ExpDesignGeneric`
    - :class:`ExpDesignMiSeq` 
    - :class:`ExpDesignHiSeq` (2500)

    The dataframe index is the list of sample identifiers (Sample_ID).
    The columns contain at least the following::

        Index1_Seq, Index1_ID, Index2_Seq, Index2_ID

    Example::

        from sequana import *
        filename = sequana_data('test_test_expdesign_hiseq.csv')
        eda = ExpDesignAdapter(filename)

    """
    def __init__(self, filename, verbose=True):
        """.. rubric:: constructor

        :param str filename: the input design file. Can also be an instance of
            :class:`ExpDesignAdapter` itself.
        :param bool verbose:

        """
        self.verbose = verbose
        try:
            self.df = filename.df.copy()
            self.name = "unset"
        except:
            self._factory(filename)

    def _factory(self, filename):
        try:
            exp = ExpDesignMiSeq(filename)
            if self.verbose:
                print("Found MiSeq design file")
        except Exception as err:
            try:
                exp = ExpDesignHiSeq(filename)
                if self.verbose:
                    print("Found HiSeq design file")
            except:
                try:
                    exp = ExpDesignGeneric(filename)
                    if self.verbose:
                        print("Found Generic Sequencer design file")
                except:
                    msg = "Input file could not be read or interpreted"
                    raise IOError(msg)
        self.df = exp.df
        self.name = exp.name

    def __repr__(self):
        txt = "ExpDesignAdapter: %s experiments\n" % len(self.df)
        txt += " read with %s\n" % self.name
        try: txt += " Number of lanes: %s \n" % len(self.df.Lane.unique())
        except: pass
        try: txt += " Number of sample reference: %s" % len(self.df.SampleRef.unique())
        except: pass
        return txt


class ExpDesignBase(object):
    """The Base class for all ExpDesignAdapter classes

    The input filename must be a CSV file with at least the following column in
    the header::

        Sample_ID

    Derived class must define at least **Index1_Seq**  and possibly **Index2_Seq**.

    Examples of specialised classes are :class:`ExpDesignMiSeq`,
    :class:`ExpDesignHiSeq`.

    """
    def __init__(self, filename):
        self.filename = filename
        self.adapter_type = "unset"
        self.name = "ExpDesignBase"

    def check(self):
        """Check the presence of the Sample_ID column"""
        for this in ["Sample_ID"]:
            if this not in self.df.columns:
                print(self.df.columns)
                raise KeyError("%s not found. " % this)

    def read(self):
        """Read a CSV file"""
        self.df = pd.read_csv(self.filename, sep=",")

    def __repr__(self):
        txt = "%s: %s entries\n" % (self.name, len(self.df))
        txt += "adapter type: %s " % (self.adapter_type)
        return txt


class ExpDesignGeneric(ExpDesignBase):
    """Generic experimental design format

    ::

        Sample_ID, Index1_Seq, Index2_Seq

    :: 

    """
    def __init__(self, filename):
        super(ExpDesignGeneric, self).__init__(filename)
        self.name = "ExpDesignGeneric"

        self.read()
        self.df.rename(columns={"index1": "Index1_ID", "index2": "Index2_ID",
            "sample_name": "Sample_ID"},  inplace=True)
        self.check()


class ExpDesignHiSeq(ExpDesignBase):
    """Dedicated experimental design format created by a demultiplexing soft.

    This format is used by a demultiplex software used locally at biomics
    platform. The format of the header is::

        FCID,Lane,SampleID,SampleRef,Index Seq, Description,Control,Recipe,Operator,Project

    This is a format that may change in the future.

    The SampleID is convert into Sample_ID, "Index Seq". Note that "Index Seq"
    may be empty, or filled with an index sequence, or 2 index sequences
    separated by a "-" sign.

    note also FCID = flowcell ID

    """
    def __init__(self, filename):
        super(ExpDesignHiSeq, self).__init__(filename)
        self.name = "ExpDesignHiSeq"
        self.read()

        for this in ["FCID","Lane","SampleID","Index Seq"]:
            if this not in self.df.columns:
                raise ValueError("Invalid header. %s column is missing" % this)

        self.df.rename(columns={"SampleID":"Sample_ID", "Index Seq":"Index_Seq"},
                       inplace=True)

        index1 = []
        index2 = []
        for this in self.df.Index_Seq.values:
            if isinstance(this, str):
                indices = this.split("-")
                index1.append(indices[0])
                if len(indices) == 2:
                    index2.append(indices[1])
                else:
                    index2.append(None)
            else:
                index1.append(None)
                index2.append(None)
        self.df['Index1_Seq'] = index1
        self.df['Index2_Seq'] = index2
        self.df.drop("Index_Seq", axis=1, inplace=True)

        self.check()


class ExpDesignMiSeq(ExpDesignBase):
    """Dedicated experimental design format from Illumina MiSeq sequencers

    This MiSeq design format has the following format::

        [Header]
        blabla

        [Reads]
        blabla

        [Settings]
        blabla

        [Data]
        blabla


    In the Data section, a CSV file is to be found with the following header::

        Sample_ID,Sample_Name,Sample_Plate,Sample_Well,I7_Index_ID,index,
        Sample_Project,Description

    The index column may be prefixed. For instance as
    NFXX where XX is the index so NF should be dropped.

    If double-indexing, the header is::

        Sample_ID,Sample_Name,Sample_Plate,Sample_Well,I7_Index_ID,
        index,I5_Index_ID,index2,Sample_Project,Description

    ::

        filename = sequana_data("test_expdesign_miseq_illumina_1.csv")
        ff = ExpDesignMiSeq(filename)
        ff.df


    """
    def __init__(self, filename):
        super(ExpDesignMiSeq, self).__init__(filename)
        self.name = "ExpDesignMiSeq"

        data = {}
        # shlex removes all white lines and split by return carriage
        # strip is also applied
        rawdata = shlex.split(open(filename, "r"))
        for line in rawdata:
            if line.startswith('[') and line.endswith(']'):
                currentkey = line.replace("[", "").replace("]", "")
                data[currentkey] = []
            else:
                data[currentkey].append(line)

        for key in data.keys():
            data[key] = "\n".join(data[key])

        for this in ["Header", "Reads", "Settings", "Data"]:
            if this not in data.keys():
                print("%s not found in the DesignExpMiSeq file" % this)

        self.data = data
        self.df = pd.read_csv(io.StringIO(data["Data"]))

        self.df.rename(columns={"I7_Index_ID":"Index1_ID", "index":"Index1_Seq",
            "I5_Index_ID": "Index2_ID", "index2":"Index2_Seq"},
                       inplace=True)

        # The name of the Index_ID is not standard....
        # Depends on the experimentalist because a prefix may be added.
        # One known prefix is NF. We agreed that future prefix must end with an
        # underscore so that it can be removed. Since ID may contain letters
        # (e.g.S501), it would be impossible otherwise to split the prefix from
        # the index.
        self.df["Index1_ID"] = self.df["Index1_ID"].apply(
                lambda x: x.replace("NF", ""))
        self.df["Index1_ID"] = self.df["Index1_ID"].apply(
                lambda x: x.split("_",1)[-1])
        try:
            self.df["Index1_ID"] = self.df["Index1_ID"].astype(int)
        except:
            pass

        if "Index2_ID" in self.df.columns:
            self.df["Index2_ID"] = self.df["Index2_ID"].apply(
                lambda x: x.replace("NF", ""))
            self.df["Index2_ID"] = self.df["Index2_ID"].apply(
                lambda x: x.split("_",1)[-1])
            try:
                self.df["Index2_ID"] = self.df["Index2_ID"].astype(int)
            except:
                pass

        # Figure out the type of adapters if possible
        try:
            header = self.data['Header']
            assay = [x for x in header.split('\n') if x.startswith("Assay")]
            assay = assay[0]
            self.adapter_type = assay.split(",")[1]
        except:
            pass

        self.check()
