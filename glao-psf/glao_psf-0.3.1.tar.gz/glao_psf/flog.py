#!/usr/bin/env python
"""Create a log file for this directory

List files and header info in a comma-separated-values (csv) format
suitalbe to be read by spreadsheet programs
"""

import os
import sys
import argparse
import pyfits
import fnmatch
try:
    import pandas as pd
    pd.set_option('display.width',150)
    has_pandas = True
except:
    has_pandas = False

default_keys = [
    'DATE-OBS',
    'TIME-OBS',
    'DATE-BEG',
    'OBJECT',
    'RA',
    'DEC',
    'AIRMASS',
    'LOOPSTAT',
    'LOOPSUB',
    'WFSRATE',
    'TTRATE',
    'FILT1NAM',
    'ITIME',
    'COADDS'
]

eptext = 'Note that -a is the default (logs the union of all keys from all the FITS file headers). It is overridden by either -i,-k or -d options'
parser = argparse.ArgumentParser(description=__doc__,epilog=eptext)
parser.add_argument('-k','--keywords',metavar='keyword',type=str,nargs='+')
parser.add_argument('-a','--all',action='store_true',help='log all keywords found (This is the default, overridden by -i,-k, or -d)')
parser.add_argument('-d','--default_keys',action='store_true',help='use a pre-defined keyword set, as well as any provided -k keywords. The predefined keyword set is %r'%default_keys)
parser.add_argument('-i','--input_file',type=str,help='file containing keywords (one keyword per line)')
parser.add_argument('-v','--verbose',action='store_true',help='explain activity')
parser.add_argument('-f','--files',metavar='pattern',type=str,help='only list files matching the pattern')
parser.add_argument('-o','--output_file',type=str,help='output file name, otherwise output goes to log.csv')
# try:
#     args = parser.parse_args(['-h'])
# except SystemExit:
#     print 'system exit'

args = parser.parse_args()

verbose = args.verbose

if has_pandas:
    def pflog(keys=[], wildcard=None, only=False, directory='.'):
        """a version of flog that returns a pandas database rather than
        creating a csv file.
        """
        if not only:
            keys = keys + default_keys

        # select the files
        file_list = os.listdir(directory)
        sfile_list = []
        for fileName in file_list:
            if (fileName.endswith('.fits')):
                if wildcard is not None:
                    if fnmatch.fnmatch(fileName,wildcard):
                        sfile_list.append(fileName)
                else:
                    sfile_list.append(fileName)
        
        #print sfile_list
        sfile_list = map(lambda x: os.path.join(directory,x),sfile_list)
        db = pd.DataFrame(columns = ['FILE']+keys)
        
        for k,fileName in zip(range(1,len(sfile_list)+1),sfile_list):
            try:
                hdu = pyfits.open(fileName)
            except:
                print 'Trouble reading file '+fileName
                print sys.exc_info()
                continue
            hdr = hdu[0].header
            db.loc[k,'FILE'] = os.path.basename(fileName)
            for keyword in keys:
                if (keyword in hdr):
                    val = hdr.cards[keyword][1]
                    db.loc[k,keyword] = val
            hdu.close()
        return db
    
    def cmflog(keys=[], wildcard=None, only=False):
        """return a pandas database of all the control matrices
        """
        defaultKeys = ['DATE','NAXIS1','NAXIS2','CONTEXT','PENALTY','WEIGHT','NS','NW','NWM','GMETHOD']
        if not only:
            keys = defaultKeys + keys
        if wildcard is None:
            wildcard = 'controlMatrix*'
        db = pflog(keys=keys,wildcard=wildcard,only=True)
        for ind in db.index:
            fileName = db.loc[ind,'FILE']
            for mode in ['8x','16x','30x']:
                if mode in fileName: db.loc[ind,'MODE'] = mode
            if 'LGS' in fileName:
                db.loc[ind,'GS'] = 'LGS'
            else:
                db.loc[ind,'GS'] = 'NGS'
            if 'sim' in fileName:
                db.loc[ind,'SIM'] = True
            else:
                db.loc[ind,'SIM'] = False
        return db

def mkLog(keys=None, keywordFile=None, wildcard=None, outputFileName='log.csv', verbose=False, test=False):
    
    if verbose:
        print 'keys:'
        print keys
        print 'wildcard:', wildcard
        
    # select the files
    file_list = os.listdir('.')
    sfile_list = []
    for fileName in file_list:
        if (fileName.endswith('.fits')):
            if wildcard is not None:
                if fnmatch.fnmatch(fileName,wildcard):
                    sfile_list.append(fileName)
            else:
                sfile_list.append(fileName)
    
    if len(sfile_list) == 0:
        if wildcard is not None:
            raise Exception, 'no files match %s'%wildcard
        else:
            raise Exception, 'no FITS (*.fits) files found'
    
    if verbose:
        print 'matching files:'
        print sfile_list

    if keywordFile:
        fp = open(keywordFile)
        keys = fp.read().split()
        fp.close()
        
    if keys == 'first':
        # open the first file and glean the keys from the header
        hdu = pyfits.open(sfile_list[0])
        keys = hdu[0].header.keys()
        hdu.close()
    if keys == 'all':
        # open each file and merge the header keys
        keys = []
        for fileName in sfile_list:
            hdu = pyfits.open(fileName)
            these_keys = hdu[0].header.keys()
            keys.extend(x for x in these_keys if x not in keys)
            hdu.close()
    
    if test:
        return keys
    
    if outputFileName is None:
        outputFileName = 'log.csv'
    f = open(outputFileName,'w')
    
    sep = ';'
    sep_replace = ',' # replace sep characters in values with this character
    lin = 'FILE NAME'
    for keyword in keys:
        lin += sep+keyword

    f.write(lin+'\n')

    for fileName in sfile_list:
        lin = fileName
        try:
            hdu = pyfits.open(fileName)
        except:
            print 'Trouble reading file '+fileName
            print sys.exc_info()
            continue
        hdr = hdu[0].header
        for keyword in keys:
            if (keyword in hdr):
                val = hdr.cards[keyword][1]
                if (type(val) == str):
                    val = val.replace(sep,sep_replace)
                lin = lin + sep + str(val)
            else:
                lin = lin + sep
        if (verbose): print lin
        f.write(lin+'\n')
        hdu.close()

    f.close()

if __name__ == '__main__':
    if not args.keywords and not args.default_keys:
        keys = 'all'
    if args.keywords and not args.default_keys:
        keys = args.keywords
    if args.default_keys and not args.keywords:
        keys = default_keys
    if args.default_keys and args.keywords:
        keys = default_keys + args.keywords
    
    if args.output_file:
        outputFileName = args.output_file
    else:
        outputFileName = 'log.csv'
    
    keywordFile = args.input_file
    fileNameWildcard = args.files
    verbose = args.verbose
    
    mkLog(keys=keys,
          wildcard=fileNameWildcard,
          keywordFile=keywordFile,
          outputFileName=outputFileName,
          verbose=verbose)

def test():
    rkeys = mkLog(keys='all',verbose=True,test=True)
    for key in rkeys:
        print key
