# Copyright (c) 2017 Thorsten Simons (sw@snomis.de)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from tempfile import TemporaryDirectory
from shutil import unpack_archive
from os import listdir, walk
from os.path import join


class Handler(object):
    """
    A class that handles the unpacking of access logs from an HCP log package.
    """

    def __init__(self, logpkg):
        """
        :param logpkg:  the filename of the HCP log package
        """
        self.logpkg = logpkg
        self.tmpdir = TemporaryDirectory(dir='.')

    def unpack(self):
        """
        Unzip the logs and copy the required files into the target folder
        structure

        :return:        a list of http_gateway_request.log file names
        """
        # Step 1: unpack the downloaded file
        #         result will be something like this:
        #           HCPLogs-hcp-domain.com-YYYMMDD-HHMM
        #               176.tar.bz2
        #               177.tar.bz2
        #               178.tar.bz2
        #               179.tar.bz2
        #               manifest.csv
        print('un-packing {}'.format(self.logpkg))
        unpack_archive(self.logpkg, self.tmpdir.name, format='zip')

        # find the folder where the file was uncompressed to
        archdir = ''
        for f in listdir(self.tmpdir.name):
            if f.startswith('HCPLogs-'):
                archdir = f

        # parse the manifest.csv to find out about the individual node's
        # logs
        nodes = self.parsemanifest(join(self.tmpdir.name, archdir,
                                        'manifest.csv'))
        # nodes =
        # [('192.168.0.176',
        #   'HCPLogs-hcp72.archivas.com-acc-20170911-1603/176.tar.bz2',
        #   'HCPLogs-hcp72.archivas.com-acc-20170911-1603/176')]

        flist = []
        for i in nodes:
            print('\tun-packing access logs for node {}'.format(i[0]))
            unpack_archive(join(self.tmpdir.name, i[1]),
                           join(self.tmpdir.name, archdir),
                           format='bztar')
            # now, we have a structure like this:
            #           HCPLogs-hcp-domain.com-YYYMMDD-HHMM
            #               176                       (where 176 is the node id)
            #                   var
            #                       ris
            #                           retired
            #                               access-logs-20151004-0345.tar.bz2
            for j in listdir(join(self.tmpdir.name, i[2], 'var', 'ris',
                                  'retired')):
                if j.startswith('access-logs'):
                    unpack_archive(join(self.tmpdir.name, i[2], 'var', 'ris',
                                        'retired', j),
                                   join(self.tmpdir.name, i[2], 'var', 'ris',
                                        'retired'),
                                   format='bztar')
                # which now ends up having the unpacked logs in the regular path

        for root, dirs, files in walk(self.tmpdir.name):
            for f in files:
                if f.startswith('http_gateway_request.log'):
                    flist.append(join(root, f))

        return flist


    def parsemanifest(self, manifest):
        """
        parse the manifest.csv and find the nodes IP addresses along with
        the compressed files holding its logs.

        :parm manifest:     the name of the manifest.csv file
        :returns:           a list of 3-tuples (containing the IP address,
                            path to the nodes compressed logs, path to
                            the logs when uncompressed)
        """
        with open(manifest, 'r') as mhdl:
            result = []
            relevant = False
            for l in mhdl.readlines():
                if l.startswith('"Node IP"'):
                    relevant = True
                    continue
                if not relevant:
                    continue
                else:
                    if not l.strip():
                        break
                    cols = l.split(',')
                    # if we have Nodes with an BE IP address with the last
                    # octet being 1- or 2-digit, only, we need to fix that
                    # and make it 3-digit, as the de-compressed folder will
                    # have a 3-digit anyway
                    tdir = cols[1][:-8].split('/')
                    tdir = '{}/{:03}'.format(tdir[0], int(tdir[1]))
                    result.append((cols[0], cols[1], tdir))

        return result


    def close(self):
        """
        Close the session with HCP
        """
        try:
            self.tmpdir.cleanup()
        except PermissionError as e:
            print('sorry, wasn\'t able to delete tmp folder {}\n\t'
                  '- please do it manually!'
                  .format(self.tmpdir.name))
