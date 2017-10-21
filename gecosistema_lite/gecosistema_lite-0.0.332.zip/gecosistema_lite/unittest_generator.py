# -------------------------------------------------------------------------------
# Licence:
# Copyright (c) 2012-2017 Luzzi Valerio 
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
#
# Name:        unittest_generator.py
# Purpose:
#
# Author:      Luzzi Valerio
#
# Created:     26/07/2017
# -------------------------------------------------------------------------------
import datetime

from filesystem import *

LICENSE = """#-------------------------------------------------------------------------------
# Licence:
# Copyright (c) 2012-{year} Luzzi Valerio for Gecosistema S.r.l.
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
#
# Name:        test_{filename}.py
# Purpose:     This file is the unittest of {filename}.py
#
# Author:      Luzzi Valerio
#
# Created:     {date}
#-------------------------------------------------------------------------------
"""


def list_functions(filename):
    text = filetostr(filename)
    if text:
        pattern = r"""def\s+(.*?)\s*\(.*?\)\s*:"""
        flist = re.findall(pattern, text, re.DOTALL | re.VERBOSE)
        return flist
    return []


def create_all(dirname):
    for filename in ls(dirname, r".*\.py$"):
        if juststem(filename).startswith("__"):
            continue
        elif juststem(filename).startswith("test_"):
            continue
        elif juststem(filename).startswith("unittest_generator"):
            continue

        create_unittest(filename)


def create_unittest(filename):
    filetest = (justpath(filename) if justpath(filename) else ".") + "/tests/test_" + justfname(filename)
    fnames = list_functions(filename)

    today = datetime.date.today()
    env = {"year": today.year, "date": today.strftime("%d/%m/%Y"), "filename": juststem(filename)}
    License = LICENSE
    License += '''
import os,sys
import unittest
sys.path.append("../..")
from gecosistema_lite import *

class test_{filename}(unittest.TestCase):

    def setUp(self):
        """
        setUp
        """


    def doCleanups(self):
        """
        doCleanups
        """

    #<!-- new testcase here -->

if __name__=="__main__":
    unittest.main()
'''
    text = filetostr(filetest)
    text = text if text else sformat(License, env)

    for fname in fnames:
        text = add_unittest(text, fname)

    fun2remove = [re.sub(r"^test_", "", item) for item in list_functions(filetest) if
                  re.sub(r"^test_", "", item) not in fnames]
    for fname in fun2remove:
        text = remove_unittest(text, "test_%s" % fname)

    strtofile(text, filetest)


def exists_unittest(text, fname):
    pattern = r"""^\s+def\s+test_{fname}\s*\(.*?\)\s*:"""
    pattern = sformat(pattern, {"fname": fname})
    if re.findall(pattern, text, re.DOTALL | re.MULTILINE):
        return True
    return False


def add_unittest(text, fname):
    if not exists_unittest(text, fname):
        print "adding function %s" % fname
        placeholder = r"""#<!-- new testcase here -->"""
        new_unittest = '''
    def test_{fname}(self):
        """
        test_{fname}
        - added at {datetime}
        """
        #self.assertEqual({fname}(...) , True)
        #print "test {fname} ...ok!" 
        #end function

    {placeholder}'''
        new_unittest = sformat(new_unittest, {"fname": fname, "placeholder": placeholder,
                                              "datetime": datetime.datetime.now().strftime("%d/%m/%Y %H:%M")})
        return re.sub(placeholder, new_unittest, text)
    return text


def find_unittest(text, fname):
    pattern = r"""(^\s+def\s+{fname}.*?:.*?\#end.*?\n)"""
    pattern = sformat(pattern, {"fname": fname})
    items = re.findall(pattern, text, re.DOTALL | re.MULTILINE)
    if items:
        return items[0]
    return None


def remove_unittest(text, fname):
    ut = find_unittest(text, fname)
    if ut:
        print  "removing function %s" % fname
        nut = ut.replace("\n", "\n##\t")
        text = text.replace(ut, nut)
    return text


if __name__ == '__main__':
    chdir(juststem(__file__))
    create_all(".")
