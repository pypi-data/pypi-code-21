
import collections
import string, pdb
from unidecode import unidecode

class OrderedSet(collections.MutableSet):

    def __init__(self, iterable=None):
        self.end = end = [] 
        end += [None, end, end]         # sentinel node for doubly linked list
        self.map = {}                   # key --> [key, prev, next]
        if iterable is not None:
            self |= iterable

    def __len__(self):
        return len(self.map)

    def __contains__(self, key):
        return key in self.map

    def add(self, key):
        if key not in self.map:
            end = self.end
            curr = end[1]
            curr[2] = end[1] = self.map[key] = [key, curr, end]

    def discard(self, key):
        if key in self.map:        
            key, prev, next = self.map.pop(key)
            prev[2] = next
            next[1] = prev

    def __iter__(self):
        end = self.end
        curr = end[2]
        while curr is not end:
            yield curr[0]
            curr = curr[2]

    def __reversed__(self):
        end = self.end
        curr = end[1]
        while curr is not end:
            yield curr[0]
            curr = curr[1]

    def pop(self, last=True):
        if not self:
            raise KeyError('set is empty')
        key = self.end[1][0] if last else self.end[2][0]
        self.discard(key)
        return key

    def __repr__(self):
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, list(self))

    def __eq__(self, other):
        if isinstance(other, OrderedSet):
            return len(self) == len(other) and list(self) == list(other)
        return set(self) == set(other)
    
def return_lines(inpath, outpath, term_list, num_lines=3, encoding='utf-8', debug=False):
    '''
    Takes a file containing text as input. Searches through file for terms in term_list. When a term
    is found, takes that line as well as num_lines surrounding that line, and adds to output file.

    Required options:
    inpath:    string, full filepath of input file
    outpath:   string, full filepath of output file
    term_list: list, terms to search for in input file
    num_lines: int, number of lines to return around each result. Passing 0 will return only the line of
               the found term. Passing 2 would return two lines above, and two below, as well as the original
               line, for a total of five lines.
    '''
    def prepare_for_search(search_list):
        '''
        Strips out punctuation, extra spacing, converts special characters, and converts to lower space. Can be used
        with a string or list.
        '''

        if isinstance(search_list,str):
            searchword_no_punc = "".join(char for char in search_list if char not in string.punctuation)
            searchword_no_punc = unidecode(searchword_no_punc)
            return searchword_no_punc.lower().strip()
        elif isinstance(search_list,list):
            out_list = []
            for searchword in search_list:
                searchword_no_punc = "".join(char for char in searchword if char not in string.punctuation)
                searchword_no_punc = unidecode(searchword_no_punc)
                out_list.append(searchword_no_punc.lower().strip())
            return out_list
        else:
            raise ValueError('must provide string or list of strings')
    
    def file_to_dict(file_path, encoding=encoding):
        '''
        Creates a dictionary from a file where the keys are line numbers and values are line strings
        '''
        with open(file_path, 'r', encoding=encoding) as f:
            line_dict = {}
            for line_num, line in enumerate(f):
                line_dict.update({line_num: line.strip()})
        return line_dict
    
    def add_to_output(line_num, outset, last_line, num_lines=num_lines):
        outset.add(line_num)
        for i in range(num_lines):
            up = line_num + i + 1
            down = line_num - i - 1
            if up <= last_line:
                outset.add(up)
            if down >= 0:
                outset.add(down)
        return outset
    
    if isinstance(term_list,str): term_list = [term_list]
    elif not isinstance(term_list,list): raise ValueError('must provide string or list of strings')
    
    search_list_str = 'Search list: ' + ', '.join(term_list)
    search_list = prepare_for_search(term_list) #strips out punctuation, etc.
    split_search_list = [term.split() for term in search_list] #divides multi-word terms into individual words
    first_word_set = {term_split[0] for term_split in split_search_list} #gets a set of the first words to search for
    infile_dict = file_to_dict(inpath)
    
    #If there are no lines in the file, exit and return zeroes
    if infile_dict == {}:
        if debug:
            print('{} is blank, cannot extract lines.'.format(inpath))
        return [0 for item in term_list]
    
    last_line = max([line for line in infile_dict])
    outset = set() #container for line numbers to be outputted
    full_match_count_list = [0] * len(term_list) #this is a counter for how many full matches, will be returned

    with open(inpath, 'r', encoding=encoding) as f_in:
        word_set = first_word_set
        match_count_list = [0] * len(term_list) #we need to count matches individually by term
        for line_num in infile_dict: 
            line = prepare_for_search(infile_dict[line_num]) #strip punctuation, etc. from search line
            word_list = line.split()
            for word in word_list:
                #Add 1 to the element of the match count list corresponding to a matched term word (addition part),
                #otherwise set match count back to zero (this is the multiplication part)
                match_count_list = [match_count * (term_split[match_count] == word) + (term_split[match_count] == word)
                                    for match_count, term_split in zip(match_count_list,split_search_list)]
                #If we've matched any of the terms completely
                if any([len(term_split) == match_count 
                        for match_count, term_split in zip(match_count_list, split_search_list)]):
                    outset = add_to_output(line_num, outset, last_line)
                    #Add to full match list
                    full_match_count_list = [full_match_count + (len(term_split) == match_count)
                                            for match_count, term_split, full_match_count
                                            in zip(match_count_list, split_search_list, full_match_count_list)]
                    #Set any fully matched back to zero
                    match_count_list = [match_count * (1 - (len(term_split) == match_count)) 
                                        for match_count, term_split in zip(match_count_list, split_search_list)]
                else:
                    word_set = {term_split[match_count] 
                                for match_count, term_split in zip(match_count_list, split_search_list)}
    
    with open(outpath,'w', encoding=encoding) as f_out:
        outlist = sorted(list(outset)) #puts lines in proper order
        f_out.write(search_list_str)
        f_out.write('\n')
        for pos, line_num in enumerate(outlist):
            if pos > 0:
                if outlist[pos - 1] != line_num - 1: f_out.write('\n') #split up sections for each match
            len_num = len(str(line_num)) #get length of line number, so that we can line up each line
            num_space = max(10 - len_num, 0) #set amount of spacing to include to left of line
            f_out.write('{}:'.format(line_num) + ' ' * num_space +  '{}'.format(infile_dict[line_num]))
            f_out.write('\n')
            
    return full_match_count_list

def filter_list(inlist, match=None, nomatch=None, remove=True):
    '''
    Returns outlist, inlist
    Takes inlist and finds items which contain match but do not contain nomatch. If remove=True, removes those
    items from inlist.
    '''
    assert not (match == None and nomatch == None)
    if isinstance(match, str):
        match = [match]
    if isinstance(nomatch, str):
        nomatch = [nomatch]
    if nomatch and match:
        q = [(i, n) for n, i in enumerate(inlist) 
                             if all(map(lambda x: x in i,match)) and all(map(lambda x: x not in i,nomatch))]
    elif nomatch:
        q = [(i, n) for n, i in enumerate(inlist) if all(map(lambda x: x not in i,nomatch))]
    else: #only match
        q = [(i, n) for n, i in enumerate(inlist) if all(map(lambda x: x in i,match))]
    if q != []:
        outlist, outindex = zip(*q) #zip(*) unzips
    else:
        outlist, outindex = ([],[])
    if remove:
            inlist = [item for index, item in enumerate(inlist) if index not in outindex]
    return outlist, inlist