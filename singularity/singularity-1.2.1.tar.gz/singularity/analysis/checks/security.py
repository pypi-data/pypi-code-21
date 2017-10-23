'''
The MIT License (MIT)

Copyright (c) 2016-2017 Vanessa Sochat, All Rights Reserved

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

'''

from singularity.cli import Singularity
from singularity.logger import bot



# history cleanup (no trace of credentials like "echo changemenow| sudo passwd --stdin root")
# user controlled whitelist/blacklist of what should be kept
# remove any file specific to the machine and not required on the container (same files as for cloning instances) e.g /etc/ssh/host, cleanup /etc/hosts, /# etc/sysconfig/network-scripts/ifcfg-, but not ifcfg-lo, /etc/udev/rules.d/persistent ) /var/log/{secure,messages*,...}
# yum clean all and the apt-get equivalent
# SElinux or ACLs transfer? tar --selinux --xattrs
# sparse file handling
# remove any non required users via userdel?
# maybe reuse|have a peak at cloud-init ?
