#!/usr/bin/env python

import os
import glob
from warnings import warn
import re

try:
	from setuptools import setup, Extension
except ImportError:	
	from distutils.core import setup, Extension
from distutils.sysconfig import get_python_lib		
import platform
import sys

with open('delune/__init__.py', 'r') as fd:
	version = re.search(r'^__version__\s*=\s*"(.*?)"',fd.read(), re.M).group(1)

if sys.argv[-1] == 'publish':
	buildopt = ['sdist', 'upload']
	if os.name == "nt":
		buildopt.insert (0, 'bdist_wheel')		
	os.system('python setup.py %s' % " ".join (buildopt))
	#os.system('twine upload dist/delune-%s*' % version)
	for each in os.listdir ("dist"):
		os.remove (os.path.join ('dist', each))
	sys.exit()

modules = []
osbit, _dummy = platform.architecture()
dira = osbit == "32bit" and "x86" or "x64"

if os.name == "nt":
	include_dirs = [
		"delune/win32inclib/zlib/%s" % dira, 
		"delune/win32inclib/pthread2/%s" % dira
	]
	library_dirs = include_dirs
	libraries = ["zlib", "pthreadVC2"]
		
else:
	include_dirs = ["/usr/include/x86_64-linux-gnu", "/usr/include"]
	library_dirs = ["/usr/lib/x86_64-linux-gnu", "/usr/lib"]
	libraries = ["z", "pthread"]

module = Extension(
	'delune._delune',
	sources = [
		'delune/extension/delune/core.c', 
		'delune/extension/delune/analyzer/analyzer.c',		
		'delune/extension/delune/analyzer/stopword.c', 
		'delune/extension/delune/analyzer/endword.c', 
		'delune/extension/delune/analyzer/formalizer.c', 		
		'delune/extension/delune/analyzer/stem.c',
		'delune/extension/delune/analyzer/stem_de.c',
		'delune/extension/delune/analyzer/stem_fr.c',
		'delune/extension/delune/analyzer/stem_it.c',
		'delune/extension/delune/analyzer/stem_fi.c',
		'delune/extension/delune/analyzer/stem_es.c',
		'delune/extension/delune/analyzer/stem_hu.c',
		'delune/extension/delune/analyzer/stem_pt.c',
		'delune/extension/delune/analyzer/stem_sv.c',
		'delune/extension/delune/analyzer/stem_ar.c',
		'delune/extension/delune/analyzer/removeaccents.c',
		'delune/extension/delune/index/sort.c', 
		'delune/extension/delune/index/osutil.c', 
		'delune/extension/delune/index/search.c', 
		'delune/extension/delune/index/compfunc.c',
		'delune/extension/delune/index/heapsort.c', 
		'delune/extension/delune/index/termhashtable.c', 
		'delune/extension/delune/index/generichash.c',
		'delune/extension/delune/index/bfile.c', 
		'delune/extension/delune/index/zip.c',
		'delune/extension/delune/index/mempool.c',
		'delune/extension/delune/index/ibucket.c',
		'delune/extension/delune/index/util.c',
		'delune/extension/delune/mod_analyzer.c',		
		'delune/extension/delune/mod_util.c', 
		'delune/extension/delune/mod_int.c', 
		'delune/extension/delune/mod_bits.c', 
		'delune/extension/delune/mod_mergeinfo.c', 
		'delune/extension/delune/mod_document.c',
		'delune/extension/delune/mod_posting.c', 
		'delune/extension/delune/mod_termtable.c',
		'delune/extension/delune/mod_terminfo.c',
		'delune/extension/delune/mod_sortmap.c',   
		'delune/extension/delune/mod_memorypool.c',		
		'delune/extension/delune/mod_selector.c',		
		'delune/extension/delune/mod_classifier.c',
		'delune/extension/delune/mod_dbint.c',
		'delune/extension/delune/mod_calculator.c',
		'delune/extension/delune/mod_binfile.c',		
		'delune/extension/delune/mod_sgmlparser.c',
		'delune/extension/delune/mod_compute.c',
	],
	include_dirs = include_dirs,
	library_dirs = library_dirs,
	libraries = libraries
)
modules.append (module)

packages = [
	'delune',
	'delune.analyzers',
	'delune.analyzers.util',
	'delune.searcher',	
	'delune.searcher.segment',
	'delune.classifier',	
	'delune.classifier.classifiers',
	'delune.classifier.segment',	
	'delune.cluster',
	'delune.util',
	'delune.lib',
	'delune.export',
	'delune.export.skitai',
	'delune.export.skitai.package'
]

package_dir = {
	'delune': 'delune'
}
   
data_files = [
	"extension/delune/*.*",
	"extension/delune/analyzer/*.*",
	"extension/delune/index/*.*",	
	"extension/delune/win32/*.*",	
	"win32inclib/pthread2/x64/*.*",
	"win32inclib/pthread2/x86/*.*",	
	"win32inclib/zlib/x64/*.*",
	"win32inclib/zlib/x86/*.*"
]

if os.name == "nt" and ("build" in sys.argv or "install" in sys.argv):
	import shutil		
	try:
		if os.path.isfile ("delune/pthreadVC2.dll"):
			os.remove ("delune/pthreadVC2.dll")
		shutil.copy ("delune/win32inclib/pthread2/%s/pthreadVC2.dll" % dira, "delune/pthreadVC2.dll")		
		pass
	except OSError:
		pass	
	data_files.extend (["pthreadVC2.dll"])

package_data = {
	"delune": data_files
}

classifiers = [
  'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
  'Development Status :: 3 - Alpha',
  'Environment :: Console',	
	'Topic :: Software Development :: Libraries :: Python Modules',
	'Intended Audience :: Developers',
	'Intended Audience :: Science/Research',
	'Programming Language :: Python',
	'Programming Language :: Python :: 3',
	'Topic :: Text Processing :: Indexing'	
]

with open ('README.rst', encoding='utf-8') as f:
	long_description = f.read()
	
setup (
	name = 'delune',
	version = version,
	author = 'Hans Roh',
	description='DeLune Python Object Storage and Search Engine',
	long_description = long_description,
	author_email = 'hansroh@gmail.com',
	url = 'https://gitlab.com/hansroh/delune',
	packages=packages,
	package_dir=package_dir,
	package_data = package_data,
	license='GPLv3',
	platforms = ["posix", "nt"],
	download_url = "https://pypi.python.org/pypi/delune",
	classifiers=classifiers,
	ext_modules = modules
)

