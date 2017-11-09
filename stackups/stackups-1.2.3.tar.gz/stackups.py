#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Kenneth Carlton

stackups module - used mechanical endgineers/designers  to calculate clearances
between components that compose a machine, i.e., like a gearbox or 
transmission.

For more information about this module, please visit 
httm://www.newconceptzdesign.com
"""

__version__ = '1.2.3'
defaultfilename = 'stackups.stk'

import re
import math
import ast
import copy
import os.path
from fnmatch import fnmatch
import pprint
from colorama import Back, Style


class Stacks():
    '''A Stacks object is special type of python list.  The first item contains
    the title that you assign to that Stacks object.  The rest of the items are 
    Stack objects. 
    
    Examples
    ========
    
    >>> mystks = Stacks()  # create a new Stacks object.
    
    >>> mystks.load('C:\\projectXYZ\\mysavedstacks.stk")  # load a file 
    
    >>> mystks[3]  # view stack no. 3.  By the way, the Stack can be edited. 
    
    Create (i.e. instantiate) a new  Stacks object:
    
    >>> mystks2 = Stacks(title = 'My title for the stackups')
    
    Alternatively, you could use the filenew function that comes with this
    module and assign a filename at the same time that you instantiate your
    Stacks object (see the the documetion thereof for more info.)
    
    >>> mystks2 = filenew('transmission01.stk')  # filename is: transmission01.stk
     
    Start your 1st stack:
    
    >>> mystks2.append()  #  Creates new Stack object named mystks2[1]
    
    Add a Stackunit to your 1st stack (dimension is 3.154 +/- 0.015, 
    pn is 34N03142, and the name of this stack unit is Shoulder Width):
    
    >>> mystks2[1].append(3.154, .015, '34N03142, 'Shoulder Width')
    
    And add other Stackunit objects:
    
    >>> mystks2[1].append(-2.000, .005, '34N33000', 'Width')
    >>> mystks2[1].append(4.250, .015, '36N41222', 'OAL') 
    
    >>> mystks2[1]  # Results will be shown
    
    Methods
    =======
    
    Use the help() method (i.e. Stacks.help()) to see available methods. 
    '''
    def __init__(self, stacks=[], 
                 title="Stacks title: None"):
        # default_Stack_title... defined here, for Stack init arg, and within
        # Stack init's definition; keep the value the same in all three places
        self.default_Stack_title = "Stack title: None"
        self.sync_on = True
        self.stacks = []
        if isinstance(stacks, Stacks):
            self.stacks = stacks.stacks
        elif stacks and isStacks(stacks):
            for x in stacks:
                if isinstance(x, dict) and 'title' in x:  # main title of all stacks
                    self.stacks.insert(0, x)
                else:
                    self.stacks.append(Stack(x, stacks=self.stacks, sync=False))
        else:
            self.stacks = [{'title':title}]
        self.indx = -1
        if len(self.stacks) > 1:
            self.sync()
        self.filename = defaultfilename
        if stacks and not isStacks(stacks):
            print("Error: Data not accepted.  The data's errant structure prevents")
            print("creating a suitable Stacks object.")
                              
    def __repr__(self):
        if _s['alter'] == True:
            return self.__str__()
        if self.stacks:
            st = ['[']
            for x1 in self.stacks:
                x2 = repr(x1) + ',\n'
                st.append(x2)
            x3 = ''.join(st)
            x3 = x3[:-2] + ']'
            x3 = re.sub(r'{', '  {',  x3)  # pretty things up
            x3 = re.sub(r'\[\[  {', '[[{',  x3)
            x3 = re.sub(r'\[  {', ' [{', x3)
            x3 = re.sub(r" \[{'main", "[{'main", x3)
            x3 = re.sub(r"'j':  {", "'j':{", x3)
            return x3
        else:
            return '[]'

    def __str__(self): 
        st = []
        for x1 in self.stacks:
            if isinstance(x1, dict):
                x2 = '\n' + x1['title'] + '\n\n'  # x1 is the main title
            else:
                x2 = str(x1) + '\n'
            st.append(x2)
        x3 = ''. join(st)
        return x3

    def __getitem__(self, key):
        self.s = key
        return self.stacks[key]

    def __setitem__(self, key, value):
        if isinstance(value, Stack):
            self.stacks[key] = value
        elif isStack(value):
            self.stacks[key] = Stack(value)

    def __delitem__(self, key):
        if key != 0:
            del self.stacks[key]

    def __contains__(self, item):
        if item in self.stacks:
            return True
        else:
            return False

    def __missing__(self, key):
        pass

    def __next__(self):
        if self.indx > len(self.stacks) -2:
            self.indx = -1
            raise StopIteration
        self.indx += 1
        return self.stacks[self.indx]

    def __iter__(self):
        return self

    def __len__(self):
        return len(self.stacks)
        
    def __mul__(self, other):
        b = []
        if isinstance(other, int) or isinstance(other, float):
            for stk in self.stacks:
                if 'title' in stk:
                    b.append(stk)
                else:
                    b.append(stk * other)
        return Stacks(b)
            
    def __rmul__(self, other):
        return self.__mul__(other)
        
    def __truediv__(self, other):
        return self * (1/other)
        
    def __rtruediv__(self, other):
        print('division with Stacks as denominator not allowed')
        
    def _update(self, *args, **kwargs):
        '''Updates data for a stack unit.
        
        Returns
        =======
        
        out : tuple
            Output is typically used by other internal functions.  Output is 
            either a tuple like (b, max value of su) or (b, 0, sudic)
            depending on what internal function called _update.  b is a list of
            user supplied su values, and sudic is a dictionary of su integer
            values vs corresponding stackunits. 
            
        Examples
        ========
        
        >>> stks._update(3.25, .015, su=9)  # _update d and dt stackunit 9.
        
        >>> stks._update(dt=.005, su=9)  # _update the tolerance of stackunit 9.

        >>> stks._update('99N3424', su=4)  # _update the pn of stackunit 4.
        
        >>> stks._update('99N3424', 'gear width', su=4) # _update the name of stackunit 4
        '''
        sudic = self.su()
        data = {**kwargs, **self._parse_data(args)}  # parse the input parameters that user provides   
        pn = data.get('pn', 'pn_unknown')
        n = data.get('n', 'unique description required')
        # if user supplied pn and n, does an su already exist?  If so, set su_old for it
        su_old = n_already_exists(pn, n, self._pndic(returnType='dict'))
        b = []
        if (su_old and 'su' in data and (isinstance(data['su'], tuple) or
                isinstance(data['su'], list)) and len(data['su']) > 1):
            pass  # user supplied data doesn't make sense; more than 1 su value not allowed when su_old exists
        elif (su_old and 'su' in data and (isinstance(data['su'], tuple) or 
                isinstance(data['su'], list)) and len(data['su']) == 1):
            b.append(su_old * sign(data['su'][0]))  # if user gave a sign to his su, get it
        elif su_old and 'd' in data:  # get sign from d
            b.append(su_old * sign(data['d']))
        elif su_old and 'su' in data and isinstance(data['su'], int):  # get sign from su
            b.append(su_old * sign(data['su']))  # like 2 steps above
        elif su_old:  # no su, no d, etc.; just _update based on other user supplied data
            b.append(su_old)
        elif 'su' in data and isinstance(data['su'], int) and abs(data['su']) in sudic:
            b.append(data['su'])
        elif 'su' in data and (isinstance(data['su'], tuple) or isinstance(data['su'], list)):
            for x in data['su']:
               if abs(x) in sudic:
                   b.append(x)
        if b:  # b is a list of su values that user wants modified
            for x in b:
                su_ = abs(x)
                sudic[su_]['d'] =   abs(data.get('d', sudic[su_]['d']))
                sudic[su_]['dt'] =  abs(data.get('dt', sudic[su_]['dt']))
                ptno = data.get('pn', sudic[su_]['pn'])
                if (ptno.find('*') < 0 and ptno.find('?') < 0 and 
                        ptno.find('[') < 0 and ptno.find(']') < 0):
                    ptno = data.get('pn', sudic[su_]['pn'])
                    sudic[su_]['pn'] =  ptno
                if 'n' in data:
                    sudic[su_]['n'] = data['n']
                sudic[su_]['sigma'] =  abs(data.get('sigma', sudic[su_]['sigma']))
        # 'set_flag' gets set at, and only at, Stack.append to True
        if sudic and 'set_flag' in data and data['set_flag'] == True:
            return b, max(list(sudic.keys()))
        elif 'set_flag' in data and data['set_flag'] == True:
            return (b, 0)
        else:
            return (b, 0, sudic)
           
    def _parse_data(self, args):
        ''' Called upon by other functions withn this module.  Used to sort user
        input.

        Parmeters
        =========

        args : tuple
            A tuple of floats and strings that might be input by the user.  
            This data is parsed.  Results are added to a dictionary.  args are
            dimensions, tolerances, part numbers, dimension descriptions.

        Returns
        =======

        out : dictionary
           Typical values: d, dt, pn, n.  If a user didn't supply a value for 
           any or all of these, then it isn't put into the dictionary.
        '''

        tuples = []  # set up collection container for any lists in args
        floats = []  # set up collection container for any floats >> OR INTS << in args
        strs = []  # set up collection container for any strings in args
        dicts = []
        stackunits = []  # <<<< Note to self: I didn't employ this.  Should I?
        for arg in args:
            if isinstance(arg, tuple):
                tuples.append(arg)
            if isinstance(arg, float) or isinstance(arg, int):
                floats.append(float(arg))
            if isinstance(arg, str):
                strs.append(arg)
            if isinstance(arg, dict):
                if 'title' in arg:
                    pass
                else:
                    dicts.append(arg)
        if dicts:
            d =  dicts[0].get('d', 0)
            dt =  dicts[0].get('dt', 0)
            pn =  dicts[0].get('pn', 'None')
            n =  dicts[0].get('n', 'Description missing! Expect program errors.')
            i = dicts[0].get('i', 0)
            sigma = dicts[0].get('sigma', 6)
            i = dicts[0].get('i', 0)
        elif stackunits:
            d =  stackunits[0]['d']
            dt =  stackunits[0]['dt']
            n =  stackunits[0]['n']
            pn =  stackunits[0]['pn']
            sigma = stackunits[0]['sigma']
            i = stackunits[0]['i']
        elif tuples:
            t0 = tuples[0]  # if more that one list, only use the first
            if (all((isinstance(item, float) or isinstance(item, int)) for item in t0)
                and len(t0) == 2):
                t00 = abs(t0[0])
                t01 = abs(t0[1])
                d = (t00 + t01)/2
                dt = abs(t00 - t01)/2
        elif floats:
            if len(floats) == 3:
                d = ((floats[0] + floats[1]) + (floats[0] + floats[2]))/2
                dt = abs(((floats[0] + floats[1]) - (floats[0] + floats[2]))/2)
            elif len(floats) == 2:
                d = floats[0]
                dt = abs(floats[1])
            elif len(floats) == 1:
                d = floats[0]
        if len(strs)>0:
            if len(strs) == 2:
                pn = strs[0]
                n = strs[1]
            elif len(strs) == 1:
                pn = strs[0]
        parsed_data = {}
        for k in ['d', 'dt', 'pn', 'n', 'i', 'sigma']:  # add these items, if exists, to the new dic
            try:
                parsed_data[k] = eval(k)
            except:
                pass
        return parsed_data  
    
    def _pn(self, *args, **kwargs):
        '''Show Stackunit data according to part numbers.  This function also
        behaves like the *update* method and thus you can update dimensions,
        tolerance, etc. with it.
        
        Parameters
        ==========
        
        ptno : string
            Enter a part no. to report only info from one part, '*' to report
            from all parts, and used wild cards to filter througe parts'
            
        returnType : ['stdout', 'dict', 'str', 'stdout2']
            'stdout' prints to the computer monitor.  'dict' outputs the
            dictionary object from which data derived.  'str' outputs a string
            object which can be piped to a text file.  'stdout2' shows the
            output from 'dict' in pprint format.
        
        Examples
        ========
        
        >>> stks.pn()  # show info for all parts  (use default pt no. = '*')
        
        >>> stks.pn('33*')  # show info for only part starting with the numbers 33
        
        >>> stks.pn('37N45?A')  # match '37N457A', '37N452A', '37N45BA', etc.
        
        # A bit more technical, not very usefull, but available:
        
        >>> stks.pn(returnType='dict')  # return a dictionary object
        
        Values can be changed for a given Stackunit as long as an su value is
        supplied:
        
        >>> stks.pn(3.55, .010, 'PN001' 'Overall length', sigma=6, su=5)
        
        Note: the dimension (d) must preceed the tolerance (dt), and the part
        number (pn) must preceed the dimension name (n); that is, 3.55 before 
        .010 and 'PN001' before 'Overall length'.  And also note: assigned 
        parameters, that is, sigma=6 and su=5, must come after all the 
        unassigned parameters (d, dt, pn, and n).
        
        Other ways of making changes:
        
        >>> stks.pn(n='Shoulder to rt. end', dt=.005, su=5)
        
        >>> stks.pn(3.600, su=5)
        '''
        caughtsu = 0
        data = {**kwargs, **self._parse_data(args)}  # make a dic of user's input
        returnType =  data.get('returnType', 'stdout')  # default is 'stdout'
        ptno = data.get('pn', '*')  # default is '*', i.e., part no.
        # if values supplied, and 'su=' value provided, update 
        # tup = (b, 0, sudic) ??
        tup = self._update(*args, **kwargs)  
        if 'su' in kwargs and isinstance(kwargs['su'], int) and ptno == '*':
            sudic = tup[2]
            ptno = sudic[kwargs['su']]['pn']
            caughtsu = kwargs['su']

        # set up a whereused dic (wudic) with su vs Stack numbers, where Stack
        # numbers are the Stacks position of the Stack in which an su value is used.
        # A wudic has this form:
        # {2: [1, 3, 5], 3: [2], 4: [2, 4, 6], 5: [1, 5] ...}
        keys = self.su().keys()
        wudic = {}
        for stknum, stk in enumerate(self.stacks):
            if stknum == 0:
                pass
            else:
                for su in stk:
                    for k in keys:
                        if 'su' in su and su['su']==k and k not in wudic:
                            wudic[k] = [stknum]
                        elif 'su' in su and su['su']==k and stknum not in wudic[k]:
                            wudic[k].append(stknum)                           
        pndic = self._pndic(returnType='dict')

        # filter names... only report on these names              
        fnames = [fname for fname in pndic.keys() if fnmatch(fname, ptno)] 

        # ref: https://docs.python.org/3/library/stdtypes.html?highlight=items#dict.items
        d = []  # collection list.
        for p in sorted(fnames):
            b = [] 
            c = []
            # pndic[p].items() = dict_items([(su1, stkunt1), (su2, stkunt2), ... ])
            # b = [[(su1, stkunt1), (su2, stkunt2 ), ...]]
            b.append(sorted(pndic[p].items(), key=lambda t: t[0])) 
            for x in b[0]:
                if not caughtsu:
                    c.append((x[1], wudic[x[1]['su']]))
                elif x[1]['su'] == caughtsu:
                    c.append((x[1], wudic[x[1]['su']]))         
            d.append((p, c))
            
        # https://www.youtube.com/watch?v=MGD_b2w_GU4
        if returnType == 'stdout2':
            pprint.pprint(d, indent=2) 
        elif returnType == 'dict':
            return d
        elif returnType == 'stdout' or returnType == 'str':
            str2 = ''
            for x in d:
                str2 += '\n ' + x[0] + '\n'
                for y in x[1]:  # go through each stack unit
                    frmt1 = '  {}, {}, {:.4f} \u00b1 {:.4f}, {}\u03c3, at:{}\n'
                    frmt2 = '  {}, {}, {:.4f} \u00b1 {:.4f}, {}\u03c3,\n      at:{}\n'
                    if len(frmt1.format(y[0]['su'], y[0]['n'], y[0]['d'], 
                                        y[0]['dt'], y[0]['sigma'], y[1])) < 77:  
                        str2 += frmt1.format(y[0]['su'], y[0]['n'], y[0]['d'], 
                                            y[0]['dt'], y[0]['sigma'], y[1])
                    else:
                        str2 += frmt2.format(y[0]['su'], y[0]['n'], y[0]['d'], 
                                            y[0]['dt'], y[0]['sigma'], y[1])
                    str3 = '      '
                    ll = 6  # len of str3, and amount of indent
                    for z in y[0]:  # go through each item of the stack unit
                        if (z != 'su' and z != 'd' and z != 'dt' and z != 'n' 
                                and z != 'pn' and z != 'sigma'):
                            if isinstance(y[0][z], float):
                                strt = '{}={:.4f}, '.format(z, y[0][z])
                            else:
                                strt = '{}={}, '.format(z, y[0][z]) 
                            if ll + len(strt) > 75:
                                str3 += '\n      ' + strt
                                ll = 6 + len(strt)   
                            else:
                                str3 += strt
                                ll += len(strt)
                    if str3 != '      ':  # 6 spaces
                        indx = str3.rfind(',')
                        str3 = str3[:(indx)]
                        str2 += str3 + '\n'  
            if returnType == 'str':                        
                return str2
            else:
                print(str2)
        
    def _pndic(self, ptno='*', depth=None, returnType='stdout'):
        '''Report Stackunits organized by part nos.
        
        Parameters
        ==========
        
        ptno : string
            Enter a part no. to report only info from one part, '*' to report
            from all parts, and used wild cards to filter througe parts'
            
        depth : int
            1 or None.  If 1, then show part nos. only.
            
        returnType : ['stdout', 'dict', 'str']
        
        Examples
        ========
        
        >>> stks._pndic()  # show info for all parts
        
        >>> stks._pndic('33*')  # show info for only part starting with the numbers 33
        
        >>> stks._pndic('37N45?A')  # match '37N457A', '37N452A', '37N45BA', etc.
        
        >>> stks._pndic(returnType='dict')  # return a dictionary object
        '''
        pndic = {}
        for stackup in self.stacks[1:]:
            for st2 in stackup[1:]:
                if not st2['pn'] in pndic:
                    pndic[st2['pn']] = {st2['su']:st2}
                elif not st2['su'] in pndic[st2['pn']]:
                    pndic[st2['pn']][st2['su']] = st2
                    
        # filter names... only report on these names
        # (https://docs.python.org/3/library/fnmatch.html)         
        fnames = [fname for fname in pndic.keys() if fnmatch(fname, ptno)]            
                    
        pndic_filtered = {}
        for x in fnames:
            pndic_filtered[x] = pndic[x]

        if returnType == 'stdout':  
            pprint.pprint(pndic_filtered, depth=depth)
        elif returnType == 'dict':
            return pndic_filtered
        elif returnType == 'str':
            return pprint.fprint(pndic_filtered, depth)
        
    def _search_floats(self, searchfor, percent_accuracy=3):
        '''Search for the float or int "searchfor" in the d and dt fields of 
        each Stackunit object.
        
        Parameters
        ==========
        
        searchfor : float or int
            Value to search for
            
        percent_accuracy : float or int
            Allow this amount of variance to obtain a hit.  Default: 2%
                
        Returns
        =======
        
        out : list
            A list of Stackunit objects whose description contain the float/int
            that matches "searchfor".
            
        Examples
        ========
        
        stks.search(7.325)
        '''
        if len(self.stacks)==1:  # i.e., No Stacks object exist... just a main title filler
            stacks = ['row 0 filler', self.stack]  # To handle a Stack object
        else: 
            stacks = self.stacks
        if not isinstance(searchfor, (float, int)):
            return []
        minacc = searchfor * (100 - percent_accuracy)/100
        maxacc = searchfor * (100 + percent_accuracy)/100
        lst = []
        for stk in stacks[1:]:
            for unit in stk[1:]:
                if minacc <= unit['d'] <= maxacc and unit not in lst:
                    lst.append(unit)
                if minacc <= unit['dt'] <= maxacc and unit not in lst:
                    lst.append(unit)
                if (minacc <= unit['sigma'] <= maxacc and unit not in lst
                        and 6 != unit['sigma']):
                    lst.append(unit)
        return lst
        
    def _search_strs(self, searchfor):
        '''Search for a text string within the pn and descrip fields of each
        Stackunit object.
        
        Parameters
        ==========
        
        searchfor : str
            Text to search for
            
        Returns
        =======
        
        out : list
            A list of Stackunit objects whose description contain text that
            matches "searchfor".
            
        Examples
        ========
        
        stks.search('Shaft')
        '''
        if len(self.stacks)==1:  # i.e., No Stacks object exist... just a main title filler
            stacks = ['row 0 filler', self.stack]  # To handle a Stack object
        else: 
            stacks = self.stacks
        if not isinstance(searchfor, str):
            return []
        lst = []
        searchfor = '*' + searchfor + '*'
        for stk in stacks[1:]:
            for unit in stk[1:]:  # ignore 1st item. It's the title
                searchforSq = re.sub("[^a-zA-Z0-9*?]", '', searchfor).upper() 
                nSq = re.sub("[^a-zA-Z0-9*?]", '', unit['n']).upper() 
                pnSq = re.sub("[^a-zA-Z0-9*?]", '', unit['pn']).upper() 
                if fnmatch(nSq, searchforSq) and unit not in lst:
                    lst.append(unit)
                if fnmatch(pnSq, searchforSq) and unit not in lst:
                    lst.append(unit)
        return lst
            
    def _sulist2str(self, sulist):
        ''' Convert a list of Stackunit objects to a human readable list of 
        those objects.  This function returns a string.  This string needs to be
        printed, via print, to properly display the list.
    
        Parmameters
        ===========
        
        sulist : list
            Each element of the list must be a Stackunit object
            
        Returns
        =======
        
        out : str
            Print the returned string to see human readable list of Stackunits.
        '''
        s = ''  # s will collect strings
        width=80
        d_s = []   # list of floats 
        dt_s = []  # list of floats
        su_s = []  # list of ints
        sigma_len = 0
        for st2 in sulist:
            su_s.append(st2['su'])  # collect all the su_s (ints)
            d_s.append(st2['d'])  # collect all the d_s
            dt_s.append(st2['dt'])  # collect all the dt_s
            if len(str(st2['sigma'])) > sigma_len:
                sigma_len = len(str(st2['sigma']))
        su_s_max = max(su_s)  # max value of su
        d_s_max = max(d_s)    # max value of d
        dt_s_max = max(dt_s)  # max value of dt
        suw = len(str(abs(su_s_max)))  # column width for su values (int)
        if suw==1:
            suw = 2
        dw = len(str(int(abs(d_s_max)))) + _s['precision'] + 2  # column width for d
        dtw = len(str(int(abs(dt_s_max)))) + _s['precision'] + 1  # column widith for dt
        pn_n_w = width - (suw + 2 + dw + 3 + dtw + 5)  # column width for pn & n
        ssuw = str(suw)
        ssigma = str(sigma_len)
        sdw = str(dw)
        sdtw = str(dtw)
        spw = str(_s['precision'])
        heading = ('{:>' + ssuw + '} {:>' + ssigma + '} {:^' + sdw + '}  {:^' + sdtw
                   + '}   {:<}').format('su', '\u03c3', 'd', 'dt', 'pn & n')
        format_str = (u'{:'+ ssuw + 'd} {:>' + str(sigma_len)
                  + '}{:>'+ sdw + '.'+ spw + 'f} \u00b1 {:'+ sdtw + '.'
                  + spw + 'f} {}')
        s += heading + '\n'
        d_sum = 0.0
        dt_sum = 0.0
        sig_sum = 0.0
        for st2 in sulist:
            su_ = st2['su']
            sigma = st2['sigma']
            sstr = str(sigma)
            d = st2['d'] # multiply times 
            dt = st2['dt'] # multipy by abs(m)  
            pn_and_n = (st2['pn'] + ', ' + st2['n'])[:pn_n_w]  # [:pn_n_w] truncates
            d_sum += d   # besides print, accumlate sum of d_s
            dt_sum += dt   # besides print, accumlate sum of dt_s
            s += format_str.format(abs(su_), sstr, abs(d), dt, pn_and_n) + '\n'
        return s

    def _wudic(self):
        '''  Create a whereused dic (wudic).  A wudic will have su (int) values
        vs a list the stacks in which that stack unit is used.  
        wudic will have the form: 
        {2: [1, 3, 5], 3: [2], 4: [2, 4, 6], 5: [1, 5] ...} 
        
        Returns
        =======
        
        out : dict
            dictionary of su values vs stack nos.
        '''
        wudic = {}
        keys = self.su().keys()
        for stknum, stk in enumerate(self.stacks):
            if stknum == 0:
                pass
            else:
                for su in stk:
                    for k in keys:
                        if 'su' in su and su['su']==k and k not in wudic:
                            wudic[k] = [stknum]
                        elif 'su' in su and su['su']==k and stknum not in wudic[k]:
                            wudic[k].append(stknum)
        wu_keys = sorted(wudic.keys())
        return wudic
            
    def a(self, stack=[], title='use default_Stack_title'):
        ''' Same as append'''
        if title == 'use default_Stack_title':
            title = self.default_Stack_title.format(len(self.stacks))
        self.append(stack, title)
            
    def append(self, stack=[], title='use default_Stack_title' ):        
        '''Append a Stack to other Stacks objects.  (Note that the functionality
        of this append method is different to that of Stack.  See Stack.append 
        for more info.)
        
        Parameters
        ==========
        
        stack : {list, Stack, or int}
            1.  If a list is provided, it must equate to a stack.  2.  A 
            Stack oject is acceptable.  3.  If an integear, then
            is the su value for a Stackunit
            
        stacktitle : str
            Name of the stack
            
        Examples
        ========

        >>> stks.append()  # starts a new stack
        
        >>> stks.append(title='Gap btwn brg and gear')
        '''
        if title == 'use default_Stack_title':
            title = self.default_Stack_title.format(len(self.stacks))
        b = []
        sudic = self.su()
        pndic = self._pn(returnType='dict')
        suoldlist = []
        if sudic:
            sumax = max(list(sudic.keys()))
        else:
            sumax = 0
        sunew = sumax + 1
        # go through stack, copy elements to b, assign brand new su values
        if stack and isinstance(stack, Stack):
            stack = stack.tolist()
              #stktmp = stack.tolist()                    # aaaaaaaa
              #stktmp[0]['title'] = '[' + str(len(self.stacks)) + '] ' + stktmp[0]['title']   
              #self.stacks.append(Stack(stack.tolist()))  # aaaaaaaa
              #return                                     # aaaaaaaa
            #for su in stack:
            #    if 'title' in su:
            #        b.append(copy.deepcopy(su))
            #    else:
            #        b.append(copy.deepcopy(su.stackunit))
            #    if 'su' in su:
            #        b[-1]['su'] = sunew
            #        sunew += 1
        if stack and isStack(stack):
            for su in stack:
                b.append(copy.deepcopy(su))
                if 'su' in su:
                    b[-1]['su'] = sunew
                    sunew += 1
        else:
            print('Error: Data not accepted.  Not suitable Stack data.')
            return
        # b now created.  In stack b, see if pn/n combo already exist.  
        # If does exist, replace new su with old su

        for  b2 in b:
            if 'pn' in b2:
                suold = n_already_exists(b2['pn'], b2['n'], pndic)
                if suold:
                    b2['su'] = suold
                    test1 = math.isclose(b2['d'], sudic[suold]['d'], rel_tol=.0005)
                    test2 = math.isclose(b2['dt'], sudic[suold]['dt'], rel_tol=.0005)
                    test3 = math.isclose(b2['sigma'], sudic[suold]['sigma'], abs_tol=.005)
                    if (not test1 or not test2 or not test3):
                        if suold not in suoldlist:
                            print('discrepancy: \n')
                            print(Stackunit(b2))
                            print()
                            print(sudic[suold])
                            print()
                        suoldlist.append(suold)
        #if title != 'Use the "stacktitle" method to assign a stacktitle':
        #    b[0]['title'] = title
        b_as_Stackobject = Stack(b)
        # attach same obj, self.stacks, from parent to child... allows sync w/ parent
        b_as_Stackobject.stacks = self.stacks  
        if title[:37] != self.default_Stack_title[:37]:  # if 1st 37 chars match
            b_as_Stackobject.title(title)

        self.stacks.append(b_as_Stackobject)
        if self.sync_on:
            self.sync()
        if _s['autoprint']:
            print(self)
            
    def append_obs(self, stack, title='use default_Stack_title'):
        if isinstance(stack, Stack):
            self.stacks.append(stack)
        if self.sync_on:
            self.sync()
        if _s['autoprint']:
            print(self)
        
    def e(self, *stack):
        ''' Same as the *extend* method except that this method also prints
        out the stacks and thus also shows the extended items.'''
        self.extend(*stack)
            
    def extend(self, *stack):
        '''Append a stack (Stack object), list of stacks, or a Stacks object.
         
        Parameters
        ==========
        
        stack : Stack object or list thereof
            A list of stacks, i.e., [stk1, stk2, ... stkN] or an instance of a
            Stacks object..
            
        Examples
        ========
        
        >>> stks.extend([mystack1, mystack2, mystack3])
        
        The above example is how a normal extend method works for a list.  But
        for this method, this works also:
        
        >>> stks.extend(mystack1, mystack2, mystack3)
        
        If you have group of stacks from some other project:
        
        >>> stks.extend(project2stacks)  # project2stacks is an instance of Stacks
        
        Result: all the stacks from this other project are added to your stacks
        '''
        ap, _s['autoprint']  = _s['autoprint'], False
        for st in stack:
            if st == self:
                print("Cannot extend self.")
            elif isinstance(st, Stack) or isStack(st):
                self.append(st)
            elif isinstance(st, Stacks):
                stlst = self.tolist()
                stl2 = st.tolist()
                stlst.extend(stl2[1:])  # combines original list and new list
                temp = Stacks(stlst)    # convert to a Stacks object
                self.stacks = temp.stacks
            elif isStacks(st):
                stlst = self.tolist()
                stlst.extend(st[1:])  # combines original list and new list
                temp = Stacks(stlst)    # convert to a Stacks object
                self.stacks = temp.stacks
            elif isinstance(st, list):
                self.extend(*st)
            else:
                print("Not valid input.")
        _s['autoprint'] = ap
        if _s['autoprint']:
            print(self)

    def help(self):
        '''List of methods belonging to Stacks:'''
        print()
        print('Methods:')
        print('   append  a  Append a Stack to a Stacks object or a Stackunit ot a Stack.') 
        print('   extend  e  Same as above, but append multiple objects simultaneously.')
        print('   insert  i  Insert a Stackunit into the middle of a Stack.')  
        print('   search  o  Search for a part no., description, dimension, etc.')
        print('   update  u  Update a dimension, tolerance, part no, etc. of a Stackunit.')
        print('   invert     Put a Stack in reverse order')
        print('   jog     j  Change the direction of a Stackunit within a particular Stack.')
        print('   load       Load stored stackup data into memory for editing.')
        print('   move    m  Move a Stack within a Stacks object or a Stackunit within a Stack.')
        print('   pop        The same as pop in a regular Python list.')
        print('   renamepn   Rename all occurances of a pt. no. to a new pt. no.')
        print('   save       Save to a data file or to a report file (extension: stk or txt)')
        print('   su         Return a dictionary of su values (ints) and their titles.')
        print('   sync       Synchronize data.  (this is run automatically.)')
        print('   title      Set the title for a Stacks object or for a Stack object.')
        print('   titles     Show the title of every stack')
        print('   tolist     Converts a Stacks or Stack object to a list object.')
        print('   whereused  wu  Show in what Stacks that Stackunits are used.')
        print()
        print('Methods only available for Stack objects are: invert, jog, and update.')     
        print('Shortcut keys are a, e, i, o, etc.  The action a method performs depends whether')
        print('a Stack or Stacks object calls it.  To obtain more specific info about a method:')
        print()
        print('>>> help(Stacks.append)')
        print()
        print('or for a Stack object:')
        print()
        print('>>> help(Stack.append)')
        print()
        print("Alter output (e.g. unit decimal places), via Stacks' settings function:")
        print()
        print('>>> settings()')
        
    def i(self, row, stack=[], title='use default_Stack_title'):
        '''Same as *insert*'''
        self.insert(row, stack, title)
        
    def insert(self, row, stack=[], title='use default_Stack_title'):
        '''Insert a Stack'''
        if title == 'use default_Stack_title':
            title = self.default_Stack_title.format(row)
        self.append(stack, title)
        self.move(10000, row)
        if _s['autoprint']:
            print(self)      
        
    def m(self, fromrow, torow):
        ''' Same as the *move* method.'''
        self.move(fromrow, torow)          
               
    def move(self, fromrow, torow):
        '''Move Stacks objects, or Stack objects, from one position in the list
        to another.  
        
        Parameters
        ==========
        
        fromrow : int or list of two ints
            The row you want to move from.  If fromrow is a list, move rows
            staring with the first row listed up to, and including, the last
            row listed.
            
        torow : int
            The row you want to move to.
            
        Examples
        ========
        
        In dealing with a *Stacks* object:  Move stack 5 to to postion 2 in the 
        list of stacks:
        
        >>> stks.move(5, 2)
        
        In dealing with a *Stacks* object:  Move stacks 2, 3, 4, and 5 to to 
        position 7 of the stacks:
        
        >>> stks.move([2, 5], 7)
        
        In dealing with a *Stack* object:  Within stack 3, move stackunit at row 
        5 to row 2:
        
        >>> stks[3].move(5, 2)
        
        In dealing with a *Stack* object:  Within stack 3, move stackunits at 
        rows 2, 3, 4, and 5 to row 7:
        
        >>> stks[3].move([2, 5], 7)        
        '''
        j_as_list = []
        if self.__class__.__name__ == 'Stacks':
            listroot = self.stacks
            flag = False
            j_as_list.extend(range(0, len(self.stacks))) # for Stacks, this of no use... just a place holder
        elif self.__class__.__name__ == 'Stack':
            listroot = self.stack
            flag = True
            for x in sorted(self.stack[0]['j'].keys()):
                j_as_list.append(self.stack[0]['j'][x])  # use this list to manipulate a dict
        else:
            print('unknown error involving the move method')
        l = len(self)
        if hasattr(fromrow, '__iter__') and torow < fromrow[0]:  # i.e., if fromrow is a list or tuple
            if torow < 1:
                torow = 1
            if fromrow[0] != 0 or torow != 0:
                if torow < fromrow[0]:
                    r = torow
                else:
                    r = torow -1
            for x in range(fromrow[0], fromrow[1] + 1):
                listroot.insert(r, listroot.pop(x))
                j_as_list.insert(r, j_as_list.pop(x))
                r += 1    
        elif hasattr(fromrow, '__iter__') and fromrow[1] < torow:  #ok
            #if torow > (l - 1):
            #    torow = l - 1
            if fromrow[0] != 0 or torow != 0:
                if torow < fromrow[0]:
                    r = torow
                else:
                    r = torow -1
            for x in range(fromrow[0], fromrow[1] + 1):
                listroot.insert(r, listroot.pop(fromrow[0]))
                j_as_list.insert(r, j_as_list.pop(fromrow[0]))
        elif isinstance(fromrow, int):
            if fromrow > (l - 1):
                fromrow = l - 1
            if fromrow < 1:
                fromrow = 1
            if torow < 1:
                torow = 1
            if fromrow != 0 or torow != 0:
                if torow < fromrow:
                    r = torow
                else:
                    r = torow -1
                listroot.insert(r, listroot.pop(fromrow))
                j_as_list.insert(r, j_as_list.pop(fromrow))
        if flag:
            for key, value in enumerate(j_as_list):
                self.stack[0]['j'][key] = value
        if _s['autoprint']:
            print(self)
            
    def o(self, searchfor='*'):
        '''Same as "search".  Why "o"?  Think of the roundness of a magnifying
        glass.'''
        self.search(searchfor)
            
    def load(self, filename):
        global _s
        # if len(self) == 1:  # next 2 lines added 10/25/2017
        #    flag = True
        f = load(filename)
        if isinstance(self, Stack) and isinstance(f, Stackunit):
            self.append(f)
        elif isinstance(self, Stack) and isinstance(f, Stack):
            if len(self) == 1:
                self.stack == f.stack
            else:
                self.append(f)
        elif isinstance(self, Stacks) and isinstance(f, Stack):
            self.append(f)
        elif isinstance(self, Stacks) and isinstance(f, Stacks):
            if len(self) == 1:
                self.stacks = f.stacks
            else:
                self.extend(f)
        # below lines added 10/25/2017
        # if isinstance(self, Stack) and flag and 'settings' in self.stack[0]:
        #    _s = self.stack[0]['settings']
        # if isinstance(self, Stacks) and flag and 'settings' in self.stacks[0]:
        #    _s = self.stacks[0]['settings']

    def pop(self, row=None):
        '''Remove the item at the given position in the list, and return it. If
        no index is specified, stks.pop() removes and returns the last item in 
        the list.
        '''
        if row != None: # and row != 0:
            tmp = self.stacks[row]
            del self.stacks[row]
            return tmp
        elif row == None:
            tmp = self.stacks[-1]
            del self.stacks[-1]
            return tmp
                 
    def renamepn(self, frm, to):
        '''Change a part no. from one no. to another.
        
        Parameters
        ==========
    
        frm : str
            The part no. to change from
            
        to : str
            The part no. to change to  
        '''
        sudic = self.su()
        pndic = self._pndic(returnType='dict')
        flag = False
        if frm in pndic and to in pndic: # if part no. "to" exist, verify OK to change.
            for su_of_t in pndic[to]:
                for su_of_f in pndic[frm]:
                    if nSquished(pndic[to][su_of_t]['n']) == nSquished(pndic[frm][su_of_f]['n']):
                        print(str(to) + " already exists, and that's OK, but"
                              + " there is a clash with")
                        print("dimension names: '" + pndic[frm][su_of_f]['n'] + "'")
                        flag = True
        for k in sudic:
            if sudic[k]['pn'] == str(frm) and not flag:
                sudic[k]['pn'] = str(to)
                
    def renumber(self, starting_su=1):
        ''' Renumber the i values of the stackups.
        
        Parameters
        ==========
    
        starting_su : int
            Starting value for su
        '''
        pndic = self._pndic(returnType='dict')
        su_new = int(starting_su)
        oldI2newI = {}
        ks = sorted(pndic.keys())  # ['PN001', 'PN5054', 'PN005', ...]
        for k in ks:  # k = 'PN001', ...
            lst = []
            for su_ in pndic[k]:  #  e.g., su_= 3 in {3: {'d': 9.34, 'dt': 0.01, 'n': 'OAL'}, 6: {'d':4.125, ...}, ...}
                lst.append((pndic[k][su_]['d'], su_))  # [(9.34, 3), (4.125, 6), ...]
            slst = sorted(lst)  # [(4.125, 6), (9.34, 3), ...]
            for sl in slst:
                oldI2newI[sl[1]] = su_new  # {6:1, 3:2, ...}  old "su"s vs new "su"s
                su_new += 1
        sudic = self.su()
        for k in oldI2newI:
            sudic[k].stackunit['su'] = oldI2newI[k]
            
    def save(self, filename=None, pagebreak=True, lines_per_page=58):
        ''' Save a Stacks object to a file.  The file extension is either 'stk'
        or 'txt'.  If 'stk', the file can be reopened for later editing.  If
        'txt', then the file is human readable and can be opened with
        Microsoft Word.
        
        Parameters
        ==========
        
        filename : str
            Default = None
            
        If filename = None, then previously assigned filename if used.  If
        no filename has been assigned, the the default filename 'stackups.stk'
        will be used.
        
        Examples
        ========
        
        >>> stks.save('myfilename.stk')
        
        >>> stks.save()  # save to previously assigned filename
        
        >>> stks.save('C:/mypath/myfilename.stk')  # on Microsoft Windows
        
        >>> stks.save('C:\\mypath\\myfilename.stk')  # another method to allow Python to accept paths
        
        >>> stks.save('myfilename.txt')  # Can open with Microsoft Word
        
        >>> stks.save('txt')  # Use previously assigned filename, but with 'txt' as extension.
        
        '''
        if filename:        
           save(self, filename, pagebreak, lines_per_page)
        else:
           save(self, self.filename, pagebreak=True, lines_per_page=58) 
            
    def search(self, searchfor='*'):
        ''' Search all the stacks for a string, float, or int that matches the
        search criterion.
        
        Parameters
        ==========
        
        searchfor : float, int, or str
            Value to search for.  Default = '*'; that is, find all stackunits.
            
        Examples
        ========
        
        >>> stks.search('Width')  # matches any string containing the word 'width'.
        '''
        def fnkey(stackunit):  # use as key for sorting; sort by pn, then by su
            return stackunit['pn'] + str(stackunit['su']).zfill(5)
        sulist = self._search_strs(searchfor) + self._search_floats(searchfor)
        if sulist:
            sulistsorted = sorted(sulist, key=fnkey)
            print(self._sulist2str(sulistsorted))
     
    def su(self, *args, **kwargs):
        sudic = {}
        try:
            stack = self.stack
        except:
            stack = []
        if self.stacks and len(self.stacks) > 1:
            for stk in self.stacks:
                if isinstance(stk, Stack):
                    for st2 in stk:  # e.g. st2 = [3, {'pn': 'MTI012346', 'd': 9.34, 'n': 'OAL', 'dt': 0.01}]
                        if 'su' in st2 and st2['su'] not in sudic:
                            sudic[st2['su']] = st2  # st2 is of type Stackunit
        elif stack:
            for st2 in stack:
                if 'su' in st2 and st2['su'] not in sudic:
                    sudic[st2['su']] = st2  # st2 is of type Stackunit
        # todo: check for isStackunit:
        if 'su' in kwargs and isinstance(kwargs['su'], int):
            su = kwargs['su']
            data = {**self._parse_data(args), **kwargs}
            sudic[su]['d'] =  float(abs(data.get('d', sudic[su]['d'])))
            sudic[su]['dt'] =  float(abs(data.get('dt', sudic[su]['dt'])))
            sudic[su]['pn'] =  str(data.get('pn', sudic[su]['pn']))
            sudic[su]['n'] =  str(data.get('n', sudic[su]['n']))
            sudic[su]['sigma'] =  float(data.get('sigma', sudic[su]['sigma']))
            if sudic[su]['sigma'] % int(sudic[su]['sigma']) < .0001:  # e.g., simgma = 6.0, then set simgma = 6
                sudic[su]['sigma'] = int(sudic[su]['sigma'])
        return sudic
            
    def sync(self):
        ''' Go through the stacks and sync all stackunits.
        
        If two or more stackunits in the stacks have the same part no. and the 
        same name (same pn and n), the sync method makes sure that they are the 
        same object (that is, sync make sure they share the same memory 
        location). Then if a value of a particular stackunit changes, for 
        example a tolerance, then all other stackunits with the sane pn and 
        name will update appropriately.
        
        Every object with the same pn and name are to have a unique su value
        assigned.  The sync methods also goes through the stacks and makes sure
        this is the case..
        
        Normally this method is automatically called, but may be invoked 
        manually if desired.
        
        Returns
        =======
        
        out : nothing
            All changes occur to the the `self.stack` variable within the stack.
            If changes occur properly, nothing will appear to change to the 
            stack except possibly updates to su values.
        '''
        #print(!', end='')
        sus = []
        pnndic = {}  # for a dic with keys = (pn, n) and values = stackunit
        sumax = 0
        for stk in self.stacks[1:]:
            for su in stk[1:]:  # Make a pnndic {('mypn1', 'MYNAME1'): stackunit1, ...}
                pnn = (su['pn'], nSquished(su['n']))
                pnndic[pnn] = su
        # In the below `for` loop, I tried the "for stk in self.stacks[1:]" approach,
        # but didn't get desired result: stackunits with same pn/n were not same
        # object.  I realized that I was making changes to loop contraints
        # (via: su = pnndic[pnn]) while looping was in progress.  So I changed 
        # my approach
        for j in range(1, len(self.stacks)):
            for k in range(1, len(self.stacks[j])):  # Make sure all stackunits with same pn/n pairing are same object.
                pnn = (self.stacks[j][k]['pn'], nSquished(self.stacks[j][k]['n']))
                self.stacks[j][k] = pnndic[pnn]  # for a given pn/n pair, pnndic has only one stackunit object.  Use it.                           
                if self.stacks[j][k]['su'] > sumax:
                    sumax = self.stacks[j][k]['su']
        for stk in self.stacks[1:]:  # make a long list of all stackunits from all stacks
            for su in stk[1:]:
                sus.append(su)  
        for j in range(len(sus)):  # Make sure all su values unique for a given pn/n pair
            pnn_j  =  (sus[j]['pn'], nSquished(sus[j]['n']))
            su_j = sus[j]['su']
            for k in range(j+1, len(sus)):  # Compare the remainder of the list with pnn_j
                pnn_k  =  (sus[k]['pn'], nSquished(sus[k]['n']))
                su_k = sus[k]['su']
                if su_j == su_k and pnn_j != pnn_k:  # Whoops.  Same su value for same pn/n combo
                    sumax +=1
                    sus[k]['su'] = sumax  # Give a new su value to the extraneous stackunit                                  
        
    def title(self, t=None):
        '''Set the title for a Stacks object.
        
        Parameters
        ==========
    
        t : str
            title for the Stacks object
            
        Examples
        ========
        
        stks.title('My title for the Stacks object')
        '''
        if t:
            self.stacks[0]['title'] = t
        else:
            return self.stacks[0]['title']
                   
    def titles(self):
        '''Show titles of all stacks, i.e., a table of contents.
        
        Returns
        =======
        
        out : list
            The list is a list of tuples.  Each tuple has two items.  The first
            item is the stack number.  The second is the title of that stack.
        '''
        b = []
        y = 1
        if isinstance(self, Stack):
            b.append(self[0]['title'])
        elif isinstance(self, Stacks):
            b.append((0, self[0]['title']))
            for stk in self[1:]:
                b.append((y, stk[0]['title']))
                y += 1
        return b  
                
    def tolist(self):
        '''Converts a Stacks object to a standard list object.'''
        b = [self.stacks[0]]
        for x in self.stacks[1:]:
            b.append(x.tolist())
        return b    
    
    def u(self, *args, **kwargs):
        self._update(*args, **kwargs)
        if _s['autoprint']:
            print(self)
 
        
    def update(self, *args, **kwargs):
        '''Updates data for a stack unit.
            
        Examples
        ========
        
        >>> stks._update(3.25, .015, su=9)  # _update d and dt stackunit 9.
        
        >>> stks._update(dt=.005, su=9)  # _update the tolerance of stackunit 9.

        >>> stks._update('99N3424', su=4)  # _update the pn of stackunit 4.
        
        >>> stks._update('99N3424', 'gear width', su=4) # _update the name of stackunit 4
        '''
        self._update(*args, **kwargs)
        if _s['autoprint']:
            print(self)
            
    def whereused(self, searchfor=[]):
        ''' Show in what stack a given stackunit is located.
        
        Parameters
        ==========
        
        searchfor : int or list
            search based on a given su value, or a list of su values.  
            Default = [].  (if an empty list is given, produce results for all 
            su values)
        
        Examples
        ========
        
        >>> stks.whereused(12)
        
        >>> stks.whereused([4, 7, 8])  # 4, 7, and 8 are su values
        
        >>> stks. whereused()
        '''
        wudic = self._wudic()
        wu_keys = sorted(wudic.keys())
        print('\nsu  stacks used in')
        if searchfor:
            if isinstance(searchfor, int):
                searchfor = [searchfor]
            if isinstance(searchfor, (list, tuple)):
                for su in wu_keys:
                    if su in searchfor:
                        print(su, ':', wudic[su])
        else:
            for su in wu_keys:
                print(su, ':', wudic[su])
                
    def wu(self, searchfor=[]):
        ''' Same as whereused'''
        self.whereused(searchfor)
                
                                
class Stack(Stacks):
    '''A Stack object is a special kind of python list.  The first item of the
    list contains the assigned title for that Stack object, and it also 
    contains a sublist called a j (or jog) list.  The j list specifies the 
    direction of each Stackunit object within the Stack.
            
    Examples
    ========
    
    Create your list to house the stacks that you will create:
    
    >>> stk = Stack(title = 'My title for the stackups')
    
    Alternatively, you could use the filenew function that comes with this
    module (see the the documetion thereof for more info.)
    
    >>> stk = filenew('transmission01.stk', objtype='Stack').
    
    Methods
    =======
    
    Use the help() method (i.e. Stack.help()) to see available methods. 
    '''
    def __init__(self, stack=[],
                 stacks=[{'title':'This stack does not have a Stacks object for a parent'}],
                 title="Stack title: None",
                 sync=True):
        self.default_Stack_title = "Stack title: None"
        global _s
        self.stacks = stacks  
        self.stack = []
        if isinstance(stack, Stack):
            self.stack = stack.stack
            for su in self.stack:
                if 'title' not in su:
                    su.stacks = self.stacks
        elif stack and isStack(stack):
            for x in stack:
                if 'title' in x and 'j' in x:  # title of a Stack
                    self.stack.append({'title': x['title'], 'j':x['j'] })
                elif 'objtype' in x and x['objtype'] == 'Tbearing':
                    tbrg = Tbearing(0, 0, 0)
                    tbrg.stackunit = x
                    tbrg.stacks = self.stacks
                    self.append(tbrg)
                elif not isinstance(x, Stackunit): 
                    self.stack.append(Stackunit(x, stacks=self.stacks))
                else:
                    self.stack.append(x)
        else:
            self.stack = [{'title':
                           self.default_Stack_title, 
                           'j':{0:0}}]
        if title != self.default_Stack_title:
            self.stack[0]['title'] = title
        self.indx = -1
        if sync == True:  # This variable False when Stacks.__init__ called
            self.sync()
        self.filename = defaultfilename
        if stack and not isStack(stack):
            print("Error: Data not accepted.  The data's errant structure prevents")
            print("creating a suitable Stack object.")
        self.sync_on = True
        
    def __repr__(self):
        if _s['alter'] == True:
            return self.__str__()
        prec = _s['precision']
        try:
            flag = _s['short_repr']  # has user set a value for 'short'?  If not, then set a default
        except NameError:
            flag = 0  # if short == 0, output lines long.  short == 1, then shorten
        self._index()              
        st = ['[']   # obs: st = ["['" + self.stack[0] + "',\n"]
        for x1 in self.stack:
            if 'title' in x1: 
                if flag:
                    linelen = 40
                    linelenfac = 2
                else:
                    linelen = 80  
                    linelenfac = 1                            
                str1 = "{'title':'" + x1['title'] + "', 'j':{"
                str3 = str1
                str4 = ''
                k = 0
                for key in sorted(x1['j'].keys()):
                    str4 = str4 + (str(key) + ':' + str(x1['j'][key])) + ', '
                    if (key - k) > len(x1['j'])/linelenfac or (len(str3) + len(str4)) > linelen:
                        str3 = str3 + str4
                        st.append(str3)
                        st.append('\n   ')
                        str3 = ''
                        str4 = ''
                        k = key
                str3 = str3 + str4
                st.append(str3)                        
                if st[-1] == '' and st[-2] == '\n   ':
                    st = st[:-2]
                st[-1] = st[-1][:-2]
                st.append("}},\n")  
            else:
                su = x1['su']
                sigma = x1['sigma']
                d = x1['d']
                dt = x1['dt']
                pn = x1['pn']
                n = x1['n']
                if flag:  # format_str doubles up text
                    format_str = "'su': {}, 'sigma': {}, 'd': {}, 'dt': {},\n      'pn': '{}', 'n': '{}'"
                else:  # format_str produces a long text line
                    format_str = ("'su': {}, 'sigma': {}, 'd': {:." + str(prec) +
                                 "f}, 'dt': {:." + str(prec) + 
                                 "f}, 'pn': '{}', 'n': '{}'")
                s_itm = format_str.format(su, sigma, d, dt, pn, n)
                st.append('{' + s_itm + '},\n')
        st[-1] = st[-1][:-2] + ']'
        return ''.join(st)

    def __str__(self):
        _index = self._index()
        if _index:
            indexstr = '[' + str(_index) + '] '
        else:
            indexstr = ''
        # what follows is: establish column widths for the table that gets printed
        s = indexstr + self.stack[0]['title'] + '\n'  # s will collect strings
        #precision=3
        width=80
        d_s = []
        dt_s = []
        su_s = []
        sigma_len = 0
        flag = False
        for st2 in self.stack[1:]:
            flag = True
            su_s.append(st2['su'])  # collect all the su_s
            d_s.append(st2['d'])  # collect all the d_s
            dt_s.append(st2['dt'])  # collect all the dt_s
            if len(str(st2['sigma'])) > sigma_len:
                sigma_len = len(str(st2['sigma']))
        if flag:
            su_s_max = max(su_s)  # find max value of su
            d_s_max = max(d_s)  # find max value of d
            dt_s_max = max(dt_s)  # find max value of dt
            rw = len(str(len(self.stack) -1)) # column width for rows
            suw = len(str(abs(su_s_max)))  # column width for su values
            if suw==1:
                suw = 2
            dw = len(str(int(abs(d_s_max)))) + _s['precision'] + 2  # column width for d (2: 1 for . and 1 for -)
            dtw = len(str(int(abs(dt_s_max)))) + _s['precision'] + 1  # column widith for dt
            pn_n_w = width - (rw + 2 + suw + 2 + dw + 3 + dtw + 5)  # column width for pn & n
            srw = str(rw)
            ssuw = str(suw)
            ssigma = str(sigma_len)
            sdw = str(dw)
            sdtw = str(dtw)
            spw = str(_s['precision'])
            arr = {1:(u'\uff1c', u'\uff1e'), 2:('<', '>'),  # diff styles rt and
                   3:(u'\u21a4', u'\u21a6'), 4:(u'\u21a2', u'\u21a3'), 
                   5:(u'\u21fd', u'\u21fe'), 6:(u'\u2190', u'\u2192'), 
                   7:(u'\u21e6', u'\u21e8'), 8:('-', '+'),
                   9:(u'\u2717', u'\u2714'), 10:(u'\u219E', u'\u21A0')}
            a_type = _s['arrow']
            heading = ('{:>' + srw + '}  {:>' + ssuw + '}  {:>' + ssigma + '}  j  {:^' + sdw + '}  {:^' + sdtw
                       + '}   {:<}').format('r', 'su', '\u03c3', 'd', 'dt', 'pn & n')
            format_str = (u'{:'+ srw + 'd}  {:'+ ssuw + 'd}  {:>' + str(sigma_len)
                      + '}  {}{:>'+ sdw + '.'+ spw + 'f} \u00b1 {:'+ sdtw + '.'
                      + spw + 'f}  {}')
            d_sum = 0.0
            dt_sum = 0.0
            sig_sum = 0.0
            for row, st2 in enumerate(self.stack):
                if row == 0:  # print title, heading, etc.
                    s += heading + '\n'  # the heading, i.e., "su   d     dt    pn & n"
                else:  # print all the elements of the stackup
                    su_ = st2['su']
                    sigma = st2['sigma']
                    sstr = str(sigma)
                    d = (self.stack[0]['j'][row]) * st2['d'] # multiply times 
                    dt = abs(self.stack[0]['j'][row]) * st2['dt'] # multipy by abs(m)
                    if self.stack[0]['j'][row] > 0:
                        arrow = arr[a_type][1]  # right arrow
                    else:
                        if _s['highlight']:
                            arrow = Back.CYAN + arr[a_type][0] + Style.RESET_ALL  # left arrow
                        else:
                            arrow = arr[a_type][0]
                    if abs(self.stack[0]['j'][row]) == 1:    
                        pn_and_n = (st2['pn'] + ', ' + st2['n'])[:pn_n_w]  # [:pn_n_w] truncates
                    else:
                        times = str(abs(self.stack[0]['j'][row])) + 'X '
                        pn_and_n = (st2['pn'] + ', ' + times + st2['n'])[:pn_n_w]
                    d_sum += d   # besides print, accumlate sum of d_s
                    dt_sum += dt   # besides print, accumlate sum of dt_s
                    sig_sum += (((2*dt)/self.stack[0]['j'][row])/sigma)**2 * abs(self.stack[0]['j'][row])
                    s += format_str.format(row, abs(su_), sstr, arrow, abs(d), dt, pn_and_n) + '\n'
            # ------------------------------------------------------------------
            sigma = math.sqrt(sig_sum)
            sm = 0
            for x in self.stack[0]['j']:  # how many items are in the stack?
                if x != 0:
                    sm += abs(self.stack[0]['j'][x])
            out_format_str1 = (u'{:>'+ str(dw + 3 + dtw) + '}')        
            out_format_str2 = (u'{:>'+ sdw + '.'+ spw + 'f} \u00b1 {:'+ sdtw + '.'
                      + spw + 'f}' + '  [{:.'+ spw + 'f}, {:.'+ spw + 'f}]  {}')
            out_format_str3a = (u'  \u03c3 = {:>.'+ str(_s['precision'] + 1) + 
                               'f} ' + '(ref: {}\u03c3 = ' + '{:.'+ spw + 'f})') 
            out_format_str3b = (u'  \u03c3 = {:>.'+ str(_s['precision']
                                + 1) + 'f}')
            s += (out_format_str1.format('-'*60) + '\n')          
            s += (out_format_str2.format(d_sum, dt_sum, 
                                            d_sum - dt_sum, d_sum + dt_sum,
                                            '100% possible') + '\n')
            if sm > _s['threshold']: # if more than 7 stackunits, show probability
                s += (out_format_str2.format(d_sum, 3*sigma, 
                                            d_sum - 3*sigma, d_sum + 3*sigma,
                                            '6\u03c3, 99.73% probable') + '\n')
                s += (out_format_str2.format(d_sum, 2*sigma, 
                                            d_sum - 2*sigma, d_sum + 2*sigma,
                                            '4\u03c3, 95.46% probable') + '\n')
                s += (out_format_str2.format(d_sum, sigma, 
                                            d_sum - sigma, d_sum + sigma,
                                            '2\u03c3, 68.26% probable') + '\n')
                if _s['sigma_mult'] > 1:
                    s += (out_format_str3a.format(sigma, _s['sigma_mult'], 
                              _s['sigma_mult']*sigma) + '\n')
                else:
                    s += (out_format_str3b.format(sigma) + '\n') 
        if len(s) < len(self.default_Stack_title) + 7:
            s += 'r su  σ  j     d       dt     pn & n\n'
            s += '------------------------------------------------------------\n'
            #s += '1  ?  6  ↦ ?????? ± ??????  ????????, ???????????????\n\n'
            #s += "(Append method assigns, e.g. stk[{}].append(-3.500, .015, 'PtNo', 'Dim Desrip'))\n".format(_index)
        return s
        
    def __mul__(self, other):
        b = []
        if isinstance(other, int) or isinstance(other, float):
            for su in self.stack:
                if 'title' in su:
                    b.append(su)
                else:
                    b.append(su * other)
        return Stack(b)
            
    def __rmul__(self, other):
        return self.__mul__(other)
        
    def __truediv__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return self * (1/other)
            
    def __rtruediv__(self):
        print('division with Stack as the denominator not allowed')
        
    def __setitem__(self, key, value):
        if isinstance(value, Stackunit):
            self.stack[key] = value
        elif isStackunit(value):
            self.stack[key] = Stackunit(value)

    def __delitem__(self, key):
        if key != 0:
            del self.stack[key]

    def __contains__(self, item):
        if item in self.stack:
            return True
        else:
            return False

    def __missing__(self, key):
        pass

    def __getitem__(self, key):
        return self.stack[key]

    def __next__(self):
        if self.indx > len(self.stack) -2:
            self.indx = -1
            raise StopIteration
        self.indx += 1
        return self.stack[self.indx]

    def __iter__(self):
        return self

    def __len__(self):
        return len(self.stack)
        
    def _index(self):
        '''Report index of self within self.stacks.  Also, place this number
        as the value of f[0] of the dictionary located on the title line.
        '''
        if self in self.stacks:
            _index = self.stacks.index(self)
            self.stack[0]['j'][0] = _index  
        else:
            _index = 0
        return _index        

    def a(self, *args, **kwargs):
        ''' Same as the *append* method.'''
        self.append(*args, **kwargs)
                
    def append(self, *args, **kwargs):
        '''Append a Stackunit to a Stack
        
        Examples
        ========
        
        The following is the primary way of entering data.  Order of parameters
        is important:  dimension before tolerance, and part number before name.
        Note: part no.[*]_ and name must be strings, i.e. must by surrounded by
        single or double quote marks:
        
        >>> stk[5].append(4.125, .015, '6080706', 'End to snap ring groove')
        
        Explicitly assign variables:
        
        >>> stk[5].append(d=4.125, dt=.015, pn='6080706', n='End to snap ring groove')
        
        Normally sigma=6, the default, is fine.  But if the user has data
        from actual machined parts allowing him to know more specifically the
        probability of a parts dimension, he can adjust sigma:
        
        >>> stk[5].append(2.445, .005, '990345', 'Spacer width', sigma=3.5)
        
        Append an already established Stackunit:
        
        >>> stk[5].append(9)  # 9 is the su value
        
        If you have an already instantiated Stackunit
        
        >>> stk[5].append(myStackunit)
        
        [*] The part number is case sensitive.  67N0315 and 67n0315 are not
        recognized by the program as the same part number.
        '''
        data = {**kwargs, **self._parse_data(args)}
        data['set_flag'] = True
        b, max_su = self._update(**data)  # will find any existing pn/n combos
        counter = len(self.stack)  # start value for ext key in 'j'
        if len(args) == 1 and isinstance(args[0], int): # user has input an su value
            b = [args[0]]
        for x in b:  # b is a list of su_s
            self.stack.append(self.su()[abs(x)])
            self.stack[0]['j'][counter] = sign(x)
            counter += 1
        if len(args)>0 and isinstance(args[0], Stackunit):  # with, and only with, arg[0] present           
            flag = False            
            if args[0]['d'] < 0:  # see __neg__ of Stackunit
                flag = True
                args[0]['d'] = abs(args[0]['d'])
            try: # I'm loading in Stacks (fileopen), and j already exists for this Stackunit
                current_j = self.stack[0]['j'][len(self.stack)]
            except:
                current_j = 0  # no j exists, so set to 0
            self.stack[0]['j'][len(self.stack)] = 1
            su_old = n_already_exists(args[0]['pn'], args[0]['n'], 
                                     self._pndic(returnType='dict'))
            if su_old:
                self.append(su_old)
            else:
                su_new = max_su + 1
                args[0].stacks = self.stacks  # attach the main self.stacks so various functions can access              
                args[0]['su'] = su_new
                self.stack.append(args[0])
            if current_j:
                self.stack[0]['j'][len(self.stack) - 1] = current_j
            if flag:
                self.stack[0]['j'][len(self.stack) - 1] = -1 * self.stack[0]['j'][len(self.stack) - 1]
        elif not b:
            su_new = max_su + 1
            if 'd' in data:
                sgn = sign(data['d'])
            else:
                sgn = 1
            new_stackunit = Stackunit(d = abs(data.get('d', 0)), 
                 dt = abs(data.get('dt', 0)), # initial guess 4 new data
                 pn = data.get('pn', 'pn_unknown'),
                 n = data.get('n', 'unique description required'),
                 sigma = data.get('sigma', 6),
                 su = su_new,
                 stacks = self.stacks)
            self.stack.append(new_stackunit)
            self.stack[0]['j'][counter] = sgn
        try:
            self.sync_on
        except AttributeError:
            self.sync_on = True
        if self.sync_on:
                self.sync()
        if _s['autoprint']:
            print(self)
            
    def e(self, *stackunits):           
        ''' Same as the *extend* method.'''
        self.extend(*stackunits)

    def extend(self, *stackunits):
        '''Append Stack object, a Stacks object, or a list of Stackunits to a
        Stack.  When extending a Stack or Stacks object, all the Stackunits
        are extracted from the object and extended to the Stack.
         
        Parameters
        ==========           
        
        stackunits : list, tuple, integers, Stackunit,  Stack, or Stacks
            If a tuple, must be able to evalutate to a Stackunit.  A list
            is optional and is provided to similate a standard list/extend
            method.
            
        Examples
        ========
        
        Emulates the standard extend Python list:
        
        >>> stks[1].extend([su1, su2, su3])   # su1, su2, and su3 are Stackunit instances
 
        But this also works:
        
        >>> stks[1].extend(su1, su2, su3) 
        
        Extend a stack based on currently established Stackunits:
        
        >>> stk[1].extend(5, 4, 2, 9)  # 5, 4, 2, and 9 are the su values of Stackunits
        
        Append multiple, new, stackunits:        
        
        >>> stks[1].extend((0.95, .005, 'PNABC', 'Width'), (-2.113, .015, 'PNDEF', 'OAL')
                           (2.95, .015, 'PNHIJ', 'OAL'))
        
        Perhaps you had a project with many of the same parts in your current
        project and you wish to use the same Stackunits.  You can throw all
        those Stackunits into a holding area, i.e., some initially empty Stack.
        
        >>> stks[2].extend(other_stks)  # other_stks is a Stacks object
        
        >>> stks[2].extend(more_stks[5])  # Extend stack 5 of more_stks
        '''
        autoprint, _s['autoprint'] = _s['autoprint'], 0
        self.sync_on = False
        sudic = self.su()
        for stkunt in stackunits:
            if stkunt == self:
                print("Cannot extend self.")
            elif isinstance(stkunt, Stackunit) or isStackunit(stkunt):
                self.stack[0]['j'][len(self.stack)] = 1
                self.append(stkunt)
            elif isinstance(stkunt, tuple) and isStackunit(Stackunit(*stkunt)):
                x = Stackunit(*stkunt)
                for y in stkunt:
                    if ((isinstance(y, float) or isinstance(y, int))
                        and y < 0):
                        x['j'] = -1
                self.append(x) 
            elif ((isinstance(stkunt, Stack) or isStack(stkunt)) and stkunt != self):
                for x in stkunt:
                    if ((isinstance(x, Stackunit) or isStackunit(x)) and
                            'title' not in x):
                        self.append(x)
            elif ((isinstance(stkunt, Stacks) or isStacks(stkunt)) and not self in stkunt):
                for stk in stkunt:
                    if ('title' not in stk and 
                            (isinstance(stk, Stack) or isStack(stk))):
                        for x in stk:
                            print('.', end='')
                            if ((isinstance(x, Stackunit) or isStackunit(x))
                                and 'title' not in x):    
                                self.append(x)
            elif isinstance(stkunt, int) and abs(stkunt) in idic:
                self.stack.append(idic[abs(stkunt)])
                self.stack[0]['j'][len(self.stack)] = sign(stkunt)
            elif isinstance(stkunt, int) and not abs(stkunt) in idic:
                print('unknown stackunit: su=' + str(stkunt))
            elif hasattr(stkunt, '__iter__') and (self in stkunt or stkunt == self):
                print('cannot extend to self')
            elif isinstance(stkunt, list):
                self.extend(*stkunt)
            else:
                print("Not valid input.")
        self.sync_on = True
        self.sync()
        _s['autoprint'] = autoprint
        if _s['autoprint']:
            print(self)
        
    def i(self, row, *args, **kwargs):
       ''' Same as the *insert* method.''' 
       self.insert(row, *args, **kwargs)
        
    def insert(self, row, *args, **kwargs):
        '''Like append, but insert Stackunit at a particular row.  The first
        argument is the row number.  See the assert more examples.
        
        Examples
        ========
        
        >>> stk[5].append(3, 4.125, .015, '6080706', 'End to snap ring groove')
        
        The first argument is the row, and is an integer.  Following that is
        the stack unit value.  Note that this is equivalent to using the
        append and move methods.        
        '''
        autoprint, _s['autoprint'] = _s['autoprint'], 0
        lgt1 = len(self.stack)
        self.append(*args, **kwargs)
        lgt2 = len(self.stack) - 1 
        self.move([lgt1, lgt2], row)
        _s['autoprint'] = autoprint
        if _s['autoprint']:
            print(self)
            
    def invert(self):
        '''Put the stack list in reverse order, put the a dictionary of that
        stack in reverse order, and multiply each value of the a dictionary
        by -1.  Of what use is this method?  It happens on rare occassions that
        a designer or engineer mistakenly does a stackup backward only to later
        realize his mistake. Insead of having to redo the stackup, the invert
        method quickly flips things around.
        '''
        b3 = []
        for x in range(1, len(self)):  # gather current a values, omitting f[0], and put in list b3
            b3.append(self.stack[0]['j'][x])
        b3 = b3[::-1]   # reverse list b3, e.g. [-1, 1, 2, -1] to [-1, 2, 1, -1]
        for key, value in enumerate(b3):  # multiply b3 by -1 and reconstruct f
            self.stack[0]['j'][key+1] = -1*b3[key]
        self.stack = self.stack[::-1]  # reverse the stack list
        self.stack.insert(0, self.stack.pop())  # put the title back at the front of the list
        
    def jog(self, *args):
        '''Make a Stackunit within a Stack have either a positive or negative
        direction.  If postitive, then the direction (jog) the Stackunit takes for 
        the stackup calculation is to the right.  And if negative, to the left.  
        
        Parameters
        ==========
        
        args : dictionary or integers
            If an integer, the integer is the row you want to change.  A
            positive value of the row number if you want the arrow pointing
            right; negative for the arrow pointing left.  Use a dictionary
            if you want values other than 1 or -1.
        
        Examples
        ========

        If integer values used:
 
        >>> stks[1].jog(-7)  # make a jog to left for the stackunit on row 7
        
        >>> stks[1].jog(3, -4, 7)  # update stackunits at rows 3, 4 and 7.
        
        If a dictionary is used, the "key", i.e, the first value, is the row,
        the second is the value.
        
        >>> stks[1].jog{{5:1, 7:-1}}  # update rows 5 and 8
        
        Perhaps you have the same stackunit repetively and in a group.
        This might occur if you have a stack of plates, each with the same part
        number.  Use a dictionary for this:
            
        >>> stks[1].jog({4:6})  # at row 4, 6 occurances of a stackunit   
        '''
        for x in args:
            if isinstance(x, dict):
                for key in x:
                    if key != 0 and key in self.stack[0]['j'] :
                        self.stack[0]['j'][key] = x[key]
                    elif key == 0:
                        print('key 0 cannot be changed')
                    else:
                        print(str(key) + ' not in dict')
            elif isinstance(x, int):
                if x != 0 and abs(x) in self.stack[0]['j']:
                    self.stack[0]['j'][abs(x)] = (sign(x) * 
                                                 abs(self.stack[0]['j'][abs(x)]))
            elif x == 0:
                print('key 0 cannot be changed')
            else:
                print(str(abs(x)) + ' not in dict')
        print(self.stack[0]['j'])
        print()
        if _s['autoprint']:
            print(self)
            
    def j(self, *args):
        ''' same as jog'''
        self.jog(*args)
        
    def pn(self, *args, **kwargs):
        '''Same as the pn method of Stacks, except also prints out the stack.
        
        Examples
        ========
        
        s[5].pn(2.465, su=19)       
        '''        
        super(Stack, self).pn(*args, **kwargs)
        print(self)
        
    def pop(self, row=None):
        '''Remove the item at the given position in the list, and return it. If
        no index is specified, stk.pop() removes and returns the last item in 
        the list.
        '''
        if row != None: # and row != 0:
            tmp = self.stack[row]
            del self.stack[row]
            return tmp
        elif row == None:
            tmp = self.stack[-1]
            del self.stack[-1]
            return tmp
                
    def sync(self):
        ''' Go through the stack and sync all stackunits.
        
        If two or more stackunits in the stack have the same part no. and the 
        same name (same pn and n), the sync method makes sure that they are the 
        same object (that is, sync make sure they share the same memory 
        location). Then if a value of a particular stackunit changes, for 
        example a tolerance, then all other stackunits with the sane pn and 
        name will update appropriately.
        
        Every object with the same pn and name are to have a unique su value
        assigned.  The sync methods also goes through the stack and makes sure
        this is the case.
        
        If the stack was created independantly of the Stacks class and later
        appended to a Stacks object, then su values may update if needed.
        
        Normally this method is automatically called, but may be invoked 
        manually if desired.  This method has no effect if the stack is part
        of a group of stacks.
        
        Returns
        =======
        
        out : nothing
            All changes occur to the the `self.stack` variable within the stack.
            If changes occur properly, nothing will appear to change to the 
            stack except possibly updates to su values.
        '''
        if len(self.stacks) < 2:
            pnndic = {}  # for a dic with keys = (pn, n) and values = stackunit
            sumax = 0  # starting value to find the max su value in the stack
            dictitle = self.stack.pop(0)  # Pull off the title.  Reattach when sync done.
            for stkunt in self.stack:  # Make a pnndic, i.e., {('mypn1', 'MYNAME1'): stackunit1, ...}
                pnn = (stkunt['pn'], nSquished(stkunt['n']))
                pnndic[pnn] = stkunt
            for k in range(len(self.stack)):  # Make sure all stackunits with same pn/n pairing are same object.              
                pnn = (self.stack[k]['pn'], nSquished(self.stack[k]['n']))
                self.stack[k] = pnndic[pnn]  # for a given pn/n pair, pnndic has only one stackunit object.  Use it.             
                if self.stack[k]['su'] > sumax:
                    sumax = self.stack[k]['su']
            for j in range(len(self.stack)):  # Make sure all su values unique for a given pn/n pair
                pnn_j  =  (self.stack[j]['pn'], nSquished(self.stack[j]['n']))
                su_j = self.stack[j]['su']
                for k in range(j+1, len(self.stack)):  # Compare the remainder of the list with pnn_j
                    pnn_k  =  (self.stack[k]['pn'], nSquished(self.stack[k]['n']))
                    su_k = self.stack[k]['su']
                    if su_j == su_k and pnn_j != pnn_k:  # Whoops.  Same su value for same pn/n combo
                        sumax +=1
                        self.stack[k]['su'] = sumax  # Give a new su value to the extraneous stackunit
            self.stack.insert(0, dictitle)  # Put the title back in
        else:
            super(Stack, self).sync()  # if stack is part of other stacks, all sync of Stacks instead

    def title(self, t=None):
        '''Provide a title for a Stack object
        
        Parameters
        ==========
    
        t : str
            title for the Stack object
            
        Examples
        ========
        
        stks[1].title('My title for the Stack object')
        '''
        if t:
            self.stack[0]['title'] = t
        else:
            return self.stack[0]['title'] 
        
    def tolist(self):
        '''Converts a Stack object to a standard list object.'''
        b = [self.stack[0]]
        for x in self.stack[1:]:
            b.append(x.todict())
        return b
        

class Stackunit(Stacks):
    '''A Stackunit object is a special dictionary that contains a dimension, 
    a dimension tolerance, part number, a value for sigma, a dimension name,
    and an su value.  An su value is a unique interger used to identify the 
    Stackunit.
    
    An example of what a Stackunit object looks like:
    
    {'su': 5, 'sigma': 6, 'd': 3.3400, 'dt': 0.0100, 'pn': 'MTI012346',
        'n': 'groove to end'}
    
    Where:
    
    - su : int
        An integer used to identify a Stackkunit.  For a given part number and
        its description this value is unique.  Note that the program may change
        this value when new Stackunit ojects are added to a Stack.  This value
        should not be altered by the user (exception: see the renumber method).
        
    - sigma : int or float
        The default is 6 and should be normally be left alone unless
        measured dimensions from actual parts exist to justify changing the
        value.
    
    - d : float
        The value of the dimension.
        
    - dt : float
        The dimension's tolerance.
        
    - pn : string
        The part number of the part to which the dimension applies.  Note:
        PART NUMBERS ARE CASE SENSITIVE!  For example 06N0314 is not the same 
        as 06n0314.  
        
    - n : string
        The name of the dimension.  Examples:  'Over all length', 'Width',
        'Rt end to groove'.  Note that for a given part number, names MUST BE
        UNIQUE.  (Names are case insensitive.)
    '''
    def __init__(self, *args, **kwargs):
        self.sync_on = True
        if 'stacks' in kwargs:
            self.stacks = kwargs['stacks']
            del kwargs['stacks']
        self.indx = -1
        self.stackunit = {}
        if args and isinstance(args[0], Stackunit):
            self.stackunit = args[0].stackunit
        elif args and isStackunit(args[0]):
            self.stackunit = args[0]
        else:            
            #self._update(*args, **kwargs) # if user supplied args, sets self.stackunit
            #sudic = self.su()
            data = {**kwargs, **self._parse_data(args)}  # parse the input parameters that user provides   
            pn = data.get('pn', 'pn_unknown')
            n = data.get('n', 'unique description required')
            d = data.get('d', 0)
            dt = data.get('dt', 0)
            sigma = data.get('sigman', 6)
            su = data.get('su', 0)
            self.stackunit = {'d':d, 'dt':dt, 'pn':pn, 'n':n, 'sigma':sigma, 'su':su}
        self.filename = defaultfilename
    
    def __add__(self, other):
        if isinstance(other, Stackunit):        
            d = self['d'] + other['d']
            dt = abs(self['dt']) + abs(other['dt'])
            return Stackunit(d, dt)
        elif isinstance(other, int) or isinstance(other, float):
            b = {}
            for x in self.stackunit:
                if x == 'd':
                    b[x] = self.stackunit[x] + other
                else:
                    b[x] = self.stackunit[x]
            return Stackunit(b)
    
    def __radd__(self, other):
        return self.__add__(other)
            
    def __sub__(self, other):
        if isinstance(other, Stackunit):        
            d = self['d'] - other['d']
            dt = abs(self['dt']) + abs(other['dt'])
            return Stackunit(d, dt)
        elif isinstance(other, int) or isinstance(other, float):
            b = {}
            for x in self.stackunit:
                if x == 'd':
                    b[x] = self.stackunit[x] - other
                else:
                    b[x] = self.stackunit[x]
            return Stackunit(b)
            
    def __rsub__(self, other):
        if isinstance(other, Stackunit):        
            d = other['d'] - self['d']
            dt = abs(self['dt']) + abs(other['dt'])
            return Stackunit(d, dt)
        elif isinstance(other, int) or isinstance(other, float):
            b = {}
            for x in self.stackunit:
                if x == 'd':
                    b[x] = other - self.stackunit[x]
                else:
                    b[x] = self.stackunit[x]
            return Stackunit(b)

    def __mul__(self, other):
        b = {}
        if isinstance(other, int) or isinstance(other, float):
            for x in self.stackunit:
                if x == 'd' or x == 'dt':
                    b[x] = self.stackunit[x] * other
                else:
                    b[x] = self.stackunit[x]
            return Stackunit(b)
            
    def __rmul__(self, other):
        return self.__mul__(other)
            
    def __repr__(self):
        return repr(self.stackunit)

    def __str__(self):
        return str(self.stackunit)
            
    def __setitem__(self, key, value):
        if key != 'pn' or key != 'n' or key != 'su':
            self.stackunit[key] = value
        #try:
        #    if self.sync_on:
        #        self.sync()
        #except:
        #    pass
        
    def __getitem__(self, key):
        return self.stackunit[key]

    def __delitem__(self, key):
        flag = False
        for k in ['d', 'dt', 'pn', 'n', 'sigma', 'su']:
            if k == key:
                flag = True
        if flag == False:
            del self.stackunit[key]
            
    def __contains__(self, item):
        if item in self.stackunit:
            return True
        else:
            return False

    def __missing__(self, key):
        pass

    def __iter__(self):
        # ref: http://stackoverflow.com/questions/19344046/iterating-through-a-dictionary-of-a-class-object-without-mixin-python
        #keys = self.stackunit.keys()
        #for k in keys:
        #    yield k
        return iter(self.stackunit.keys())

    def __len__(self):
        return len(self.stackunit)
        
    def __neg__(self):
        d = self.stackunit['d']
        dct = self.stackunit
        dct['d'] = -abs(d)
        su = Stackunit(dct)
        return su
        
    def __pos__(self):
        return self
        
    def get(self, key, default=None):
        return self.stackunit.get(key, default)
        
    def lim(self, units=None):
        '''Based on d and dt, calulate the min and max value for the dimension.
        If units is specified, and is 'mm' or 'in', then the value is converted
        to mm or inch.
        '''
        try:
            if units[0] == 'm':
                fac = 25.4
            elif units[0] == 'i':
                fac = 1/25.4
            else:
                fac = 1.0
        except TypeError:
            fac = 1.0     
        return ((self.stackunit['d'] - self.stackunit['dt'])*fac, 
                (self.stackunit['d'] + self.stackunit['dt'])*fac)
        
    def todict(self):
        '''Converts a Stacks object to a standard dictionary object.'''
        return self.stackunit

    def _update(self, *args, **kwargs):
        '''update self.stackunit'''
        stackunit = {**self._parse_data(args), **kwargs}
        if stackunit and isStackunit(stackunit):
            self.stackunit = stackunit
            

class Tbearing(Stackunit):
    '''Find the length of a tapered roller bearing after press fit onto a shaft
    and/or after the bearing cup is press fit into a housing.
    
    An object of this class can be used as a Stackunit object, and can
    therefore be directly used within a stackup.  Furthermore, if a parameter
    of this object is updated, such as a bearing fit, then the stackup that
    containing this Stackunit object automatically updates.
    
    After instantiating this object, run the methods *cone* and/or *cup* to
    put the pressfit onto the bearing.
    
    Parameters
    ==========
    
    Y : float
        Y factor of the bearing (reference: Y = K/.9725)
    
    widthMin : float
        Minimum overall bearing width, not including the effect of a pressfit
        on the cone or cup.

    widthMax : float
        Maximum overall bearing width (width across cone and cup), not
        including the effect of a pressfit on the cone or cup.
        
    pn : str
        Bearing's part number
        
    n :  str 
        description of the dimension.  default: 'Bearing pressed width'
    
    sigma : float
        sigma value.  default: 6
    
    Examples
    ========

    Instantiate the bearing, where: widthMin = .8465, widthMax = .8504,
    Y = 1.97:  
    
    >>> tbrg = Tbearing(.8465, .8504, 1.97, pn='JLM104948/JLM104910')  

    Add pressfit to the the inner ring (i.e., the cone).  Where:
    coneID = 1.9685 , meanConeOD = 2.3417 (where the roller sits), 
    coneFitMax = .0021, coneFitMin = .001 (diametral interferances).     
    
    >>> tbrg.cone(1.9685, 2.3417, .0021, .001)
    
    Add a pressfit to the outer ring... cupOD = 3.2283, meanCupID = 2.837 
    (where the roller sits), cupFitMax = .003, cupFitMin = .001
    
    >>> tbrg.cup(3.2283, 2.837, .0021, .001)
    
    Add that bearing onto a stack you are currently working on; say stack 3 
    of stks in this case:
    
    >>> stks[3].append(tbrg)
    
    If, for example, your bearing is at row 14 in the stacks, and you want to
    see ALL the parameters for the bearing:
    
    >>> stks[3][14]
    {'objtype': 'Tbearing', 'su': 0, 'widthMin': 0.8465, 
    'dt': 0.004272767387264675, 'cupFitMax': 0.0021, 
    'n': 'Bearing pressed width', 'cupFitMin': 0.001, 'Y': 1.97, 
    'cupOD': 3.2283, 'widthMax': 0.8504, 'sigma': 6, 'meanCupID': 2.837, 
    'd': 0.8549959808186551, 'pn': 'JLM104948/JLM104910', 'meanConeOD': 2.3417, 
    'housingOD': inf, 'ConeID': 1.9685, 'j': 1, 'shaftID': 0, 
    'coneFitMin': 0.001, 'coneFitMax': 0.0021}
    
    (Note: the outbput above looks like a Python dictionary, functions like a
    Python dictionary, but is not a Python dictionary.  It is a Tbearing 
    object.)
    And if later you need to change a pamarameter, such as a fit:
    
    >>> stks[3][14]['coneFitMin'] = .002
    >>> stks[3][14]['coneFitMax'] = .0031
    >>> stks[3][14]
    {'objtype': 'Tbearing', 'su': 0, 'widthMin': 0.8465, 
    'dt': 0.004272767387264675, 'cupFitMax': 0.0021, 
    'n': 'Bearing pressed width', 'cupFitMin': 0.001, 'Y': 1.97, 
    'cupOD': 3.2283, 'widthMax': 0.8504, 'sigma': 6, 'meanCupID': 2.837, 
    'd': 0.8570607209386972, 'pn': 'JLM104948/JLM104910', 'meanConeOD': 2.3417,
    'housingOD': inf, 'ConeID': 1.9685, 'j': 1, 'shaftID': 0, 
    'coneFitMin': 0.002, 'coneFitMax': 0.0031}
    
    The press fit is recalculated; d and/or dt are updated.  Or you can use the 
    cone method again:
    
    >>> stks[3][14].cone(1.9685, 2.3417, .0031, .002)
    '''    
    def __init__(self, Y, widthMin, widthMax, pn='trbearing1', 
                 n='Bearing pressed width', sigma=6):
        self.sync_on = True
        self.indx = -1
        self.stackunit = {}
        if abs(widthMax) > abs(widthMin):
            self.stackunit['widthMax'] = widthMax
            self.stackunit['widthMin'] = widthMin 
        else:
            self.stackunit['widthMin'] = widthMax
            self.stackunit['widthMax'] = widthMin 
        self.stackunit['Y'] = Y
        self.stackunit['pn'] = pn
        self.stackunit['n'] = n
        self.stackunit['sigma'] = sigma
        self.stackunit['su'] = 0
        self.stackunit['objtype'] = 'Tbearing'
        self.stacks = []
        self.calculate()
    
    def __getitem__(self, key):
        return self.stackunit[key]
         
    def __setitem__(self, key, value):
        if (key in self.stackunit and (key != 'pn' or 
                key != 'n' or key != 'su' or key != 'd' or key != 'dt')):
            super(Tbearing, self).__setitem__(key, value)
            self.calculate()
        else:
            print(str(key) + ' is not currently a part of this stackunit.  This')
            print('seems to be an error in spelling on your part???  This key/value')
            print('has not been added... that is, nothing happened')
            
    def __add__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            b = {}
            for x in self.stackunit:
                if x == 'widthMax' or x == 'widthMin':
                    b[x] = self.stackunit[x] + other
                else:
                    b[x] = self.stackunit[x]
            tb = Tbearing(0, 0, 0)
            tb.stackunit = b
            tb.calculate()
            return tb
    
    def __radd__(self, other):
        return self.__add__(other)
            
    def __sub__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            b = {}
            for x in self.stackunit:
                if x == 'widthMax' or x == 'widthMin':
                    b[x] = self.stackunit[x] - other
                else:
                    b[x] = self.stackunit[x]
            tb = Tbearing(0, 0, 0)
            tb.stackunit = b
            tb.calculate()
            return tb
            
    def __rsub__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            b = {}
            for x in self.stackunit:
                if x == 'widthMax' or x == 'widthMin':
                    b[x] = other - self.stackunit[x]
                else:
                    b[x] = self.stackunit[x]
            tb = Tbearing(0, 0, 0)
            tb.stackunit = b
            tb.calculate()
            return tb

    def __mul__(self, other):
        b = {}
        if isinstance(other, int) or isinstance(other, float):
            for x in self.stackunit:
                if x in ['ConeID', 'meanConeOD', 'd', 'widthMin', 'widthMax', 
                         'cupOD', 'coneFitMin', 'dt', 'housingOD', 'shaftID', 
                         'coneFitMax', 'cupFitMin', 'meanCupID', 'cupFitMax']:
                    b[x] = self.stackunit[x] * other
                else:
                    b[x] = self.stackunit[x]
            tb = Tbearing(0, 0, 0)
            tb.stackunit = b
            tb.calculate()
            return tb
            
    def __rmul__(self, other):
        return self.__mul__(other)
        
    def cone(self, coneID, meanConeOD, coneFitMin, coneFitMax, shaftID=0):
        '''Apply parameters for an interferance fit between the inner race 
        (i.e., the cone) and the shaft.  With an interferance fit, the length
        of the bearing will increase slightly.
        
        Parameters
        ==========
        
        coneID : float
            The bore diameter of the bearing.
            
        meanConeOD : float
            The outside of the diameter of the cone where the roller sits, and
            at the middle of the roller.
            
        coneFitMin : float
            The minimum diametral interferance between the coneID and the shaft
            
        coneFitMax : float
            The maximum diametral interferance between the coneID and the shaft.
            If the coneID is 2.5, and the shaft diameter is 2.502, the the 
            coneFitMax is .002.. 
            
        shaftID : float
            The ID of the shaft.  The inside diameter of the hole through the
            middle of the shaft.  default: 0
            
        Reference
        =========
        
        SKF bearing catalog,
        http://www.skf.com/binary/77-121486/SKF-rolling-bearings-catalogue.pdf,
        page 173, gives some recommened fits for coneFitMin and coneFitMax.
        '''
        if coneID < meanConeOD:
            self.stackunit['ConeID'] = coneID
            self.stackunit['meanConeOD'] = meanConeOD
        else:
            self.stackunit['ConeID'] = meanConeOD
            self.stackunit['meanConeOD'] = coneID
        if coneFitMax > coneFitMin:
            self.stackunit['coneFitMax'] = coneFitMax
            self.stackunit['coneFitMin'] = coneFitMin
        else:
            self.stackunit['coneFitMax'] = coneFitMin
            self.stackunit['coneFitMin'] = coneFitMax
        self.stackunit['shaftID'] = shaftID
        self.calculate()

    def conegrowth(self):
        ''' Report how much the bearing length increases due to a press fit
        of the inner raceway, the cone, onto the shaft'''
        try:
            d = self.stackunit['ConeID']
            do = self.stackunit['meanConeOD']
            Y = self.stackunit['Y']
            fitMax = self.stackunit['coneFitMax']
            fitMin = self.stackunit['coneFitMin']
            ds = self.stackunit['shaftID']
            return conegrowth(d, do, Y, fitMax, fitMin, ds)
        except KeyError:
            print('No fit has yet been established.')            
        
    def cup(self, cupOD, meanCupID, cupFitMin, cupFitMax, housingOD=float('inf')):
        '''Apply parameters for an interferance fit between the outer race 
        (i.e., the cup) and the housing bore.  With an interferance fit, the 
        length of the bearing will increase slightly.
        
        Parameters
        ==========
        
        cupOD : float
            The outside diameter of the bearing..
            
        meanCupID : float
            On the tapered surface, the mean inside diameter.
            
        cupFitMin : float
            The minimum diametral interferance between the cupOD and the 
            housing. 
            
        cupFitMax : float
            The maximum diametral interferance between the cupOD and the 
            housing.  That is, if the coneID is 2.5, and the shaft diameter is 
            2.502, the the cupFitMax is .002.
                    
        housingOD : float
            The OD of the housing over the area where the cup fits.
            default: inf (infinity)
            
        Reference
        =========
        
        SKF catalog,
        http://www.skf.com/binary/77-121486/SKF-rolling-bearings-catalogue.pdf,
        page 174 and 175 gives some recommended fits cupFitMin and cupFitMax.
        '''
        if meanCupID < cupOD:
            self.stackunit['meanCupID'] = meanCupID
            self.stackunit['cupOD'] = cupOD
        else:
            self.stackunit['meanCupID'] = cupOD
            self.stackunit['cupOD'] = meanCupID
        if cupFitMax > cupFitMin:
            self.stackunit['cupFitMax'] = cupFitMax
            self.stackunit['cupFitMin'] = cupFitMin 
        else:
            self.stackunit['cupFitMax'] = cupFitMin
            self.stackunit['cupFitMin'] = cupFitMax 
        self.stackunit['housingOD'] = housingOD
        self.calculate()
        
    def cupgrowth(self):
        ''' Report how much the bearing length increases due to a press fit
        of the outer raceway, the cup, into the housing'''
        try:
            D = self.stackunit['cupOD']
            Do = self.stackunit['meanCupID']
            Y = self.stackunit['Y']
            fitMax = self.stackunit['cupFitMax']
            fitMin = self.stackunit['cupFitMin']
            Dh = self.stackunit['housingOD']        
            return cupgrowth(D, Do, Y, fitMax, fitMin, Dh)
        except KeyError:
            print('No fit has yet been established.') 
             
    def help():
        print('Methods: cone (set fit of cone on shaft), cup (set fit of')
        print('cup in housing), conegrowth, cupgrowth')
        
    def calculate(self):
        '''Calculate the length changes due to a pressfit on the cone or cup.
        This is done automatically when a variable is changed, so it is not
        necessary to execute this method manually.'''
        d = self.stackunit.get('ConeID', 0.0)
        do = self.stackunit.get('meanConeOD', 0.0)
        Do = self.stackunit.get('meanCupID', 0.0)
        D = self.stackunit.get('cupOD', 0.0)
        wMax = self.stackunit.get('widthMax', 0.0)
        wMin = self.stackunit.get('widthMin', 0.0)
        coneFitMax = abs(self.stackunit.get('coneFitMax', 0.0))
        coneFitMin = abs(self.stackunit.get('coneFitMin', 0.0))
        cupFitMax = abs(self.stackunit.get('cupFitMax', 0.0))
        cupFitMin = abs(self.stackunit.get('cupFitMin', 0.0))
        Y = abs(self.stackunit.get('Y', 0.0))
        Dh = self.stackunit.get('housingOD', float('inf'))
        ds = self.stackunit.get('shaftID', 0)        
        coneG = conegrowth(d, do, Y, coneFitMax, coneFitMin, ds)
        cupG = cupgrowth(D, Do, Y, cupFitMax, cupFitMin, Dh)
        w = (abs(wMax), abs(wMin))
        widthMax = max(w) + max(coneG) + max(cupG)
        widthMin = min(w) + min(coneG) + min(cupG)
        d = (widthMax + widthMin)/2.0
        dt = abs(widthMax - widthMin)/2.0
        self.stackunit['d'] = d
        self.stackunit['dt'] = dt
            

def isStackunit(test_item):
    '''Determine if test_item would be suitible to be a valid Stackunit object.
    
    Parameters
    ==========
    
    test_item : dictionary
        test_item must be a dictionary, and the dictionary must contain the
        keys 'su', 'sigma', 'd', 'dt', 'pn', and 'n'.
    '''
    if isinstance(test_item, Stackunit):
        return True
    flag = True
    try:
        if 'title' in test_item:
            return True
        else:
            for y in ['su', 'sigma', 'd', 'dt', 'pn', 'n']:
                if y not in test_item:
                    flag = False
    except:
        return False
    if flag == False:
        return False
    if (not isinstance(test_item['su'], int) or
          not (isinstance(test_item['d'], float) or 
               isinstance(test_item['d'], int)) or 
          not ( isinstance(test_item['dt'], float) or 
                isinstance(test_item['dt'], int)) 
          or not isinstance(test_item['pn'], str) or not isinstance(test_item['n'], str)):
              return False   
    return True


def isStack(test_item):
    '''Determine if test_item would be suitible to be a valid Stack object.
    '''
    if isinstance(test_item, Stack):
        return True
    hastitle = False
    try:
        for x in test_item:
            if  'title' in x and 'j' in x:
                hastitle = True
            else:
                if not isStackunit(x):
                    return False
    except:
        return False
    if hastitle:     # at this point, is valid... but last check: hastitle?
        return True
    else:
        return False
    
def isStacks(test_item):
    '''Determine if test_item would be suitible to be a valid Stacks object.
    '''
    if isinstance(test_item, Stacks):
        return True
    hastitle = False
    try:
        for x in test_item:
            if isinstance(x, dict) and 'title' in x:
                hastitle = True
            else:
                if not isStack(x):
                    return False
    except:
        return False
    if hastitle:  # at this point, is valid... but last check: hastitle?
        return True
    else:
        return False

def sign(x):
    if isinstance(x, bool):
        if x:
            return 1
        else:
            return -1
    if x > -1e-10:
        return 1
    else:
        return -1


def lim(upper_limit, lower_limit):
    ''' Takes the upper and lower allowable limits of a dimension and returns
    the mean +/- tolerance.

    Parameters
    ==========

    upper_limit : float
        The upper limit value of a tolerance

    lower_limit : float
        The lower limit value of a tolerance

    Returns
    =======

    out : tuple
        A tuple of length two containing two floats: the first is the mean
        value, and the second is the plus/minus tolerance

    Note that the order of the parameters makes no difference; output is the
    same reguardless
    '''
    mean = (upper_limit + lower_limit)/2
    plus_minus_tolerance = abs((upper_limit - lower_limit)/2)
    return mean, plus_minus_tolerance


def n_already_exists(pn, n, pndic):
    ''' Determine if the dimension description, n, already exists for a
    dimension that pertains to a particular part number.

    A match will occur if all letters and numbers are the same.  Characters
    such as -, #, $, and spaces, etc., are ignored.  Furthermore the search is
    case insensive.  Reason: users tend to fat finger letters when they're in
    a hurry, such as when doing stackups; that is, duuplicatee letterrs
    or   spaces occuur.  This *fuzzy* matching tries to eliminate
    unintended duplicate stack dimensions.

    Parameters
    ==========

    pn : str
         The part number for the dimension description you wish to investigate.

    n : str
        The dimension description that you are investigating.

    pndic : dic
        pndic created via the pn method of a Stacks object.

    Returns
    =======

    out : int
        Returns the value of i if found.  Else returns 0.
    '''
    if pn in pndic:
        for key in pndic[pn]:
            if nSquished(n) == nSquished(pndic[pn][key]['n']):
                return key
    return 0


def nSquished(n):
    ''' Take a string, n, and return it in upper case and also remove charaters
    that are not letters or numbers.  This is used to check if a dimension
    name is unique or not.  For example, the names 'groove to end' and
    'Groove-to-end' are, as far as the programs concerns, the same.
    Same names for two different stack units is not allowed.  This function
    is called upon other functions of this program.
    '''
    return (re.sub("[^a-zA-Z0-9]", '', n)).upper()  # ectract ONLY letters & nos., and then make uppercase


def conegrowth(d, do, Y, fitMax=0, fitMin=0, ds=0.0):
    """Find the additional length accrued by a tapered roller bearing due
    the press fit of the bearing cone on a shaft.

    Parameters
    ==========
    
    d : float
        bore diameter of the cone

    do : float
        mean outside diameter of the cone
        
    Y : Y factor

    fitMax : float
        Maximum diametral interference between the cone and shaft.
        
    fitMin : float
        Minimum diametral interference between the cone and shaft.

    ds : float
        bore diameter of the shaft.  default: 0.0
        
    Cone growth calculation based on the equation provided in Timken's catalog.
    (K = Y * .9725)
    
    Returns
    =======
    
    out: tuple
        (conegrowthMax, conegrowthMin)... i.e., axial length increase
    """
    K = Y * .9725
    try:
        conegrowthMin = .5 * (K/.39) * ((d/do) *
            (1 - (ds/d)**2) / (1 - (ds/do)**2)) * abs(fitMin)
        conegrowthMax = .5 * (K/.39) * ((d/do) *
            (1 - (ds/d)**2) / (1 - (ds/do)**2)) * abs(fitMax)
        return conegrowthMax, conegrowthMin
    except ZeroDivisionError:
        return (0.0, 0.0)


def cupgrowth(D, Do, Y, fitMax=0.0, fitMin=0.0, Dh=float('inf')):
    """Find the additional length accrued by a tapered roller bearing due
    the press fit of the bearing cup in a housing bore.

    Parameters
    ==========
    
    D : float
        outside diameter of the cup.

    Do : float
        mean inside diameter of the outer ring (at midpoint of roller).

.   Y : float
        Y factor

    fitMax : float
        Maximum diametral interference of the cup in the housing bore.
        
    fitMin: float
        Minimum diametral interference of the cup in the housing bore.

    Dh : float
        housing outside diameter.  default: infinity

    Cone growth calculation based on the equation provided in Timken's catalog.
    (K = Y * .9725)
    
    Returns
    =======
    
    out: tuple
        (cupgrowthMax, cupgrowthMin)... i.e., axial length increase
    """        
    K = Y *.9725
    try:
        cupgrowthmin = .5 * (K/.39) * ((Do/D) *
            (1 - (D/Dh)**2) / (1 - (Do/Dh)**2)) * abs(fitMin)
        cupgrowthmax = .5 * (K/.39) * ((Do/D) *
            (1 - (D/Dh)**2) / (1 - (Do/Dh)**2)) * abs(fitMax)
        return cupgrowthmax, cupgrowthmin
    except ZeroDivisionError:
        return (0.0, 0.0)
    

def get_version():
    return __version__

       
def strike(text, s=True):
    '''Alter text so that a line is drawn through the text'''
    result = ''
    for c in text:
        result = result + c + '\u0336'
    if s:
        return result
    else:
        return text


def load(filename):
    '''Open a file containing stackup data and use it for the stackups 
    program.  If data for a Stacks object is encountered, then a Stacks
    object is created.  If data for a Stack, then a Stack object is
    created, and if for a Stackunit, then a Stackunit is created.
    
    When a file is opened, in order to use it, it needs to be assigned to 
    a variable.  For example: mach01 = fileopen(C:/project1/machine01.stk)
    
    Parameters
    ==========
    
    filename : string
        The name of the file to open.
        
    Examples
    ========
    
    View the current filename:        
    
    >>> stks.filename
    
    Save file in the current working directory:
    
    >>> mach123 = fileopen('machine123.stk')
    
    Specify the path to the file (Microsoft Windows):        
    
    >>> s = fileopen('C:/tractorproject/transmission/06N3422.stk')
    
    **NOTE THAT A FORWARD SLASH, /, AND NOT A BACKSLASH, \\, IS USED**.
    Due to Python's way of functioning, a backslash cannot be used
    for a file path. Python will itself take care of the details of 
    translating the forward slash to a backslash when the file is opened.
    '''
    global _s
    if filename:
        filename = os.path.expanduser(filename)
        filename = os.path.abspath(filename)  # if filename = '', returns cwd
    else:
        print('no filename provided')
        return  
    s = ''
    with open(filename, 'r') as inp: 
        for line in inp.readlines():
            if line[0] != '#':
                s += line
    s_list = ast.literal_eval(s)
    if 'settings' in s_list[0] and _s['defaults']:
        _s = s_list[0]['settings']  # load the settings that were stored in the file.
    ap, _s['autoprint']  = _s['autoprint'], False
    if isStackunit(s_list):
        if 'objtype' in input and input['objtype'] == 'Tbearing':
            su = Tbearing(0, 0, 0)
            su.stackunit = s_list
            su.stacks = self.stacks
        else:
            su = Stackunit(s_list)
        su.filename = filename
        _s['autoprint'] = ap
        return su
    elif isStack(s_list):
        stk = Stack(s_list)
        stk.filename = filename
        _s['autoprint'] = ap
        return stk
    elif isStacks(s_list):
        stks = Stacks(s_list)
        stks.filename = filename 
        _s['autoprint'] = ap
        return stks
    else:
        print(filename + ' not valid for a Stacks, Stack, or Stackunit')
        
    
def save(stkobject, filename, pagebreak=True, lines_per_page=58):
    ''' Save a Stacks, Stack, or Stackunit object.  If the filename extension
    is txt (e.g., myfile.txt) then saves the file as a human readable text file
    which can be opened up with Microsoft Word, etc.
    
    If not saved as a text file, the filename should have the extension stk
    (e.g., myfile.stk).  This stk file can be opened for editing with the
    stackups program.
    
    Parameters
    ==========
    
    filename : str
        filename can include a path, but the pathname must be Python compatible.
        That is, insead of using a backlash character, either of forward slash
        or two consecutive backslashes should be used in place of a backslash
        (see examples).
        
    pagebreak : bool
        A page break character is inserted at appropriate intervals.  This 
        character has an affect when the output file is to be used with 
        Microsoft Word or equivalent.  The value only affects output in txt 
        format.  default: True
        
    lines_per_page : int
        This causes the pagebreak to be invoked at appropriate intervals.
        
    Examples
    ========
    
    >>> stksave('C:\\mypath\\myfile.stk')   # data can later be edited
    
    >>> stksave(''C:/mypath/myfile.stk')   # does the same as above
    
    >>> stksave('myfile.stk')  # saved to the current working directory
    
    >>> sktsave('myfile.txt')   # Can print to a printer with this format. 
    '''
    global _s
    if not isinstance(stkobject, Stacks):
        print('stkobject is not an instance of Stacks')
        return
    elif not isinstance(stkobject, Stackunit) and isinstance(stkobject, Stack):
        stkobject.stack[0]['settings'] = _s
    elif not isinstance(stkobject, Stackunit) and isinstance(stkobject, Stacks):
        stkobject.stacks[0]['settings'] = _s
    
    lt = []
    datatype = ''
    
    if ((filename.lower() == 'txt' or filename.lower() == '.txt')
            and stkobject.filename):
        filename = stkobject.filename + '.txt'
    elif (filename.lower() == 'txt' or filename.lower() == '.txt'):
        print('Object has no attribute named "filename".  Nothing saved')
        return
    
    if filename:
        filename = os.path.expanduser(filename)
        filename = os.path.abspath(filename)  # if filename = '', returns cwd
    else:
        print('no filename provided')
        return     
        
    if os.path.splitext(filename)[1] != '.txt':
        filename = os.path.splitext(filename)[0] + '.stk' 
        stkobject.filename = filename  # attach new filename to stk object
                         
    if isinstance(stkobject, Stackunit):  # start looking to gather object's data
        lt = stkobject.stackunit
        datatype = '# Stackunit data\n'
    elif isinstance(stkobject, Stack):   
        for su in stkobject:
            if isinstance(su, Stackunit):
                lt.append(su.stackunit)
            else:
                lt.append(su)
        datatype = '# Stack data\n'
    elif isinstance(stkobject, Stacks):
        lt.append(stkobject[0])
        for x in stkobject:
            stk = []
            if isinstance(x, Stack):
                for su in x:
                    if isinstance(su, Stackunit):
                        stk.append(su.stackunit)
                    else:
                        stk.append(su)
                lt.append(stk)
        datatype = '# Stacks data\n'
    else:
        print('stkobject not valid')
        return

    ltstr =  str(lt)   # if not a Stacks or Stack, then Stackunit.  Put this in the file
    if isStacks(stkobject):  # make Stacks data in a file human readable    
        ltstr = '[' +  str(lt[0]) + ',\n\n'
        for stk in lt[1:]:
            ltmp = ''
            for su in stk:
                ltmp += str(su) + ',\n'
            ltstr += '[' + ltmp[:-2] + '],\n\n'
        ltstr = ltstr[:-3] +  '\n\n]'
    elif isStack(lt):  # make Stack data in a file human readable  
        ltstr = '['
        for su in lt:
            ltstr += str(su) + ',\n'
        ltstr = ltstr[:-2] +  ']'
            
    filetype = os.path.splitext(filename)[1].lower()
      
    if filetype == '.stk':        
        with open(stkobject.filename, 'w') as f:
            f.write(datatype)
            f.write('# This data created by, and used by, the Python computer program "stackups.py".\n')
            f.write('# The "stackups.py" program was written by Kenneth E. Carlton.\n')
            f.write('# "stackups.py" does stackup calculations to determine clearances between machined\n')
            f.write('# parts within a machine.\n')
            f.write('# The data of this file is not meant to be altered by a human.  Use the program\n')
            f.write('# to open this file and make changes.\n\n')
            f.write(ltstr)
            # print('file saved as: ' + stkobject.filename)
        return
    elif filetype == '.txt' and datatype == '# Stacks data\n':
        lpp = lines_per_page  # with page break active, lines per page
        with open(filename, 'w') as f:
            s = ''  # string collector... at end, wiil save to file
            lngth = 0  # keep sum of lines per page
            
            # Main title and Contents:
            titles = stkobject.titles()
            s1 = titles[0][1] + '\n'  # main title
            s1 += (len(s1) - 1)*'=' + '\n\n\n'
            s1 += 'Stack Titles\n============\n'
            for t in titles[1:]:
                s1 += '[' + str(t[0]) + ']: ' + str(t[1]) + '\n'
            s1 += '\n\n'
            s1_count = s1.count('\n')            
            lngth = lngth + s1_count
            if lngth >= lpp:        # Add a page break (\f).  Effect is seen in
                lngth = s1_count    # Word doc, but is not seen in a text file.
                s += '\f' + s1
            else:
                s = s1   
            
            s2 = 'Stackunits\n==========\n'
            def fnkey(stackunit):  # use as key for sorting; sort by pn, then by su
                return stackunit['pn'] + str(stackunit['su']).zfill(5) 
            sulist = stkobject._search_strs('*')
            if sulist:
                sulistsorted = sorted(sulist, key=fnkey)
                s2 += (stkobject._sulist2str(sulistsorted))
            s2 += '\n\n'
            s2_count = s2.count('\n')         
            lngth = lngth + s2_count
            if lngth >= lpp:
                lngth = s2_count
                s += '\f' + s2
            else:
                s += s2 
                
            s3 = 'Where used\n==========\n'
            wudic = stkobject._wudic()
            wu_keys = sorted(wudic.keys())
            for su in wu_keys:
                s3 += str(su) + ' : ' + str(wudic[su]) + '\n'
            s3 += '\n\n'
            s3_count = s3.count('\n')
            lngth = lngth + s3_count
            if lngth >= lpp:
                lngth = s3_count
                s += '\f' + s3
            else:
                s += s3 
            
            if len(stkobject) > 4:  # if a lot of stacks, then page break
                lngth = 0
                s += '\f'
                
            s4 = 'Stacks\n======\n\n'
            for sobj in stkobject[1:]:
                s4 += str(sobj)
                s4 += '\n'
                s4_count = s4.count('\n') 
                lngth = lngth + s4_count
                if lngth >= lpp:
                    lngth = s4_count
                    s += '\f' + s4
                    s4 = ''
                else:
                    s += s4
                    s4 = ''
                
            f.write(s)
            # print('file saved as: ' + filename)
            
    elif filetype == '.txt' and datatype == '# Stack data\n':
        with open(filename, 'w') as f:
            s = 'Stack\n=====\n\n'
            s += str(stkobject)
            f.write(s)
            print('file saved as: ' + filename)
            
    elif filetype == '.txt' and datatype == '# Stackunit data\n':
        with open(filename, 'w') as f:
            s = 'Stackunit\n=========\n\n'
            s += str(stkobject)
            f.write(s)
            print('file saved as: ' + filename)
        
def settings(**kwargs):
    '''Control the appearance of the output for the stackups program
    
    Parameters
    ==========
    
    Acceptable arguments (any others will be ignored):
        
    alter : bool
        Alter normal python output.  Normal output shows object data (via
        python's __repr__ method).  Altered output shows human readable text
        (as would be derived via python's __str__ method.)  Default: True 
        (that is, alter the output.)
    arrow : int
        1, 2, 3, ..., 10.  Changes the appearance of the arrow to different
        styles. {1: ('＜', '＞'), 2: ('<', '>'), 3: ('↤', '↦'), 4: ('↢', '↣'),
        5: ('⇽', '⇾'), 6: ('←', '→'), 7: ('⇦', '⇨'), 8: ('-', '+'),
        9: ('✗', '✔'), 10: ('↞', '↠')}  Default: 8        
    autoprint : bool
        Automatically print stack results after appending new data to a stack
        (i.e., via the methods append, a, extend, e).  Default: True
    defaults: bool
        If true, reset all settings back to their defaults.
    highlight : bool
        Distinguish left arrow better.  In the stackup table, add some color
        in back of the left arrow to better distinguish it from the right
        Reset all settings to defaults.  Default: True
    reset : bool
        reset all variables to their defaults
    sigma_mult : int
        Show, as a reference, the calulated sigma value multiplied by this
        number.  Default: 0
    short_repr : bool
        If True: shorten lines of repr's data ouput to about half so that it
        may fit on small screen displays (if "alter" setting is False).
        Default: False
    silent : bool
        Suppress output.  (This value is not stored.)  Default: False
    threshold : int
        Show probability calculations for a stack once this number of stack
        units is surpassed.  Default: 1

    Examples
    ========
    
    >>> settings(precision=3, alter=False)
    
    >>> settings(defaults=True)   # reset all settings to their defaults
    
    >>> settings()  # show current settings
    '''
    global _s
    defaults = {'precision':4, 'alter':True, 'short_repr':False, 'threshold':1, 
       'sigma_mult':0, 'highlight': False, 'arrow':8, 'autoprint':True, 
       'defaults':True}
    try:
        _s
    except:
        _s = defaults
    silent = False
    if kwargs:
        for key in kwargs:
            if key == 'arrow' and kwargs[key] > 10:
                print('arrow 1 to 10 only')
            elif key == 'defaults' and kwargs['defaults'] == True:
                _s = defaults
                _s['defaults'] = True
            elif key == 'silent':  # e.g., no output with: settings('silent'=True) 
                silent = True               
            elif key in _s:
                _s[key] = kwargs[key]
            else:
                print('Not valid:', key)
                print('Valid parameters are: ', end='')
                listofkeys = []
                for key in _s:
                    listofkeys.append(key)
                print(', '.join(listofkeys) + '.')
                print('See the documentation for an explanation about settings.\n')
    if not silent:
        for key in _s:
            print(key + ' = ' + str(_s[key]))
    for k in defaults:
        if defaults[k] != _s[k]:
            _s['defaults'] = False
            
           
settings(silent=True)  # Establish settings.  If not done, program will not fuction.

        
def _inherit_test(test_object):
    '''Test to see if all of the objects, i.e. Stacks objects Stack objects,
    and Stackunit objects, have inherited the same dictionary named "stacks"
    that originated from the Stacks and/or Stack object.  This dictionary needs
    to be present in all objects for the program to function properly.
    (This function created for trouble shooting only.  It is not required for
    the operation of the stackups program.)
    
    Parameters
    ==========
    
    test_object : A Stacks or Stack object
    
    If test proves poitive, response to user is "OK", otherwise some
    error messages.
    '''
    stks = test_object.stacks
    flag = True
    if isinstance(test_object, Stack):
        for stkunt in test_object:
            if 'title' in stkunt:
                pass
            else:
                try:
                    if  stkunt.stacks != stks:
                        print('"stacks" of this Stackunit did not match that of root.')
                        print(stkunt)
                    else:
                        pass # print('.', end='')
                    flag = False
                except:
                    print('An exception occured.  The following did not contain a copy of "stacks":')
                    print(stkunt)
                    flag = False
            if flag:
                print('OK')
    elif isinstance(test_object, Stacks):
        for stk in test_object:
            try:
                if 'title' not in stk and stk.stacks != stks:
                    print('"stacks" of this Stack did not match that of root.')
                    print(stk)
                else:
                    pass # print('.', end='')
            except:
                print('An exception occured.  The following did not contain a copy of "stacks":')
                print(stk)
                flag = False
        for stk in test_object:
            for stkunt in stk:
                try:
                    if 'title' not in stkunt and stkunt.stacks != stks:
                        print('"stacks" of this Stackunit did not match that of root.')
                        print(stkunt)
                    else:
                        pass #print('.', end='')
                except:
                    print('An exception occured.  The following did not contain a copy of "stacks":')
                    print(stkunt)
                    flag = False
        if flag:
            print('OK')
    else:
        print('test_object is not a Stacks or Stack object')

