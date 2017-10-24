#!/usr/bin/env python
###############################################################################
# (c) Copyright 2012-2016 CERN                                                #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
'''
Simple tool to extract LHCb RPMs to a specific directory,
without using the RPM command itself.

'''
import logging
import os
import subprocess
import tempfile
import stat

RPM_PREFIXES = {}
RPM_PREFIXES["lhcb"] = "/opt/LHCbSoft/lhcb/"


def rpm(*args, **kargs):
    ''' Wrapper to invoke RPM '''
    cmd = ['rpm'] + list(args)
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    output = process.communicate()[0]
    exit_code = process.wait()
    if kargs.get('error_output', False):
        return (output, exit_code)
    return output


def sanitycheckrpmfile(filename):
    ''' Checks if a rpm file is correctly downloaded

    .. warning::
       BEWARE: Returns None if we could not run the test because RPM is not
       installed!

    :param filename: the rpm filename
    :returns: True if the rpm was correctly downloaded
    '''
    try:
        res = rpm('-K', filename, error_output=True)
        return res[1] == 0
    except:
        return None


def getrpmgroup(filename):
    ''' Get the group of the RPM

    :param filename: the rpm filename
    :returns: the rpm group
    '''
    res = rpm('-qp', '--queryformat', '%{GROUP}', filename)
    if res:
        res.strip()
    return res.decode('utf-8')


def getrpmprefixes(filename):
    ''' Get the group of the RPM

    :param filename: the rpm filename
    :returns: the rpm prefixes
    '''
    res = rpm('-qp', '--queryformat', '%{PREFIXES}', filename)
    if res:
        res.strip()
    return res.decode('utf-8')


def checkrpminstall(rpmfilename, prefix, installdir):
    ''' Check that the extraction happended correctly

    :param rpmfilename: the rpm filename
    :param prefix: the prefix of the rpm
    :param installdir: the installation directory
    '''

    #     we use rpm --dump Dump file information as follows (implies -l):
    #     path size mtime digest mode owner group isconfig isdoc rdev symlink
    res = rpm("-qp", "--dump", rpmfilename)
    for l in res.splitlines():
        try:
            (path, size, _mtime, _digest, _mode, _owner, _group,
             _isconfig, _isdoc, _rdev, _symlink) = l.split(" ")
            lpath = os.path.join(installdir, path.replace(prefix, ""))
            s = os.stat(lpath)
            if not stat.S_ISDIR(s.st_mode):
                if int(size) != s[stat.ST_SIZE]:
                    logging.error("Size mismatch for %s. local:%s, RPM: %s"
                                  % (lpath, s[stat.ST_SIZE], int(size)))
        except Exception as e:
            logging.error("Problem checking file %s, %s" % (lpath, str(e)))


#
# Second version with cpio interactive
###############################################################################
def _extractone(rpmname, prefix, keepfilelist=False):
    ''' extract a specific rpm in the localdir

    :param rpmfilename: the rpm filename
    :param prefix: the prefix of the rpm
    :param keepfilelist: flag to keep the temporary files

    :returns: thre return code
    '''

    # Dump the list of files
    cmdrpm2cpio = ["rpm2cpio", rpmname]
    cmdcpiolist = ["cpio", "-t"]
    outfile = tempfile.NamedTemporaryFile(prefix="cpiotout",
                                          delete=not keepfilelist)
    # Chaining the processes with a pipe
    p1 = subprocess.Popen(cmdrpm2cpio, stdout=subprocess.PIPE)
    p2 = subprocess.Popen(cmdcpiolist, stdin=p1.stdout,
                          stdout=outfile,
                          stderr=subprocess.PIPE)

    (_stdoutdata, _stderrdata) = p2.communicate()
    outfile.flush()

    fixedoutfile = tempfile.NamedTemporaryFile(prefix="fixedcpiotout",
                                               delete=not keepfilelist)
    # Replacing the prefixes in the file
    with open(outfile.name) as f:
        for l in f.readlines():
            fixedoutfile.write(l.replace(prefix, '/'))
    # We don;t close the file so we must flush...
    fixedoutfile.flush()

    if keepfilelist:
        logging.info("Extracting file list %s in %s " %
                     (fixedoutfile.name, os.getcwd()))

    # Now proceeding to the installation
    cmdcpioextract = ["cpio", "-imd", "--rename-batch-file", fixedoutfile.name]
    p3 = subprocess.Popen(cmdrpm2cpio, stdout=subprocess.PIPE)
    p4 = subprocess.Popen(cmdcpioextract, stdin=p3.stdout,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE)

    (stdoutdata, stderrdata) = p4.communicate()
    ret = p4.returncode
    if ret != 0:
        logging.error(stderrdata)
    else:
        if stdoutdata and len(stdoutdata) > 0:
            logging.info(stdoutdata)
    return ret


def extract(rpmlist, basedir, prefixes=None, keepfilelist=False):
    ''' extract the files

    :param rpmlist: the list of rpm files
    :param basedir: the top directory of the rpms
    :param prefix: the map fo prefixes
    :param keepfilelist: flag to keep the temporary files

    :returns: thre return code
    '''

    # And check it exists
    if not os.path.exists(basedir):
        raise Exception("basedir %s does not exist" % basedir)

    # table with group to prefix mapping
    if prefixes is None:
        prefixes = RPM_PREFIXES

    # checking that the RPM files to install  exist
    missing = []
    for f in rpmlist:
        if not os.path.exists(f):
            missing.append(f)
    if len(missing) > 0:
        raise Exception("Missing RPM files: %s" % ",".join(missing))

    logging.debug("Basedir: %s" % basedir)
    # backup current workdir dir to get back to it
    previousdir = os.getcwd()
    try:
        # We need to cd to the directory for
        # extraction unfortunately
        os.chdir(basedir)

        # Iterating on files to find the prefix and extract them
        for r in rpmlist:
            filename = os.path.join(previousdir, r)
            g = getrpmgroup(filename)
            prefix = prefixes[g.lower()]
            logging.warning("Extracting %s to %s" % (filename, basedir))
            _retval = _extractone(filename, prefix, keepfilelist=keepfilelist)
            checkrpminstall(filename, prefix, basedir)
    except Exception as e:
        logging.error(e)
    os.chdir(previousdir)
