# -*- encoding: utf-8 -*-
"""Small module to parse and read barcode files.

File specification: barcodes file (default: 'barcodes.txt')
-------------------------------------------------------------

This file contains all barcode information for one ddRADseq experiment.
These consist of a mapping of indices to barcode sequences and a 
mapping of index combinations to individuals.
The entries are formatted as follows:

The first block is a mapping from p5-barcode indices to p5-barcode
sequences as tab-separated values.

The second block (separated by at least on empty or commented line)
is a mapping from p7-barcode indices to p7-barcode sequences as
tab-separated values.

The third block (also separated by at least one empty or commented line)
contains all individual and their pair of (p5, p7) barcodes
as well as their inserts and further information.
These are saved as tab separated strings in the following order:
p5_index, p7_index, p5_insert, p7_insert, individual_name, population_name, ...
All columns after the population name are optional and can be used for 
further information for the individual, like place of origin,
personal notes, or the used preparation techniques.

Example (with two additional columns)::

    # p5 barcodes
    1    ATCACG
    2    CGATGT
    3    TTAGGC
    
    # p7 barcodes
    1    ATCACG
    8    ACTTGA
    10   TAGCTT
    
    # individual
    1	1			Individual 1	Population 1	Info_1	Info_2
    2	8	GAC	G	Individual 2	Population 1	Info_1	Info_2
    3	10	AC	AT	Individual 3	Population 1	Info_1	Info_2
    4	11	C	CGA	Individual 4	Population 2	Info_1	Info_2
    5	1	AC		Individual 5	Population 2	Info_1	Info_2
    6	8		G	Individual 6	Population 2	Info_1	Info_2

"""
import itertools
import re
import sys
import os
from os.path import exists, abspath


# Dictionary used to create the 1-ball around all barcode sequences
# which are used for error tolerant barcode mapping.
not_this = dict({
    "A": ("C", "G", "T"),
    "C": ("A", "G", "T"),
    "G": ("A", "C", "T"),
    "T": ("A", "C", "G"),
    65: (67, 71, 84),
    67: (65, 71, 84),
    71: (65, 67, 84),
    84: (65, 67, 71),
})


class DeBarcoder:
    """Class that contains all information regarding barcode pairs.
    
    This includes:

        * Valid barcodes and barcode pairs
        * Insert sequences and their association to barcodes / barcode pairs
        * Population and individual information encoded by the barcodes
        * All of the above, allowing for errors of 1 (hamming distance) in both barcodes
    """

    def __init__(self, path, dtype=bytes):
        """Create a new Barcodes object from the given filepath.

        Arguments:
            path (str): Path to a barcodes.txt file
            dtype (str or bytes): Return type of the sequences from DeBarcoder and
                type of the entries.
                If set to str, all barcodes, inserst, etc. will be created and returned
                as strings. Default: bytes
        """
        # data structures for perfect barcodes
        # maps: int(p5/7_index) -> p5/7_barcode
        self.p5_index_dict = dict({})
        self.p7_index_dict = dict({})
        # maps: (p5bc, p7bc) -> (p5_ins, p7_ins, name, pop, in_1ball, misc)
        self.bc_pairs = dict({})
        # maps: p5_bc -> p7_bc; p7_bc -> p5_bc
        self.p5_partners = dict({})
        self.p7_partners = dict({})
        # maps: p5/7_bc -> p5/7_insert
        self.p5_insert = dict({})
        self.p7_insert = dict({})
    
        # data structures for tainted barcodes (i.e. adding the 1 ball)
        # maps are the same as above, but also allowing for one error
        # i.e. The whole neighbourhood of hamming distance one barcodes is
        # added as well
        self.bc_pairs_1b = dict({})
        self.p5_partners_1b = dict({})
        self.p7_partners_1b = dict({})
        self.p5_insert_1b = dict({})
        self.p7_insert_1b = dict({})

        # set splitting and merging chars according to input dtype.
        if dtype == str:
            self.dtype=dtype
            self._replace = self._replace_str
            self._make_mutable = list
            self.tab = '\t'
            self.linebreak = '\n'
            self.read_mode = 'r'
            self.empty = ''
            self.underscore = '_'
            self.space = ' '
            self.nr_sign = '#'
        elif dtype == bytes:
            self.dtype=dtype
            self._replace = self._replace_bytearray
            self._make_mutable = bytearray
            self.tab = b'\t'
            self.linebreak = b'\n'
            self.read_mode = 'rb'
            self.empty = b''
            self.underscore = b'_'
            self.space = b' '
            self.nr_sign = b'#'
        else:
            raise TypeError("Invalid dtype '{}' should be either str or bytes.".format(dtype))

        # validate input path
        self.bc_path = self._expand_path(path)

        # populate dicts from input files
        self._read_barcodes_file()
        self._initialize_bc_pairs()
        self._initialize_partner_dicts()
        self._initialize_insert_dicts()

    def __str__(self):
        return "Barcode dict containing the following pairs:\n{}".format("\n".join(map(str, self.bc_pairs.items())))

    def to_str(self):
        entries = [([p5_bc.decode(), p7_bc.decode()], [item.decode() if isinstance(item, bytes) else item for item in values]) for (p5_bc, p7_bc), values in self.bc_pairs.items()]
        return "Barcode dict containing the following pairs:\n{}".format("\n".join(map(str, entries)))

    def _expand_path(self, path):
        """Expand path to barcodes file to find p5 and p7 barcodes.

        Also validates the files existance.

        Arguments:
            path (str): Path to a barcodes file.

        Returns:
            str: The absolute path to the barcodes file, if it exists.

        Raises:
            IOError: If the file does not exist.
        """
        abs_path = abspath(path)
        if exists(abs_path):
            return abs_path
        else:
            raise IOError("The file {} does not exist. Are you sure it is there?".format(abs_path))

    def _parse(self, line):
        """Split a line by tabs."""
        return line.strip().split(self.tab)

    def _replace_str(self, seq, item, i):
        """Replace the item at index i of the list with the given item.

        Arguments:
            seq (list of chars): List of items of a string in which the
                character will be replaced.
            item (char): The char to be inserted.
            i (int): Index at which the item will be inserted.

        Returns:
            str: Joined from the elements of the input list.
        """
        return self.empty.join(seq[:i]+[item]+seq[i+1:])

    def _replace_bytearray(self, seq, item, i):
        """Replace the item at index i of the bytearray with the given item. 

        Arguments:
            seq (bytearray): Input sequence in which a character will be replaced.
            item (char): The char to be inserted.
            i (int): Index at which the item will be inserted.

        Returns:
            bytes: from the input bytearray.
        """
        seq[i]=item
        return bytes(seq)

    def _read_barcodes_file(self):
        """Read in barcodes file and split it up into blocks.

        Returns:
            None: But populates the p5_bcs_raw, p7_bcs_raw and individual_raw lists.
            The type of the list entries (bytes or str) depends on the dtype parameter
            of the constructor.
        """
        # read in the complete barcodes file
        with open(self.bc_path, self.read_mode) as barcodes_file:
            file_raw = barcodes_file.readlines()

        # replace commented lines by empty ones
        cleaned_lines = [self.empty if line[0:1] == self.nr_sign else line for line in file_raw]

        found_lists = []
        active_list = []
        just_split = True
        # split the list of the complete file on each occurence of
        # one or more empty lines (native or removed comment line)
        # A valid file should contain three blocks
        for line in cleaned_lines:
            if line in (self.empty, self.linebreak):
                if just_split:
                    # last line was empty as well
                    continue
                else:
                    # last line was not empty
                    # finalize this block and start the next one
                    just_split = True
                    found_lists.append(active_list)
                    active_list = []
            else:
                just_split = False
                active_list.append(line.strip(self.linebreak))
        # append last list
        found_lists.append(active_list)

        # split up list into three blocks
        # if this fails, the file was malformed
        try:
            self.p5_bcs_raw, self.p7_bcs_raw, self.individual_raw = found_lists
        except ValueError as ve:
            if "values to unpack" in str(ve):
                ve.args += ("The barcodes file might be malformed. Please take a look at the specification and verify that the file contains three blocks of information separated by empty lines.", )
                raise ve
            else:
                raise

    def _initialize_bc_pairs(self, error_tolerant=False):
        """Initialize the bc_pairs dict from the files.

        Create mappings between:
            p5 indices -> p5 barcodes
            p7 indices -> p7 barcodes
            (p5 barcode, p7 barcode) -> (p5 insert, p7 insert, name, pop, in_1_ball, misc)
            (p5 barcode, p7 barcode) -> (p5 insert, p7 insert, name, pop, in_1_ball, misc) with 1 ball
        """
        # create dictionary to map p5_indices to p5_sequences
        self.p5_index_dict = {int(p5_index) : p5_barcode for p5_index, p5_barcode in map(self._parse, self.p5_bcs_raw)}

        # create dictionary to map p7_indices to p7_sequences
        self.p7_index_dict = {int(p7_index) : p7_barcode for p7_index, p7_barcode in map(self._parse, self.p7_bcs_raw)}

        # Use the created dict to build full barcode dictionary.
        # All columns after the population name are optional
        # and therefore returned as a (potentially empty) list.

        # with open(self.bc_path, self.read_mode) as barcodes_file:
        for line in self.individual_raw:
            p5_index, p7_index, p5_insert, p7_insert, name, population, *misc = self._parse(line)
            p5_bc = self.p5_index_dict[int(p5_index)]
            p7_bc = self.p7_index_dict[int(p7_index)]
            # Each entry is composed of the inserts, individual name, pop name,
            # a boolean value which indicates, if the pair contains errors
            # i.e. at leat one of the barcodes is form the 1-ball 
            # this is followid by a list of meta information
            self.bc_pairs[(p5_bc, p7_bc)] = (p5_insert, p7_insert, name, population, False, misc)

        # add 1-ball
        for ((p5_bc, p7_bc), (p5_ins, p7_ins, name, pop, error, misc)) in self.bc_pairs.items():
            p5 = self._make_mutable(p5_bc) # make the p5 barcode mutable
            p7 = self._make_mutable(p7_bc) # make the p7 barcode mutable
            
            if error_tolerant:
                # create all p5 barcodes with distance 1
                p5_1ball = [p5_bc]
                for index_p5, base_p5 in enumerate(p5):
                    p5_1ball += [self._replace(p5, new_base_p5, index_p5) for new_base_p5 in not_this[base_p5]]
                # create all p7 barcodes with distance 1
                p7_1ball = [p7_bc]
                for index_p7, base_p7 in enumerate(p7):
                    p7_1ball += [self._replace(p7, new_base_p7, index_p7) for new_base_p7 in not_this[base_p7]]
                # create all possible combinations (cross product) of all p5 barcodes
                # and p7 barcodes.
                for new_p5_bc, new_p7_bc in itertools.product(p5_1ball, p7_1ball):
                    self.bc_pairs_1b[(new_p5_bc, new_p7_bc)] = (p5_ins, p7_ins, name, pop, self.underscore.join([p5_bc, p7_bc]), misc)
    
                # original item with errors=False, overwrites the one created by itertools.product
                self.bc_pairs_1b[(p5_bc, p7_bc)] = (p5_ins, p7_ins, name, pop, False, misc)

        # remove raw file information, which is no longer needed
        del self.p5_bcs_raw
        del self.p7_bcs_raw
        del self.individual_raw

    def _initialize_partner_dicts(self, error_tolerant=False):
        """Initialize the valid pairs / partner dict using the barcode pairs dict.

        This dict maps:
            p5 barcode -> [all valid p7 barcodes]
            p7 barcode -> [all valid p5 barcodes]
            p5 barcode -> [all valid p7 barcodes] with 1 ball
            p7 barcode -> [all valid p5 barcodes] with 1 ball
        """
        # iterate all valid p5 barcode p7 barcode pairs
        for (p5_bc, p7_bc) in self.bc_pairs.keys():
            try:
                # try to read a list of partner bcs
                partners = self.p7_partners[p5_bc]
                # if the barcode isn't already in the list, add it.
                if p7_bc not in partners:
                    self.p7_partners[p5_bc].append(p7_bc)
            except KeyError:
                # create a new list of partner bcs
                self.p7_partners[p5_bc] = [p7_bc]
            try:
                partners = self.p5_partners[p7_bc]
                if p5_bc not in partners:
                    self.p5_partners[p7_bc].append(p5_bc)
            except KeyError:
                self.p5_partners[p7_bc] = [p5_bc]
                
        if error_tolerant:
            # 1 ball
            for (p5_bc, p7_bc) in self.bc_pairs_1b.keys():
                try:
                    partners = self.p7_partners_1b[p5_bc]
                    if p7_bc not in partners:
                        self.p7_partners_1b[p5_bc].append(p7_bc)
                except KeyError:
                    self.p7_partners_1b[p5_bc] = [p7_bc]
                try:
                    partners = self.p5_partners_1b[p7_bc]
                    if p5_bc not in partners:
                        self.p5_partners_1b[p7_bc].append(p5_bc)
                except KeyError:
                    self.p5_partners_1b[p7_bc] = [p5_bc]

    def _initialize_insert_dicts(self, error_tolerant=False):
        """Initialize the insert dicts using the bc pairs dict.

        This dict maps:
            p5 insert -> p5 barcode
            p7 insert -> p7 barcode
            p5 insert -> p5 barcode with 1 ball
            p7 insert -> p7 barcode with 1 ball
        """
        # create perfect insert dicts
        for (p5_bc, p7_bc), (p5_insert, p7_insert, name, population, error, misc) in self.bc_pairs.items():
            try:
                check = self.p5_insert[p5_bc]
                if check != p5_insert:
                    raise ValueError("Conflicting information about the p5 insert for the barcode {}. Found both '{}' and '{}'.".format(p5_bc, check, p5_insert))
            except KeyError:
                self.p5_insert[p5_bc] = p5_insert
            try:
                check = self.p7_insert[p7_bc]
                if check != p7_insert:
                    raise ValueError("Conflicting information about the p7 insert for the barcode {}. Found both '{}' and '{}'.".format(p7_bc, check, p7_insert))
            except KeyError:
                self.p7_insert[p7_bc] = p7_insert
        if error_tolerant:
            # add 1-ball for p5 barcodes
            for bc, insert in self.p5_insert.items():
                self.p5_insert_1b[bc] = (insert, False) # original item
                mutable_bc = self._make_mutable(bc)
                for index, base in enumerate(mutable_bc):
                    # create one-neighbourhood by replacing the found base at each
                    # position with the three alternatives from not_this
                    one_neighbourhood =[self._replace(mutable_bc, new_base, index) for new_base in not_this[base]]
                    for one_distance_bc in one_neighbourhood:
                        self.p5_insert_1b[one_distance_bc] = (one_distance_bc, bc) # 1 neighbourhood item
            # add 1-ball for p7 barcodes
            for bc, insert in self.p7_insert.items():
                self.p7_insert_1b[bc] = (insert, False) # original item
                mutable_bc = self._make_mutable(bc)
                for index, base in enumerate(mutable_bc):
                    # create one-neighbourhood by replacing the found base at each
                    # position with the three alternatives from not_this
                    one_neighbourhood =[self._replace(mutable_bc, new_base, index) for new_base in not_this[base]]
                    for one_distance_bc in one_neighbourhood:
                        self.p7_insert_1b[one_distance_bc] = (one_distance_bc, bc) # 1 neighbourhood item

    def get_p7_barcodes(self, p5_barcode, error_tolerant=False):
        """Return all valid p7 barcodes to the given p5 barcode.
        
        Arguments:
            p5_barcode (bytes or str): A p5 barcode sequences for which the p7
                barcodes will be returned. Depending on the dtype specified at
                creation of the DeBarcoder.
            error_tolerant (bool): If set to True the 1 ball dicts will be queried,
                i.e. also barcode sequences with an error of 1 will be concerned.

        Returns:
            list of str or bytes: Containing all valid p7 barcodes for the given p5 barcode.
        """
        if error_tolerant:
            return self.p7_partners_1b[p5_barcode]
        else:
            return self.p7_partners[p5_barcode]

    def get_p5_barcodes(self, p7_barcode, error_tolerant=False):
        """Return all valid p5 barcodes to the given p7 barcode.
        
        Arguments:
            p7_barcode (bytes or str): A p7 barcode sequences for which the p5
                barcodes will be returned. Depending on the dtype specified at
                creation of the DeBarcoder.
            error_tolerant (bool): If set to True the 1 ball dicts will be queried,
                i.e. also barcode sequences with an error of 1 will be concerned.

        Returns:
            list of str or bytes: Containing all valid p5 barcodes for the given p7 barcode.
        """
        if error_tolerant:
            return self.p5_partners_1b[p7_barcode]
        else:
            return self.p5_partners[p7_barcode]

    def get_p5_insert(self, p5_barcode, error_tolerant=False):
        """Return the insert for the given p5 barcode.
        
        Arguments:
            p5_barcode (bytes or str): A p5 barcode sequences for which the insert.
                Depending on the dtype specified at creation of the DeBarcoder.
            error_tolerant (bool): If set to True the 1 ball dicts will be queried,
                i.e. also barcode sequences with an error of 1 will be concerned.

        Returns:
            str or bytes: Sequence of the p5 insert for the given p5 barcode.
            The type depends on the dtype parameter used at creation the the
            DeBarcoder object.
        """
        if error_tolerant:
            return self.p5_insert_1b[p5_barcode]
        else:
            return self.p5_insert[p5_barcode]

    def get_p7_insert(self, p7_barcode, error_tolerant=False):
        """Return the insert for the given p7 barcode.

        Arguments:
            p7_barcode (bytes or str): A p7 barcode sequences for which the insert.
                Depending on the dtype specified at creation of the DeBarcoder.
            error_tolerant (bool): If set to True the 1 ball dicts will be queried,
                i.e. also barcode sequences with an error of 1 will be concerned.

        Returns:
            str or bytes: Sequence of the p7 insert for the given p7 barcode.
            The type depends on the dtype parameter used at creation the the
            DeBarcoder object.
        """
        if error_tolerant:
            return self.p7_insert_1b[p7_barcode]
        else:
            return self.p7_insert[p7_barcode]

    def get_insert(self, p5_barcode, p7_barcode, error_tolerant=False):
        """Get the insert pair for the given barcode pair.

        Arguments:
            p5_barcode (bytes or str): A p5 barcode sequences for which the insert.
                Depending on the dtype specified at creation of the DeBarcoder.
            p7_barcode (bytes or str): A p7 barcode sequences for which the insert.
                Depending on the dtype specified at creation of the DeBarcoder.
            error_tolerant (bool): If set to True the 1 ball dicts will be queried,
                i.e. also barcode sequences with an error of 1 will be concerned.

        Returns:
            tuple of str or bytes: Sequences of the p5 and p7 inserts for the 
            given p5 and p7 barcodes. 
            The type depends on the dtype parameter used at creation the the
            DeBarcoder object.
        """
        if error_tolerant:
            p5_ins, p7_ins, *_ = self.bc_pairs_1b[(p5_barcode, p7_barcode)]
            return (p5_ins, p7_ins)
        else:
            p5_ins, p7_ins, *_ = self.bc_pairs[(p5_barcode, p7_barcode)]
            return (p5_ins, p7_ins)

    def get_individual(self, p5_barcode, p7_barcode, error_tolerant=False):
        """Get the individual for the given barcode pair.

        Note:
            Here we assume that a barcode combination is enough to uniquely identify 
            an individual. Additionally a run and lane number from the FASTQ name line
            might be needed to identify individuals across samples.

        Arguments:
            p5_barcode (bytes or str): A p5 barcode sequences for which the insert.
                Depending on the dtype specified at creation of the DeBarcoder.
            p7_barcode (bytes or str): A p7 barcode sequences for which the insert.
                Depending on the dtype specified at creation of the DeBarcoder.
            error_tolerant (bool): If set to True the 1 ball dicts will be queried,
                i.e. also barcode sequences with an error of 1 will be concerned.

        Returns:
            str or bytes: Name of the individual, specified by this combination of p5
            barcode and p7 barcode.
            The type depends on the dtype parameter used at creation the the
            DeBarcoder object.
        """
        if error_tolerant:
            _, _, individual, *_ = self.bc_pairs_1b[(p5_barcode, p7_barcode)]
            return individual
        else:
            _, _, individual, *_ = self.bc_pairs[(p5_barcode, p7_barcode)]
            return individual

    def get_population(self, p5_barcode, p7_barcode, error_tolerant=False):
        """Get the individual for the given barcode pair.

        Arguments:
            p5_barcode (bytes or str): A p5 barcode sequences for which the insert.
                Depending on the dtype specified at creation of the DeBarcoder.
            p7_barcode (bytes or str): A p7 barcode sequences for which the insert.
                Depending on the dtype specified at creation of the DeBarcoder.
            error_tolerant (bool): If set to True the 1 ball dicts will be queried,
                i.e. also barcode sequences with an error of 1 will be concerned.

        Returns:
            str or bytes: Name of the population specified by this combination of p5
            barcode and p7 barcode.
            The type depends on the dtype parameter used at creation the the
            DeBarcoder object.
        """
        if error_tolerant:
            _, _, _, population, *_ = self.bc_pairs_1b[(p5_barcode, p7_barcode)]
            return population
        else:
            _, _, _, population, *_ = self.bc_pairs[(p5_barcode, p7_barcode)]
            return population
    
    def get_meta_info(self, p5_barcode, p7_barcode, error_tolerant=False):
        """Get the meta info for the given barcode pair.

        Arguments:
            p5_barcode (bytes or str): A p5 barcode sequences for which the insert.
                Depending on the dtype specified at creation of the DeBarcoder.
            p7_barcode (bytes or str): A p7 barcode sequences for which the insert.
                Depending on the dtype specified at creation of the DeBarcoder.
            error_tolerant (bool): If set to True the 1 ball dicts will be queried,
                i.e. also barcode sequences with an error of 1 will be concerned.

        Returns:
            list of str or bytes: The additional information saved for this combination
            of p5 and p7 barcodes.
            The type depends on the dtype parameter used at creation the the
            DeBarcoder object.
        """
        if error_tolerant:
            *_, meta = self.bc_pairs_1b[(p5_barcode, p7_barcode)]
            return meta
        else:
            *_, meta = self.bc_pairs[(p5_barcode, p7_barcode)]
            return meta

    def valid(self, p5_barcode, p7_barcode, error_tolerant=False):
        """Return true, if the combination of barcodes is valid."""
        if error_tolerant:
            try:
                _ = self.bc_pairs_1b[(p5_barcode, p7_barcode)]
                return True
            except KeyError:
                return False
        else:
            try:
                _ = self.bc_pairs[(p5_barcode, p7_barcode)]
                return True
            except KeyError:
                return False

    def get(self, p5_barcode, p7_barcode, error_tolerant=False):
        """Return info for the given barcode pair, if it is valid.

        Arguments:
            p5_barcode (bytes or str): The p5 (forward) barcode.
                Depending on the dtype specified at creation of the DeBarcoder.
            p7_barcode (bytes or str): The p7 (backward) barcode.
                Depending on the dtype specified at creation of the DeBarcoder.
            error_tolerant (bool): If set to True the 1 ball dicts will be queried,
                i.e. also barcode sequences with an error of 1 will be concerned.

        Returns:
            A tuple containing:
                * p5 insert
                * p7 insert
                * individual name
                * population name
                * list with meta info
        """
        if error_tolerant:
            return self.bc_pairs_1b[(p5_barcode, p7_barcode)]
        else:
            return self.bc_pairs[(p5_barcode, p7_barcode)]

    def index_to_barcode(self, index):
        """Return the barcode for the given index (int, str or bytes).

        Note:
            Assumes, that the indices for p5 and p7 barcodes are the same.
            This means, that identical p5 and p7 barcodes also have identical indices.

        Arguments:
            index (int, str, bytes): Either an integer or any str or bytes containing
                a decimal number.

        Returns:
            str or bytes: The barcode associated with the given index.
        """
        try:
            return self.p5_index_dict[index]
        except TypeError:
            if isinstance(index, str):
                pattern = "\d+"
            elif isinstance(index, bytes):
                pattern = b"\d+"
            matches = re.search(pattern, index)
            i = matches.group()[0]
            return self.p5_index_dict[i]
        except KeyError:
            print(self.p5_index_dict, index, type(index), file=sys.stderr)
            raise

    def get_individual_matrix(self, empty="-", sort_by="index"):
        """Format the matrix of p5 and p7 barcodes and the encoded individual as string.

        Arguments:
            empty (str): The string that will be written in empty cells (Default: '-')
            sort_by (str): Sorting key for the barcodes. Can either be 'index'
                or 'barcode'. (Default: 'index')

        Returns:
            str: The formtted matrix, ready for printing.

        Raises:
            ValueError: If an invalid sorting key is provided.
        """
        if sort_by in ("index", "indices", "numeric"):
            # create index + bc pairs and sort them by index
            p5_barcodes = sorted([(index, bc) for index, bc in self.p5_index_dict.items()])
            p7_barcodes = sorted([(index, bc) for index, bc in self.p7_index_dict.items()])
        elif sort_by in ("barcode", "barcodes", "alphabetic"):
            # create index + bc pairs and sort them by barcode
            p5_barcodes = sorted([(index, bc) for index, bc in self.p5_index_dict.items()], key=lambda x: x[1])
            p7_barcodes = sorted([(index, bc) for index, bc in self.p7_index_dict.items()], key=lambda x: x[1])
        else:
            raise ValueError("Please either pick 'index' (default) or 'barcode' as values for sort_by")

        # format pairs into single string objects for insertion into matrix
        if self.dtype == bytes:
            p5_bc_items = ["{:>2} {}".format(index, bc.decode()) for index, bc in p5_barcodes]
            p7_bc_items = ["{:>2} {}".format(index, bc.decode()) for index, bc in p7_barcodes]
        else:
            p5_bc_items = ["{:>2} {}".format(index, bc) for index, bc in p5_barcodes]
            p7_bc_items = ["{:>2} {}".format(index, bc) for index, bc in p7_barcodes]

        # collect all individual and create items to insert into matrix by p5 barcode.
        p5_individual = []
        longest_individual_name = 0
        for _, p5_bc in p5_barcodes:
            items = []
            for _, p7_bc in p7_barcodes:
                try:
                    # valid individual
                    if self.dtype == bytes:
                        individual = self.get_individual(p5_bc, p7_bc).decode()
                    else:
                        individual = self.get_individual(p5_bc, p7_bc)
                    longest_individual_name = max(longest_individual_name, len(individual))
                except KeyError:
                    # invalid individual, leave cell empty
                    individual = empty
                items.append(individual)
            p5_individual.append(items)

        # get parameters for drawing the table
        spacing = 3
        # cell content width is either index + barcode, the longest name or the 'empty' entry,
        # whichever is the longest
        cell_width = max(6 + 2 + 1, longest_individual_name, len(empty)) + (2*spacing)
        columns = len(p7_bc_items)+1

        # create template for empty line
        line = ("{{:^{cw}}}|".format(cw=cell_width))*(columns)
        # format headline with p7 barcodes
        headline = line.format("", *p7_bc_items)
        toprule = line.format(*columns*[cell_width*"-"])

        # assemble line for each p5 barcode
        lines = []
        for p5_bc, items in zip(p5_bc_items, p5_individual):
            lines.append(line.format(p5_bc, *items))

        return "\n".join([headline, toprule]+lines)


def test():
    print("Testing barcode file parser")
    p = abspath("barcodes/barcodes.txt")
    dbc = DeBarcoder(p)
    print(dbc.to_str())
    print(dbc.get_individual_matrix())

if __name__ == "__main__":
    test()

