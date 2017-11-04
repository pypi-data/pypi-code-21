#! /usr/bin/python
#
# execsql.py
#
# PURPOSE
# 	Read a sequence of SQL statements from a file and execute them against a PostgreSQL,
# 	MS-Access, SQLite, SQL Server, MySQL, or Firebird database, and supplement the SQL
# 	statements with metacommands that allow import and export of data, and conditional
# 	execution of parts of the script.  This program provides a standard tool for
# 	execution of SQL scripts with DBMSs that have varying--or no--capabilities for
# 	scripting.
#
# AUTHOR
# 	Dreas Nielsen (RDN)
#
# COPYRIGHT AND LICENSE
# 	Copyright (c) 2007, 2008, 2009, 2014, 2015, 2016, 2017, R.Dreas Nielsen
# 	This program is free software: you can redistribute it and/or modify
# 	it under the terms of the GNU General Public License as published by
# 	the Free Software Foundation, either version 3 of the License, or
# 	(at your option) any later version.
# 	This program is distributed in the hope that it will be useful,
# 	but WITHOUT ANY WARRANTY; without even the implied warranty of
# 	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# 	GNU General Public License for more details.
# 	The GNU General Public License is available at <http://www.gnu.org/licenses/>
#
# ===============================================================================

__version__ = "1.24.0.0"
__vdate = "2017-11-04"

import os
import os.path
import sys
import datetime
import time
from decimal import Decimal		# pyodbc may return Decimal objects.
import codecs
import getpass
from optparse import OptionParser
import io
import re
import random
import uuid
import atexit
import traceback
import errno
import subprocess
import shlex
import tempfile
import ConfigParser
import copy
if os.name == 'posix':
	import termios
	import tty
else:
	import msvcrt
import signal
# Get the codec dictionary to check encoding/decoding names
from encodings.aliases import aliases as codec_dict
import threading
import Queue

# Placeholders/documentation for other possible imports.

# win32com.client is imported if an Access database will be used.
global win32com
# pyodbc is imported if an Access or SQL Server database, or an ODBC DSN, will be used.
global pyodbc
# psycopg2 is imported if Postgres will be used.
global psycopg2
# pymysql or other connector library is imported as mysql_lib for MySQL
global mysql_lib
# fdb or other connector library is imported as firebird_lib for Firebird
global firebird_lib
# pymssql is imported if a SQL Server database will be used (deprecated; pyodbc is now used)
#global pymssql
# sqlite3 is imported if a SQLite database will be used.
global sqlite3
# odf is imported to read or write ODF files
global odf
# json is used to write JSON
global json
# xlrd is used to read Excel files
global xlrd
# imports for Encrypt
global itertools
global base64
# imports for email
global smtplib
global MIMEMultipart
global MIMEText
global MIMEBase
global encoders
# imports for reporting templates
global string
global jinja2
global airspeed


#===============================================================================================
#-----  GLOBAL VARIABLES
# See also the global objects defined just prior to main().

# Configuration data, initialized in main()
conf = None

# Default encodings
logfile_encoding = 'utf8'	# Should never be changed; is not configurable.

# Global lists of MetaCommand objects (commands and conditional tests).
# These are filled in the 'MetaCommand Functions' and 'Conditional Tests for Metacommands' sections.
metacommands = []
conditionals = []

#	End of global variables
#===============================================================================================


class StatObj(object):
	# A generic object to which status indicators are assigned as attributes.
	def __init__(self):
		self.halt_on_err = True
		self.sql_error = False
		self.halt_on_metacommand_err = True
		self.metacommand_error = False
		self.cancel_halt = True

#===============================================================================================
#-----  SUBSTITUTION VARIABLES

class SubVarSet(object):
	# A pool of substitution variables.
	# This is implemented as a list of tuples rather than a dictionary to enforce
	# ordered substitution.  All variable names are stored as lowercase text.
	var_rx = re.compile(r'^\w+$', re.I)
	def __init__(self):
		self.substitutions = []
	def var_name_ok(self, varname):
		return self.var_rx.match(varname) is not None
	def remove_substitution(self, template_str):
		old_sub = template_str.lower()
		self.substitutions = [sub for sub in self.substitutions if sub[0] != old_sub]
	def add_substitution(self, varname, repl_str):
		varname = varname.lower()
		self.remove_substitution(varname)
		self.substitutions.append((varname, repl_str))
	def append_substitution(self, varname, repl_str):
		oldsub = [x for x in self.substitutions if x[0] == varname]
		if len(oldsub) == 0:
			self.add_substitution(varname, repl_str)
		else:
			self.add_substitution(varname, "%s\n%s" % (oldsub[0][1], repl_str))
	def sub_exists(self, template_str):
		test_str = template_str.lower()
		if test_str in [s[0] for s in self.substitutions]:
			return True
	def substitute(self, command_str):
		# Replace any substitution variables in the command string.
		# This does only one round of replacements: if the first round of replacements
		# produces more substitution variables that could be replaced, those derived
		# matching strings are not replaced.  The second value returned by this
		# function indicates whether any substitutions were made, so that it can
		# be called again if necessary.
		match_found = False
		if isinstance(command_str, basestring):
			for match, sub in self.substitutions:
				if sub is None:
					sub = ''
				sub = str(sub)
				if match[0] == "$":
					match = "\\"+match
				pat = "!!%s!!" % match
				if re.search(pat, command_str, re.I):
					if os.name != 'posix':
						sub = sub.replace("\\", "\\\\")
					command_str = re.sub(pat, sub, command_str, flags=re.I)
					match_found = True
		return command_str, match_found
	def substitute_all(self, any_text):
		if isinstance(any_text, basestring):
			subbed = True
			while subbed:
				any_text, subbed = self.substitute(any_text)
		return any_text

# End of substitution variables
#===============================================================================================


#===============================================================================================
#-----  CONFIGURATION

class ConfigError(Exception):
	def __init__(self, msg):
		self.value = msg
	def __repr__(self):
		return "ConfigError(%r)" % self.value

class ConfigData(object):
	config_file_name = "execsql.conf"
	_CONNECT_SECTION = "connect"
	_ENCODING_SECTION = "encoding"
	_INPUT_SECTION = "input"
	_OUTPUT_SECTION = "output"
	_INTERFACE_SECTION = "interface"
	_CONFIG_SECTION = "config"
	_EMAIL_SECTION = "email"
	_VARIABLES_SECTION = "variables"
	_INCLUDE_REQ_SECTION = "include_required"
	_INCLUDE_OPT_SECTION = "include_optional"
	def __init__(self, script_path, variable_pool):
		self.db_type = 'a'
		self.server = None
		self.port = None
		self.db = None
		self.username = None
		self.access_username = None
		self.passwd_prompt = True
		self.db_file = None
		self.new_db = False
		self.db_encoding = None
		self.script_encoding = 'utf8'
		self.output_encoding = 'utf8'
		self.import_encoding = 'utf8'
		self.enc_err_disposition = None
		self.import_common_cols_only = False
		self.max_int = 2147483647
		self.boolean_int = True
		self.boolean_words = False
		self.empty_strings = True
		self.access_use_numeric = False
		self.scan_lines = 100
		self.gui_level = 0
		self.gui_wait_on_exit = False
		self.gui_wait_on_error_halt = False
		self.import_buffer = 32 * 1024
		self.css_file = None
		self.css_styles = None
		self.make_export_dirs = False
		self.template_processor = None
		self.tee_write_log = False
		self.smtp_host = None
		self.smtp_port = None
		self.smtp_username = None
		self.smtp_password = None
		self.smtp_ssl = False
		self.smtp_tls = False
		self.email_format = 'plain'
		self.email_css = None
		self.include_req = []
		self.include_opt = []
		if os.name == 'posix':
			sys_config_file = os.path.join("/etc", self.config_file_name)
		else:
			sys_config_file = os.path.join(os.path.expandvars(r'%APPDIR%'), self.config_file_name)
		current_script = os.path.abspath(sys.argv[0])
		user_config_file = os.path.join(os.path.expanduser(r'~/.config'), self.config_file_name)
		script_config_file = os.path.join(script_path, self.config_file_name)
		config_files = [sys_config_file, user_config_file, script_config_file]
		self.files_read = []
		for ix, configfile in enumerate(config_files):
			if not configfile in self.files_read and os.path.isfile(configfile):
				self.files_read.append(configfile)
				cp = ConfigParser.SafeConfigParser()
				cp.read(configfile)
				if cp.has_option(self._CONNECT_SECTION, "db_type"):
					t = cp.get(self._CONNECT_SECTION, "db_type").lower()
					if len(t) != 1 or t not in ('a', 'l', 'p', 'f', 'm', 's', 'd'):
						raise ConfigError("Invalid database type: %s" % t)
					self.db_type = t
				if cp.has_option(self._CONNECT_SECTION, "server"):
					self.server = cp.get(self._CONNECT_SECTION, "server")
					if self.server is None:
						raise ConfigError("The server name cannot be missing.")
				if cp.has_option(self._CONNECT_SECTION, "db"):
					self.db = cp.get(self._CONNECT_SECTION, "db")
					if self.db is None:
						raise ConfigError("The database name cannot be missing.")
				if cp.has_option(self._CONNECT_SECTION, "port"):
					try:
						self.port = cp.getint(self._CONNECT_SECTION, "port")
					except:
						raise ConfigError("Invalid port number.")
				if cp.has_option(self._CONNECT_SECTION, "database"):
					self.db = cp.get(self._CONNECT_SECTION, "database")
					if self.db is None:
						raise ConfigError("The database name cannot be missing.")
				if cp.has_option(self._CONNECT_SECTION, "db_file"):
					self.db_file = cp.get(self._CONNECT_SECTION, "db_file")
					if self.db_file is None:
						raise ConfigError("The database file name cannot be missing.")
				if cp.has_option(self._CONNECT_SECTION, "username"):
					self.username = cp.get(self._CONNECT_SECTION, "username")
					if self.username is None:
						raise ConfigError("The user name cannot be missing.")
				if cp.has_option(self._CONNECT_SECTION, "access_username"):
					self.access_username = cp.get(self._CONNECT_SECTION, "access_username")
				if cp.has_option(self._CONNECT_SECTION, "password_prompt"):
					try:
						self.passwd_prompt = cp.getboolean(self._CONNECT_SECTION, "password_prompt")
					except:
						raise ConfigError("Invalid argument for password_prompt.")
				if cp.has_option(self._CONNECT_SECTION, "new_db"):
					try:
						self.new_db = cp.getboolean(self._CONNECT_SECTION, "new_db")
					except:
						raise ConfigError("Invalid argument for new_db.")
				if cp.has_option(self._ENCODING_SECTION, "database"):
					self.db_encoding = cp.get(self._ENCODING_SECTION, "database")
				if cp.has_option(self._ENCODING_SECTION, "script"):
					self.script_encoding = cp.get(self._ENCODING_SECTION, "script")
					if self.script_encoding is None:
						raise ConfigError("The script encoding cannot be missing.")
				if cp.has_option(self._ENCODING_SECTION, "import"):
					self.import_encoding = cp.get(self._ENCODING_SECTION, "import")
					if self.import_encoding is None:
						raise ConfigError("The import encoding cannot be missing.")
				if cp.has_option(self._ENCODING_SECTION, "output"):
					self.output_encoding = cp.get(self._ENCODING_SECTION, "output")
					if self.output_encoding is None:
						raise ConfigError("The output encoding cannot be missing.")
				if cp.has_option(self._ENCODING_SECTION, "error_response"):
					handler = cp.get(self._ENCODING_SECTION, "error_response").lower()
					if handler not in ('ignore', 'replace', 'xmlcharrefreplace', 'backslashreplace'):
						raise ConfigError("Invalid encoding error handler: %s" % handler)
					self.enc_err_disposition = handler
				if cp.has_option(self._INPUT_SECTION, "max_int"):
					try:
						maxint = cp.getint(self._INPUT_SECTION, "max_int")
					except:
						raise ConfigError("Invalid argument to max_int.")
					else:
						self.max_int = maxint
				if cp.has_option(self._INPUT_SECTION, "boolean_int"):
					try:
						self.boolean_int = cp.getboolean(self._INPUT_SECTION, "boolean_int")
					except:
						raise ConfigError("Invalid argument to boolean_int.")
				if cp.has_option(self._INPUT_SECTION, "boolean_words"):
					try:
						self.boolean_words = cp.getboolean(self._INPUT_SECTION, "boolean_words")
					except:
						raise ConfigError("Invalid argument to boolean_words.")
				if cp.has_option(self._INPUT_SECTION, "empty_strings"):
					try:
						self.empty_strings = cp.getboolean(self._INPUT_SECTION, "empty_strings")
					except:
						raise ConfigError("Invalid argument to empty_strings.")
				if cp.has_option(self._INPUT_SECTION, "access_use_numeric"):
					try:
						self.access_use_numeric = cp.getboolean(self._INPUT_SECTION, "access_use_numeric")
					except:
						raise ConfigError("Invalid argument to access_use_numeric.")
				if cp.has_option(self._INPUT_SECTION, "import_common_columns_only"):
					try:
						self.import_common_cols_only = cp.getboolean(self._INPUT_SECTION, "import_common_columns_only")
					except:
						raise ConfigError("Invalid argument to import_common_columns_only.")
				if cp.has_option(self._INPUT_SECTION, "scan_lines"):
					try:
						self.scan_lines = cp.getint(self._INPUT_SECTION, "scan_lines")
					except:
						raise ConfigError("Invalid argument to scan_lines.")
				if cp.has_option(self._INPUT_SECTION, "import_buffer"):
					try:
						self.import_buffer = cp.getint(self._INPUT_SECTION, "import_buffer") * 1024
					except:
						raise ConfigError("Invalid argument for import_buffer.")
				if cp.has_option(self._OUTPUT_SECTION, "log_write_messages"):
					try:
						self.tee_write_log = cp.getboolean(self._OUTPUT_SECTION, "log_write_messages")
					except:
						raise ConfigError("Invalid argument to log_write_messages")
				if cp.has_option(self._OUTPUT_SECTION, "css_file"):
					self.css_file = cp.get(self._OUTPUT_SECTION, "css_file")
					if self.css_file is None:
						raise ConfigError("The css_file name is missing.")
				if cp.has_option(self._OUTPUT_SECTION, "css_styles"):
					self.css_styles = cp.get(self._OUTPUT_SECTION, "css_styles")
					if self.css_file is None:
						raise ConfigError("The css_styles are missing.")
				if cp.has_option(self._OUTPUT_SECTION, "make_export_dirs"):
					try:
						self.make_export_dirs = cp.getboolean(self._OUTPUT_SECTION, "make_export_dirs")
					except:
						raise ConfigError("Invalid argument for make_export_dirs.")
				if cp.has_option(self._OUTPUT_SECTION, "template_processor"):
					tp = cp.get(self._OUTPUT_SECTION, "template_processor").lower()
					if tp not in ('jinja', 'airspeed'):
						raise ConfigError("Invalid template processor name: %s" % tp)
					self.template_processor = tp
				if cp.has_option(self._INTERFACE_SECTION, "gui_level"):
					self.gui_level = cp.getint(self._INTERFACE_SECTION, "gui_level")
					if self.gui_level not in (0, 1, 2, 3):
						raise ConfigError("Invalid GUI level: %d" % self.gui_level)
				if cp.has_option(self._INTERFACE_SECTION, "console_wait_when_done"):
					try:
						self.gui_wait_on_exit = cp.getboolean(self._INTERFACE_SECTION, "console_wait_when_done")
					except:
						raise ConfigError("Invalid argument for console_wait_when_done.")
				if cp.has_option(self._INTERFACE_SECTION, "console_wait_when_error_halt"):
					try:
						self.gui_wait_on_error_halt = cp.getboolean(self._INTERFACE_SECTION, "console_wait_when_error_halt")
					except:
						raise ConfigError("Invalid argument for console_wait_when_error_halt.")
				if cp.has_option(self._CONFIG_SECTION, "config_file"):
					conffile = cp.get(self._CONFIG_SECTION, "config_file")
					if not os.path.isfile(conffile):
						conffile = os.path.join(conffile, self.config_file_name)
					config_files.insert(ix+1, conffile)
				if cp.has_option(self._EMAIL_SECTION, "host"):
					self.smtp_host = cp.get(self._EMAIL_SECTION, "host")
				if cp.has_option(self._EMAIL_SECTION, "port"):
					self.smtp_port = cp.get(self._EMAIL_SECTION, "port")
					try:
						self.smtp_port = cp.getint(self._EMAIL_SECTION, "port")
					except:
						raise ConfigError("Invalid argument for email port.")
				if cp.has_option(self._EMAIL_SECTION, "username"):
					self.smtp_username = cp.get(self._EMAIL_SECTION, "username")
				if cp.has_option(self._EMAIL_SECTION, "password"):
					self.smtp_password = cp.get(self._EMAIL_SECTION, "password")
				if cp.has_option(self._EMAIL_SECTION, "enc_password"):
					self.smtp_password = Encrypt().decrypt(cp.get(self._EMAIL_SECTION, "enc_password"))
				if cp.has_option(self._EMAIL_SECTION, "use_ssl"):
					try:
						self.smtp_ssl = cp.getboolean(self._EMAIL_SECTION, "use_ssl")
					except:
						raise ConfigError("Invalid argument for email use_ssl.")
				if cp.has_option(self._EMAIL_SECTION, "use_tls"):
					try:
						self.smtp_tls = cp.getboolean(self._EMAIL_SECTION, "use_tls")
					except:
						raise ConfigError("Invalid argument for email use_tls.")
				if cp.has_option(self._EMAIL_SECTION, "email_format"):
					fmt = cp.get(self._EMAIL_SECTION, "email_format").lower()
					if fmt not in ('plain', 'html'):
						raise ConfigError("Invalid email format: %s" % fmt)
					self.email_format = fmt
				if cp.has_option(self._EMAIL_SECTION, "message_css"):
					self.email_css = cp.get(self._EMAIL_SECTION, "message_css")
				if cp.has_section(self._VARIABLES_SECTION) and variable_pool:
					varsect = cp.items(self._VARIABLES_SECTION)
					for sub, repl in varsect:
						if not variable_pool.var_name_ok(sub):
							raise ConfigError("Invalid variable name: %s" % sub)
						variable_pool.add_substitution(sub, repl)
				if cp.has_section(self._INCLUDE_REQ_SECTION):
					imp_items = cp.items(self._INCLUDE_REQ_SECTION)
					ord_items = sorted([(int(i[0]), i[1]) for i in imp_items], key=lambda x:x[0])
					newfiles = [os.path.abspath(f[1]) for f in ord_items]
					u_files = []
					for f in newfiles:
						if not (f in u_files or f in self.include_req or f in self.include_opt) and f != current_script:
							if not os.path.exists(f):
								raise ConfigError("Required include file %s does not exist." % f)
							u_files.append(f)
					self.include_req.extend(u_files)
				if cp.has_section(self._INCLUDE_OPT_SECTION):
					imp_items = cp.items(self._INCLUDE_OPT_SECTION)
					ord_items = sorted([(int(i[0]), i[1]) for i in imp_items], key=lambda x:x[0])
					newfiles = [os.path.abspath(f[1]) for f in ord_items]
					u_files = []
					for f in newfiles:
						if not (f in u_files or f in self.include_req or f in self.include_opt) and f != current_script:
							if os.path.exists(f):
								u_files.append(f)
					self.include_opt.extend(u_files)

# End of configuration.
#===============================================================================================



#===============================================================================================
#-----  SUPPORT FUNCTIONS AND CLASSES (1)


class WriteHooks(object):
	def __repr__(self):
		return u"WriteHooks(%r, %r, %r)" % (self.write_func, self.err_func, self.status_func)
	def __init__(self, standard_output_func=None, error_output_func=None, status_output_func=None):
		# Arguments should be functions that take a single string and
		# write it to the desired destination.  Both stdout and stderr can be hooked.
		# If a hook function is not specified, the default of stdout or stderr will
		# be used.
		# The purpose is to allow writing to be redirected to a GUI.
		self.write_func = standard_output_func
		self.err_func = error_output_func
		self.status_func = status_output_func
		self.tee_stderr = True
	def reset(self):
		# Resets output to stdout and stderr.
		self.write_func = None
		self.err_func = None
	def redir_stdout(self, standard_output_func):
		self.write_func = standard_output_func
	def redir_stderr(self, error_output_func, tee=True):
		self.err_func = error_output_func
		self.tee_stderr = tee
	def redir(self, standard_output_func, error_output_func):
		self.redir_stdout(standard_output_func)
		self.redir_stderr(error_output_func)
	def write(self, strval):
		global conf
		if conf:
			enc = conf.output_encoding
		else:
			enc = 'utf8'
		if self.write_func:
			self.write_func(strval.encode(enc))
		else:
			sys.stdout.write(strval.encode(enc))
	def write_err(self, strval):
		global conf
		if conf:
			enc = conf.output_encoding
		else:
			enc = 'utf8'
		msg = u"%s\n" % strval
		msg = msg.encode(enc)
		if self.err_func:
			self.err_func(msg)
			if self.tee_stderr:
				sys.stderr.write(msg)
		else:
			sys.stderr.write(msg)
	def write_status(self, str):
		global conf
		if conf:
			enc = conf.output_encoding
		else:
			enc = 'utf8'
		if self.status_func:
			self.status_func(str.encode(enc))


def ins_rxs(rx_list, fragment1, fragment2):
	# Returns a tuple of all strings consisting of elements of the 'rx_list' tuple
	# inserted between 'fragment1' and 'fragment2'.  The fragments may themselves
	# be tuples.
	if type(fragment1) != tuple:
		fragment1 = (fragment1, )
	if fragment2 is None:
		fragment2 = ('', )
	if type(fragment2) != tuple:
		fragment2 = (fragment2, )
	rv = []
	for te in rx_list:
		for f1 in fragment1:
			for f2 in fragment2:
				rv.append(f1 + te + f2)
	return tuple(rv)

def ins_quoted_rx(fragment1, fragment2, rx):
	return ins_rxs((rx, r'"%s"' % rx), fragment1, fragment2)

def ins_table_rxs(fragment1, fragment2, suffix=None):
	tbl_exprs = (r'(?:"(?P<schema>[A-Za-z0-9_\- ]+)"\.)?"(?P<table>[A-Za-z0-9_\-\# ]+)"',
					r'(?:(?P<schema>[A-Za-z0-9_\-]+)\.)?(?P<table>[A-Za-z0-9_\-\#]+)',
					r'(?:"(?P<schema>[A-Za-z0-9_\- ]+)"\.)?(?P<table>[A-Za-z0-9_\-\#]+)',
					r'(?:(?P<schema>[A-Za-z0-9_\-]+)\.)?"(?P<table>[A-Za-z0-9_\-\# ]+)"',
					r'(?:\[(?P<schema>[A-Za-z0-9_\- ]+)\]\.)?\[(?P<table>[A-Za-z0-9_\-\# ]+)\]',
					r'(?:(?P<schema>[A-Za-z0-9_\-]+)\.)?(?P<table>[A-Za-z0-9_\-\#]+)',
					r'(?:\[(?P<schema>[A-Za-z0-9_\- ]+)\]\.)?(?P<table>[A-Za-z0-9_\-\#]+)',
					r'(?:(?P<schema>[A-Za-z0-9_\-]+)\.)?\[(?P<table>[A-Za-z0-9_\-\# ]+)\]'
					)
	if suffix:
		tbl_exprs = tuple([s.replace("schema", "schema"+suffix).replace("table", "table"+suffix) for s in tbl_exprs])
	return ins_rxs(tbl_exprs, fragment1, fragment2)

def ins_fn_rxs(fragment1, fragment2, symbolicname="filename"):
	if os.name == 'posix':
		fns = (r'(?P<%s>[\w\.\-\\\/\'~`!@#$^&()+={}\[\]:;,]+)' % symbolicname, r'"(?P<%s>[\w\s\.\-\\\/\'~`!@#$^&()+={}\[\]:;,]+)"' % symbolicname)
	else:
		fns = (r'(?P<%s>([A-Z]\:)?[\w+\,\(\)!@#$^&\+=;\'{}\[\]~`\.\-\\\/]+)' % symbolicname, r'"(?P<%s>([A-Z]\:)?[\w+\,\(\)!@#$^&\+=;\'{}\[\]~`\s\.\-\\\/]+)"' % symbolicname)
		#fns = (r'(?P<%s>([A-Z]\:)?[\w+\.\-\\\/]+)' % symbolicname, r'"(?P<%s>([A-Z]\:)?[\w+\s\.\-\\\/]+)"' % symbolicname )
	return ins_rxs(fns, fragment1, fragment2)

def leading_zero_num(dataval):
	# Returns True if the data value is potentially a number but has a leading zero
	if not isinstance(dataval, basestring):
		return False
	if len(dataval) < 2:
		return False
	if dataval[0] != u'0':
		return False
	try:
		x = float(dataval[1:])
	except:
		return False
	if x > 1:
		return True
	return False

def encodings_match(enc1, enc2):
	# Compares two encoding labels and returns T/F depending on whether or not
	# they match.  This implements the alias matching rules from Unicode Technical
	# Standard #22 (http://www.unicode.org/reports/tr22/tr22-7.html#Charset_Alias_Matching)
	# and a subset of the encoding equivalences listed at
	# https://encoding.spec.whatwg.org/#names-and-labels.
	enc1 = enc1.strip().lower()
	enc2 = enc2.strip().lower()
	if enc1==enc2:
		return True
	rx = re.compile(r'[^a-z0-9]')
	enc1 = re.sub(rx, '', enc1)
	enc2 = re.sub(rx, '', enc2)
	if enc1==enc2:
		return True
	rx = re.compile(r'0+(?P<tz>[1-9][0-9]*)')
	enc1 = re.sub(rx, '\g<tz>', enc1)
	enc2 = re.sub(rx, '\g<tz>', enc2)
	if enc1==enc2:
		return True
	equivalents = (
		('cp1252', 'win1252', 'windows1252', 'latin1', 'cp819', 'csisolatin1', 'ibm819', 'iso88591', 'l1', 'xcp1252'),
		('latin2', 'csisolatin2', 'iso88592', 'isoir101', 'l2'),
		('latin3', 'csisolatin3', 'iso88593', 'isoir109', 'l3'),
		('latin4', 'csisolatin4', 'iso88594', 'isoir110', 'l4'),
		('latin5', 'iso88599'),
		('latin6', 'iso885910', 'csisolatin6', 'isoir157', 'l6'),
		('latin7', 'iso885913'),
		('latin8', 'iso885914'),
		('latin9', 'iso885915', 'csisolatin9', 'l9'),
		('latin10', 'iso885916'),
		('cyrillic', 'csisolatincyrillic', 'iso88595', 'isoir144', 'win866', 'windows866', 'cp866'),
		('arabic', 'win1256', 'asmo708', 'iso88596', 'csiso88596e', 'csiso88596i', 'csisolatinarabic', 'ecma114', 'isoir127'),
		('greek', 'win1253', 'ecma118', 'elot928', 'greek8', 'iso88597', 'isoir126', 'suneugreek'),
		('hebrew', 'win1255', 'iso88598', 'csiso88598e', 'csisolatinhebrew', 'iso88598e', 'isoir138', 'visual'),
		('logical', 'csiso88598i'),
		('cp1250', 'win1250', 'windows1250', 'xcp1250'),
		('cp1251', 'win1251', 'windows1251', 'xcp1251'),
		('windows874', 'win874', 'cp874', 'dos874', 'iso885911', 'tis620'),
		('mac', 'macintosh', 'csmacintosh', 'xmacroman'),
		('xmaccyrillic', 'xmacukrainian'),
		('koi8u', 'koi8ru'),
		('koi8r', 'koi', 'koi8', 'cskoi8r'),
		('euckr', 'cseuckr', 'csksc56011987', 'isoir149', 'korean', 'ksc56011987', 'ksc56011989', 'ksc5601', 'windows949'),
		('eucjp', 'xeucjp', 'cseucpkdfmtjapanese'),
		('csiso2022jp', 'iso2022jp'),
		('csshiftjis', 'ms932', 'ms-kanji', 'shiftjis', 'sjis', 'windows-31j', 'xsjis'),
		('big5', 'big5hkscs', 'cnbig5', 'csbig5', 'xxbig5'),
		('chinese', 'csgb2312', 'csiso58gb231280', 'gb2312', 'gb231280', 'gbk', 'isoir58', 'xgbk', 'gb18030')
		)
	for eq in equivalents:
		if enc1 in eq and enc2 in eq:
			return True
	return False


#	End of support functions (1)
#===============================================================================================

#===============================================================================================
#----  ALARM TIMER
# This class is intended specifically for use with the PAUSE metacommand ('pause()' function).
# It writes to the console.
# This is Linux-only; Windows has no alarm timer signal.

class TimeoutError(Exception):
	pass

class TimerHandler(object):
	def __init__(self, maxtime):
		# maxtime should be in seconds, may be floating-point.
		self.maxtime = maxtime
		self.start_time = time.time()
	def alarm_handler(self, sig, stackframe):
		elapsed_time = time.time() - self.start_time
		if elapsed_time > self.maxtime:
			signal.setitimer(signal.ITIMER_REAL, 0)
			raise TimeoutError
		else:
			time_left = self.maxtime - elapsed_time
			barlength = 30
			bar_left = int(round(barlength * time_left/self.maxtime, 0))
			#sys.stdout.write("%s  |%s%s|\r" % ("{:8.1f}".format(time_left), "+"*bar_left, "-"*(barlength-bar_left)))
			output.write("%s  |%s%s|\r" % ("{:8.1f}".format(time_left), "+"*bar_left, "-"*(barlength-bar_left)))



#===============================================================================================
#----  FILE I/O

class GetChar(object):
	# A class to wrap the getch() function to ensure that its destructor is called
	# to restore normal terminal operation, so that a character can be gotten in a process
	# that may be terminated before a character is received.
	def __init__(self):
		self.fd = sys.stdin.fileno()
		self.default_attrs = termios.tcgetattr(self.fd)
		self.restored = True
	def __del__(self):
		self.done()
	def done(self):
		if not self.restored:
			termios.tcsetattr(self.fd, termios.TCSANOW, self.default_attrs)
			self.restored = True
	def getch(self):
		# Get and return a single character from the terminal.
		# Adapted from http://stackoverflow.com/questions/27750536/python-input-single-character-without-enter
		try:
			self.restored = False
			tty.setraw(self.fd)
			ch = sys.stdin.read(1)
		finally:
			self.done()
		return ch


class EncodedFile(object):
	# A class providing an open method for an encoded file, allowing reading
	# and writing using unicode, without explicit decoding or encoding.
	def __repr__(self):
		return u"EncodedFile(%r, %r)" % (self.filename, self.encoding)
	def __init__(self, filename, file_encoding):
		self.filename = filename
		def detect_by_bom(path, default_enc):
			# Detect whether a file starts wtih a BOM, and if it does, return the encoding.
			# Otherwise, return the default encoding specified.
			# Modified from code posted to
			# http://stackoverflow.com/questions/13590749/reading-unicode-file-data-with-bom-chars-in-python
			# by ivan_posdeev.
			with open(path, 'rb') as f:
				raw = f.read(4)
			for enc, boms in (
							('utf-8-sig', (codecs.BOM_UTF8,)),
							('utf_16', (codecs.BOM_UTF16_LE, codecs.BOM_UTF16_BE)),
							('utf_32', (codecs.BOM_UTF32_LE, codecs.BOM_UTF32_BE))):
				if any(raw.startswith(bom) for bom in boms):
					return enc
			return default_enc
		if os.path.exists(filename):
			self.encoding = detect_by_bom(filename, file_encoding)
		else:
			self.encoding = file_encoding
	def open(self, mode):
		fo = io.open(file=self.filename, mode=mode, encoding=self.encoding, errors=conf.enc_err_disposition, newline=None)
		return fo


class WriteSpec(object):
	def __repr__(self):
		return u"WriteSpec(%s, %s, %s)" % (self.msg, self.outfile, self.tee)
	def __init__(self, message, dest=None, tee=None, repeatable=False):
		# Inputs
		#	message: Text to write.  May contain substitution variable references.
		#	dest: The to which the text should be written.  If omitted, the message
		#			is written to the console.
		#	tee: Write to the console as well as to the specified file.  The argument
		#			is coerced to a Boolean.
		#	repeatable: Can the message be written more than once?
		# Actions
		#	Stores the arguments as properties for later use.
		self.msg = message
		self.outfile = dest
		self.tee = bool(tee)
		self.repeatable = bool(repeatable)
		self.written = False
	def write(self):
		# Writes the message per the specifications given to '__init__()'.  Substitution
		# variables are processed.
		# Inputs: no inputs.
		# Return value: None.
		global conf
		global subvars
		if self.repeatable or not self.written:
			self.written = True
			msg = subvars.substitute_all(self.msg)
			if self.outfile:
				EncodedFile(self.outfile, conf.output_encoding).open('a').write(msg)
			if (not self.outfile) or self.tee:
				try:
					output.write(msg.encode(conf.output_encoding))
				except ConsoleUIError as e:
					output.reset()
					exec_log.log_status_info("Console UI write failed (message {%s}); output reset to stdout." % e.value)
					output.write(msg.encode(conf.output_encoding))
			if conf.tee_write_log:
				exec_log.log_user_msg(msg)
		return None



class Logger(object):
	# A custom logger for execsql that writes several different types of messages to a log file.
	# All messages have a 'run identifier' to link them so that the different types could be
	# parsed out into different tables of a database.  The name and path of the script file
	# can be specified, but by default the file name is "execsql.log" and it will be placed
	# in the same directory as the script file.  This file will be created if it does not exist,
	# and appended to if it does exist.  The different types of messages are:
	#	* run: Information about the run as a whole:
	#		+ Script name
	#		+ Script path
	#		+ Script file revision date (from OS, not from notes)
	#		+ Script file size
	#		+ User name
	#		+ Command-line options
	#	* run_db_file: Information about the Access or SQLite database used:
	#		+ Database file name with full path
	#	* run_db_server: Information about the Postgres or SQL Server database used:
	#		+ Server name
	#		+ Database name
	#	* action: Significant actions carried out by the script, primarily those that affect the results.
	#		+ Sequence number: automatically generated
	#		+ Action type
	#			- export: Data are exported to a file.  The 'description' value contains the query name and export file name.
	#			- prompt_quit: A prompt has been displayed to continue or cancel.  The 'description' value identifies the user's decision.
	#		* line_no: The script line number on which the action is taken
	#		* Description: Free text with details of the action
	#	* status: Status messages, generally errors
	#		* Sequence number: automatically generated, and shared with actions and user messages
	#		* Status type
	#			- exception
	#			- error
	#		* Description: Free text with details of the status
	#	* user_msg: A message provided by the user with the LOG metacommand
	#		* Sequence number: automatically generated, and shared with status and actions
	#		* Message: text provided by the user.
	#	* exit: Program status at exit
	#		+ Exit type
	#			- end_of_script
	#			- prompt_quit: Exited in response to a prompt metacommand
	#			- halt: Exited in response to a halt metacommand
	#			- error: Exited in response to an error
	#			- exception: Exited due to an exception
	#		+ line_no: The script line number from which the exit was triggered
	#		+ Description: Free text with any additional details about the exit conditions.
	log_file = None
	def __repr__(self):
		return u"Logger(%d, %d, %d, %d, %d)" % (self.script_file_name, self.db_name,
				self.server_name, self.cmdline_options, self.log_file_name)
	def __init__(self, script_file_name, db_name, server_name, cmdline_options, log_file_name=None):
		# For Access and SQLite, 'db_name' should be the file name and 'server_name' should be null.
		self.script_file_name = script_file_name
		self.db_name = db_name
		self.server_name = server_name
		self.cmdline_options = cmdline_options
		if log_file_name:
			self.log_file_name = log_file_name
		else:
			self.log_file_name = os.path.join(os.path.dirname(os.path.abspath(script_file_name)), 'execsql.log')
		f_exists = os.path.isfile(self.log_file_name)
		try:
			ef = EncodedFile(self.log_file_name, logfile_encoding)
			self.log_file = ef.open("a")
		except:
			errmsg = "Can't open log file %s" % self.log_file_name
			e = ErrInfo("exception", exception_msg=exception_desc(), other_msg=errmsg)
			exit_now(1, e, errmsg)
		if not f_exists:
			self.writelog(u"# Execsql log.\n# The first value on each line is the record type.\n# The second value is the run identifier.\n# See the documentation for details.\n")
		self.run_id = datetime.datetime.now().strftime("%Y%m%d_%H%M_%S")
		self.user = getpass.getuser()
		sz, dt = file_size_date(script_file_name)
		msg = u"run\t%s\t%s\t%s\t%s\t%s\t%s\n" % (self.run_id,
							os.path.abspath(script_file_name),
							dt,
							sz,
							self.user,
							u", ".join([ u"%s: %s" % (k, cmdline_options[k]) for k in cmdline_options.keys()]))
		self.writelog(msg)
		if server_name:
			msg = u"run_db_server\t%s\t%s\t%s\n" % (self.run_id, server_name, db_name)
		else:
			msg = u"run_db_file\t%s\t%s\n" % (self.run_id, db_name)
		self.writelog(msg)
		self.seq_no = 0
		atexit.register(self.close)
		self.exit_type = None
		self.exit_scriptfile = None
		self.exit_lno = None
		self.exit_description = None
		atexit.register(self.log_exit)
	def writelog(self, msg):
		self.log_file.write(msg)
	def close(self):
		if self.log_file:
			self.log_file.close()
			self.log_file = None
	def log_db_connect(self, db):
		self.seq_no += 1
		msg = u"connect\t%s\t%s\t%s\n" % (self.run_id, self.seq_no, db.name())
		self.writelog(msg)
	def log_action_export(self, line_no, query_name, export_file_name):
		self.seq_no += 1
		msg = u"action\t%s\t%d\texport\t%d\t%s\n" % (self.run_id, self.seq_no, line_no, u"Query %s exported to %s" %(query_name, export_file_name))
		self.writelog(msg)
	def log_action_prompt_quit(self, line_no, do_quit, msg):
		# 'do_quit' is Boolean: True to quit, False if not.
		msg = None if not msg else msg.replace('\n', '')
		self.seq_no += 1
		descrip = u'%s after prompt "%s"' % (u"Quitting" if do_quit else u"Continuing", msg)
		wmsg = u"action\t%s\t%d\tprompt_quit\t%s\t%s\n" % (self.run_id, self.seq_no, str(line_no) or '', descrip)
		self.writelog(wmsg)
	def log_status_exception(self, msg):
		msg = None if not msg else msg.replace('\n', '')
		self.seq_no += 1
		wmsg = u"status\t%s\t%d\texception\t%s\n" % (self.run_id, self.seq_no, msg or '')
		self.writelog(wmsg)
	def log_status_error(self, msg):
		msg = None if not msg else msg.replace('\n', '')
		self.seq_no += 1
		wmsg = u"status\t%s\t%d\terror\t%s\n" % (self.run_id, self.seq_no, msg or '')
		self.writelog(wmsg)
	def log_status_info(self, msg):
		msg = None if not msg else msg.replace('\n', '')
		self.seq_no += 1
		wmsg = u"status\t%s\t%d\tinfo\t%s\n" % (self.run_id, self.seq_no, msg or '')
		self.writelog(wmsg)
	def log_user_msg(self, msg):
		msg = None if not msg else msg.replace('\n', '')
		if msg != '':
			self.seq_no += 1
			wmsg = u"user_msg\t%s\t%d\tinfo\t%s\n" % (self.run_id, self.seq_no, msg)
			self.writelog(wmsg)
	def log_exit_end(self, script_file_name=None, line_no=None):
		# Save values to be used by exit() function triggered on program exit
		self.exit_type = u'end_of_script'
		self.exit_scriptfile = script_file_name
		self.exit_lno = line_no
		self.exit_description = None
	def log_exit_halt(self, script_file_name, line_no, msg=None):
		# Save values to be used by exit() function triggered on program exit
		self.exit_type = u'halt'
		self.exit_scriptfile = script_file_name
		self.exit_lno = line_no
		self.exit_description = msg
	def log_exit_exception(self, msg):
		# Save values to be used by exit() function triggered on program exit
		self.exit_type = u'exception'
		self.exit_scriptfile = None
		self.exit_lno = None
		self.exit_description = msg.replace(u'\n', u'')
	def log_exit_error(self, msg):
		# Save values to be used by exit() function triggered on program exit
		self.exit_type = u'error'
		self.exit_scriptfile = None
		self.exit_lno = None
		self.exit_description = None if not msg else msg.replace('\n', '')
	def log_exit(self):
		wmsg = u"exit\t%s\t%s\t%s(%s)\t%s\n" % (self.run_id, self.exit_type, self.exit_scriptfile or '', str(self.exit_lno or ''), self.exit_description or '')
		self.writelog(wmsg)


class TempFileMgr(object):
	def __repr__(self):
		return u"TempFileMgr()"
	def __init__(self):
		# Initialize a list of temporary file names.
		self.temp_file_names = []
		atexit.register(self.remove_all)
	def new_temp_fn(self):
		# Get a file object, get its name, and throw away the object
		fn = tempfile.NamedTemporaryFile().name
		self.temp_file_names.append(fn)
		return fn
	def remove_all(self):
		for fn in self.temp_file_names:
			if os.path.exists(fn):
				try:
					# This may fail if the user has it open; let it go.
					os.unlink(fn)
				except:
					pass


class OdsFileError(Exception):
	def __init__(self, error_message):
		self.value = error_message
	def __repr__(self):
		return u"OdsFileError(%r)" % self.value
	def __str__(self):
		return repr(self.value)

class OdsFile(object):
	def __repr__(self):
		return u"OdsFile()"
	def __init__(self):
		global odf
		try:
			import odf.opendocument
			import odf.table
			import odf.text
			import odf.number
			import odf.style
		except:
			fatal_error("The odfpy library is needed to create OpenDocument spreadsheets.")
		self.filename = None
		self.wbk = None
		self.cell_style_names = []
	def open(self, filename):
		self.filename = filename
		if os.path.isfile(filename):
			self.wbk = odf.opendocument.load(filename)
			# Get a list of all cell style names used, so as not to re-define them.
			# Adapted from http://www.pbertrand.eu/reading-an-odf-document-with-odfpy/
			for sty in self.wbk.automaticstyles.childNodes:
				fam = sty.getAttribute("family")
				if fam == "table-cell":
					name = sty.getAttribute("name")
					if not name in self.cell_style_names:
						self.cell_style_names.append(name)
		else:
			self.wbk = odf.opendocument.OpenDocumentSpreadsheet()
	def define_iso_datetime_style(self):
		st_name = "iso_datetime"
		if not st_name in self.cell_style_names:
			dt_style = odf.number.DateStyle(name="iso-datetime")
			dt_style.addElement(odf.number.Year(style="long"))
			dt_style.addElement(odf.number.Text(text=u"-"))
			dt_style.addElement(odf.number.Month(style="long"))
			dt_style.addElement(odf.number.Text(text=u"-"))
			dt_style.addElement(odf.number.Day(style="long"))
			# odfpy collapses text elements that have only spaces, so trying to insert just a space between the date
			# and time actually results in no space between them.  Other Unicode invisible characters
			# are also trimmed.  The delimiter "T" is used instead, and conforms to ISO-8601 specifications.
			dt_style.addElement(odf.number.Text(text=u"T"))
			dt_style.addElement(odf.number.Hours(style="long"))
			dt_style.addElement(odf.number.Text(text=u":"))
			dt_style.addElement(odf.number.Minutes(style="long"))
			dt_style.addElement(odf.number.Text(text=u":"))
			dt_style.addElement(odf.number.Seconds(style="long", decimalplaces="3"))
			self.wbk.styles.addElement(dt_style)
			dts = odf.style.Style(name=st_name, datastylename="iso-datetime", parentstylename="Default", family="table-cell")
			self.wbk.automaticstyles.addElement(dts)
			self.cell_style_names.append(st_name)
	def define_iso_date_style(self):
		st_name = "iso_date"
		if st_name not in self.cell_style_names:
			dt_style = odf.number.DateStyle(name="iso-date")
			dt_style.addElement(odf.number.Year(style="long"))
			dt_style.addElement(odf.number.Text(text=u"-"))
			dt_style.addElement(odf.number.Month(style="long"))
			dt_style.addElement(odf.number.Text(text=u"-"))
			dt_style.addElement(odf.number.Day(style="long"))
			self.wbk.styles.addElement(dt_style)
			dts = odf.style.Style(name=st_name, datastylename="iso-date", parentstylename="Default", family="table-cell")
			self.wbk.automaticstyles.addElement(dts)
			self.cell_style_names.append(st_name)
	def sheetnames(self):
		# Returns a list of the worksheet names in the specified ODS spreadsheet.
		return [sheet.getAttribute("name") for sheet in self.wbk.spreadsheet.getElementsByType(odf.table.Table)]
	def sheet_named(self, sheetname):
		# Return the sheet with the matching name.  If the name is actually an integer,
		# return that sheet number.
		if isinstance(sheetname, int):
			sheet_no = sheetname
		else:
			try:
				sheet_no = int(sheetname)
				if sheet_no < 1:
					sheet_no = None
			except:
				sheet_no = None
		if sheet_no is not None:
			for i, sheet in enumerate(self.wbk.spreadsheet.getElementsByType(odf.table.Table)):
				if i+1 == sheet_no:
					return sheet
			else:
				sheet_no = None
		if sheet_no is None:
			for sheet in self.wbk.spreadsheet.getElementsByType(odf.table.Table):
				if sheet.getAttribute("name").lower() == sheetname.lower():
					return sheet
		return None
	def sheet_data(self, sheetname, junk_header_rows=0):
		sheet = self.sheet_named(sheetname)
		if not sheet:
			raise OdsFileError("There is no sheet named %s" % sheetname)
		def row_data(sheetrow):
			# Adapted from http://www.marco83.com/work/wp-content/uploads/2011/11/odf-to-array.py
			cells = sheetrow.getElementsByType(odf.table.TableCell)
			rowdata = []
			for cell in cells:
				ps = cell.getElementsByType(odf.text.P)
				p_content = []
				for p in ps:
					p_content.append(unicode(p))
				if len(p_content) == 0:
					rowdata.append(None)
				elif unicode(p_content[0]) != u'#':
					rowdata.extend(p_content)
			return rowdata
		rows = sheet.getElementsByType(odf.table.TableRow)
		if junk_header_rows > 0:
			rows = rows[junk_header_rows: ]
		return [row_data(r) for r in rows]
	def new_sheet(self, sheetname):
		# Returns a sheet (a named Table) that has not yet been added to the workbook
		return odf.table.Table(name=sheetname)
	def add_row_to_sheet(self, datarow, odf_table):
		tr = odf.table.TableRow()
		odf_table.addElement(tr)
		for item in datarow:
			if isinstance(item, float) or isinstance(item, int) or isinstance(item, long):
				tc = odf.table.TableCell(valuetype="float", value=item)
			elif isinstance(item, bool):
				tc = odf.table.TableCell(booleanvalue=item)
				#tc = odf.table.TableCell(valuetype="boolean", value=item)
			elif isinstance(item, datetime.datetime):
				self.define_iso_datetime_style()
				tc = odf.table.TableCell(valuetype="date", datevalue=item.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3], stylename="iso_datetime")
				#tc.addElement(odf.text.P(text=item.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]))
			elif isinstance(item, datetime.date):
				self.define_iso_date_style()
				tc = odf.table.TableCell(valuetype="date", datevalue=item.strftime("%Y-%m-%d"), stylename="iso_date")
				#tc.addElement(odf.text.P(text=item.strftime("%Y-%m-%d")))
			elif isinstance(item, datetime.time):
				self.define_iso_datetime_style()
				timeval = datetime.datetime(1899, 12, 30, item.hour, item.minute, item.second, item.microsecond, item.tzinfo)
				tc = odf.table.TableCell(timevalue=timeval.strftime("PT%HH%MM%S.%fS"), stylename="iso_datetime")
				tc.addElement(odf.text.P(text=unicode(timeval.strftime("%H:%M:%S.%f"))))
				#tc = odf.table.TableCell(valuetype="time", value=datetime.datetime(1899,12,30, item.hour, item.minute, item.second, item.microsecond, item.tzinfo))
			elif isinstance(item, basestring):
				#tc = odf.table.TableCell(stringvalue=item)
				item = item.replace(u'\n', u' ').replace(u'\r', u' ')
				tc = odf.table.TableCell(valuetype="string", stringvalue=item)
				#tc.addElement(odf.text.P(text=unicode(item)))
			else:
				tc = odf.table.TableCell(value=item)
			if item is not None:
				tc.addElement(odf.text.P(text=unicode(item)))
			tr.addElement(tc)
	def add_sheet(self, odf_table):
		self.wbk.spreadsheet.addElement(odf_table)
	def save_close(self):
		ofile = open(self.filename, "wb")
		self.wbk.write(ofile)
		ofile.close()
		self.filename = None
		self.wbk = None
	def close(self):
		self.filename = None
		self.wbk = None


class XlsFileError(Exception):
	def __init__(self, error_message):
		self.value = error_message
	def __repr__(self):
		return u"XlsFileError(%r)" % self.value
	def __str__(self):
		return repr(self.value)

class XlsFile(object):
	def __repr__(self):
		return u"XlsFile()"
	class XlsLog(object):
		def __init__(self):
			self.log_msgs = []
		def write(self, msg):
			self.log_msgs.append(msg)
	def __init__(self):
		try:
			global xlrd
			import xlrd
		except:
			fatal_error("The xlrd library is needed to read Excel spreadsheets.")
		self.filename = None
		self.encoding = None
		self.wbk = None
		self.datemode = 0
		self.errlog = self.XlsLog()
	def open(self, filename, encoding=None):
		self.filename = filename
		self.encoding = encoding
		if os.path.isfile(filename):
			self.wbk = xlrd.open_workbook(filename, logfile=self.errlog, encoding_override=self.encoding)
			self.datemode = self.wbk.datemode
		else:
			raise XlsFileError("There is no Excel file %s." % self.filename)
	def sheet_named(self, sheetname):
		# Return the sheet with the matching name.  If the name is actually an integer,
		# return that sheet number.
		if isinstance(sheetname, int):
			sheet_no = sheetname
		else:
			try:
				sheet_no = int(sheetname)
				if sheet_no < 1:
					sheet_no = None
			except:
				sheet_no = None
		if sheet_no is None:
			sheet = self.wbk.sheet_by_name(unicode(sheetname))
		else:
			# User-specified sheet numbers should be 1-based; xlrd sheet indexes are 0-based
			sheet = self.wbk.sheet_by_index(max(0, sheet_no-1))
		return sheet
	def sheet_data(self, sheetname, junk_header_rows=0):
		try:
			sheet = self.sheet_named(sheetname)
		except:
			raise XlsFileError("There is no Excel worksheet named %s in %s." % (sheetname, self.filename))
		# Don't rely on sheet.ncols and sheet.nrows, because Excel will count columns
		# and rows that have ever been filled, even if they are now empty.  Base the column count
		# on the number of contiguous non-empty cells in the first row, and process the data up to nrows until
		# a row is entirely empty.
		def row_data(sheetrow, columns=None):
			cells = sheet.row_slice(sheetrow)
			if columns:
				d = [cells[c] for c in range(columns)]
			else:
				d = [cell for cell in cells]
			datarow = []
			for c in d:
				if c.ctype == 0:
					# empty
					datarow.append(None)
				elif c.ctype == 1:
					# This might be a timestamp with time zone that xlrd treats as a string.
					try:
						dt = DT_TimestampTZ()._from_data(c.value)
						datarow.append(dt)
					except:
						datarow.append(c.value)
				elif c.ctype == 2:
					# float, but maybe should be int
					if c.value - int(c.value) == 0:
						datarow.append(int(c.value))
					else:
						datarow.append(c.value)
				elif c.ctype == 3	:
					# date
					dt = xlrd.xldate_as_tuple(c.value, self.datemode)
					# Convert to time or datetime
					if not any(dt[:3]):
						# No date values
						datarow.append(datetime.time(*dt[3:]))
					else:
						datarow.append(datetime.datetime(*dt))
				elif c.ctype == 4:
					# Boolean
					datarow.append(bool(c.value))
				elif c.ctype == 5:
					# Error code
					datarow.append(xlrd.error_text_from_code(c.value))
				elif c.ctype == 6:
					# blank
					datarow.append(None)
				else:
					datarow.append(c.value)
			return datarow
		hdr_row = row_data(junk_header_rows)
		ncols = 0
		for c in range(len(hdr_row)):
			if not hdr_row[c]:
				break
			ncols += 1
		sheet_data = []
		for r in range(junk_header_rows, sheet.nrows - junk_header_rows):
			datarow = row_data(r, ncols)
			if datarow.count(None) == len(datarow):
				break
			sheet_data.append(datarow)
		return sheet_data
			
		

# End of file I/O.
#===============================================================================================


#===============================================================================================
#----  SIMPLE ENCRYPTION

class Encrypt(object):
	ky = {}
	ky['0'] = u'6f2bba010bdf450a99c1c324ace5d765'
	ky['3'] = u'4a69dd15b6304ed491f10d0ebc7498cf'
	ky['9'] = u'c06d0798e55a4ea2822cf6e3f0d32520'
	ky['e'] = u'1ab984b7c7574c18a5eee2be92236f19'
	ky['g'] = u'ee66e201ca9c4b55b7037eb5f94be9e4'
	ky['n'] = u'63fad3d6c81c4668b89533b9af182aa1'
	ky['p'] = u'647ff4e2bfec48b9a7a8ca4e4878769e'
	ky['w'] = u'5274bb5b1421406fa57c4863321dd111'
	ky['z'] = u'624b1d0835fb45caa2d0664c103179f3'
	def __repr__(self):
		return u"Encrypt()"
	def __init__(self):
		global itertools
		global base64
		import itertools, base64
	def xor(self, text, enckey):
		return u''.join(chr(ord(t)^ord(k)) for t,k in itertools.izip(text, itertools.cycle(enckey)))
	def encrypt(self, plaintext):
		random.seed()
		kykey = self.ky.keys()[random.randint(0, len(self.ky.keys())-1)]
		kyval = self.ky[kykey]
		noiselen = random.randint(1, 15)
		noise = unicode(uuid.uuid4()).replace('-', '')[0:noiselen]
		encstr = kykey + format(noiselen, '1x') + self.xor(noise + unicode(plaintext), kyval)
		return base64.encodestring(encstr)[:-1]
	def decrypt(self, crypttext):
		encstr = base64.decodestring(crypttext + '\n')
		kyval = self.ky[encstr[0]]
		noiselen = int(encstr[1], 16)
		return self.xor(encstr[2:], kyval)[noiselen:]

# End of Encrypt
#===============================================================================================



#===============================================================================================
#----  EMAIL

class Mailer(object):
	def __repr__(self):
		return u"Mailer()"
	def __del__(self):
		if hasattr(self, 'smtpconn'):
			self.smtpconn.quit()
	def __init__(self):
		global smtplib
		global MIMEMultipart
		global MIMEText
		global MIMEBase
		global encoders
		import smtplib
		from email.mime.multipart import MIMEMultipart
		from email.mime.text import MIMEText
		from email.mime.base import MIMEBase
		from email import encoders
		global conf
		if conf.smtp_host is None:
			raise ErrInfo(type="error", other_msg="Can't send email; the email host is not configured.")
		if conf.smtp_port is None:
			if conf.smtp_ssl:
				self.smtpconn = smtplib.SMTP_SSL(conf.smtp_host)
			else:
				self.smtpconn = smtplib.SMTP(conf.smtp_host)
		else:
			if conf.smtp_ssl:
				self.smtpconn = smtplib.SMTP_SSL(conf.smtp_host, conf.smtp_port)
			else:
				self.smtpconn = smtplib.SMTP(conf.smtp_host, conf.smtp_port)
		self.smtpconn.ehlo_or_helo_if_needed()
		if conf.smtp_tls:
			self.smtpconn.starttls()
			self.smtpconn.ehlo(conf.smtp_host)
		if conf.smtp_username:
			if conf.smtp_password:
				self.smtpconn.login(conf.smtp_username, conf.smtp_password)
			else:
				self.smtpconn.login(conf.smtp_username)
	def sendmail(self, send_from, send_to, subject, msg_content, content_filename=None, attach_filename=None):
		global smtplib
		global MIMEMultipart
		global MIMEText
		global MIMEBase
		global encoders
		if conf.email_format == 'html':
			msg = MIMEMultipart('alternative')
		else:
			msg = MIMEMultipart()
		recipients = re.split(r'[;,]', send_to)
		msg['From'] = send_from
		msg['To'] = ','.join(recipients)
		msg['Subject'] = subject
		if conf.email_format == 'html':
			msg_body = "<html><head>"
			if conf.email_css is not None:
				msg_body += "<style>%s</style>" % conf.email_css
			msg_body += "</head><body>%s" % msg_content if msg_content else ""
		else:
			msg_body = msg_content if msg_content else ""
		if content_filename is not None:
			msg_body += "\n" + open(content_filename, "rt").read()
		if conf.email_format == 'html':
			msg_body += "</body></html>"
			msg.attach(MIMEText(msg_body, 'html'))
		else:
			msg.attach(MIMEText(msg_body, 'plain'))
		if attach_filename is not None:
			f = open(attach_filename, "rb")
			fdata = MIMEBase('application', 'octet-stream')
			fdata.set_payload(f.read())
			f.close()
			encoders.encode_base64(fdata)
			fdata.add_header('Content-Disposition', "attachment",  filename=attach_filename)
			msg.attach(fdata)
		self.smtpconn.sendmail(send_from, recipients, msg.as_string())


class MailSpec(object):
	def __init__(self, send_from, send_to, subject, msg_content, content_filename=None, attach_filename=None, repeatable=False):
		self.send_from = send_from
		self.send_to = send_to
		self.subject = subject
		self.msg_content = msg_content
		self.content_filename = content_filename
		self.attach_filename = attach_filename
		self.repeatable = repeatable
		self.sent = False
	def send(self):
		if self.repeatable or not self.sent:
			self.sent = True
			send_from = subvars.substitute_all(self.send_from)
			send_to = subvars.substitute_all(self.send_to)
			subject = subvars.substitute_all(self.subject)
			msg_content = subvars.substitute_all(self.msg_content)
			content_filename = subvars.substitute_all(self.content_filename)
			attach_filename = subvars.substitute_all(self.attach_filename)
			Mailer().sendmail(send_from, send_to, subject, msg_content, content_filename, attach_filename)
		return None
			

# End of email
#===============================================================================================


#===============================================================================================
#-----  TIMER

class Timer(object):
	def __repr__(self):
		return u"Timer()"
	def __init__(self):
		self.running = False
		self.start_time = 0.0
		self.elapsed_time = 0.0
	def start(self):
		self.running = True
		self.start_time = time.time()
	def stop(self):
		self.elapsed_time = time.time() - self.start_time
		self.running = False
	def elapsed(self):
		if self.running:
			return time.time() - self.start_time
		else:
			return self.elapsed_time
# End of Timer
#===============================================================================================


#===============================================================================================
#-----  ERROR HANDLING

class ErrInfo(Exception):
	def __repr__(self):
		return u"ErrInfo(%r, %r, %r, %r)" % (self.type, self.command, self.exception, self.other)
	def __init__(self, type, command_text=None, exception_msg=None, other_msg=None):
		# Argument 'type' should be "db", "cmd", "log", "error", "exception", or "other".
		# Arguments for each type are as follows:
		# 	"db"		: command_text, exception_msg
		# 	"cmd"	: command_text, <exception_msg | other_msg>
		# 	"log"	: other_msg [, exception_msg]
		# 	"error"	: other_msg [, exception_msg]
		#	"systemexit" : other_msg
		# 	"exception"	: exception_msg [, other_msg]
		self.type = type
		self.command = command_text
		self.exception = None if not exception_msg else exception_msg.replace(u'\n', u'\n     ')
		self.other = None if not other_msg else other_msg.replace(u'\n', u'\n     ')
		if working_script and working_script.last_command:
			self.script_file, self.script_line_no = working_script.current_script_line()
			self.cmd = working_script.last_command.sql
			self.cmdtype = working_script.last_command.command_type
		else:
			self.script_file = None
			self.script_line_no = None
			self.cmd = None
			self.cmdtype = None
		self.error_message = None
		if type == 'exception':
			if exec_log:
				exec_log.log_status_exception(exception_msg)
		elif type == 'error':
			if exec_log:
				exec_log.log_status_error(other_msg)
		subvars.add_substitution("$ERROR_MESSAGE", self.errmsg())
	def script_info(self):
		if self.script_line_no:
			return u"Line %d of script %s" % (self.script_line_no, self.script_file)
		else:
			return None
	def cmd_info(self):
		if self.cmdtype:
			if self.cmdtype == "cmd":
				em = u"Metacommand: %s" % self.cmd
			else:
				em = u"SQL statement: \n         %s" % self.cmd.replace(u'\n', u'\n         ')
			return em
		else:
			return None
	def eval_err(self):
		if self.type == 'db':
			self.error_message = u"**** Error in SQL statement."
		elif self.type == 'cmd':
			self.error_message = u"**** Error in metacommand."
		elif self.type == 'log':
			self.error_message = u"**** Error in logging."
		elif self.type == 'error':
			self.error_message = u"**** General error."
		elif self.type == 'systemexit':
			self.error_message = u"**** Exit."
		elif self.type == 'exception':
			self.error_message = u"**** Exception."
		else:
			self.error_message = u"**** Error of unknown type: %s" % self.type
		sinfo = self.script_info()
		cinfo = self.cmd_info()
		if sinfo:
			self.error_message += u"\n     %s" % sinfo
		if self.exception:
			self.error_message += u"\n     %s" % self.exception
		if self.other:
			self.error_message += u"\n     %s" % self.other
		if self.command:
			self.error_message += u"\n     %s" % self.command
		if cinfo:
			self.error_message += u"\n     %s" % cinfo
		self.error_message += u"\n     Error occurred at %s UTC." % time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
		return self.error_message
	def write(self):
		errmsg = self.eval_err()
		output.write_err(errmsg)
		return errmsg
	def errmsg(self):
		return self.eval_err()


def exception_info():
	# Returns the exception type, value, source file name, source line number, and source line text.
	strace = traceback.extract_tb(sys.exc_info()[2])[-1:]
	traces = traceback.extract_tb(sys.exc_info()[2])
	xline = 0
	for trace in traces:
		if u"execsql" in trace[0]:
			xline = trace[1]
	exc_message = u''
	exc_param = sys.exc_info()[1]
	if isinstance(exc_param, basestring):
		exc_message = exc_param
	else:
		if hasattr(exc_param, 'message') and isinstance(exc_param.message, basestring) and len(exc_param.message) > 0:
			exc_message = exc_param.message
		elif hasattr(exc_param, 'value') and isinstance(exc_param.value, basestring) and len(exc_param.value) > 0:
			exc_message = exc_param.value
		else:
			exc_message = repr(exc_param)
	exc_message = unicode(exc_message, errors='replace')
	return sys.exc_info()[0].__name__, exc_message, strace[0][0], xline, strace[0][3]


def exception_desc():
	exc_type, exc_strval, exc_filename, exc_lineno, exc_linetext = exception_info()
	return u"%s: %s in %s on line %s of execsql." % (exc_type, exc_strval, exc_filename, exc_lineno)

def exit_now(exit_status, errinfo, logmsg=None):
	global exec_log
	em = None
	if errinfo is not None:
		em = errinfo.write()
		if err_halt_writespec is not None:
			try:
				err_halt_writespec.write()
			except:
				exec_log.log_status_error("Failed to write the ON ERROR_HALT WRITE message.")
	if gui_console_isrunning():
		if errinfo is not None:
			if conf.gui_wait_on_error_halt or conf.gui_wait_on_exit:
				gui_console_wait_user("Script error; close the console window to exit execsql.")
		elif conf.gui_wait_on_exit:
			gui_console_wait_user("Script complete; close the console window to exit execsql.")
	disable_gui()
	if errinfo is not None and err_halt_email is not None:
		try:
			err_halt_email.send()
		except:
			exec_log.log_status_error("Failed to send the ON ERROR_HALT EMAIL message.")
	if exit_status > 0:
		if exec_log:
			if logmsg:
				exec_log.log_exit_error(logmsg)
			else:
				if em:
					exec_log.log_exit_error(em)
	sys.exit(exit_status)

def fatal_error(error_msg=None):
	exit_now(1, ErrInfo("error", other_msg=error_msg))

# End of error handling.
#===============================================================================================


#===============================================================================================
#-----  DATA TYPES
# These are data types that may be used in database tables.


class DataTypeError(Exception):
	def __init__(self, data_type_name, error_msg):
		self.data_type_name = data_type_name or "Unspecified data type"
		self.error_msg = error_msg or "Unspecified error"
	def __repr__(self):
		return u"DataTypeError(%r, %r)" % (self.data_type_name, self.error_msg)
	def __str__(self):
		return "%s: %s" % (self.data_type_name, self.error_msg)


class DataType(object):
	data_type_name = None
	data_type = None
	lenspec = False		# Is a length specification required for a (SQL) declaration of this data type?
	varlen = False		# Do we need to know if a set of data values varies in length?
	precspec = False	# Do we need to know the precision and scale of the data?
	precision = None	# Precision (total number of digits) for numeric values.
	scale = None		# Scale (number of digits to the right of the decimal point) for numeric values.
	_CONV_ERR = "Can't convert %s"
	def __repr__(self):
		return u"DataType(%r, %r)" % (self.data_type_name, self.data_type)
	def is_null(self, data):
		return data is None or (isinstance(data, basestring) and len(data) == 0)
	def matches(self, data):
		# Returns T/F indicating whether the given data value could be of this data type.
		# The data value should be non-null.
		if self.is_null(data):
			return False
		return self._is_match(data)
	def from_data(self, data):
		# Returns the data value coerced to this type, or raises a DataTypeError exception.
		# The data value should be non-null.
		if self.is_null(data):
			return None
			#raise DataTypeError(self.data_type_name, "Conversion of None is not allowed.")
		return self._from_data(data)
	def _is_match(self, data):
		# This method may be overridden in child classes.
		#raise DataTypeError(self.data_type_name, "The ._is_match() method is unimplemented.")
		try:
			self._from_data(data)
		except DataTypeError:
			return False
		return True
	def _from_data(self, data):
		# This method may be overridden in child classes.
		#raise DataTypeError(self.data_type_name, "The ._from_data() method is unimplemented.")
		if type(data) == self.data_type:
			return data
		try:
			i = self.data_type(data)
		except:
			raise DataTypeError(self.data_type_name, self._CONV_ERR % data)
		return i


class Tz(datetime.tzinfo):
	def __init__(self, sign, hr, min):
		self.sign = sign
		self.hr = hr
		self.min = min
	def utcoffset(self, dt):
		return self.sign * datetime.timedelta(hours=self.hr, minutes=self.min)


class DT_TimestampTZ(DataType):
	data_type_name = "timestamptz"
	data_type = datetime.datetime
	# There is no distinct Python type corresponding to a timestamptz, so the data_type
	# is not exactly appropriate, and methods need to be overridden.
	def __repr__(self):
		return u"DT_TimestampTZ()"
	def _is_match(self, data):
		# data must be non-null
		if type(data) == datetime.datetime:
			if data.tzinfo is not None and data.tzinfo.utcoffset(data) is not None:
				return True
			return False
		if not isinstance(data, basestring):
			return False
		try:
			self.from_data(data)
		except DataTypeError:
			return False
		return True
	def _from_data(self, data):
		dt = parse_datetimetz(data)
		if not dt:
			raise DataTypeError(self.data_type_name, self._CONV_ERR % data)
		return dt


class DT_Timestamp(DataType):
	data_type_name = "timestamp"
	data_type = datetime.datetime
	def __repr__(self):
		return u"DT_Timestamp()"
	def _from_data(self, data):
		dt = parse_datetime(data)
		if not dt:
			raise DataTypeError(self.data_type_name, self._CONV_ERR % data)
		return dt


class DT_Date(DataType):
	data_type_name = "date"
	data_type = datetime.date
	def __repr__(self):
		return u"DT_Date()"
	date_fmts = ("%x",
			"%m/%d/%Y",
			"%m/%d/%y",
			"%Y-%m-%d",
			"%Y/%m/%d",
			"%b %d, %Y",
			"%b %d %Y",
			"%d %b, %Y",
			"%d %b %Y",
			"%b. %d, %Y",
			"%b. %d %Y",
			"%d %b., %Y",
			"%d %b. %Y",
			"%B %d, %Y",
			"%B %d %Y",
			"%d %B, %Y",
			"%d %B %Y"
			)
	def _from_data(self, data):
		if type(data) == self.data_type:
			return data
		if not isinstance(data, basestring):
			raise DataTypeError(self.data_type_name, self._CONV_ERR % data)
		for f in self.date_fmts:
			try:
				dt = datetime.datetime.strptime(data, f)
				dtt = datetime.date(dt.year, dt.month, dt.day)
			except:
				continue
			break
		else:
			raise DataTypeError(self.data_type_name, self._CONV_ERR % data)
		return dtt


class DT_Time(DataType):
	data_type_name = "time"
	data_type = datetime.time
	def __repr__(self):
		return u"DT_Time()"
	time_fmts = ("%H:%M", "%H%M:%S", "%H%M:%S.%f", "%H:%M:%S", "%H:%M:%S.%f",
				"%I:%M%p", "%I:%M:%S%p", "%I:%M:%S.%f%p",
				"%I:%M %p", "%I:%M:%S %p", "%I:%M:%S.%f %p", "%X")
	def _from_data(self, data):
		if type(data) == self.data_type:
			return data
		if type(data) == datetime.datetime:
			return datetime.time(data.hour, data.minute, data.second, data.microsecond)
		if not isinstance(data, basestring):
			raise DataTypeError(self.data_type_name, self._CONV_ERR % data)
		for f in self.time_fmts:
			try:
				dt = datetime.datetime.strptime(data, f)
				t = datetime.time(dt.hour, dt.minute, dt.second, dt.microsecond)
			except:
				continue
			break
		else:
			raise DataTypeError(self.data_type_name, self._CONV_ERR % data)
		return t


class DT_Boolean(DataType):
	data_type_name = "boolean"
	data_type = bool
	def __repr__(self):
		return u"DT_Boolean()"
	def set_bool_matches(self):
		self.true = (u'yes', u'true')
		self.false = (u'no', u'false')
		if not conf.boolean_words:
			self.true += (u'y', u't')
			self.false += (u'n', u'f')
		if conf.boolean_int:
			self.true += (u'1',)
			self.false += (u'0',)
		self.bool_repr = self.true + self.false
	def _is_match(self, data):
		self.set_bool_matches()
		if type(data) == bool:
			return True
		elif conf.boolean_int and type(data) in (int, long) and data in (0, 1):
			return True
		elif isinstance(data, basestring) and unicode(data).lower() in self.bool_repr:
			return True
		return False
	def _from_data(self, data):
		self.set_bool_matches()
		if type(data) == bool:
			return data
		elif conf.boolean_int and type(data) in (int, long) and data in (0, 1):
			return data == 1
		elif isinstance(data, basestring) and unicode(data).lower() in self.bool_repr:
			return unicode(data).lower() in self.true
		else:
			raise DataTypeError(self.data_type_name, self._CONV_ERR % data)


class DT_Integer(DataType):
	data_type_name = "integer"
	data_type = int
	def __repr__(self):
		return u"DT_Integer()"
	def _is_match(self, data):
		if type(data) == int:
			return data <= conf.max_int and data >= -1*conf.max_int-1
		elif type(data) == float:
			return False
		elif isinstance(data, basestring):
			if leading_zero_num(data):
				return False
			try:
				i = int(data)
			except:
				return False
			return i <= conf.max_int and i >= -1*conf.max_int-1
		else:
			return False
	def _from_data(self, data):
		if type(data) == int:
			return data
		if type(data) == float:
			if int(data) == data:
				return int(data)
			else:
				raise DataTypeError(self.data_type_name, self._CONV_ERR % data)
		try:
			i = int(data)
		except:
			raise DataTypeError(self.data_type_name, self._CONV_ERR % data)
		if type(i) == long or leading_zero_num(data):
			raise DataTypeError(self.data_type_name, self._CONV_ERR % data)
		return i


class DT_Long(DataType):
	data_type_name = "long"
	data_type = long
	def __repr__(self):
		return u"DT_Long()"
	def _from_data(self, data):
		if type(data) == long:
			return data
		if type(data) == float:
			if long(data) == data:
				return long(data)
			else:
				raise DataTypeError(self.data_type_name, self._CONV_ERR % data)
		if type(data) == Decimal:
			raise DataTypeError(self.data_type_name, self._CONV_ERR % data)
		if leading_zero_num(data):
			raise DataTypeError(self.data_type_name, self._CONV_ERR % data)
		try:
			i = long(data)
		except:
			raise DataTypeError(self.data_type_name, self._CONV_ERR % data)
		return i


class DT_Float(DataType):
	data_type_name = "float"
	data_type = float
	def __repr__(self):
		return u"DT_Float()"
	def _from_data(self, data):
		if type(data) == float:
			return data
		if leading_zero_num(data):
			raise DataTypeError(self.data_type_name, self._CONV_ERR % data)
		try:
			i = float(data)
		except:
			raise DataTypeError(self.data_type_name, self._CONV_ERR % data)
		return i


class DT_Decimal(DataType):
	data_type_name = "decimal"
	data_type = Decimal
	precspec = True
	def __repr__(self):
		return u"DT_Character()"
	def _from_data(self, data):
		if type(data) == Decimal:
			x = data.as_tuple()
			digits = len(x.digits)
			if x.exponent < 0 and abs(x.exponent) > digits:
				self.precision = abs(x.exponent) + 1
			else:
				self.precision = digits
			self.scale = abs(x.exponent)
			return data
		elif isinstance(data, basestring):
			try:
				dec = Decimal(data)
			except:
				raise DataTypeError(self.data_type_name, self._CONV_ERR % data)
			x = dec.as_tuple()
			scale = abs(x.exponent)
			if scale > 0:
				digits = len(x.digits)
				if x.exponent < 0 and abs(x.exponent) > digits:
					self.precision = abs(x.exponent) + 1
				else:
					self.precision = digits
				self.scale = scale
			else:
				raise DataTypeError(self.data_type_name, self._CONV_ERR % data)
			return dec
		raise DataTypeError(self.data_type_name, self._CONV_ERR % data)


class DT_Character(DataType):
	data_type_name = "character"
	data_type = unicode
	lenspec = True
	def __repr__(self):
		return u"DT_Character()"
	def _is_match(self, data):
		if type(data) == bytearray:
			return False
		return super(DT_Character, self)._is_match(data)
	def _from_data(self, data):
		# data must be non-null.
		# This identifies data as character only if it is convertable to a string and its
		# length is no more than 255 characters; otherwise it should be considered
		# to be of the text data type.  Most DBMSs allow varchar data to be greater
		# than 255 characters, but Access does not, hence this length-based limitation.
		if not isinstance(data, basestring):
			try:
				data = unicode(data)
			except ValueError:
				raise DataTypeError(self.data_type_name, self._CONV_ERR % data)
		if len(data) > 255:
			raise DataTypeError(self.data_type_name, self._CONV_ERR % data)
		return data


class DT_Varchar(DataType):
	data_type_name = "varchar"
	data_type = unicode
	lenspec = True
	varlen = True
	def __repr__(self):
		return u"DT_Varchar()"
	def _is_match(self, data):
		if type(data) == bytearray:
			return False
		return super(DT_Varchar, self)._is_match(data)
	def _from_data(self, data):
		# data must be non-null.
		# This varchar data type is the same as the character data type.  The choice
		# of which is appropriate for a specific use should be based on the constancy
		# of data lengths in a particular case--information that is outside the scope
		# of the data type definition.
		if not isinstance(data, basestring):
			try:
				data = unicode(data)
			except ValueError:
				raise DataTypeError(self.data_type_name, self._CONV_ERR % data)
		if len(data) > 255:
			raise DataTypeError(self.data_type_name, self._CONV_ERR % data)
		return data


class DT_Text(DataType):
	data_type_name = "character"
	data_type = unicode
	def __repr__(self):
		return u"DT_Text)"
	def _is_match(self, data):
		if type(data) == bytearray:
			return False
		return super(DT_Text, self)._is_match(data)
	def _from_data(self, data):
		if not isinstance(data, basestring):
			try:
				data = unicode(data)
			except ValueError:
				raise DataTypeError(self.data_type_name, self._CONV_ERR % data)
		return data


class DT_Binary(DataType):
	data_type_name = "binary"
	data_type = bytearray
	def __repr__(self):
		return u"DT_Binary)"


#	End of data type definitions.
#===============================================================================================


#===============================================================================================
#-----  DATABASE TYPES


class DbTypeError(Exception):
	def __init__(self, dbms_id, data_type, error_msg):
		self.dbms_id = dbms_id
		self.data_type = data_type
		self.error_msg = error_msg or "Unspecified error"
	def __repr__(self):
		return u"DbTypeError(%r, %r)" % (self.dbms_id, self.data_type, self.error_msg)
	def __str__(self):
		if self.data_type:
			return "%s DBMS type error with data type %s: %s" % (self.dbms_id, self.data_type.data_type_name, self.error_msg)
		else:
			return "%s DBMS type error: %s" % (self.dbms_id, self.error_msg)


class DbType(object):
	def __init__(self, DBMS_id, db_obj_quotes=u'""'):
		# The DBMS_id is the name by which this DBMS is identified.
		# db_obj_quotechars is a string of two characters that are the opening and closing quotes
		# for identifiers (schema, table, and column names) that need to be quoted.
		self.dbms_id = DBMS_id
		self.quotechars = unicode(db_obj_quotes)
		# The dialect is a dictionary of DBMS-specific names for each column type.
		# Dialect keys are DataType classes.
		# Dialect objects are 4-tuples consisting of:
		#	0. a data type name (str)--non-null
		#	1. a Boolean indicating whether or not the length is part of the data type definition
		#		(e.g., for varchar)--non-null
		#	2. a name to use with the 'cast' operator as an alternative to the data type name--nullable.
		#	3. a function to perform a dbms-specific modification of the type conversion result produced
		#		by the 'from_data()' method of the data type.
		#	4. the precision for numeric data types.
		#	5. the scale for numeric data types.
		self.dialect = None
		# The dt_xlate dictionary translates one data type to another.
		# This is specifically needed for Access pre v. 4.0, which has no numeric type, and which 
		# therefore requires the numeric data type to be treated as a float data type.
		self.dt_xlate = {}
	def __repr__(self):
		return u"DbType(%r, %r)" % (self.dbms_id, self.quotechars)
	def name_datatype(self, data_type, dbms_name, length_required=False, casting_name=None, conv_mod_fn=None, precision=None, scale=None):
		# data_type is a DataType class object.
		# dbms_name is the DBMS-specific name for this data type.
		# length_required indicates whether length information is required.
		# casting_name is an alternate to the data type name to use in SQL "cast(x as <casting_name>)" expressions.
		# conv_mod_fn is a function that modifies the result of data_type().from_data(x).
		if self.dialect is None:
			self.dialect = {}
		self.dialect[data_type] = (dbms_name, length_required, casting_name, conv_mod_fn, precision, scale)
	def datatype_name(self, data_type):
		# A convenience function to simplify access to data type namess.
		#if not isinstance(data_type, DataType):
		#	raise DbTypeError(self.dbms_id, None, "Unrecognized data type: %s" % data_type)
		try:
			return self.dialect[data_type][0]
		except:
			raise DbTypeError(self.dbms_id, data_type, "%s DBMS type has no specification for data type %s" % (self.dbms_id, data_type.data_type_name))
	def quoted(self, dbms_object):
		if re.search(r'\W', dbms_object):
			if self.quotechars[0] == self.quotechars[1] and self.quotechars[0] in dbms_object:
				dbms_object = dbms_object.replace(self.quotechars[0], self.quotechars[0]+self.quotechars[0])
			return self.quotechars[0] + dbms_object + self.quotechars[1]
		return dbms_object
	def spec_type(self, data_type):
		# Returns a translated data type or the original if there is no translation.
		if data_type in self.dt_xlate.keys():
			return self.dt_xlate[data_type]
		return data_type
	def column_spec(self, column_name, data_type, max_len=None, is_nullable=False, precision=None, scale=None):
		# Returns a column specification as it would be used in a CREATE TABLE statement.
		# The arguments conform to those returned by Column().column_type
		#if not isinstance(data_type, DataType):
		#	raise DbTypeError(self.dbms_id, None, "Unrecognized data type: %s" % data_type)
		data_type = self.spec_type(data_type)
		try:
			dts = self.dialect[data_type]
		except:
			raise DbTypeError(self.dbms_id, data_type, "%s DBMS type has no specification for data type %s" % (self.dbms_id, data_type.data_type_name))
		if max_len and max_len > 0 and dts[1]:
			spec = "%s %s(%d)" % (self.quoted(column_name), dts[0], max_len)
		elif data_type.precspec and precision and scale:
			# numeric
			spec = "%s %s(%s,%s)" % (self.quoted(column_name), dts[0], precision, scale)
		else:
			spec = "%s %s" % (self.quoted(column_name), dts[0])
		if not is_nullable:
			spec += " NOT NULL"
		return spec

# Create a DbType object for each DBMS supported by execsql.

dbt_postgres = DbType("PostgreSQL")
dbt_postgres.name_datatype(DT_TimestampTZ, "timestamp with time zone")
dbt_postgres.name_datatype(DT_Timestamp, "timestamp")
dbt_postgres.name_datatype(DT_Date, "date")
dbt_postgres.name_datatype(DT_Time, "time")
dbt_postgres.name_datatype(DT_Integer, "integer")
dbt_postgres.name_datatype(DT_Long, "bigint")
dbt_postgres.name_datatype(DT_Float, "double precision")
dbt_postgres.name_datatype(DT_Decimal, "numeric")
dbt_postgres.name_datatype(DT_Boolean, "boolean")
dbt_postgres.name_datatype(DT_Character, "character", True)
dbt_postgres.name_datatype(DT_Varchar, "character varying", True)
dbt_postgres.name_datatype(DT_Text, "text")
dbt_postgres.name_datatype(DT_Binary, "bytea")

dbt_sqlite = DbType("SQLite")
dbt_sqlite.name_datatype(DT_TimestampTZ, "TEXT")
dbt_sqlite.name_datatype(DT_Timestamp, "TEXT")
dbt_sqlite.name_datatype(DT_Date, "TEXT")
dbt_sqlite.name_datatype(DT_Time, "TEXT")
dbt_sqlite.name_datatype(DT_Integer, "INTEGER")
dbt_sqlite.name_datatype(DT_Long, "BIGINT")
dbt_sqlite.name_datatype(DT_Float, "REAL")
dbt_sqlite.name_datatype(DT_Decimal, "NUMERIC")
dbt_sqlite.name_datatype(DT_Boolean, "INTEGER")
dbt_sqlite.name_datatype(DT_Character, "TEXT")
dbt_sqlite.name_datatype(DT_Varchar, "TEXT")
dbt_sqlite.name_datatype(DT_Text, "TEXT")
dbt_sqlite.name_datatype(DT_Binary, "BLOB")

dbt_sqlserver = DbType("SQL Server")
dbt_sqlserver.name_datatype(DT_TimestampTZ, "varchar", True)
dbt_sqlserver.name_datatype(DT_Timestamp, "datetime")
dbt_sqlserver.name_datatype(DT_Date, "date")
dbt_sqlserver.name_datatype(DT_Time, "time")
dbt_sqlserver.name_datatype(DT_Integer, "int")
dbt_sqlserver.name_datatype(DT_Long, "bigint")
dbt_sqlserver.name_datatype(DT_Float, "double precision")
dbt_sqlserver.name_datatype(DT_Decimal, "decimal")
dbt_sqlserver.name_datatype(DT_Boolean, "bit")
dbt_sqlserver.name_datatype(DT_Character, "character", True)
dbt_sqlserver.name_datatype(DT_Varchar, "varchar", True)
dbt_sqlserver.name_datatype(DT_Text, "varchar(max)")
dbt_sqlserver.name_datatype(DT_Binary, "varbinary(max)")

dbt_access = DbType("Access")
dbt_access.name_datatype(DT_TimestampTZ, "VARCHAR", True)
# Timestamp, date, and time types are all represented as varchar because
# the Access ODBC driver does not recognize None as representing a null
# value for these data types.
#dbt_access.name_datatype(DT_Timestamp, "DATETIME")
dbt_access.name_datatype(DT_Timestamp, "VARCHAR", True)
#dbt_access.name_datatype(DT_Date, "DATETIME", True)
dbt_access.name_datatype(DT_Date, "VARCHAR", True)
# See http://www.syware.com/support/customer_support/tip_of_the_month/tip_0802.php re the use of 1899-12-30 below.
#dbt_access.name_datatype(DT_Time, "DATETIME", conv_mod_fn = lambda x: datetime.datetime(1899, 12, 30, x.hour, x.minute, x.second, x.microsecond) if x is not None else "NULL")
#dbt_access.name_datatype(DT_Time, "DATETIME")
dbt_access.name_datatype(DT_Time, "VARCHAR", True)
dbt_access.name_datatype(DT_Integer, "LONG")
dbt_access.name_datatype(DT_Long, "DOUBLE")
dbt_access.name_datatype(DT_Float, "DOUBLE")
dbt_access.name_datatype(DT_Decimal, "NUMERIC")
dbt_access.dt_xlate[DT_Decimal] = DT_Float
dbt_access.name_datatype(DT_Boolean, "LONG")
dbt_access.name_datatype(DT_Character, "VARCHAR", True)
dbt_access.name_datatype(DT_Varchar, "VARCHAR", True)
dbt_access.name_datatype(DT_Text, "LONGTEXT")
dbt_access.name_datatype(DT_Binary, "LONGBINARY")

dbt_dsn = DbType("DSN")
# Because the most common use case expected for DSNs is to link to 32-bit Access
# on 64-bit Windows systems, the data type specifications are identical to those
# for Access
dbt_dsn.name_datatype(DT_TimestampTZ, "VARCHAR", True)
dbt_dsn.name_datatype(DT_Timestamp, "VARCHAR", True)
dbt_dsn.name_datatype(DT_Date, "VARCHAR", True)
dbt_dsn.name_datatype(DT_Time, "VARCHAR", True)
dbt_dsn.name_datatype(DT_Integer, "LONG")
dbt_dsn.name_datatype(DT_Long, "DOUBLE")
dbt_dsn.name_datatype(DT_Float, "DOUBLE")
dbt_dsn.name_datatype(DT_Decimal, "NUMERIC")
dbt_dsn.name_datatype(DT_Boolean, "LONG")
dbt_dsn.name_datatype(DT_Character, "VARCHAR", True)
dbt_dsn.name_datatype(DT_Varchar, "VARCHAR", True)
dbt_dsn.name_datatype(DT_Text, "LONGTEXT")
dbt_dsn.name_datatype(DT_Binary, "LONGBINARY")

dbt_mysql = DbType("MySQL")
dbt_mysql.name_datatype(DT_TimestampTZ, "varchar", True, "char")
dbt_mysql.name_datatype(DT_Timestamp, "datetime", conv_mod_fn=lambda x: unicode(x) if x is not None else u'')
dbt_mysql.name_datatype(DT_Date, "date", conv_mod_fn=lambda x: unicode(x) if x is not None else u'')
dbt_mysql.name_datatype(DT_Time, "time")
dbt_mysql.name_datatype(DT_Integer, "integer", False, "signed integer")
dbt_mysql.name_datatype(DT_Long, "bigint", False, "signed integer")
dbt_mysql.name_datatype(DT_Float, "double precision", False, "binary")
dbt_mysql.name_datatype(DT_Decimal, "numeric")
dbt_mysql.name_datatype(DT_Boolean, "boolean", False, "binary", conv_mod_fn=lambda x: int(x) if x is not None else None)
dbt_mysql.name_datatype(DT_Character, "character", True, "char")
dbt_mysql.name_datatype(DT_Varchar, "character varying", True, "char")
dbt_mysql.name_datatype(DT_Text, "longtext", False, "char")
dbt_mysql.name_datatype(DT_Binary, "longblob", False, "binary")

dbt_firebird = DbType("Firebird")
dbt_firebird.name_datatype(DT_TimestampTZ, "CHAR", True)
dbt_firebird.name_datatype(DT_Timestamp, "TIMESTAMP")
dbt_firebird.name_datatype(DT_Date, "DATE")
dbt_firebird.name_datatype(DT_Time, "TIME")
dbt_firebird.name_datatype(DT_Integer, "INTEGER")
dbt_firebird.name_datatype(DT_Long, "BIGINT")
dbt_firebird.name_datatype(DT_Float, "DOUBLE PRECISION")
dbt_firebird.name_datatype(DT_Decimal, "NUMERIC")
dbt_firebird.name_datatype(DT_Boolean, "INTEGER", conv_mod_fn=lambda x: int(x) if x is not None else None)
dbt_firebird.name_datatype(DT_Character, "CHAR", True)
dbt_firebird.name_datatype(DT_Varchar, "VARCHAR", True)
dbt_firebird.name_datatype(DT_Text, "BLOB")
dbt_firebird.name_datatype(DT_Binary, "BLOB")

# End of database types.
#===============================================================================================


#===============================================================================================
#-----  COLUMNS AND TABLES

class ColumnError(Exception):
	def __init__(self, errmsg):
		self.value = errmsg
	def __repr__(self):
		return u"ColumnError(%r)" % self.value
	def __str__(self):
		return repr(self.value)

class Column(object):
	# Column objects are used to compile information about the data types that a set of data
	# values may match.  A Column object is intended to be used to identify the data type of a column when
	# scanning a data stream (such as a CSV file) to create a new data table.
	class Accum(object):
		# Accumulates the count of matches for each data type, plus the maximum length if appropriate.
		def __init__(self, data_type_obj):
			self.dt = data_type_obj
			self.failed = False
			self.count = 0
			self.maxlen = 0
			self.varlen = False
			self.maxprecision = None
			self.scale = None
			self.varscale = False
		def __repr__(self):
			return "Data type %s; failed=%s; count=%d; maxlen=%d; varlen=%s, precision=%s, scale=%s, varscale=%s" % \
				(self.dt.data_type_name, self.failed, self.count, self.maxlen, self.varlen, self.maxprecision, self.scale, self.varscale)
		def check(self, datavalue):
			# datavalue must be non-null
			if not self.failed:
				is_match = self.dt.matches(datavalue)
				if is_match:
					self.count += 1
					if isinstance(datavalue, basestring):
						vlen = len(datavalue)
					else:
						# This column may turn out to have to be text, so we need the maximum length
						# of any data value when represented as text.
						vlen = len(unicode(datavalue))
					if self.maxlen > 0 and vlen != self.maxlen:
						self.varlen = True
					if vlen > self.maxlen:
						self.maxlen = vlen
					if self.dt.precision and self.dt.scale:
						self.maxprecision = max(self.dt.precision, self.maxprecision)
						if self.scale is None:
							self.scale = self.dt.scale
						else:
							if self.dt.scale != self.scale:
								self.varscale = True
								self.failed = True
				else:
					self.failed = True
	def __init__(self, colname):
		if not colname:
			raise ErrInfo(type="error", other_msg="No column name is specified for a new column object to characterize a data source.")
		self.name = colname.strip()
		# The rowcount for a column may not match the data rows read from the file if some data rows are short,
		# and not all columns are represented.
		self.rowcount = 0
		# Counts of data values (rows) matching each data type.
		self.nullrows = 0
		# The list of accumulators of matching rows must be in order from most specific data type to
		# least specific data type.  After a set of data has been evaluated, the first accumulator
		# in this list that matches all data values (i.e., Accum.count == self.rowcount - self.nullrows),
		# and for which the variable length specification matches, should be identified as the matching data type.
		self.accums = (self.Accum(DT_TimestampTZ()), self.Accum(DT_Timestamp()), self.Accum(DT_Date()), self.Accum(DT_Time()),
					self.Accum(DT_Boolean()), self.Accum(DT_Integer()), self.Accum(DT_Long()), 
					self.Accum(DT_Decimal()), 
					self.Accum(DT_Float()), self.Accum(DT_Character()), self.Accum(DT_Varchar()), self.Accum(DT_Text()), 
					self.Accum(DT_Binary()))
		# The data type of this column can be evaluated at any time (using column_type()), but because
		# it is a potentially expensive step, after it's done the result is saved.  The result is invalidated
		# if more data are evaluated.
		self.dt_eval = False
		# self.dt is a tuple of: 0: the column name; 1: the data type class; 2: the maximum length or None if NA;
		# 3; a boolean indicating whether any values were null; 4: the precision or None if NA;
		# 5: the scale or None if NA.  The type and order of these values matches the arguments to DbType().column_spec().
		self.dt = (None, None, None, None, None, None)
	def __repr__(self):
		return u"Column(%r)" % self.name
	def eval_types(self, column_value):
		# Evaluate which data type(s) the value matches, and increment the appropriate counter(s).
		self.dt_eval = False
		self.rowcount += 1
		if column_value is None or (isinstance(column_value, basestring) and len(column_value) == 0):
			self.nullrows += 1
			return
		for dt in self.accums:
			dt.check(column_value)
	def column_type(self):
		# Return the type of this column, consisting of a tuple consisting of four items:
		#	the column name,
		#	the data type *class*,
		#	the maximum length or None if NA,
		#	a boolean indicating whether any values were null.
		#	an integer indicating the precision if this is numeric, or None.
		#	an integer indicating the scale if this is numeric, or None.
		# Note that the type and order of these values matches the arguments to DbType().column_spec().
		if self.dt_eval:
			return self.dt
		sel_type = None		# Will be set to an Accum instance.
		if self.nullrows == self.rowcount:
			sel_type = self.Accum(DT_Text())
		else:
			for ac in self.accums:
				if (not ac.failed) and (ac.count == self.rowcount - self.nullrows):
					if ac.dt.lenspec:
						if ac.dt.varlen:
							sel_type = ac
							break
						else:
							if not ac.varlen:
								sel_type = ac
								break
					else:
						if ac.dt.precspec:
							if ac.dt.precision is not None and ac.dt.scale is not None:
								sel_type = ac
								break
						else:
							sel_type = ac
							break
			else:
				raise ColumnError("Could not determine data type for column %s" % self.name)
		self.dt = (self.name,
			sel_type.dt.__class__,
			None if not sel_type.dt.lenspec else ac.maxlen,
			self.nullrows > 0,
			sel_type.maxprecision,
			sel_type.scale)
		self.dt_eval = True
		return self.dt


class DataTableError(Exception):
	def __init__(self, errmsg):
		self.value = errmsg
	def __repr__(self):
		return u"DataTableError(%s)" % self.value
	def __str__(self):
		return repr(self.value)


class DataTable(object):
	def __init__(self, column_names, rowsource):
		self.inputrows = 0		# Total number of rows in the row source.
		self.datarows = 0		# Number of non-empty rows (with data values).
		self.shortrows = 0		# Number of rows without as many data values as column names.
		self.cols = []			# List of Column objects.
		for n in column_names:
			self.cols.append(Column(n))
		# Read and evaluate columns in the rowsource until done (or until an error).
		for datarow in rowsource:
			self.inputrows += 1
			dataitems = len(datarow)
			if dataitems > 0:
				self.datarows += 1
				chkcols = len(self.cols)
				if dataitems < chkcols:
					self.shortrows += 1
					chkcols = len(datarow)
				else:
					if dataitems > chkcols:
						raise DataTableError("Too many columns (%d) on data row %d" % (dataitems, self.inputrows))
				for i in range(chkcols):
					self.cols[i].eval_types(datarow[i])
		for col in self.cols:
			col.column_type()
	def __repr__(self):
		return u"DataTable(%s, rowsource)" %  [col.name for col in self.cols]
	def column_declarations(self, database_type):
		# Returns a list of column specifications.
		spec = []
		for col in self.cols:
			spec.append(database_type.column_spec(*col.column_type()))
		return spec
	def create_table(self, database_type, schemaname, tablename, pretty=False):
		tb = "%s.%s" % (database_type.quoted(schemaname), database_type.quoted(tablename)) if schemaname else database_type.quoted(tablename)
		if pretty:
			return u"CREATE TABLE %s (\n    %s\n    );" % (tb, u",\n    ".join(self.column_declarations(database_type)))
		else:
			return u"CREATE TABLE %s ( %s );" % (tb, u", ".join(self.column_declarations(database_type)))

# End of column and table class definitions.
#===============================================================================================


#===============================================================================================
#-----  DATABASE CONNECTIONS

class DatabaseNotImplementedError(Exception):
	def __init__(self, db_name, method):
		self.db_name = db_name
		self.method = method
	def __repr__(self):
		return u"DatabaseNotImplementedError(%r, %r)" % (self.db_name, self.method)
	def __str__(self):
		return "Method %s is not implemented for database %s" % (self.method, self.db_name)


#class DictRows(object):
#	def __init__(self, cursor, encoding):
#		self.headers = [d[0] for d in cursor.description]
#		self.curs = cursor
#		self.encoding = encoding
#		self.dict = None
#	def __iter__(self):
#		return self
#	def next(self):
#		row = self.curs.fetchone()
#		if row:
#			r = [c.decode(self.encoding) if isinstance(c, basestring) else c for c in row]
#			self.dict = dict(zip(self.headers, r))
#			return self.dict
#		else:
#			raise StopIteration

class Database(object):
	dt_cast = {int: int, long: long, float: float, str: str, unicode: unicode,
				bool: DT_Boolean().from_data,
				datetime.datetime: DT_Timestamp().from_data,
				datetime.date: DT_Date().from_data,
				bytearray: bytearray}
	def __init__(self, server_name, db_name, user_name=None, need_passwd=None, port=None, encoding=None):
		self.type = None
		self.server_name = server_name
		self.db_name = db_name
		self.user = user_name
		self.need_passwd = need_passwd
		self.password = None
		self.port = port
		self.encoding = encoding
		self.paramstr = '?'
		self.conn = None
		self.autocommit = True
	def __repr__(self):
		return u"Database(%r, %r, %r, %r, %r, %r)" % (self.server_name, self.db_name, self.user,
				self.need_passwd, self.port, self.encoding)
	def name(self):
		if self.server_name:
			return "%s(server %s; database %s)" % (self.type.dbms_id, self.server_name, self.db_name)
		else:
			return "%s(file %s)" % (self.type.dbms_id, self.db_name)
	def open_db(self):
		raise DatabaseNotImplementedError(self.name(), 'open_db')
	def cursor(self):
		if self.conn is None:
			self.open_db()
		return self.conn.cursor()
	def close(self):
		if self.conn:
			if not self.autocommit:
				exec_log.log_status_info(u"Closing %s when AUTOCOMMIT is OFF; transactions may not have completed." % self.name())
			self.conn.close()
			self.conn = None
	def execute(self, sql):
		# A shortcut to self.cursor().execute() that handles encoding.
		global subvars
		if type(sql) in (tuple, list):
			sql = u" ".join(sql)
		try:
			curs = self.cursor()
			if self.encoding:
				curs.execute(sql.encode(self.encoding))
			else:
				curs.execute(sql)
			subvars.add_substitution("$LAST_ROWCOUNT", curs.rowcount)
		except Exception as e:
			try:
				self.rollback()
			except:
				pass
			raise e
	def exec_cmd(self, querycommand):
		raise DatabaseNotImplementedError(self.name(), 'exec_cmd')
	def autocommit_on(self):
		self.autocommit = True
	def autocommit_off(self):
		self.autocommit = False
	def commit(self):
		if self.conn and self.autocommit:
			self.conn.commit()
	def rollback(self):
		if self.conn:
			self.conn.rollback()
	def schema_qualified_table_name(self, schema_name, table_name):
		table_name = self.type.quoted(table_name)
		if schema_name:
			schema_name = self.type.quoted(schema_name)
			return u'%s.%s' % (schema_name, table_name)
		return table_name
	def select_data(self, sql):
		# Returns the results of the sql select statement as unicode.
		curs = self.cursor()
		try:
			curs.execute(sql)
		except:
			self.rollback()
			raise
		subvars.add_substitution("$LAST_ROWCOUNT", curs.rowcount)
		rows = curs.fetchall()
		return [d[0] for d in curs.description], rows
	def select_rowsource(self, sql):
		# Return 1) a list of column names as unicode, and 2) an iterable that yields rows.
		curs = self.cursor()
		try:
			curs.execute(sql)
		except:
			self.rollback()
			raise
		subvars.add_substitution("$LAST_ROWCOUNT", curs.rowcount)
		def decode_row():
			row = curs.fetchone()
			if row:
				if self.encoding:
					return [c.decode(self.encoding) if isinstance(c, basestring) else c for c in row]
				else:
					return row
			else:
				return None
		return [unicode(d[0]) for d in curs.description], iter(decode_row, None)
	def select_rowdict(self, sql):
		# Return an iterable that yields dictionaries of row data
		curs = self.cursor()
		try:
			curs.execute(sql)
		except:
			self.rollback()
			raise
		subvars.add_substitution("$LAST_ROWCOUNT", curs.rowcount)
		hdrs = [unicode(d[0]) for d in curs.description]
		def dict_row():
			row = curs.fetchone()
			if row:
				if self.encoding:
					r = [c.decode(self.encoding) if isinstance(c, basestring) else c for c in row]
				else:
					r = row
				return dict(zip(hdrs, r))
			else:
				return None
		return hdrs, iter(dict_row, None)
	def schema_exists(self, schema_name):
		curs = self.cursor()
		curs.execute(u"SELECT schema_name FROM information_schema.schemata WHERE schema_name = '%s';" % schema_name)
		rows = curs.fetchall()
		curs.close()
		return len(rows) > 0
	def table_exists(self, table_name, schema_name=None):
		curs = self.cursor()
		sql = "select table_name from information_schema.tables where table_name = '%s'%s;" % (table_name, "" if not schema_name else " and table_schema='%s'" % schema_name)
		try:
			curs.execute(sql)
		except ErrInfo:
			raise
		except:
			self.rollback()
			raise ErrInfo(type="db", command_text=sql, exception_msg=exception_desc(),
								other_msg=u"Failed test for existence of table %s in %s" % (table_name, self.name()))
		rows = curs.fetchall()
		curs.close()
		return len(rows) > 0
	def column_exists(self, table_name, column_name, schema_name=None):
		curs = self.cursor()
		sql = "select column_name from information_schema.columns where table_name='%s'%s and column_name='%s';" % (table_name, "" if not schema_name else " and table_schema='%s'" % schema_name, column_name)
		try:
			curs.execute(sql)
		except ErrInfo:
			raise
		except:
			self.rollback()
			if working_script:
				script, line_no = working_script.current_script_line()
			else:
				script = None
				line_no = None
			raise ErrInfo(type="db", command_text=sql, exception_msg=exception_desc(),
							other_msg=u"Failed test for existence of column %s in table %s of %s" % (column_name, table_name, self.name()))
		rows = curs.fetchall()
		curs.close()
		return len(rows) > 0
	def table_columns(self, table_name, schema_name=None):
		curs = self.cursor()
		sql = "select column_name from information_schema.columns where table_name='%s'%s order by ordinal_position;" % (table_name, "" if not schema_name else " and table_schema='%s'" % schema_name)
		try:
			curs.execute(sql)
		except ErrInfo:
			raise
		except:
			self.rollback()
			raise ErrInfo(type="db", command_text=sql, exception_msg=exception_desc(),
							other_msg=u"Failed to get column names for table %s of %s" % (table_name, self.name()))
		rows = curs.fetchall()
		curs.close()
		return [row[0] for row in rows]
	def view_exists(self, view_name, schema_name=None):
		curs = self.cursor()
		sql = "select table_name from information_schema.views where table_name = '%s'%s;" % (view_name, "" if not schema_name else " and table_schema='%s'" % schema_name)
		try:
			curs.execute(sql)
		except ErrInfo:
			raise
		except:
			self.rollback()
			if working_script:
				script, line_no = working_script.current_script_line()
			else:
				script = None
				line_no = None
			raise ErrInfo(type="db", command_text=sql, exception_msg=exception_desc(),
							other_msg=u"Failed test for existence of view %s in %s" % (view_name, self.name()),
							script_file=script, script_line_no=line_no)
		rows = curs.fetchall()
		curs.close()
		return len(rows) > 0
	def drop_table(self, tablename):
		# The 'tablename' argument should be schema-qualified and quoted as necessary.
		self.execute(u"drop table if exists %s cascade;" % tablename)
		self.commit()
	def populate_table(self, schema_name, table_name, rowsource, column_list, tablespec_src):
		# The rowsource argument must be a generator yielding a list of values for the columns of the table.
		# The column_list argument must an iterable containing column names.  This may be a subset of
		# the names of columns in the rowsource.
		#
		sq_name = self.schema_qualified_table_name(schema_name, table_name)
		# Check that the specified column names are in the input data.
		tablespec = tablespec_src()
		ts_colnames = [col.name for col in tablespec.cols]
		src_missing_cols = [col for col in column_list if col not in ts_colnames]
		if len(src_missing_cols) > 0:
			raise ErrInfo(type="error", other_msg="Data source is missing the following columns: %s." % ", ".join(src_missing_cols))
		# Create a list of selected columns in the order in which they appear in the rowsource,
		# and a list of Booleans indicating whether each column in the rowsource should be included.
		sel_cols = [col for col in ts_colnames if col in column_list]
		incl_col = [col in column_list for col in ts_colnames]
		# Type conversion functions for the rowsource.
		type_objs = [col.column_type()[1]() for col in tablespec.cols]
		type_mod_fn = [self.type.dialect[col.column_type()[1]][3] for col in tablespec.cols]
		# Construct INSERT statement.
		columns = [self.type.quoted(col) for col in sel_cols]
		colspec = ",".join(columns)
		paramspec = ",".join([self.paramstr for c in columns])
		sql = u"insert into %s (%s) values (%s);" % (sq_name, colspec, paramspec)
		def load_line(line):
			if len(line) > len(ts_colnames):
				raise ErrInfo(type="error", other_msg="Too many data columns on line {%s}" % line)
			if len(line) == 1 and line[0] is None:
				return
			if not conf.empty_strings:
				# Replace all empty strings with None
				for i in range(len(line)):
					if line[i] == u'':
						line[i] = None
			lt = [type_objs[i].from_data(val) if val is not None else None for i, val in enumerate(line)]
			lt = [type_mod_fn[i](v) if type_mod_fn[i] else v for i, v in enumerate(lt)]
			l = []
			for i, v in enumerate(lt):
				if incl_col[i]:
					l.append(v)
			try:
				curs.execute(sql, tuple(l))
			except ErrInfo:
				raise
			except:
				self.rollback()
				raise ErrInfo(type="db", command_text=sql, exception_msg=exception_desc(), other_msg=u"Can't load data into table %s of %s from line {%s}" % (sq_name, self.name(), line))
		curs = self.cursor()
		for line in rowsource:
			load_line(line)
	def import_file(self, schema_name, table_name, csv_file_obj, skipheader):
		# Import a file to a table.  Columns must be compatible.
		if not self.table_exists(table_name, schema_name):
			raise ErrInfo(type="error", other_msg=u"Table doesn't exist for import of file to table %s; check that capitalization is consistent." % table_name)
		f = csv_file_obj.reader()
		csv_cols = f.next()
		f.close()
		table_cols = self.table_columns(table_name, schema_name)
		global conf
		if conf.import_common_cols_only:
			import_cols = [col for col in csv_cols if col.lower() in [tc.lower() for tc in table_cols]]
		else:
			src_extra_cols = [col for col in csv_cols if col.lower() not in [tc.lower() for tc in table_cols]]
			if len(src_extra_cols) > 0:
				raise ErrInfo(type="error", other_msg=u"The input file %s has the following columns that are not in table %s: %s." % (csv_file_obj.csvfname, table_name, ", ".join(src_extra_cols)))
			import_cols = csv_cols
		def get_ts():
			if not get_ts.tablespec:
				get_ts.tablespec = csv_file_obj.data_table_def()
			return get_ts.tablespec
		get_ts.tablespec = None
		f = csv_file_obj.reader()
		f.next()
		self.populate_table(schema_name, table_name, f, import_cols, get_ts)

class AccessDatabase(Database):
	# Regex for the 'create temporary view' SQL extension
	temp_rx = re.compile(r'^\s*create(?:\s+or\s+replace)?(\s+temp(?:orary)?)?\s+(?:(view|query))\s+(\w+) as\s+', re.I)
	connection_strings = (
						"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=%s;",
						"DRIVER={Microsoft Access Driver (*.mdb)};DBQ=%s;",
						"Provider=Microsoft.ACE.OLEDB.15.0; Data Source=%s;",
						"Provider=Microsoft.ACE.OLEDB.12.0; Data Source=%s;"
						)
	def __init__(self, Access_fn, need_passwd=False, user_name=None, encoding=None, password=None):
		global pyodbc
		global win32com
		try:
			import win32com.client
		except:
			fatal_error(u"The win32com module is required.  See http://sourceforge.net/projects/pywin32/")
		try:
			import pyodbc
		except:
			fatal_error(u"The pyodbc module is required.  See http://github.com/mkleehammer/pyodbc")
		self.type = dbt_access
		self.server_name = None
		self.db_name = unicode(Access_fn)
		self.user = user_name
		self.need_passwd = need_passwd
		self.password = password
		self.encoding = encoding or 'windows_1252'
		self.dao_conn = None
		self.conn = None				# ODBC connection
		self.paramstr = '?'
		self.dt_cast[datetime.date] = self.as_datetime
		self.dt_cast[datetime.datetime] = self.as_datetime
		self.dt_cast[int] = self.int_or_bool
		self.last_dao_time = 0.0
		self.temp_query_names = []
		self.autocommit = True
		# Create the DAO connection
		self.open_dao()
		# Create the ODBC connection
		self.open_db()
	def __repr__(self):
		return u"AccessDatabase(%s, %s)" % (self.db_name, self.encoding)
	def open_db(self):
		# Open an ODBC connection.
		if self.conn is not None:
			self.conn.close()
			self.conn = None
		if self.need_passwd and self.user and self.password is None:
			self.password = get_password("MS-Access", self.db_name, self.user)
		connected = False
		db_name = os.path.abspath(self.db_name)
		for cs in self.connection_strings:
			if self.need_passwd:
				connstr = "%s Uid=%s; Pwd=%s;" % (cs % db_name, self.user, self.password)
			else:
				connstr = cs % db_name
			try:
				self.conn = pyodbc.connect(connstr)
			except:
				pass
			else:
				connected = True
				break
		if not connected:
			raise ErrInfo(type="exception", exception_msg=exception_desc(), other_msg=u"Can't open Access database %s using ODBC" % self.db_name)
	def open_dao(self):
		if self.dao_conn is not None:
			self.dao_conn.Close
			self.dao_conn = None
		if self.need_passwd and self.user and self.password is None:
			self.password = get_password("MS-Access", self.db_name, self.user)
		dao_engines = ('DAO.DBEngine.120', 'DAO.DBEngine.36')
		connected = False
		for engine in dao_engines:
			try:
				daoEngine = win32com.client.Dispatch(engine)
				if self.need_passwd:
					self.dao_conn = daoEngine.OpenDatabase(self.db_name, False, False, "MS Access;UID=%s;PWD=%s;" % (self.user, self.password))
				else:
					self.dao_conn = daoEngine.OpenDatabase(self.db_name)
			except:
				pass
			else:
				connected = True
				break
		if not connected:
			raise ErrInfo(type="exception", exception_msg=exception_desc(), other_msg=u"Can't open Access database %s using any of the following DAO engines: %s." % (self.db_name, ", ".join(dao_engines)))
	def exec_dao(self, querystring):
		# Execute a query using DAO.
		if self.dao_conn is None:
			self.open_dao()
		self.dao_conn.Execute(querystring)
		self.last_dao_time = time.time()
	def close(self):
		if self.dao_conn:
			for qn in self.temp_query_names:
				try:
					self.dao_conn.QueryDefs.Delete(qn)
					self.last_dao_time = time.time()
				except:
					pass
			self.dao_conn = None
		if self.conn:
			self.conn.close()
			self.conn = None
	def dao_flush_check(self):
		if time.time() - self.last_dao_time < 5.0:
			time.sleep(5 - (time.time() - self.last_dao_time))
	def execute(self, sqlcmd):
		# A shortcut to self.cursor().execute() that handles encoding and that
		# ensures that at least 5 seconds have passed since the last DAO command,
		# to allow Jet's read buffer to be flushed (see https://support.microsoft.com/en-us/kb/225048).
		# This also handles the 'CREATE TEMPORARY QUERY' extension to Access.
		# For Access, commands in a tuple (batch) are executed singly.
		def exec1(sql):
			tqd = self.temp_rx.match(sql)
			if tqd:
				#qn = tqd.group(3).encode(self.encoding)
				qn = tqd.group(3)
				qsql = sql[tqd.end():].encode(self.encoding)
				if self.dao_conn is None:
					self.open_dao()
				try:
					self.dao_conn.QueryDefs.Delete(qn)
				except:
					# If we can't delete it because it doesn't exist, that's fine.
					pass
				self.dao_conn.CreateQueryDef(qn, qsql)
				self.last_dao_time = time.time()
				if self.conn is not None:
					self.conn.close()
					self.conn = None
				if tqd.group(1) and tqd.group(1).strip().lower()[:4] == 'temp':
					if not qn in self.temp_query_names:
						self.temp_query_names.append(qn)
			else:
				self.dao_flush_check()
				curs = self.cursor()
				curs.execute(sql.encode(self.encoding))
				subvars.add_substitution("$LAST_ROWCOUNT", curs.rowcount)
		if type(sqlcmd) in (list, tuple):
			for sql in sqlcmd:
				exec1(sql)
		else:
			exec1(sqlcmd)
	def exec_cmd(self, querycommand):
		self.exec_dao(querycommand.encode(self.encoding))
	def select_data(self, sql):
		# Returns the results of the sql select statement as unicode.
		# The Access driver returns data as unicode, so no decoding is necessary.
		self.dao_flush_check()
		curs = self.cursor()
		curs.execute(sql)
		rows = curs.fetchall()
		return [unicode(d[0]) for d in curs.description], rows
	def select_rowsource(self, sql):
		# Return 1) a list of column names as unicode, and 2) an iterable that yields rows.
		self.dao_flush_check()
		curs = self.cursor()
		curs.execute(sql)
		subvars.add_substitution("$LAST_ROWCOUNT", curs.rowcount)
		return [unicode(d[0]) for d in curs.description], iter(curs.fetchone, None)
	def select_rowdict(self, sql):
		# Return an iterable that yields dictionaries of row data.
		self.dao_flush_check()
		curs = self.cursor()
		curs.execute(sql)
		subvars.add_substitution("$LAST_ROWCOUNT", curs.rowcount)
		headers = [unicode(d[0]) for d in curs.description]
		def dict_row():
			row = curs.fetchone()
			if row:
				if self.encoding:
					r = [c.decode(self.encoding) if isinstance(c, basestring) else c for c in row]
				else:
					r = row
				return dict(zip(headers, r))
			else:
				return None
		return headers, iter(dict_row, None)
	def table_exists(self, table_name, schema_name=None):
		self.dao_flush_check()
		curs = self.cursor()
		try:
			sql = "select Name from MSysObjects where Name='%s' And Type In (1,4,6);" % table_name
			curs.execute(sql)
		except ErrInfo:
			raise
		except:
			raise ErrInfo(type="db", command_text=sql, exception_msg=exception_desc(), other_msg=u"Failure on test for existence of Access table %s" % table_name)
		rows = curs.fetchall()
		return len(rows) > 0
	def column_exists(self, table_name, column_name, schema_name=None):
		self.dao_flush_check()
		curs = self.cursor()
		sql = "select top 1 %s from %s;" % (column_name, table_name)
		try:
			curs.execute(sql)
		except:
			return False
		return True
	def table_columns(self, table_name, schema_name=None):
		self.dao_flush_check()
		curs = self.cursor()
		curs.execute("select top 1 * from %s;" % table_name)
		return [d[0] for d in curs.description]
	def view_exists(self, view_name, schema_name=None):
		self.dao_flush_check()
		curs = self.cursor()
		try:
			sql = "select Name from MSysObjects where Name='%s' And Type = 5;" % view_name
			curs.execute(sql)
		except ErrInfo:
			raise
		except:
			raise ErrInfo(type="db", command_text=sql, exception_msg=exception_desc(), other_msg=u"Test for existence of Access view/query %s" % view_name)
		rows = curs.fetchall()
		return len(rows) > 0
	def schema_exists(self, schema_name):
		return False
	def drop_table(self, tablename):
		self.dao_flush_check()
		tablename = self.type.quoted(tablename)
		self.execute(u"drop table %s;" % tablename)
	def as_datetime(self, val):
		if val is None or (isinstance(val, basestring) and len(val) == 0):
			return None
		if type(val) == datetime.date or type(val) == datetime.datetime or type(val) == datetime.time:
			return val
		else:
			try:
				v = DT_Timestamp().from_data(val)
			except DataTypeError:
				try:
					v = DT_Date().from_data(val)
				except DataTypeError:
					# If this generates an exception, let it go up to get caught.
					v = DT_Time().from_data(val)
					n = datetime.datetime.now()
					v = datetime.datetime(n.year, n.month, n.day, v.hour, v.minute, v.second, v.microsecond)
			except:
				raise
			return v
	def int_or_bool(self, val):
		# Because Booleans are stored as integers in Access (at least, if execsql
		# creates the table), we have to recognize Boolean values as legitimate
		# integers.
		if val is None or (isinstance(val, basestring) and len(val) == 0):
			return None
		try:
			v = int(val)
		except:
			try:
				b = DT_Boolean().from_data(val)
			except:
				# Re-trigger the exception on conversion to int
				v = int(val)
			if b is None:
				return None
			return 1 if b else 0
		return v


class DsnDatabase(Database):
	# There's no telling what is actually connected to a DSN, so this uses
	# generic Database methods almost exclusively.  Only 'exec_cmd()' is
	# overridden, and that uses the method for SQL Server because the DAO
	# methods used for Access may not be appropriate for whatever is actually
	# connected to the DSN.
	def __init__(self, dsn_name, user_name, need_passwd=False, encoding=None, password=None):
		global pyodbc
		try:
			import pyodbc
		except:
			fatal_error(u"The pyodbc module is required.  See http://github.com/mkleehammer/pyodbc")
		self.type = dbt_dsn
		self.server_name = None
		self.db_name = dsn_name
		self.user = user_name
		self.need_passwd = need_passwd
		self.password = password
		self.port = None
		self.encoding = encoding
		self.paramstr = '?'
		self.conn = None
		self.autocommit = True
		self.open_db()
	def __repr__(self):
		return u"DsnDatabase(%r, %r, %r, %r, %r)" % (self.db_name, self.user,
				self.need_passwd, self.port, self.encoding)
	def open_db(self):
		# Open an ODBC connection using a DSN.
		if self.conn is not None:
			self.conn.close()
			self.conn = None
		if self.need_passwd and self.user and self.password is None:
			self.password = get_password("DSN", self.db_name, self.user)
		cs = "DSN=%s;"
		try:
			if self.need_passwd:
				self.conn = pyodbc.connect("%s Uid=%s; Pwd=%s;" % (cs % self.db_name, self.user, self.password))
			else:
				self.conn = pyodbc.connect(cs % self.db_name)
		except:
			excdesc = exception_desc()
			if "Optional feature not implemented" in excdesc:
				try:
					if self.need_passwd:
						self.conn = pyodbc.connect("%s Uid=%s; Pwd=%s;" % (cs % self.db_name, self.user, self.password), autocommit=True)
					else:
						self.conn = pyodbc.connect(cs % self.db_name, autocommit=True)
				except:
					raise ErrInfo(type="exception", exception_msg=exception_desc(), other_msg=u"Can't open DSN database %s using ODBC" % self.db_name)
			else:
				raise ErrInfo(type="exception", exception_msg=excdesc, other_msg=u"Can't open DSN database %s using ODBC" % self.db_name)
	def exec_cmd(self, querycommand):
		# The querycommand must be a stored procedure
		curs = self.cursor()
		cmd = u"execute %s;" % querycommand
		try:
			curs.execute(cmd.encode(self.encoding))
			subvars.add_substitution("$LAST_ROWCOUNT", curs.rowcount)
		except:
			self.rollback()
			raise


class SqlServerDatabase(Database):
	def __init__(self, server_name, db_name, user_name, need_passwd=False, port=1433, encoding='latin1', password=None):
		global pyodbc
		try:
			import pyodbc
		except:
			fatal_error(u"The pyodbc module is required.  See http://github.com/mkleehammer/pyodbc")
		self.type = dbt_sqlserver
		self.server_name = unicode(server_name)
		self.db_name = db_name
		self.user = user_name
		self.need_passwd = need_passwd
		self.password = password
		self.port = port if port else 1433
		self.encoding = encoding or 'latin1'    # Default on installation of SQL Server
		self.paramstr = '?'
		self.conn = None
		self.autocommit = True
		self.open_db()
	def __repr__(self):
		return u"SqlServerDatabase(%r, %r, %r, %r, %r, %r)" % (self.server_name, self.db_name, self.user,
				self.need_passwd, self.port, self.encoding)
	def open_db(self):
		if self.conn is None:
			if self.user and self.need_passwd and not self.password:
				self.password = get_password("SQL Server", self.db_name, self.user, server_name=self.server_name)
			# Use pyodbc to connect.  Try different driver versions from newest to oldest.
			ssdrivers = ('ODBC Driver 13 for SQL Server', 'ODBC Driver 11 for SQL Server', 
				'SQL Server Native Client 11.0', 'SQL Server Native Client 10.0', 
				'SQL Native Client', 'SQL Server')
			for drv in ssdrivers:
				if self.user:
					if self.password:
						connstr = "DRIVER={%s};SERVER=%s;DATABASE=%s;Uid=%s;Pwd=%s" % (drv, self.server_name, self.db_name, self.user, self.password)
					else:
						connstr = "DRIVER={%s};SERVER=%s;DATABASE=%s;Uid=%s" % (drv, self.server_name, self.db_name, self.user)
				else:
					connstr = "DRIVER={%s};SERVER=%s;DATABASE=%s;Trusted_Connection=yes" % (drv, self.server_name, self.db_name)
				try:
					self.conn = pyodbc.connect(connstr)
				except:
					pass
				else:
					break
			if not self.conn:
				raise ErrInfo(type="error", other_msg=u"Can't open SQL Server database %s on %s" % (self.db_name, self.server_name))
			self.execute(u"SET ANSI_DEFAULTS ON;")
	def exec_cmd(self, querycommand):
		# The querycommand must be a stored procedure
		curs = self.cursor()
		cmd = u"execute %s;" % querycommand
		try:
			curs.execute(cmd.encode(self.encoding))
			subvars.add_substitution("$LAST_ROWCOUNT", curs.rowcount)
		except:
			self.rollback()
			raise
	def schema_exists(self, schema_name):
		curs = self.cursor()
		curs.execute(u"select * from sys.schemas where name = '%s';" % schema_name)
		rows = curs.fetchall()
		curs.close()
		return len(rows) > 0
	def drop_table(self, tablename):
		# SQL Server and Firebird will throw an error if there are foreign keys to the table.
		tablename = self.type.quoted(tablename)
		self.execute(u"drop table %s;" % tablename)
	def populate_table(self, schema_name, table_name, rowsource, column_list, tablespec_src):
		# The rowsource argument must be a generator yielding a list of values for the columns of the table.
		# The column_list argument must an iterable containing column names in the same order as produced by the rowsource.
		# The tablespec_src argument is a callback function to produce a DataTable object.
		sq_name = self.schema_qualified_table_name(schema_name, table_name)
		# Check that the specified column names are in the input data.
		tablespec = tablespec_src()
		ts_colnames = [col.name for col in tablespec.cols]
		src_missing_cols = [col for col in column_list if col not in ts_colnames]
		if len(src_missing_cols) > 0:
			raise ErrInfo(type="error", other_msg="Data source is missing the following columns: %s." % ", ".join(src_missing_cols))
		# Create a list of selected columns in the order in which they appear in the rowsource,
		# and a list of Booleans indicating whether each column in the rowsource should be included.
		sel_cols = [col for col in ts_colnames if col in column_list]
		incl_col = [col in column_list for col in ts_colnames]
		colsel = ",".join([self.type.quoted(c) for c in sel_cols])
		try:
			curs = self.cursor()
			sql = "select top 1 %s from %s;" % (colsel, sq_name)
			curs.execute(sql)
		except ErrInfo:
			raise
		except:
			self.rollback()
			raise ErrInfo(type="db", command_text=sql, exception_msg=exception_desc(), other_msg=u"Can't get column information in table %s for columns %s." % (sq_name, colsel))
		columns = [self.type.quoted(d) for d in sel_cols]
		paramspec = ",".join(['?' for c in sel_cols])
		type_funcs = [self.dt_cast[d[1]] for d in curs.description]
		sql = "insert into %s (%s) values (%s);" % (sq_name, colsel, paramspec)
		curs = self.cursor()
		for line in rowsource:
			if len(line) > len(columns):
				raise ErrInfo(type="error", other_msg="Too many data columns on line {%s}" % line)
			if len(line) == 1 and line[0] is None:
				continue
			if not conf.empty_strings:
				# Replace empty strings with None
				for i in range(len(line)):
					if line[i] == u'':
						line[i] = None
			# Get data for only selected columns
			linedata = []
			for i,v in enumerate(line):
				if incl_col[i]:
					linedata.append(v)
			# Convert data types
			tr = zip(linedata, type_funcs)
			lt = [col[1](col[0]) if col[0] is not None else None for col in tr]
			try:
				curs.execute(sql, tuple(lt))
			except ErrInfo:
				raise
			except:
				self.rollback()
				raise ErrInfo(type="db", command_text=sql, exception_msg=exception_desc(), other_msg=u"Can't load data into table %s from line {%s}" % (sq_name, line))
		#self.commit()


class PostgresDatabase(Database):
	def __init__(self, server_name, db_name, user_name, need_passwd=False, port=5432, new_db=False, encoding='UTF8', password=None):
		global psycopg2
		try:
			import psycopg2
		except:
			fatal_error(u"The psycopg2 module is required to connect to PostgreSQL.   See http://initd.org/psycopg/")
		self.type = dbt_postgres
		self.server_name = server_name
		self.db_name = db_name
		self.user = user_name
		self.need_passwd = need_passwd
		self.password = password
		self.port = port if port else 5432
		self.new_db = new_db
		self.encoding = encoding or 'UTF8'
		self.paramstr = '%s'
		self.conn = None
		self.autocommit = True
		self.open_db()
	def __repr__(self):
		return u"PostgresDatabase(%r, %r, %r, %r, %r, %r, %r)" % (self.server_name, self.db_name, self.user,
				self.need_passwd, self.port, self.new_db, self.encoding)
	def open_db(self):
		def db_conn(db, db_name):
			if db.user and db.password:
				return psycopg2.connect(host=str(db.server_name), database=str(db_name), port=db.port, user=unicode(db.user), password=unicode(db.password))
			else:
				return psycopg2.connect(host=str(db.server_name), database=db_name, port=db.port)
		def create_db(db):
			conn = db_conn(db, 'postgres')
			conn.autocommit = True
			curs = conn.cursor()
			curs.execute("create database %s encoding '%s';" % (db.db_name, db.encoding))
			conn.close()
		if self.conn is None:
			try:
				if self.user and self.need_passwd and not self.password:
					self.password = get_password("PostgreSQL", self.db_name, self.user, server_name=self.server_name)
				if self.new_db:
					create_db(self)
				self.conn = db_conn(self, self.db_name)
			except SystemExit:
				# If the user canceled the password prompt.
				raise
			except ErrInfo:
				raise
			except:
				msg = u"Failed to open PostgreSQL database %s on %s" % (self.db_name, self.server_name)
				raise ErrInfo(type="exception", exception_msg=exception_desc(), other_msg=msg)
			# (Re)set the encoding to match the database.
			self.encoding = self.conn.encoding
	def exec_cmd(self, querycommand):
		# The querycommand must be a stored function (/procedure)
		curs = self.cursor()
		cmd = u"select %s()" % querycommand
		try:
			curs.execute(cmd)
			subvars.add_substitution("$LAST_ROWCOUNT", curs.rowcount)
		except:
			self.rollback()
			raise
	def vacuum(self, argstring):
		self.commit()
		self.conn.set_session(autocommit=True)
		self.conn.cursor().execute("VACUUM %s;" % argstring)
		self.conn.set_session(autocommit=False)
	def import_file(self, schema_name, table_name, csv_file_obj, skipheader):
		# Import a file to a table.  Columns must be compatible.
		global conf
		sq_name = self.schema_qualified_table_name(schema_name, table_name)
		if not self.table_exists(table_name, schema_name):
			raise ErrInfo(type="error", other_msg=u"Table doesn't exist for import of file to table %s; check that capitalization is consistent." % sq_name)
		csv_file_obj.evaluate_line_format()
		# Create a comma-delimited list of column names in the input file.
		table_cols = self.table_columns(table_name, schema_name)
		data_table_cols = [d.lower() for d in table_cols]
		csv_file_cols = [ch.lower() for ch in csv_file_obj.column_headers()]
		if conf.import_common_cols_only:
			import_cols = [col for col in csv_file_cols if col in data_table_cols]
		else:
			unmatched_cols = list(set(csv_file_cols) - set(data_table_cols))
			if len(unmatched_cols) > 0:
				raise ErrInfo(type="error", other_msg=u"The input file %s has the following columns that are not in table %s: %s" % (csv_file_obj.csvfname, sq_name, ", ".join(unmatched_cols)))
			import_cols = csv_file_cols
		input_col_list = ",".join(import_cols)
		# If encodings match, use copy_expert.
		# If encodings don't match, and the file encoding isn't recognized by CSV, read as CSV.
		pg_encodings = ('big5', 'euc_cn', 'euc_jp', 'euc_jis_2004', 'euc_kr', 'euc_tw',
			'gb18030', 'gbk', 'iso_8859_5', 'iso_8859_6', 'iso_8859_7', 'iso_8859_8',	  
			'johab', 'koi8r', 'koi8u', 'latin1', 'latin2', 'latin3', 'latin4', 'latin5',
			'latin6', 'latin7', 'latin8', 'latin9', 'latin10', 'mule_internal', 'sjis',
			'shift_jis_2004', 'sql_ascii', 'uhc', 'utf8', 'win866', 'win874', 'win1250',
			'win1251', 'win1252', 'win1253', 'win1254', 'win1255', 'win1256', 'win1257',
			'win1258')
		enc_match = encodings_match(csv_file_obj.encoding, self.encoding)
		if (enc_match or csv_file_obj.encoding.lower() in pg_encodings) \
					and data_table_cols == csv_file_cols \
					and conf.empty_strings:
			# Use Postgres' COPY FROM method via psycopg2's copy_expert() method.
			curs = self.cursor()
			rf = csv_file_obj.open("rt")
			if skipheader:
				rf.next()
			# Copy_from() requires a delimiter, but if there is none, feed it an
			# ASCII unit separator, which, if it had been used for its intended purpose,
			# should have been identified as the delimiter, so presumably it has not been used.
			delim = csv_file_obj.delimiter if csv_file_obj.delimiter else chr(31)
			copy_cmd = "copy %s (%s) from stdin with (format csv, null '', delimiter '%s'" % (sq_name, input_col_list, delim)
			if csv_file_obj.quotechar:
				copy_cmd = copy_cmd + ", quote '%s'" % csv_file_obj.quotechar
			if not enc_match:
				copy_cmd = copy_cmd + ", encoding '%'" % csv_file_obj.encoding
			copy_cmd = copy_cmd + ")"
			try:
				curs.copy_expert(copy_cmd, rf, conf.import_buffer)
			except ErrInfo:
				raise
			except:
				self.rollback()
				raise ErrInfo(type="exception", exception_msg=exception_desc(), other_msg=u"Can't import from file to table %s" % sq_name)
		else:
			def load_line(line):
				if len(line) > len(csv_file_cols):
					raise ErrInfo(type="error", other_msg="Too many data columns on line {%s}" % line)
				if not conf.empty_strings:
					# Replace empty strings with None; psycopg2 passes empty strings in numeric columns to Postgres as strings, not None.
					for i in range(len(line)):
						if line[i] == u'':
							line[i] = None
				# Pad short line with nulls
				line.extend([None]*(len(import_cols)-len(line)))
				linedata = [line[ix] for ix in data_indexes]
				try:
					curs.execute(sql_template, linedata)
				except ErrInfo:
					raise
				except:
					self.rollback()
					raise ErrInfo(type="db", command_text=sql_template, exception_msg=exception_desc(), other_msg=u"Import from file into table %s, line {%s}" % (sq_name, line))
			data_indexes = [csv_file_cols.index(col) for col in import_cols]
			paramspec = ",".join(['%s']*len(import_cols))
			sql_template = u"insert into %s (%s) values (%s);" % (sq_name, input_col_list, paramspec)
			# Read as CSV
			f = csv_file_obj.reader()
			if skipheader:
				f.next()
			curs = self.cursor()
			for line in f:
				load_line(line)


class SQLiteDatabase(Database):
	def __init__(self, SQLite_fn):
		global sqlite3
		try:
			import sqlite3
		except:
			fatal_error(u"The sqlite3 module is required.")
		self.type = dbt_sqlite
		self.server_name = None
		self.db_name = SQLite_fn
		self.user = None
		self.need_passwd = False
		self.encoding = 'UTF-8'
		self.paramstr = '?'
		self.conn = None
		self.autocommit = True
		self.open_db()
	def __repr__(self):
		return u"SQLiteDabase(%r)" % self.db_name
	def open_db(self):
		if self.conn is None:
			try:
				self.conn = sqlite3.connect(self.db_name)
			except ErrInfo:
				raise
			except:
				raise ErrInfo(type="exception", exception_msg=exception_desc(), other_msg=u"Can't open SQLite database %s" % self.db_name)
		pragma_cols, pragma_data = self.select_data("pragma encoding;")
		self.encoding = pragma_data[0][0]
	def exec_cmd(self, querycommand):
		# SQLite does not support stored functions or views, so the querycommand
		# is treated as (and therefore must be) a view.
		curs = self.cursor()
		cmd = u"select * from %s;" % querycommand
		try:
			curs.execute(cmd.encode(self.encoding))
			subvars.add_substitution("$LAST_ROWCOUNT", curs.rowcount)
		except:
			self.rollback()
			raise
	def table_exists(self, table_name, schema_name=None):
		curs = self.cursor()
		sql = "select name from sqlite_master where type='table' and name='%s';" % table_name
		try:
			curs.execute(sql)
		except ErrInfo:
			raise
		except:
			self.rollback()
			raise ErrInfo(type="db", command_text=sql, exception_msg=exception_desc(), other_msg=u'Failed test for existence of SQLite table "%s";' % table_name)
		rows = curs.fetchall()
		return len(rows) > 0
	def column_exists(self, table_name, column_name, schema_name=None):
		curs = self.cursor()
		sql = "select %s from %s limit 1;" % (column_name, table_name)
		try:
			curs.execute(sql)
		except:
			return False
		return True
	def table_columns(self, table_name, schema_name=None):
		curs = self.cursor()
		sql = "select * from %s where 1=0;" % table_name
		try:
			curs.execute(sql)
		except ErrInfo:
			raise
		except:
			self.rollback()
			raise ErrInfo(type="db", command_text=sql, exception_msg=exception_desc(),
							other_msg=u"Failed to get column names for table %s of %s" % (table_name, self.name()))
		return [d[0] for d in curs.description]
	def view_exists(self, view_name):
		curs = self.cursor()
		sql = "select name from sqlite_master where type='view' and name='%s';" % view_name
		try:
			curs.execute(sql)
		except ErrInfo:
			raise
		except:
			self.rollback()
			raise ErrInfo(type="db", command_text=sql, exception_msg=exception_desc(), other_msg=u'Failed test for existence of SQLite view "%s";' % view_name)
		rows = curs.fetchall()
		return len(rows) > 0
	def schema_exists(self, schema_name):
		return False
	def drop_table(self, tablename):
		tablename = self.type.quoted(tablename)
		self.execute(u"drop table if exists %s;" % tablename)
	def populate_table(self, schema_name, table_name, rowsource, column_list, tablespec_src):
		# The rowsource argument must be a generator yielding a list of values for the columns of the table.
		# The column_list argument must an iterable containing column names in the same order as produced by the rowsource.
		sq_name = self.schema_qualified_table_name(None, table_name)
		# Check specified column names.
		tablespec = tablespec_src()
		ts_colnames = [col.name for col in tablespec.cols]
		src_missing_cols = [col for col in column_list if col not in ts_colnames]
		if len(src_missing_cols) > 0:
			raise ErrInfo(type="error", other_msg="Data source is missing the following columns: %s." % ", ".join(src_missing_cols))
		# Get column indexes for selected column names.
		columns = column_list
		data_indexes = [ts_colnames.index(col) for col in columns]
		# Construct prepared SQL statement
		colspec = ",".join([self.type.quoted(c) for c in columns])
		paramspec = ",".join(['?' for c in columns])
		sql = u"insert into %s (%s) values (%s);" % (sq_name, colspec, paramspec)
		curs = self.cursor()
		for line in rowsource:
			# Skip empty rows.
			if not (len(line) == 1 and line[0] is None):
				linedata = [line[ix] for ix in data_indexes]
				if not conf.empty_strings:
					# Replace empty strings with None and convert datetime and time values to strings.
					for i in range(len(linedata)):
						if linedata[i] == u'':
							linedata[i] = None
				# Convert datetime, time, and Decimal values to strings.
				for i in range(len(linedata)):
					if type(linedata[i]) in (datetime.datetime, datetime.time, Decimal):
						linedata[i] = str(linedata[i])
				try:
					curs.execute(sql, linedata)
				except ErrInfo:
					raise
				except:
					self.rollback()
					raise ErrInfo(type="db", command_text=sql, exception_msg=exception_desc(), other_msg=u"Can't load data into table %s from line {%s}" % (sq_name, line))
		#self.commit()


class MySQLDatabase(Database):
	def __init__(self, server_name, db_name, user_name, need_passwd=False, port=3306, encoding='latin1', password=None):
		global mysql_lib
		try:
			import pymysql as mysql_lib
		except:
			fatal_error(u"The pymysql module is required to connect to MySQL.   See https://pypi.python.org/pypi/PyMySQL")
		self.type = dbt_mysql
		self.server_name = str(server_name)
		self.db_name = str(db_name)
		self.user = str(user_name)
		self.need_passwd = need_passwd
		self.password = password
		self.port = 3306 if not port else port
		self.encoding = encoding or 'latin1'
		self.paramstr = '%s'
		self.conn = None
		self.autocommit = True
		self.open_db()
	def __repr__(self):
		return u"MySQLDatabase(%r, %r, %r, %r, %r, %r)" % (self.server_name, self.db_name, self.user,
				self.need_passwd, self.port, self.encoding)
	def open_db(self):
		def db_conn():
			if self.user and self.password:
				return mysql_lib.connect(host=self.server_name, database=self.db_name, port=self.port, user=self.user, password=self.password, charset=self.encoding, local_infile=True)
			else:
				return mysql_lib.connect(host=self.server_name, database=self.db_name, port=self.port, charset=self.encoding, local_infile=True)
		if self.conn is None:
			try:
				if self.user and self.need_passwd and not self.password:
					self.password = get_password("MySQL", self.db_name, self.user, server_name=self.server_name)
				self.conn = db_conn()
				self.execute("set session sql_mode='ANSI';")
			except SystemExit:
				# If the user canceled the password prompt.
				raise
			except ErrInfo:
				raise
			except:
				msg = u"Failed to open MySQL database %s on %s" % (self.db_name, self.server_name)
				raise ErrInfo(type="exception", exception_msg=exception_desc(), other_msg=msg)
	def exec_cmd(self, querycommand):
		# The querycommand must be a stored function (/procedure)
		curs = self.cursor()
		cmd = u"call %s();" % querycommand
		try:
			curs.execute(cmd)
			subvars.add_substitution("$LAST_ROWCOUNT", curs.rowcount)
		except:
			self.rollback()
			raise
	def schema_exists(self, schema_name):
		return False
	def import_file(self, schema_name, table_name, csv_file_obj, skipheader):
		# Import a file to a table.  Columns must be compatible.
		global conf
		sq_name = self.schema_qualified_table_name(schema_name, table_name)
		if not self.table_exists(table_name, schema_name):
			raise ErrInfo(type="error", other_msg=u"Table doesn't exist for import of file to table %s; check that capitalization is consistent." % sq_name)
		csv_file_obj.evaluate_line_format()
		# Create a comma-delimited list of column names in the input file.
		table_cols = self.table_columns(table_name, schema_name)
		data_table_cols = [d.lower() for d in table_cols]
		csv_file_cols = csv_file_obj.column_headers()
		if conf.import_common_cols_only:
			import_cols = [col for col in csv_file_cols if col in data_table_cols]
		else:
			unmatched_cols = list(set(csv_file_cols) - set(data_table_cols))
			if len(unmatched_cols) > 0:
				raise ErrInfo(type="error", other_msg=u"The input file %s has the following columns that are not in table %s: %s" % (csv_file_obj.csvfname, sq_name, ", ".join(unmatched_cols)))
			import_cols = csv_file_cols
		input_col_list = ",".join(import_cols)
		if data_table_cols == csv_file_cols and conf.empty_strings:
			import_sql = "load data local infile '%s' into table %s" % (csv_file_obj.csvfname, sq_name)
			if csv_file_obj.encoding:
				import_sql = "%s character set %s" % (import_sql, csv_file_obj.encoding)
			if csv_file_obj.delimiter or csv_file_obj.quotechar:
				import_sql = import_sql + " columns"
				if csv_file_obj.delimiter:
					import_sql = "%s terminated by '%s'" % (import_sql, csv_file_obj.delimiter)
				if csv_file_obj.quotechar:
					import_sql = "%s optionally enclosed by '%s'" % (import_sql, csv_file_obj.quotechar)
			import_sql = "%s ignore %d lines" % (import_sql, 1 + csv_file_obj.junk_header_lines)
			import_sql = "%s (%s);" % (import_sql, input_col_list)
			self.execute(import_sql)
		else:
			def load_line(line):
				if len(line) > len(csv_file_cols):
					raise ErrInfo(type="error", other_msg="Too many data columns on line {%s}" % line)
				if not conf.empty_strings:
					# Replace empty strings with None; psycopg2 passes empty strings in numeric columns to Postgres as strings, not None.
					for i in range(len(line)):
						if line[i] == u'':
							line[i] = None
				# Pad short line with nulls
				line.extend([None]*(len(import_cols)-len(line)))
				linedata = [line[ix] for ix in data_indexes]
				try:
					curs.execute(sql_template, linedata)
				except ErrInfo:
					raise
				except:
					self.rollback()
					raise ErrInfo(type="db", command_text=sql_template, exception_msg=exception_desc(), other_msg=u"Import from file into table %s, line {%s}" % (sq_name, line))
			data_indexes = [csv_file_cols.index(col) for col in import_cols]
			paramspec = ",".join(['%s']*len(import_cols))
			sql_template = u"insert into %s (%s) values (%s);" % (sq_name, input_col_list, paramspec)
			# Read as CSV
			f = csv_file_obj.reader()
			if skipheader:
				f.next()
			curs = self.cursor()
			for line in f:
				load_line(line)



class FirebirdDatabase(Database):
	def __init__(self, server_name, db_name, user_name, need_passwd=False, port=3050, encoding='latin1', password=None):
		global firebird_lib
		try:
			import fdb as firebird_lib
		except:
			fatal_error(u"The fdb module is required to connect to MySQL.   See https://pypi.python.org/pypi/fdb/")
		self.type = dbt_firebird
		self.server_name = str(server_name)
		self.db_name = str(db_name)
		self.user = str(user_name)
		self.need_passwd = need_passwd
		self.password = password
		self.port = 3050 if not port else port
		self.encoding = encoding or 'latin1'
		self.paramstr = '?'
		self.conn = None
		self.autocommit = True
		self.open_db()
	def __repr__(self):
		return u"FirebirdDatabase(%r, %r, %r, %r, %r, %r)" % (self.server_name, self.db_name, self.user,
				self.need_passwd, self.port, self.encoding)
	def open_db(self):
		def db_conn():
			if self.user and self.password:
				return firebird_lib.connect(host=self.server_name, database=self.db_name, port=self.port, user=self.user, password=self.password, charset=self.encoding)
			else:
				return firebird_lib.connect(host=self.server_name, database=self.db_name, port=self.port, charset=self.encoding)
		if self.conn is None:
			try:
				if self.user and self.need_passwd and not self.password:
					self.password = get_password("Firebird", self.db_name, self.user, server_name=self.server_name)
				self.conn = db_conn()
				#self.execute('set autoddl off;')
			except SystemExit:
				# If the user canceled the password prompt.
				raise
			except ErrInfo:
				raise
			except:
				msg = u"Failed to open Firebird database %s on %s" % (self.db_name, self.server_name)
				raise ErrInfo(type="exception", exception_msg=exception_desc(), other_msg=msg)
	def exec_cmd(self, querycommand):
		# The querycommand must be a stored function (/procedure)
		curs = self.cursor()
		cmd = u"execute procedure %s;" % querycommand
		try:
			curs.execute(cmd)
		except:
			self.rollback()
			raise
		subvars.add_substitution("$LAST_ROWCOUNT", curs.rowcount)
	def table_exists(self, table_name, schema_name=None):
		curs = self.cursor()
		sql = "SELECT RDB$RELATION_NAME FROM RDB$RELATIONS WHERE RDB$SYSTEM_FLAG=0 AND RDB$VIEW_BLR IS NULL AND RDB$RELATION_NAME='%s';" % table_name.upper()
		try:
			curs.execute(sql)
		except ErrInfo:
			raise
		except:
			e = ErrInfo(type="db", command_text=sql, exception_msg=exception_desc(), other_msg=u"Failed test for existence of Firebird table %s" % table_name)
			try:
				self.rollback()
			except:
				pass
			raise e
		rows = curs.fetchall()
		self.conn.commit()
		curs.close()
		return len(rows) > 0
	def column_exists(self, table_name, column_name, schema_name=None):
		curs = self.cursor()
		sql = "select first 1 %s from %s;" % (column_name, table_name)
		try:
			curs.execute(sql)
		except:
			return False
		return True
	def table_columns(self, table_name, schema_name=None):
		curs = self.cursor()
		sql = "select first 1 * from %s;" % table_name
		try:
			curs.execute(sql)
		except ErrInfo:
			raise
		except:
			self.rollback()
			raise ErrInfo(type="db", command_text=sql, exception_msg=exception_desc(),
							other_msg=u"Failed to get column names for table %s of %s" % (table_name, self.name()))
		return [d[0] for d in curs.description]
	def view_exists(self, view_name, schema_name=None):
		curs = self.cursor()
		sql = "select distinct rdb$view_name from rdb$view_relations where rdb$view_name = '%s';" % view_name
		try:
			curs.execute(sql)
		except ErrInfo:
			raise
		except:
			self.rollback()
			raise ErrInfo(type="db", command_text=sql, exception_msg=exception_desc(), other_msg=u"Failed test for existence of Firebird view %s" % view_name)
		rows = curs.fetchall()
		curs.close()
		return len(rows) > 0
	def schema_exists(self, schema_name):
		return False
	def drop_table(self, tablename):
		# Firebird will thrown an error if there are foreign keys into the table.
		tablename = self.type.quoted(tablename)
		self.execute(u"DROP TABLE %s;" % tablename)
		#self.execute(u"COMMIT;")
		self.conn.commit()


class DatabasePool(object):
	# Define an object that maintains a set of database connection objects, each with
	# a name (alias), and with the current and initial databases identified.
	def __init__(self):
		self.pool = {}
		self.initial_db = None
		self.current_db = None
		self.do_rollback = True
	def __repr__(self):
		return u"DatabasePool()"
	def add(self, db_alias, db_obj):
		db_alias = db_alias.lower()
		if db_alias == 'initial' and len(self.pool) > 0:
			raise ErrInfo(type="error", other_msg="You may not use the name 'INITIAL' as a database alias.")
		if len(self.pool) == 0:
			self.initial_db = db_alias
			self.current_db = db_alias
		if db_alias in self.pool.keys():
			exec_log.log_status_info(u"Reassigning database alias '%s' from %s to %s." % (db_alias, self.pool[db_alias].name(), db_obj.name()))
			self.pool[db_alias].close()
		self.pool[db_alias] = db_obj
	def aliases(self):
		# Return a list of the currently defined aliases
		return self.pool.keys()
	def current(self):
		# Return the current db object.
		return self.pool[self.current_db]
	def current_alias(self):
		# Return the alias of the current db object.
		return self.current_db
	def initial(self):
		return self.pool[self.initial_db]
	def aliased_as(self, db_alias):
		return self.pool[db_alias]
	def make_current(self, db_alias):
		# Change the current database in use.
		db_alias = db_alias.lower()
		if not db_alias in self.pool.keys():
			raise ErrInfo(type="error", other_msg=u"Database alias '%s' is unrecognized; cannnot use it." % db_alias)
		self.current_db = db_alias
	def disconnect(self, alias):
		if alias == self.current_db or (alias == 'initial' and 'initial' in self.pool.keys()):
			raise ErrInfo(type="error", other_msg=u"Database alias %s can't be removed or redefined while it is in use." % alias)
		if alias in self.pool.keys():
			self.pool[alias].close()
			del self.pool[alias]
	def closeall(self):
		for alias, db in self.pool.items():
			nm = db.name()
			try:
				if self.do_rollback:
					db.rollback()
				db.close()
			except:
				exec_log.log_status_error(u"Can't close database %s aliased as %s" % (nm, alias))
		self.__init__()


#	End of database connections.
#===============================================================================================


#===============================================================================================
#----  CSV FILES
# This is a replacement for the Python csv library because:
#	1. The format sniffer in the standard library reports that a double quote is used
#		when there is actually no quote character, and it is necessary to know when there
#		is actually no quote character so that Postgres' 'COPY FROM' command can be used.
#	2. The number of rows evaluated by the format sniffer in the standard library is
#		limited and cannot be controlled.  Data tables in CSV format may not have quote
#		characters used until hundreds of lines into a file, so configurability is necessary.
#		In this implementation of the class, the number of lines scanned is specified in
#		configuration data (conf.scan_lines) rather than as an argument.

class CsvFile(EncodedFile):
	def __init__(self, csvfname, file_encoding, junk_header_lines=0):
		super(CsvFile, self).__init__(csvfname, file_encoding)
		self.csvfname = csvfname
		self.encoding = file_encoding
		self.junk_header_lines = junk_header_lines
		self.lineformat_set = False		# Indicates whether delimiter, quotechar, and escapechar have been set
		self.delimiter = None
		self.quotechar = None
		self.escapechar = None
		self.parse_errors = []
		self.table_data = None		# Set to a DataTable object by 'evaluate_column_types()'
	def __repr__(self):
		return u"CsvFile(%r, %r)" % (self.csvfname, self.encoding)
	def openclean(self, mode):
		# Returns an opened file object with junk headers stripped.
		f = self.open(mode)
		for l in range(self.junk_header_lines):
			f.readline()
		return f
	def lineformat(self, delimiter, quotechar, escapechar):
		# Specifies the format of a line.
		self.delimiter = delimiter
		self.quotechar = quotechar
		self.escapechar = escapechar
		self.lineformat_set = True
	class CsvLine(object):
		escchar = u"\\"
		def __init__(self, line_text):
			self.text = line_text
			self.delim_counts = {}
			self.item_errors = []		# A list of error messages.
		def __str__(self):
			return u"; ".join([u"Text: <<%s>>" % self.text, \
				u"Delimiter counts: <<%s>>" % ", ".join([u"%s: %d" % (k, self.delim_counts[k]) for k in self.delim_counts.keys()])])
		def count_delim(self, delim):
			# If the delimiter is a space, consider multiple spaces to be equivalent
			# to a single delimiter, split on the space(s), and consider the delimiter
			# count to be one fewer than the items returned.
			if delim == u" ":
				self.delim_counts[delim] = max(0, len(re.split(r' +', self.text)) - 1)
			else:
				self.delim_counts[delim] = self.text.count(delim)
		def delim_count(self, delim):
			return self.delim_counts[delim]
		def _well_quoted(self, element, qchar):
			# A well-quoted element has either no quotes, a quote on each end and none
			# in the middle, or quotes on both ends and every internal quote is either
			# doubled or escaped.
			# Returns a tuple of three booleans; the first indicates whether the element is
			# well-quoted, the second indicates whether the quote character is used
			# at all, and the third indicates whether the escape character is used.
			if qchar not in element:
				return (True, False, False)
			if len(element) == 0:
				return (True, False, False)
			if element[0] == qchar and element[-1] == qchar and qchar not in element[1:-1]:
				return (True, True, False)
			# The element has quotes; if it doesn't have one on each end, it is not well-quoted.
			if not (element[0] == qchar and element[-1] == qchar):
				return (False, True, False)
			e = element[1:-1]
			# If there are no quotes left after removing doubled quotes, this is well-quoted.
			if qchar not in e.replace(qchar+qchar, u''):
				return (True, True, False)
			# if there are no quotes left after removing escaped quotes, this is well-quoted.
			if qchar not in e.replace(self.escchar+qchar, u''):
				return (True, True, True)
			return (False, True, False)
		def record_format_error(self, pos_no, errmsg):
			self.item_errors.append(u"%s in position %d." % (errmsg, pos_no))
		def items(self, delim, qchar):
			# Parses the line into a list of items, breaking it at delimiters that are not
			# within quoted stretches.  (This is a almost CSV parser, for valid delim and qchar,
			# except that it does not eliminate quote characters or reduce escaped quotes.)
			self.item_errors = []
			if qchar is None:
				if delim is None:
					return self.text
				if delim == u" ":
					return re.split(r' +', self.text)
				else:
					return self.text.split(delim)
			elements = []		# The list of items on the line that will be returned.
			eat_multiple_delims = delim == u" "
			# States of the FSM:
			#	_IN_QUOTED: An opening quote has been seen, but no closing quote encountered.
			#		Actions / transition:
			#			quote: save char in escape buffer / _QUOTE_IN_QUOTED
			#			esc_char : save char in escape buffer / _ESCAPED
			#			delimiter: save char in element buffer / _IN_QUOTED
			#			other: save char in element buffer / _IN_QUOTED
			#	_ESCAPED: An escape character has been seen while _IN_QUOTED (and is in the escape buffer).
			#		Actions / transitions
			#			quote: save escape buffer in element buffer, empty escape buffer,
			#				save char in element buffer / _IN_QUOTED
			#			delimiter: save escape buffer in element buffer, empty escape buffer,
			#				save element buffer, empty element buffer / _BETWEEN
			#			other: save escape buffer in element buffer, empty escape buffer,
			#				save char in element buffer / _IN_QUOTED
			#	_QUOTE_IN_QUOTED: A quote has been seen while _IN_QUOTED (and is in the escape buffer).
			#		Actions / transitions
			#			quote: save escape buffer in element buffer, empty escape buffer,
			#				save char in element buffer / _IN_QUOTED
			#			delimiter: save escape buffer in element buffer, empty escape buffer,
			#				save element buffer, empty element buffer / _DELIMITED
			#			other: save escape buffer in element buffer, empty escape buffer,
			#				save char in element buffer / _IN_QUOTED
			#					(An 'other' character in this position represents a bad format:
			#					a quote not followed by another quote or a delimiter.)
			#	_IN_UNQUOTED: A non-delimiter, non-quote has been seen.
			#		Actions / transitions
			#			quote: save char in element buffer / _IN_UNQUOTED
			#				(This represents a bad format.)
			#			delimiter: save element buffer, empty element buffer / _DELIMITED
			#			other: save char in element buffer / _IN_UNQUOTED
			#	_BETWEEN: Not in an element, and a delimiter not seen.  This is the starting state,
			#			and the state following a closing quote but before a delimiter is seen.
			#		Actions / transition:
			#			quote: save char in element buffer / _IN_QUOTED
			#			delimiter: save element buffer, empty element buffer / _DELIMITED
			#				(The element buffer should be empty, representing a null data item.)
			#			other: save char in element buffer / _IN_UNQUOTED
			#	_DELIMITED: A delimiter has been seen while not in a quoted item.
			#		Actions / transition:
			#			quote: save char in element buffer / _IN_QUOTED
			#			delimiter: if eat_multiple: no action / _DELIMITED
			#					if not eat_multiple: save element buffer, empty element buffer / _DELIMITED
			#			other: save char in element buffer / _IN_UNQUOTED
			# At end of line: save escape buffer in element buffer, save element buffer.  For a well-formed
			# line, these should be empty, but they may not be.
			#
			# Define the state constants, which will also be used as indexes into an execution vector.
			_IN_QUOTED, _ESCAPED, _QUOTE_IN_QUOTED, _IN_UNQUOTED, _BETWEEN, _DELIMITED = range(6)
			#
			# Because of Python 2.7's scoping rules:
			#	* The escape buffer and current element are defined as mutable objects that will have their
			#		first elements modified, rather than as string variables.  (Python 2.x does not allow
			#		modification of a variable in an enclosing scope that is not the global scope, but
			#		mutable objects like lists can be altered.  Another approach would be to implement this
			#		as a class and use instance variables.)
			#	* The action functions return the next state rather than assigning it directly to the 'state' variable.
			esc_buf = [u'']
			current_element = [u'']
			def in_quoted():
				if c == self.escchar:
					esc_buf[0] = c
					return _ESCAPED
				elif c == qchar:
					esc_buf[0] = c
					return _QUOTE_IN_QUOTED
				else:
					current_element[0] += c
					return _IN_QUOTED
			def escaped():
				if c == delim:
					current_element[0] += esc_buf[0]
					esc_buf[0] = u''
					elements.append(current_element[0])
					current_element[0] = u''
					return _BETWEEN
				else:
					current_element[0] += esc_buf[0]
					esc_buf[0] = u''
					current_element[0] += c
					return _IN_QUOTED
			def quote_in_quoted():
				if c == qchar:
					current_element[0] += esc_buf[0]
					esc_buf[0] = u''
					current_element[0] += c
					return _IN_QUOTED
				elif c == delim:
					current_element[0] += esc_buf[0]
					esc_buf[0] = u''
					elements.append(current_element[0])
					current_element[0] = u''
					return _DELIMITED
				else:
					current_element[0] += esc_buf[0]
					esc_buf[0] = u''
					current_element[0] += c
					self.record_format_error(i+1, "Unexpected character following a closing quote")
					return _IN_QUOTED
			def in_unquoted():
				if c == delim:
					elements.append(current_element[0])
					current_element[0] = u''
					return _DELIMITED
				else:
					current_element[0] += c
					return _IN_UNQUOTED
			def between():
				if c == qchar:
					current_element[0] += c
					return _IN_QUOTED
				elif c == delim:
					elements.append(current_element[0])
					current_element[0] = u''
					return _DELIMITED
				else:
					current_element[0] += c
					return _IN_UNQUOTED
			def delimited():
				if c == qchar:
					current_element[0] += c
					return _IN_QUOTED
				elif c == delim:
					if not eat_multiple_delims:
						elements.append(current_element[0])
						current_element[0] = u''
					return _DELIMITED
				else:
					current_element[0] += c
					return _IN_UNQUOTED
			# Functions in the execution vector must be ordered identically to the
			# indexes represented by the state constants.
			exec_vector = [in_quoted, escaped, quote_in_quoted, in_unquoted, between, delimited]
			# Set the starting state.
			state = _BETWEEN
			# Process the line of text.
			for i, c in enumerate(self.text):
				state = exec_vector[state]()
			# Process the end-of-line condition.
			if len(esc_buf[0]) > 0:
				current_element[0] += esc_buf[0]
			if len(current_element[0]) > 0:
				elements.append(current_element[0])
			return elements
		def well_quoted_line(self, delim, qchar):
			# Returns a tuple of boolean, int, and boolean, indicating: 1) whether the line is
			# well-quoted, 2) the number of elements for which the quote character is used,
			# and 3) whether the escape character is used.
			wq = [self._well_quoted(el, qchar) for el in self.items(delim, qchar)]
			return (all([b[0] for b in wq]), sum([b[1] for b in wq]), any([b[2] for b in wq]))
	def diagnose_delim(self, linestream, possible_delimiters=None, possible_quotechars=None):
		# Returns a tuple consisting of the delimiter, quote character, and escape
		# character for quote characters within elements of a line.  All may be None.
		# If the escape character is not None, it will be u"\".
		# Arguments:
		#	* linestream: An iterable file-like object with a 'next()' method that returns lines of text
		#		as bytes or unicode.
		#	* possible_delimiters: A list of single characters that might be used to separate items on
		#		a line.  If not specified, the default consists of tab, comma, semicolon, and vertical rule.
		#		If a space character is included, multiple space characters will be treated as a single
		#		delimiter--so it's best if there are no missing values on space-delimited lines, though
		#		that is not necessarily a fatal flaw unless there is a very high fraction of missing values.
		#	* possible_quotechars: A list of single characters that might be used to quote items on
		#		a line.  If not specified, the default consists of single and double quotes.
		if not possible_delimiters:
			possible_delimiters = [u"\t", u",", u";", u"|", unicode(chr(31))]
		if not possible_quotechars:
			possible_quotechars = [u'"', u"'"]
		lines = []
		for i in range(conf.scan_lines if conf.scan_lines and conf.scan_lines > 0 else 1000000):
			try:
				ln = linestream.next()
			except StopIteration:
				break
			except:
				raise
			while len(ln) > 0 and ln[-1] in (u"\n", u"\r"):
				ln = ln[:-1]
			if len(ln) > 0:
				lines.append(self.CsvLine(ln))
		if len(lines) == 0:
			raise ErrInfo(type="error", other_msg=u"CSV diagnosis error: no lines read")
		for ln in lines:
			for d in possible_delimiters:
				ln.count_delim(d)
		# For each delimiter, find the minimum number of delimiters found on any line, and the number of lines
		# with that minimum number
		delim_stats = {}
		for d in possible_delimiters:
			dcounts = [ln.delim_count(d) for ln in lines]
			min_count = min(dcounts)
			delim_stats[d] = (min_count, dcounts.count(min_count))
		# Remove delimiters that were never found.
		for k in delim_stats.keys():
			if delim_stats[k][0] == 0:
				del delim_stats[k]
		def all_well_quoted(delim, qchar):
			# Returns a tuple of boolean, int, and boolean indicating: 1) whether the line is
			# well-quoted, 2) the total number of lines and elements for which the quote character
			# is used, and 3) the escape character used.
			wq = [l.well_quoted_line(delim, qchar) for l in lines]
			return (all([b[0] for b in wq]), sum([b[1] for b in wq]), self.CsvLine.escchar if any([b[2] for b in wq]) else None)
		def eval_quotes(delim):
			# Returns a tuple of the form to be returned by 'diagnose_delim()'.
			ok_quotes = {}
			for q in possible_quotechars:
				allwq = all_well_quoted(delim, q)
				if allwq[0]:
					ok_quotes[q] = (allwq[1], allwq[2])
			if len(ok_quotes) == 0:
				return (delim, None, None)	# No quotes, no escapechar
			else:
				max_use = max([v[0] for v in ok_quotes.values()])
				if max_use == 0:
					return (delim, None, None)
				# If multiple quote characters have the same usage, return (arbitrarily) the first one.
				for q in ok_quotes.keys():
					if ok_quotes[q][0] == max_use:
						return (delim, q, ok_quotes[q][1])
		if len(delim_stats) == 0:
			# None of the delimiters were found.  Some other delimiter may apply,
			# or the input may contain a single value on each line.
			# Identify possible quote characters.
			return eval_quotes(None)
		else:
			if len(delim_stats) > 1:
				# If one of them is a space, prefer the non-space
				if u" " in delim_stats.keys():
					del delim_stats[u" "]
			if len(delim_stats) == 1:
				return eval_quotes(delim_stats.keys()[0])
			# Assign weights to the delimiters.  The weight is the square of the minimum number of delimiters
			# on a line times the number of lines with that delimiter.
			delim_wts = {}
			for d in delim_stats.keys():
				delim_wts[d] = delim_stats[d][0]**2 * delim_stats[d][1]
			# Evaluate quote usage for each delimiter, from most heavily weighted to least.
			# Return the first good pair where the quote character is used.
			delim_order = sorted(delim_wts, key=delim_wts.get, reverse=True)
			for d in delim_order:
				quote_check = eval_quotes(d)
				if quote_check[0] and quote_check[1]:
					return quote_check
			# There are no delimiters for which quotes are OK.
			return (delim_order[0], None, None)
		# Should never get here
		raise ErrInfo(type="error", other_msg=u"CSV diagnosis coding error: an untested set of conditions are present")
	def evaluate_line_format(self):
		# Scans the file to determine the delimiter, quote character, and escapechar.
		if not self.lineformat_set:
			self.delimiter, self.quotechar, self.escapechar = self.diagnose_delim(self.openclean("rt"))
			self.lineformat_set = True
	def _record_format_error(self, pos_no, errmsg):
		self.parse_errors.append(u"%s in position %d." % (errmsg, pos_no))
	def read_and_parse_line(self, f):
		# Returns a list of line elements, parsed according to the established delimiter and quotechar.
		elements = []		# The list of items on the line that will be returned.
		eat_multiple_delims = self.delimiter == u" "
		# States of the FSM
		#	_START: The starting state
		#		Actions / transition:
		#			quote: <no action> / _IN_QUOTED
		#			delimiter: save (empty) element buffer / _DELIMITED
		#			newline: <no action> / _END
		#			other: save char in element buffer / _IN_UNQUOTED
		#	_IN_QUOTED: An opening quote has been seen, but no closing quote encountered.
		#		Actions / transition:
		#			quote: save char in escape buffer / _QUOTE_IN_QUOTED
		#			esc_char : save char in escape buffer / _ESCAPED
		#			delimiter: save char in element buffer / _IN_QUOTED
		#			other: save char in element buffer / _IN_QUOTED
		#	_ESCAPED: An escape character has been seen while _IN_QUOTED (and is in the escape buffer).
		#		Actions / transitions
		#			quote: empty escape buffer; save char in element buffer / _IN_QUOTED
		#			delimiter: save escape buffer in element buffer, empty escape buffer,
		#				save char in element buffer / _IN_QUOTED
		#			other: save escape buffer in element buffer, empty escape buffer,
		#				save char in element buffer / _IN_QUOTED
		#	_QUOTE_IN_QUOTED: A quote has been seen while _IN_QUOTED (and is in the escape buffer).
		#		Actions / transitions
		#			quote: empty escape buffer; save char in element buffer / _IN_QUOTED
		#			delimiter: empty escape buffer, save element buffer, empty element buffer / _DELIMITED
		#			newline: empty escape buffer, save element buffer, empty element buffer / _END
		#			other: empty escape buffer, save element buffer,
		#				save char in element buffer / _IN_UNQUOTED
		#					(An 'other' character in this position represents a bad format:
		#					a [closing] quote not followed by another quote or a delimiter.)
		#	_IN_UNQUOTED: A non-delimiter, non-quote has been seen.
		#		Actions / transitions
		#			quote: save element buffer, empty element buffer / _IN_QUOTED
		#				(This represents a bad format.)
		#			delimiter: save element buffer, empty element buffer / _DELIMITED
		#			newline: save element buffer, empty element buffer / _END
		#			other: save char in element buffer / _IN_UNQUOTED
		#	_BETWEEN: Not in an element, and a delimiter not seen.  This is the state
		#			following a closing quote but before a delimiter is seen.
		#		Actions / transition:
		#			quote: <no action> / _IN_QUOTED
		#			delimiter: save (empty) element buffer / _DELIMITED
		#			newline: <no action> / _END
		#			other: save char in element buffer / _IN_UNQUOTED
		#				(This represents a bad format.)
		#	_DELIMITED: A delimiter has been seen while not in a quoted item.
		#		Actions / transition:
		#			quote: <no action> / _IN_QUOTED
		#			delimiter: if eat_multiple: no action / _DELIMITED
		#					if not eat_multiple: save element buffer, empty element buffer / _DELIMITED
		#			newline: <no action> / _END
		#			other: save char in element buffer / _IN_UNQUOTED
		#	_END: The end of a line has been reached
		#			If prev_state==_ESCAPED, save escape buffer in element buffer.
		#			If characters in element buffer, save element buffer.
		# 			If prev_state==_ESCAPED, save empty element buffer (missing value at end of line)
		#
		# Define the state constants, which will also be used as indexes into an execution vector.
		_START, _IN_QUOTED, _ESCAPED, _QUOTE_IN_QUOTED, _IN_UNQUOTED, _BETWEEN, _DELIMITED, _END = range(8)
		#
		# Because of Python 2.7's scoping rules:
		#	* The escape buffer and current element are defined as mutable objects that will have their
		#		first elements modified, rather than as string variables.  (Python 2.x does not allow
		#		modification of a variable in an enclosing scope that is not the global scope, but
		#		mutable objects like lists can be altered.  Another approach would be to implement this
		#		as a class and use instance variables.)
		#	* The action functions return the next state rather than assigning it directly to the 'state' variable.
		esc_buf = [u'']
		current_element = [u'']
		def start():
			if c == self.quotechar:
				return _IN_QUOTED
			elif c == self.delimiter:
				elements.append(None)
				return _DELIMITED
			elif c == u'\n':
				return _END
			else:
				current_element[0] += c
				return _IN_UNQUOTED
		def in_quoted():
			if c == self.escapechar:
				esc_buf[0] = c
				return _ESCAPED
			elif c == self.quotechar:
				esc_buf[0] = c
				return _QUOTE_IN_QUOTED
			else:
				current_element[0] += c
				return _IN_QUOTED
		def escaped():
			if c == self.quotechar:
				esc_buf[0] = u''
				current_element[0] += c
				return _IN_QUOTED
			elif c == self.delimiter:
				current_element[0] += esc_buf[0]
				esc_buf[0] = u''
				current_element[0] += c
				return _IN_QUOTED
			else:
				current_element[0] += esc_buf[0]
				esc_buf[0] = u''
				current_element[0] += c
				return _IN_QUOTED
		def quote_in_quoted():
			if c == self.quotechar:
				esc_buf[0] = u''
				current_element[0] += c
				return _IN_QUOTED
			elif c == self.delimiter:
				esc_buf[0] = u''
				elements.append(current_element[0])
				current_element[0] = u''
				return _DELIMITED
			elif c == u'\n':
				esc_buf[0] = u''
				elements.append(current_element[0])
				current_element[0] = u''
				return _END
			else:
				esc_buf[0] = u''
				elements.append(current_element[0] if len(current_element[0]) > 0 else None)
				current_element[0] += c
				self._record_format_error(i+1, "Unexpected character following a closing quote")
				return _IN_UNQUOTED
		def in_unquoted():
			if c == self.delimiter:
				elements.append(current_element[0] if len(current_element[0]) > 0 else None)
				current_element[0] = u''
				return _DELIMITED
			elif c == u'\n':
				elements.append(current_element[0] if len(current_element[0]) > 0 else None)
				current_element[0] = u''
				return _END
			elif c == self.quotechar:
				elements.append(current_element[0] if len(current_element[0]) > 0 else None)
				current_element[0] = u''
				return _IN_QUOTED
			else:
				current_element[0] += c
				return _IN_UNQUOTED
		def between():
			if c == self.quotechar:
				return _IN_QUOTED
			elif c == self.delimiter:
				current_element[0] = u''
				return _DELIMITED
			elif c == u'\n':
				return _END
			else:
				current_element[0] += c
				self._record_format_error(i+1, "Unexpected character following a closing quote")
				return _IN_UNQUOTED
		def delimited():
			if c == self.quotechar:
				return _IN_QUOTED
			elif c == self.delimiter:
				if not eat_multiple_delims:
					elements.append(current_element[0] if len(current_element[0]) > 0 else None)
					current_element[0] = u''
				return _DELIMITED
			elif c == u'\n':
				return _END
			else:
				current_element[0] += c
				return _IN_UNQUOTED
		def end():
			# Process the end-of-line condition.
			if len(esc_buf[0]) > 0 and prev_state == _ESCAPED:
				current_element[0] += esc_buf[0]
			if len(current_element[0]) > 0:
				if prev_state == _QUOTE_IN_QUOTED:
					elements.append(current_element[0][:-1])
				else:
					elements.append(current_element[0])
			if prev_state == _DELIMITED:
				elements.append(None)
			return None
		# Functions in the execution vector must be ordered identically to the
		# indexes represented by the state constants.
		exec_vector = [start, in_quoted, escaped, quote_in_quoted, in_unquoted, between, delimited, end]
		# Set the starting state.
		state = _START
		prev_state = None
		i = 0	# Character counter per line
		while state != _END:
			# Read one *character*
			c = f.read(1)
			if c == u'\n':
				i = 0
			if c == u'':
				state = _END
			else:
				i += 1
				prev_state = state
				state = exec_vector[state]()
		end()
		return elements
	def reader(self):
		self.evaluate_line_format()
		f = self.openclean("rt")
		while True:
			elements = self.read_and_parse_line(f)
			if len(elements) > 0:
				yield elements
			else:
				break
		f.close()
	class _Writer(object):
		def __init__(self, filename, file_encoding, delim, quote, escchar, append=False):
			self.delimiter = delim
			self.joinchar = delim if delim else u""
			self.quotechar = quote
			if quote:
				if escchar:
					self.quotedquote = escchar+quote
				else:
					self.quotedquote = quote+quote
			else:
				self.quotedquote = None
			mode = "wt" if not append else "at"
			if filename.lower() == 'stdout':
				self.output = sys.stdout
			else:
				self.output = EncodedFile(filename, file_encoding).open(mode)
		def writerow(self, datarow):
			if self.quotechar:
				d_row = []
				for e in datarow:
					if isinstance(e, basestring):
						if (self.quotechar in e) or (self.delimiter is not None and self.delimiter in e) or (u'\n' in e):
							d_row.append(u"%s%s%s" % (self.quotechar, e.replace(self.quotechar, self.quotedquote), self.quotechar))
						else:
							d_row.append(e)
					else:
						if e is None:
							d_row.append('')
						else:
							d_row.append(unicode(e))
				text = self.joinchar.join(d_row)
			else:
				d_row = []
				for e in datarow:
					if e is None:
						d_row.append('')
					else:
						d_row.append(unicode(e))
				text = self.joinchar.join(d_row)
			self.output.write(u"%s\n" % text)
		def close(self):
			self.output.close()
			self.output = None
	def writer(self, append=False):
		return self._Writer(self.filename, self.encoding, self.delimiter, self.quotechar, self.escapechar, append)
	def column_headers(self):
		if not self.lineformat_set:
			self.evaluate_line_format()
		inf = self.reader()
		try:
			colnames = inf.next()
		except:
			raise ErrInfo(type="exception", exception_msg=exception_desc(), other_msg=u"Can't read column header line from %s" % self.filename)
		return colnames
	def data_table_def(self):
		if self.table_data is None:
			self.evaluate_column_types()
		return self.table_data
	def evaluate_column_types(self):
		if not self.lineformat_set:
			self.evaluate_line_format()
		inf = self.reader()
		try:
			colnames = inf.next()
		except:
			raise ErrInfo(type="exception", exception_msg=exception_desc(), other_msg=u"Can't read column header line from %s" % self.filename)
		self.table_data = DataTable(colnames, inf)
	def create_table(self, database_type, schemaname, tablename, pretty=False):
		return self.table_data.create_table(database_type, schemaname, tablename, pretty)

# End of file handlers.
#===============================================================================================


#===============================================================================================
#-----  TEMPLATE-BASED REPORTS/EXPORTS


class StrTemplateReport(object):
	# Exporting/reporting using Python's default string.Template, iterated over all
	# rows of a data table.
	def __init__(self, template_file):
		global string
		import string
		self.infname = template_file
		inf = EncodedFile(template_file, conf.script_encoding)
		self.template = string.Template(inf.open("r").read())
	def __repr__(self):
		return u"StrTemplateReport(%s)" % self.infname
	def write_report(self, headers, data_dict_rows, output_dest, append=False):
		if output_dest == 'stdout':
			ofile = output
		else:
			if append:
				ofile = EncodedFile(output_dest, conf.output_encoding).open("a")
			else:
				ofile = EncodedFile(output_dest, conf.output_encoding).open("w")
		for dd in data_dict_rows:
			ofile.write(self.template.safe_substitute(dd))

class JinjaTemplateReport(object):
	# Exporting/reporting using the Jinja2 templating library.
	def __init__(self, template_file):
		global jinja2
		try:
			import jinja2
		except:
			fatal_error(u"The jinja2 library is required to produce reports with the Jinja2 templating system.   See http://jinja.pocoo.org/")
		self.infname = template_file
		inf = EncodedFile(template_file, conf.script_encoding)
		self.template = jinja2.Template(inf.open("r").read())
	def __repr__(self):
		return u"StrTemplateReport(%s)" % self.infname
	def write_report(self, headers, data_dict_rows, output_dest, append=False):
		if output_dest == 'stdout':
			ofile = output
		else:
			if append:
				ofile = EncodedFile(output_dest, conf.output_encoding).open("a")
			else:
				ofile = EncodedFile(output_dest, conf.output_encoding).open("w")
		try:
			ofile.write(self.template.render(headers=headers, datatable=data_dict_rows))
		except jinja2.TemplateSyntaxError as e:
			raise ErrInfo("error", other_msg=e.message + " on template line %d" % e.lineno)
		except jinja2.TemplateError as e:
			raise ErrInfo("error", other_msg="Jinja2 template error (%s)" % e.message)
		except:
			raise

class AirspeedTemplateReport(object):
	# Exporting/reporting using the Airspeed templating library.
	def __init__(self, template_file):
		global airspeed
		try:
			import airspeed
		except:
			fatal_error(u"The airspeed library is required to produce reports with the Airspeed templating system.   See https://github.com/purcell/airspeed")
		self.infname = template_file
		inf = EncodedFile(template_file, conf.script_encoding)
		self.template = airspeed.Template(inf.open("r").read())
	def __repr__(self):
		return u"StrTemplateReport(%s)" % self.infname
	def write_report(self, headers, data_dict_rows, output_dest, append=False):
		# airspeed requires an entire list to be passed, not just an iterable,
		# so produce a list of dictioaries.  This may be too big for memory if
		# the data set is very large.
		data = [ d for d in data_dict_rows ]
		if output_dest == 'stdout':
			ofile = output
		else:
			if append:
				ofile = EncodedFile(output_dest, conf.output_encoding).open("a")
			else:
				ofile = EncodedFile(output_dest, conf.output_encoding).open("w")
		try:
			ofile.write(self.template.merge({'headers': headers, 'datatable': data}))
		except airspeed.TemplateExecutionError as e:
			raise ErrInfo("error", other_msg=e.msg)
		except:
			raise


# End of template-based exports.
#===============================================================================================



#===============================================================================================
#-----  SCRIPTING


class SqlCmd(object):
	# A SQL script object that is either a SQL statement or an execsql metacommand.
	# The definition includes source file information.
	def __init__(self, command_source_name, command_line_no, command_type, sql_text):
		self.source = command_source_name
		self.line_no = command_line_no
		# command_type is "sql" or "cmd".
		self.command_type = command_type
		self.sql = sql_text
	def __repr__(self):
		return u"SqlCmd(%r, %r, %r, %r)" % (self.source, self.line_no, self.command_type, self.sql)


class MetaCommand(object):
	def __init__(self, matching_regexes, exec_func, name=None, description=None, run_in_batch=False, run_when_false=False, set_error_flag=True):
		# matching_regexes: a single or tuple of string regular expressions to match.
		# exec_func: a function object that carries out the work of the metacommand.
		#			This function must take keyword arguments corresponding to those named
		#			in the regex, and must return a value (which is used only for conditional
		#			metacommands) or None.
		# run_in_batch: determines whether a metacommand should be run inside a batch.  Only 'END BATCH'
		#			should be run inside a batch.
		# run_when_false: determines whether a metacommand should be run when the exec state is False.
		#			only 'ELSE', 'ELSEIF', 'ORIF', and 'ENDIF' should be run when False, and only when
		#			all higher levels are True.  This condition is evaluated by the script processor.
		# set_error_flag: When run, sets or clears status.metacommand_error.
		if type(matching_regexes) in (tuple, list):
			self.regexes = [re.compile(rx, re.I) for rx in tuple(matching_regexes)]
		else:
			self.regexes = [re.compile(matching_regexes, re.I)]
		self.exec_fn = exec_func
		self.name = name
		self.description = description
		self.run_in_batch = run_in_batch
		self.run_when_false = run_when_false
		self.set_error_flag = set_error_flag
	def __repr__(self):
		return u"MetaCommand(%r, %r, %r, %r, %r, %r)" % ([e.pattern for e in self.regexes],
					self.exec_fn, self.name, self.description, self.run_in_batch, self.run_when_false)
	def run(self, cmd_str):
		# Runs the metacommand if the command string matches the regex.
		# Returns a 2-tuple consisting of:
		#	0. True or False indicating whether the metacommand applies.  If False, the
		#		remaining return value is None and has no meaning.
		#	1. The return value of the metacommand function.
		#		Exceptions other than SystemExit are caught and converted to ErrInfo exceptions.
		for rx in self.regexes:
			m = rx.match(cmd_str.strip())
			if m:
				cmdargs = m.groupdict()
				cmdargs['metacommandline'] = cmd_str
				e = None
				try:
					rv = self.exec_fn(**cmdargs)
				except SystemExit:
					raise
				except ErrInfo as e:
					pass
				except:
					e = ErrInfo("cmd", command_text=cmd_str, exception_msg=exception_desc())
				if e:
					if status.halt_on_metacommand_err:
						exit_now(1, e)
					if self.set_error_flag:
						status.metacommand_error = True
						return True, None
				else:
					if self.set_error_flag:
						status.metacommand_error = False
					return True, rv
		return False, None
	def __str__(self):
		if self.name:
			return "%s:\t%s" % (self.name, self.description)
		else:
			return None


class ScriptFile(EncodedFile):
	# A file reader that returns lines and records the line number.
	def __init__(self, scriptfname, file_encoding):
		super(ScriptFile, self).__init__(scriptfname, file_encoding)
		self.lno = 0
		self.f = self.open("r")
	def __repr__(self):
		return u"ScriptFile(%r, %r)" % (super(ScriptFile, self).filename, super(ScriptFile, self).encoding)
	def __iter__(self):
		return self
	def next(self):
		l = self.f.next()
		self.lno += 1
		return l


class ScriptCommands(object):
	# A dynamically extensible list of SqlCmd objects (SQL statements and metacommands).
	_COUNTER_RX = re.compile(r'!!\$(COUNTER_\d+)!!', re.I)
	def __init__(self, scriptfile_name):
		# Function parameters:
		#    scriptfile_name: The name of a SQL script file to read, or a list of multiple file names.
		self.scriptfile_name = scriptfile_name
		self.scripts = {}				# Dictionary of scripts.  The key None identifies the main script; non-None keys are as defined with the BEGIN SCRIPT metacommand.
		self.scripts[None] = []
		if isinstance(scriptfile_name, basestring):
			self.append_sqlfile(scriptfile_name)
		else:
			# Must be a list or tuple
			for fn in list(scriptfile_name):
				self.append_sqlfile(fn)
		self.command_list = self.scripts.get(None, [])
		self.last_command = None
		# self.curr_pos is the index of the next command to be executed.
		self.curr_pos = 0
		self.counters = {}
		self.batch_level = 0
		self.batched_commands = []
		self.exec_states = []			# Stack of T/F values controlling execution of script commands.
		self.cmds_run = 0
		self.sub_metacommand = None		# The function that carries out the 'SUB' metacommand.
	def __repr__(self):
		return u"ScriptCommands(%r)" % (self.scriptfile_name)
	def insert_commands(self, more_cmds):
		# Inserts the given list of SqlCmd objects into the current script at the current position.
		self.command_list[self.curr_pos:self.curr_pos] = more_cmds
	def insert_sub_script(self, script_id):
		# Inserts the list of SqlCmd objects from the named subscript into the
		# current script at the current position.
		s = script_id.lower()
		if not s in self.scripts.keys():
			raise ErrInfo(type="cmd", command_text=self.last_command.sql, other_msg="There is no sub-script named %s." % script_id)
		self.insert_commands(copy.deepcopy(self.scripts[s]))
	def read_sqlfile(self, sql_file_name):
		sz, dt = file_size_date(sql_file_name)
		fn, lno = self.current_script_line()
		exec_log.log_status_info("Reading and inserting script %s (size: %d; date: %s) at line %d of %s" % (sql_file_name, sz, dt, lno, fn))
		newscripts = {}
		read_sqlscriptfile(sql_file_name, newscripts, None)
		for k in newscripts.keys():
			if k is None:
				self.insert_commands(newscripts[k])
			else:
				self.scripts[k] = newscripts[k]
	def append_sqlfile(self, sql_file_name):
		sz, dt = file_size_date(sql_file_name)
		exec_log.log_status_info("Reading and appending script %s (size: %d; date: %s)" % (sql_file_name, sz, dt))
		newscripts = {}
		read_sqlscriptfile(sql_file_name, newscripts, None)
		for k in newscripts.keys():
			if k is None:
				self.scripts[None].extend(newscripts[k])
			else:
				self.scripts[k] = newscripts[k]
	def script_lines(self, script_id):
		s = script_id.lower()
		if s in self.scripts.keys():
			return [cmd.sql if cmd.command_type == "sql" else "-- !x! " + cmd.sql for cmd in self.scripts[s]]
		else:
			return []
	def append_substitution(self, template_str, sub_str):
		subvars.append_substitution(template_str, sub_str)
	def sub_exists(self, template_str):
		if subvars.sub_exists(template_str):
			return True
		return template_str in self.counters.keys()
	def set_counter(self, ctr_no, ctr_val):
		ctr_id = u'counter_%d' % ctr_no
		self.counters[ctr_id] = ctr_val
	def remove_counter(self, n):
		ctr_id = u'counter_%d' % n
		if ctr_id in self.counters.keys():
			del self.counters[ctr_id]
	def remove_all_counters(self):
		self.counters = {}
	def current_script_line(self):
		# Returns a tuple of the script name and script line number of the
		# current (or last) command.
		if self.curr_pos > 0:
			cmdobj = self.last_command
			if cmdobj:
				return cmdobj.source, cmdobj.line_no
			else:
				return "", 0
		else:
			if len(self.command_list) == 0:
				return "", 0
			else:
				return self.command_list[0].source, 0
	def new_if_level(self, tf_value):
		self.exec_states.insert(0, tf_value)
	def exit_if_level(self):
		if len(self.exec_states) == 0:
			raise ErrInfo(type="error", other_msg="Can't exit an IF block; no IF block is active.")
		else:
			self.exec_states.pop(0)
	def invert_if_level(self):
		if len(self.exec_states) == 0:
			raise ErrInfo(type="error", other_msg="Can't change the IF state; no IF block is active.")
		else:
			self.exec_states[0] = not self.exec_states[0]
	def replace_if_level(self, tf_value):
		if len(self.exec_states) == 0:
			raise ErrInfo(type="error", other_msg="Can't change the IF state; no IF block is active.")
		else:
			self.exec_states[0] = tf_value
	def current_if_level(self):
		if len(self.exec_states) == 0:
			raise ErrInfo(type="error", other_msg="No IF block is active.")
		else:
			return self.exec_states[0]
	def all_true(self):
		# Returns True if all the if levels are true, or if there is no if level.
		return all(self.exec_states)
	def only_current_false(self):
		# Returns True if the current if level is false and all higher levels are True.
		if len(self.exec_states) == 0:
			return False
		return self.exec_states[0] is False and all(self.exec_states[1:])
	def evaluate_metacommands(self, sqlcmd_obj, in_batch_only=False, when_false_only=False):
		# Tries all metacommands in the global list 'metacommands' until one runs.
		# Returns the result of the metacommand that was run, or None
		something_tried = False
		for cmd in metacommands:
			if (not in_batch_only) or (in_batch_only and cmd.run_in_batch):
				if (not when_false_only) or (when_false_only and cmd.run_when_false):
					try:
						if (not when_false_only) and (not in_batch_only):
							something_tried = True
						applies, result = cmd.run(sqlcmd_obj.sql)
						if applies:
							return result
					except (ErrInfo, SystemExit):
						raise
					except:
						raise ErrInfo(type="cmd", command_text=sqlcmd_obj.sql, other_msg="Unknown metacommand error")
		if something_tried:
			# but nothing applied.
			status.metacommand_error = True
			raise ErrInfo(type="cmd", other_msg="Unrecognized metacommand")
		return None
	def run_db_sql(self, db, sql):
		# Execute a SQL command but do not commit it.
		db.execute(sql)
	def runone(self, sql, outfile):
		# Run a single SQL statement (not a metacommand)
		e = None
		try:
			if outfile is not None:
				sql = sql.strip()
				if sql[-1] == ';':
					sql = u'(' + sql[:-1] +u') as xxxxx'
				x_export(**{'queryname': sql, 'outputname': outfile, 'append': 'false', 'format': 'csv'})
			else:
				db = dbs.current()
				if self.batch_level == 0:
					self.run_db_sql(db, sql)
					db.commit()
				else:
					self.batched_commands.append((db, sql))
		except ErrInfo as e:
			pass
		except SystemExit:
			raise
		except:
			e = ErrInfo(type="exception", exception_msg=exception_desc())
		if e:
			subvars.add_substitution("$LAST_ERROR", sql)
			status.sql_error = True
			if status.halt_on_err:
				exit_now(1, e)
			return
		subvars.add_substitution("$LAST_SQL", sql)
		status.sql_error = False
	def start_batch(self):
		self.batch_level += 1
	def rollback_batch(self):
		self.batched_commands = []
	def end_batch(self):
		self.batch_level -= 1
		if self.batch_level == 0:
			dblist = []
			for db, sqlcmd in self.batched_commands:
				self.run_db_sql(db, sqlcmd)
				if not db in dblist:
					dblist.append(db)
			for db in dblist:
				db.commit()
			self.batched_commands = []
	def run(self):
		# Run the set of script commands.  If an output file is specified and the last
		# command is a SQL statement, export the results to the specified output file as CSV.
		self.cmds_run = 0
		subvars.add_substitution("$LAST_ROWCOUNT", None)
		for cmd_index, cmditem in enumerate(self.command_list):
			subvars.add_substitution("$CURRENT_SCRIPT", cmditem.source)
			subvars.add_substitution("$SCRIPT_LINE", str(cmditem.line_no))
			subvars.add_substitution("$CANCEL_HALT_STATE", "ON" if status.cancel_halt else "OFF")
			subvars.add_substitution("$ERROR_HALT_STATE", "ON" if status.halt_on_err else "OFF")
			subvars.add_substitution("$METACOMMAND_ERROR_HALT_STATE", "ON" if status.halt_on_metacommand_err else "OFF")
			subvars.add_substitution("$CONSOLE_WAIT_WHEN_ERROR_HALT_STATE", "ON" if conf.gui_wait_on_error_halt else "OFF")
			subvars.add_substitution("$CONSOLE_WAIT_WHEN_DONE_STATE", "ON" if conf.gui_wait_on_exit else "OFF")
			subvars.add_substitution("$CURRENT_TIME", datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
			subvars.add_substitution("$CURRENT_DIR", os.path.abspath(os.path.curdir))
			subvars.add_substitution("$CURRENT_ALIAS", dbs.current_alias())
			subvars.add_substitution("$AUTOCOMMIT_STATE", "ON" if dbs.current().autocommit else "OFF")
			subvars.add_substitution("$TIMER", unicode(datetime.timedelta(seconds=timer.elapsed())))
			subvars.add_substitution("$DB_USER", dbs.current().user if dbs.current().user else '')
			subvars.add_substitution("$DB_SERVER", dbs.current().server_name if dbs.current().server_name else '')
			subvars.add_substitution("$DB_NAME", dbs.current().db_name)
			subvars.add_substitution("$DB_NEED_PWD", "TRUE" if dbs.current().need_passwd else "FALSE")
			subvars.add_substitution("$RANDOM", str(random.random()))
			subvars.add_substitution("$UUID", str(uuid.uuid4()))
			self.last_command = cmditem
			while True:
				match_found = False
				cmditem.sql, match_found = subvars.substitute(cmditem.sql)
				# Check all counter variable substitutions
				m = self._COUNTER_RX.search(cmditem.sql, re.I)
				if m:
					ctr_id = m.group(1).lower()
					if not ctr_id in self.counters.keys():
						self.counters[ctr_id] = 0
					new_count = self.counters[ctr_id] + 1
					self.counters[ctr_id] = new_count
					cmditem.sql = cmditem.sql.replace(u'!!$'+ctr_id+u'!!', unicode(new_count))
					match_found = True
				if not match_found:
					break
			self.cmds_run += 1
			self.curr_pos = cmd_index + 1
			if self.all_true():
				if cmditem.command_type == 'sql':
					self.runone(cmditem.sql, (None, self.outfile)[self.outfile is not None and self.curr_pos == len(self.command_list)])
				elif cmditem.command_type == 'cmd':
					e = None
					try:
						self.evaluate_metacommands(cmditem)
					except SystemExit:
						raise
					except ErrInfo as e:
						pass
					except:
						e = ErrInfo(type="exception", exception_msg=exception_desc())
					if e:
						raise e
			else:
				# Run only metacommands allowed in False exec levels
				if cmditem.command_type == 'cmd':
					e = None
					try:
						self.evaluate_metacommands(cmditem, when_false_only=True)
					except ErrInfo as e:
						pass
					except SystemExit:
						raise
					except:
						e = ErrInfo(type="cmd", exception_msg=exception_desc())
					if e:
						raise e
			# De-allocate memory for the command just completed.
			self.command_list[cmd_index] = None
		return None
	def register_sub_cmd(self, sub_cmd):
		# Identifies the function that carries out the 'SUB' metacommand.
		# This is needed only for the .showcommands() method.
		self.sub_metacommand = sub_cmd
	def commands_run(self):
		return self.cmds_run

# End of scripting classes.
#===============================================================================================


#===============================================================================================
#-----  UI

# All GUI (Tkinter) displays are created in a single thread separate from the main thread.
# This thread runs a GUI manager process that a) monitors a threading.Event waiting for
# a shutdown signal, and b) monitors a Queue waiting for messages and data telling it
# what GUI operations to launch.  The messages consist of a message type and a dictionary
# of data.  The message type determines what type of GUI to display.  The message data
# include arguments to be used during UI creation, and either an event or a queue to
# be used to return information when the GUI component is done.

# GUI/message types
GUI_DISPLAY, GUI_CONNECT, GUI_CONSOLE, GUI_SELECTSUB, GUI_PAUSE, GUI_HALT, GUI_ENTRY, QUERY_CONSOLE, \
	GUI_OPENFILE, GUI_SAVEFILE, GUI_DIRECTORY = range(11)

gui_manager_queue = None
gui_manager_stop_event = None
gui_manager_thread = None

class GuiSpec(object):
	def __init__(self, gui_type, gui_args, return_queue, return_event=None):
		self.gui_type = gui_type
		self.gui_args = gui_args
		self.return_queue = return_queue
		self.return_event = return_event

def gui_manager():
	# This function is to be run only as a thread.
	import Tkinter as tk
	import ttk
	import tkFont
	import tkFileDialog
	class Var(object):
		def __init__(self):
			self.run_gui_manager = True
			self.console = None
			self.console_running = False
	varobj = Var()
	def unset_console():
		global output
		varobj.console = None
		varobj.console_running = False
		output.reset()
	def monitor(var):
		def self_callback():
			if var.run_gui_manager:
				monitor(var)
				return True
			else:
				return False
		if gui_manager_stop_event.is_set():
			if var.console or var.console_running:
				if var.console:
					var.console.kill()
				var.console = None
				var.console_running = False
			var.run_gui_manager = False
		else:
			if not gui_manager_queue.empty():
				msg = gui_manager_queue.get(False)
				if msg.gui_type == GUI_DISPLAY:
					ui = DisplayUI(**msg.gui_args)
					btn, rv = ui.activate()
					msg.return_queue.put({"button": btn, "return_value": rv})
					ui = None
				elif msg.gui_type == GUI_CONNECT:
					ui = ConnectUI(**msg.gui_args)
					ui.activate()
					msg.return_queue.put({"exit_status": ui.exit_status,
											"db_type": as_none(ui.db_type_var.get()),
											"server": as_none(ui.server.get()),
											"port": as_none(ui.port.get()),
											"db": as_none(ui.db.get()),
											"db_file": as_none(ui.db_file.get()),
											"user": as_none(ui.user.get()),
											"pw": as_none(ui.pw.get()),
											"encoding": as_none(ui.encoding.get())})
					ui = None
				elif msg.gui_type == GUI_CONSOLE:
					if not var.console_running:
						var.console_return_event = msg.return_event
						args = msg.gui_args
						args["monitor_callback"] = self_callback
						args["unset_callback"] = unset_console
						var.console_running = True
						var.console = ConsoleUI(**args)
						var.console = None
						var.console_running = False
				elif msg.gui_type == GUI_SELECTSUB:
					ui = DisplayUI(**msg.gui_args)
					ui.tbl.config(selectmode="browse")
					# Disable the OK button until something is clicked in the table.
					ok_btn = ui.buttons[0]
					ok_btn.config(state='disabled')
					def save_selection(*args):
						ui.return_value = ui.tbl.selection()
						ui.tbl.selection_set(ui.return_value)
						ok_btn.config(state='normal')
					ui.tbl.bind("<ButtonRelease-1>", save_selection)
					# Make a double-click on the table save the selection and execute the 'OK' button action.
					# A custom attribute of the ttk.Button, created by DisplayUI(), is used.
					dbl_click_func = chainfuncs(save_selection, ok_btn.command_func)
					ui.tbl.bind("<Double-1>", dbl_click_func)
					btn, rv = ui.activate()
					msg.return_queue.put({"button": btn, "return_value": rv})
					ui = None
				elif msg.gui_type == GUI_PAUSE:
					ui = PauseUI(**msg.gui_args)
					btn, timed_out = ui.activate()
					quitted = btn is None and not timed_out
					msg.return_queue.put({"quitted": quitted})
					ui = None
				elif msg.gui_type == GUI_HALT:
					ui = DisplayUI(**msg.gui_args)
					ui.msg_label.configure(foreground="red")
					btn, rv = ui.activate()
					msg.return_queue.put({"button": btn})
					ui = None
				elif msg.gui_type == GUI_ENTRY:
					ui = EntryFormUI(**msg.gui_args)
					btn, rv = ui.activate()
					msg.return_queue.put({"button": btn, "return_value": rv})
					ui = None
				elif msg.gui_type == QUERY_CONSOLE:
					# Is the console running?
					msg.return_queue.put({"console_running": var.console_running})
				elif msg.gui_type == GUI_OPENFILE:
					ui = OpenFileUI(**msg.gui_args)
					fn = ui.activate()
					msg.return_queue.put({"filename": fn})
					ui = None
				elif msg.gui_type == GUI_SAVEFILE:
					ui = SaveFileUI(**msg.gui_args)
					fn = ui.activate()
					msg.return_queue.put({"filename": fn})
					ui = None
				elif msg.gui_type == GUI_DIRECTORY:
					ui = GetDirectoryUI(**msg.gui_args)
					dir = ui.activate()
					msg.return_queue.put({"directory": dir})
					ui = None
				gui_manager_queue.task_done()
	while varobj.run_gui_manager:
		if gui_manager_stop_event.is_set():
			varobj.run_gui_manager = False
		else:
			monitor(varobj)
	if varobj.console:
		unset_console()


def enable_gui():
	global gui_manager_thread, gui_manager_queue, gui_manager_stop_event
	if not gui_manager_thread:
		gui_manager_queue = Queue.Queue()
		gui_manager_stop_event = threading.Event()
		gui_manager_thread = threading.Thread(target=gui_manager)
		gui_manager_thread.start()

def disable_gui():
	global gui_manager_thread, gui_manager_stop_event
	if gui_manager_thread:
		gui_manager_stop_event.set()
		gui_manager_thread.join()
		gui_manager_thread = None


class DisplayUI(object):
	def __init__(self, title, message, button_list, selected_button=0, no_cancel=False, column_headers=None, rowset=None, textentry=None, hidetext=False):
		# button_list is a *list* of 3-tuples where the first item is the button label,
		# 	the second item is the button's value, and the third (optional) value is the key
		# 	to bind to the button.  Key identifiers must be in the form taken by the Tk bind()
		# 	function, e.g., "<Return>" and "<Escape>" for those keys, respectively.
		# no_cancel is a boolean indicating whether or not a 'Cancel' button should be added.
		# 	This class will, by default add a 'Cancel' button with the Esc key bound to it,
		#	and a return value of None.
		# selected_button is an integer identifying which button should get the focus (0-based).
		# textentry is a boolean; if True, an entry box will be added after the message.
		import Tkinter as tk
		import ttk
		import tkFont
		import tkFileDialog
		self.column_headers = column_headers
		self.rowset = rowset
		self.return_value = None
		self.win = tk.Toplevel()
		self.win.title(title)
		self.msg_label = None
		self.entryvar = None		# The tk.StringVar object used for text entry.
		self.entryctrl = None	# The ttk.Entry object used for text entry.
		self.tbl = None			# The ttk.Treeview widget that may display data.
		self.buttons = []		# A list of ttk.Button objects, with an extra attribute "command_func"
		#							(because the Button callback function is not queryable)
		self.focus_button = selected_button
		self.button_clicked_value = None
		def wrap_msg(event):
			self.msg_label.configure(wraplength=event.width - 5)
		# Message frame and control.
		msgframe = ttk.Frame(master=self.win, padding="3 3 3 3")
		self.msg_label = ttk.Label(msgframe, text=message)
		self.msg_label.bind("<Configure>", wrap_msg)
		self.msg_label.grid(column=0, row=0, sticky=tk.EW)
		# Button frame
		btnframe = ttk.Frame(master=self.win, padding="3 3 3 3")
		# Add text entry box if needed.
		if textentry:
			self.entryvar = tk.StringVar()
			self.entryctrl = ttk.Entry(msgframe, width=60, textvariable=self.entryvar)
			if hidetext:
				self.entryctrl.configure(show="*")
			self.entryctrl.grid(column=0, row=1, sticky=tk.W, padx=3, pady=3)
		# Add data table if needed.
		if rowset and column_headers:
			# Get the data to display.
			nrows = range(len(rowset))
			ncols = range(len(column_headers))
			hdrwidths = [len(column_headers[j]) for j in ncols]
			datawidthtbl = [[len(rowset[i][j] if isinstance(rowset[i][j], basestring) else unicode(rowset[i][j])) for i in nrows] for j in ncols]
			datawidths = [max(cwidths) for cwidths in datawidthtbl]
			colwidths = [max(hdrwidths[i], datawidths[i]) for i in ncols]
			# Set the font.
			ff = tkFont.nametofont("TkFixedFont")
			tblstyle = ttk.Style()
			tblstyle.configure('tblstyle', font=ff)
			charpixels = int(1.3 * ff.measure(u"0"))
			pixwidths = [charpixels * col for col in colwidths]
			tableframe = ttk.Frame(master=self.win, padding="3 3 3 3")
			statusframe = ttk.Frame(master=self.win)
			# Create and configure the Treeview table widget
			self.tbl = ttk.Treeview(tableframe, columns=column_headers, selectmode="none", show="headings")
			self.tbl.configure()["style"] = tblstyle
			ysb = ttk.Scrollbar(tableframe, orient='vertical', command=self.tbl.yview)
			xsb = ttk.Scrollbar(tableframe, orient='horizontal', command=self.tbl.xview)
			self.tbl.configure(yscrollcommand=ysb.set, xscrollcommand=xsb.set)
			# Fill the Treeview table widget with data
			for i in range(len(column_headers)):
				self.tbl.column(column_headers[i], width=pixwidths[i])
				self.tbl.heading(column_headers[i], text=column_headers[i])
			for i, row in enumerate(rowset):
				enc_row = [c if c is not None else '' for c in row]
				self.tbl.insert(parent='', index='end', iid=str(i), values=enc_row)
			tableframe.grid(column=0, row=1, sticky=tk.NSEW)
			self.tbl.grid(column=0, row=0, sticky=tk.NSEW)
			ysb.grid(column=1, row=0, sticky=tk.NS)
			xsb.grid(column=0, row=1, sticky=tk.EW)
			statusframe.grid(column=0, row=3, sticky=tk.EW)
			tableframe.columnconfigure(0, weight=1)
			tableframe.rowconfigure(0, weight=1)
			# Status bar
			statusmsg = "    %d rows" % len(rowset)
			statusbar = ttk.Label(statusframe, text=statusmsg, relief=tk.RIDGE, anchor=tk.W)
			statusbar.pack(side=tk.BOTTOM, fill=tk.X)
			# Allow resizing of the table
			tableframe.columnconfigure(0, weight=1)
			tableframe.rowconfigure(0, weight=1)
			# Menu bar and functions
			def save_as():
				script, line_no = working_script.current_script_line()
				working_dir = os.path.dirname(os.path.abspath(script))
				outfile = tkFileDialog.asksaveasfilename(initialdir=working_dir, parent=self.win, title="File to save",
					filetypes=[('CSV files', '.csv'), ('ODS files', '.ods'), ('HTML files', '.html'), ('Text files', '.txt'),
							('TSV files', '.tsv')])
				if outfile:
					if outfile[-4:].lower() == 'html' or outfile[-3:].lower() == 'htm':
						export_html(outfile, self.column_headers, self.rowset, append=False, desc=message)
					elif outfile[-3:].lower() == 'csv':
						write_delimited_file(outfile, "csv", self.column_headers, self.rowset)
					elif outfile[-3:].lower() == 'tsv':
						write_delimited_file(outfile, "tsv", self.column_headers, self.rowset)
					elif outfile[-3:].lower() == 'ods':
						export_ods(outfile, self.column_headers, self.rowset, append=True, sheetname=title, desc=message)
					elif outfile[-3:].lower() == 'txt':
						prettyprint_rowset(self.column_headers, self.rowset, outfile, append=False, desc=message)
					else:
						# Force write as CSV.
						outfile = outfile + ".csv"
						write_delimited_file(outfile, "csv", self.column_headers, self.rowset)
			mnu = tk.Menu(self.win)
			mnu.add_command(label="Save as...", command=save_as)
			self.win.config(menu=mnu)
		else:
			# Don't allow user resizing if no data table is displayed.
			self.win.resizable(width=0, height=0)
		# Put the frames and other widgets in place.
		msgframe.grid(column=0, row=0, sticky=tk.EW)
		btnframe.grid(column=0, row=2, sticky=tk.E)
		# Create buttons.
		if not no_cancel:
			button_list.append(('Cancel', None, "<Escape>"))
		for colno, btn_spec in enumerate(button_list):
			btn_action = self.ClickSet(self, btn_spec[1]).click
			btn = ttk.Button(btnframe, text=btn_spec[0], command=btn_action)
			btn.command_func = btn_action
			if btn_spec[2] is not None:
				self.win.bind(btn_spec[2], btn_action)
			self.buttons.append(btn)
			btn.grid(column=colno, row=0, sticky=tk.E, padx=3)
		# Allow resizing.
		self.win.columnconfigure(0, weight=1)
		self.win.rowconfigure(1, weight=1)
		msgframe.columnconfigure(0, weight=1)
		btnframe.columnconfigure(0, weight=1)
		# Other key bindings
		self.win.protocol("WM_DELETE_WINDOW", self.cancel)
		# Position window.
		self.win.update_idletasks()
		m = re.match(r"(\d+)x(\d+)\+(-?\d+)\+(-?\d+)", self.win.geometry())
		if m is not None:
			wwd = int(m.group(1))
			wht = int(m.group(2))
			swd = self.win.winfo_screenwidth()
			sht = self.win.winfo_screenheight()
			xpos = (swd/2) - (wwd/2)
			ypos = (sht/2) - (wht/2)
			self.win.geometry("%dx%d+%d+%d" % (wwd, wht, xpos, ypos))
		# Limit resizing
		self.win.minsize(width=500, height=0)
	def cancel(self):
		self.win.destroy()
	class ClickSet(object):
		def __init__(self, ui_obj, button_value):
			self.ui_obj = ui_obj
			self.button_value = button_value
		def click(self, *args):
			self.ui_obj.button_clicked_value = self.button_value
			self.ui_obj.win.destroy()
	def activate(self):
		# Window control
		self.win.grab_set()
		self.win._root().withdraw()
		self.win.focus_force()
		if self.entryctrl:
			self.entryctrl.focus()
		else:
			if self.focus_button:
				self.buttons[self.focus_button].focus()
		self.win.wait_window(self.win)
		if self.entryvar:
			self.return_value = self.entryvar.get()
		self.win.update_idletasks()
		# Deallocate self.entryvar to avoid error message from Tkinter.
		self.entryvar = None
		return (self.button_clicked_value, self.return_value)


class ConnectUI(object):
	# Types of prompts for different database requirements.
	FILE, SERVER, FILE_PW = range(3)
	def __init__(self, title, message):
		import Tkinter as tk
		import ttk
		self.exit_status = 0	# Canceled
		self.exit_svr = None	# For caller
		self.exit_db = None	# For caller
		if working_script:
			self.script, self.lno = working_script.current_script_line()
			self.working_dir = os.path.dirname(os.path.abspath(self.script))
		else:
			self.script = self.lno = None
			self.working_dir = "."
		self.title = title
		self.xpos = None
		self.ypos = None
		# Values of db_params indicate whether server information is needed.
		self.db_params = {u"PostgreSQL": self.SERVER, u"MS-Access": self.FILE_PW, u"SQLite": self.FILE,
							u"SQL Server": self.SERVER, u"MySQL": self.SERVER, u"Firebird": self.SERVER}
		self.win = tk.Toplevel()
		self.win.title(title)
		# Use vertically-stacked frames for:
		#	* the message
		#	* the database type selector and server/db/file entries
		#	* Connect and Cancel buttons
		#	* the status bar.
		#
		# Set up message frame
		if message:
			msgframe = ttk.Frame(master=self.win, padding="3 3 3 3")
			self.msg_label = ttk.Label(msgframe, text=message, anchor=tk.W, justify=tk.LEFT, wraplength=500)
			self.msg_label.grid(column=0, row=0, sticky=tk.EW)
			msgframe.grid(column=0, row=0, sticky=tk.EW)
		# Set up database selector frame
		# On the left side will be a combobox to choose the database type.
		# On the right side will be a prompt for the server, db, user name, and pw,
		# or for the filename (and possibly user name and pw).  Each of these alternative
		# types of prompts will be in its own frame, which will be in the same place.
		# Only one will be shown, controlled by the item in the self.db_params dictionary.
		dbframe = ttk.Frame(master=self.win, padding="3 3 3 3")
		dbtypeframe = ttk.Frame(master=dbframe)
		paramframe = ttk.Frame(master=dbframe)
		self.db_type_var = tk.StringVar()
		self.encoding = tk.StringVar()
		self.status_msg = tk.StringVar()
		# Database type selection
		ttk.Label(dbtypeframe, text="DBMS:").grid(column=0, row=0, padx=3, pady=3, sticky=tk.NE)
		dbmss = self.db_params.keys()
		dbmss.sort()
		self.db_choices = ttk.Combobox(dbtypeframe, textvariable=self.db_type_var, width=12,
						values=dbmss)
		self.db_choices.bind("<<ComboboxSelected>>", self.param_choices)
		self.db_choices.config(state='readonly')
		self.db_choices.grid(column=1, row=0, padx=3, pady=3, sticky=tk.NW)
		ttk.Label(dbtypeframe, text="Encoding:").grid(column=0, row=1, padx=3, pady=3, sticky=tk.NE)
		self.db_choices.set('PostgreSQL')
		enc_choices = ttk.Combobox(dbtypeframe, textvariable=self.encoding, width=12,
						values=('UTF8', 'Latin1', 'Win-1252'))
		enc_choices.bind("<<ComboboxSelected>>", self.clearstatus)
		enc_choices.set('UTF8')
		enc_choices.grid(column=1, row=1, padx=3, pady=3, sticky=tk.NW)
		# Database parameter entry frames
		self.server = tk.StringVar()
		self.server.trace("w", self.clearstatus)
		self.port = tk.StringVar()
		self.port.trace("w", self.clearstatus)
		self.db = tk.StringVar()
		self.db.trace("w", self.clearstatus)
		self.user = tk.StringVar()
		self.user.trace("w", self.clearstatus)
		self.pw = tk.StringVar()
		self.pw.trace("w", self.clearstatus)
		self.db_file = tk.StringVar()
		self.db_file.trace("w", self.clearstatus)
		self.serverparamframe = ttk.Frame(master=paramframe)
		# Server databases
		ttk.Label(self.serverparamframe, text="Server:").grid(column=0, row=0, padx=3, pady=3, sticky=tk.E)
		ttk.Entry(self.serverparamframe, width=30, textvariable=self.server).grid(column=1, row=0, padx=3, pady=3, sticky=tk.W)
		ttk.Label(self.serverparamframe, text="Database:").grid(column=0, row=1, padx=3, pady=3, sticky=tk.E)
		ttk.Entry(self.serverparamframe, width=30, textvariable=self.db).grid(column=1, row=1, padx=3, pady=3, sticky=tk.W)
		ttk.Label(self.serverparamframe, text="User:").grid(column=0, row=2, padx=3, pady=3, sticky=tk.E)
		ttk.Entry(self.serverparamframe, width=30, textvariable=self.user).grid(column=1, row=2, padx=3, pady=3, sticky=tk.W)
		ttk.Label(self.serverparamframe, text="Password:").grid(column=0, row=3, padx=3, pady=3, sticky=tk.E)
		ttk.Entry(self.serverparamframe, width=30, textvariable=self.pw, show="*").grid(column=1, row=3, padx=3, pady=3, sticky=tk.W)
		ttk.Label(self.serverparamframe, text="Port:").grid(column=0, row=4, padx=3, pady=3, sticky=tk.E)
		ttk.Entry(self.serverparamframe, width=4, textvariable=self.port).grid(column=1, row=4, padx=3, pady=3, sticky=tk.W)
		# File databases
		self.fileparamframe = ttk.Frame(master=paramframe)
		ttk.Label(self.fileparamframe, text="Database file:").grid(column=0, row=0, padx=3, pady=3, sticky=tk.NW)
		ttk.Entry(self.fileparamframe, width=40, textvariable=self.db_file).grid(column=0, row=1, padx=3, pady=3, sticky=tk.NW)
		ttk.Button(self.fileparamframe, text="Browse...", command=self.set_sel_fn).grid(column=1, row=1)
		# File databases with user name and password
		self.filepwparamframe = ttk.Frame(master=paramframe)
		ttk.Label(self.filepwparamframe, text="Database file:").grid(column=0, row=0, padx=3, pady=3, sticky=tk.NW)
		ttk.Entry(self.filepwparamframe, width=40, textvariable=self.db_file).grid(column=1, row=0, padx=3, pady=3, sticky=tk.NW)
		ttk.Button(self.filepwparamframe, text="Browse...", command=self.set_sel_fn).grid(column=2, row=0)
		ttk.Label(self.filepwparamframe, text="User:").grid(column=0, row=1, padx=3, pady=3, sticky=tk.E)
		ttk.Entry(self.filepwparamframe, width=30, textvariable=self.user).grid(column=1, row=1, padx=3, pady=3, sticky=tk.W)
		ttk.Label(self.filepwparamframe, text="Password:").grid(column=0, row=2, padx=3, pady=3, sticky=tk.E)
		ttk.Entry(self.filepwparamframe, width=30, textvariable=self.pw, show="*").grid(column=1, row=2, padx=3, pady=3, sticky=tk.W)
		# Put serverparamframe, fileparamframe, and filepwparamframe in the same place in paramframe
		self.fileparamframe.grid(row=0, column=0, sticky=tk.NW)
		self.fileparamframe.grid_remove()
		self.filepwparamframe.grid(row=0, column=0, sticky=tk.NW)
		self.filepwparamframe.grid_remove()
		self.serverparamframe.grid(row=0, column=0, sticky=tk.NW)
		self.db_type_var.set(u"PostgreSQL")
		self.param_choices()
		dbtypeframe.grid(column=0, row=0, padx=5, sticky=tk.NW)
		paramframe.grid(column=1, row=0, padx=5, sticky=tk.E)
		dbframe.grid(column=0, row=1, sticky=tk.W)
		# Create Connect and Cancel buttons
		btnframe = ttk.Frame(master=self.win, padding="3 3 3 3")
		ttk.Button(btnframe, text='Connect', command=self.connect).grid(row=0, column=0, sticky=tk.E, padx=3)
		ttk.Button(btnframe, text='Cancel', command=self.cancel).grid(row=0, column=1, sticky=tk.E, padx=3)
		self.win.protocol("WM_DELETE_WINDOW", self.cancel)
		btnframe.grid(column=0, row=2, sticky=tk.E)
		# Create status bar
		statusframe = ttk.Frame(master=self.win)
		statusbar = ttk.Label(statusframe, text='', textvariable=self.status_msg, foreground="red", relief=tk.RIDGE, anchor=tk.W)
		statusbar.pack(side=tk.BOTTOM, fill=tk.X)
		statusframe.grid(column=0, row=3, sticky=tk.EW)
		# Bindings
		self.win.bind('<Return>', self.connect)
		self.win.bind('<Escape>', self.cancel)
		# Limit resizing
		self.win.resizable(width=0, height=0)
		self.redraw()
	def redraw(self):
		# Position window.
		self.win.update_idletasks()
		m = re.match(r"(\d+)x(\d+)([-+]\d+)([-+]\d+)", self.win.geometry())
		wwd = int(m.group(1))
		wht = int(m.group(2))
		if not self.xpos:
			swd = self.win.winfo_screenwidth()
			sht = self.win.winfo_screenheight()
			self.xpos = (swd/2) - (wwd/2)
			self.ypos = (sht/2) - (wht/2)
		self.win.geometry("+%d+%d" % (self.xpos, self.ypos))
	def set_sel_fn(self):
		global tkFileDialog
		import tkFileDialog
		fn = tkFileDialog.askopenfilename(initialdir=self.working_dir,
				parent=self.fileparamframe, title=self.title)
		if fn:
			self.db_file.set(fn)
			self.clearstatus()
	def param_choices(self, *args, **kwargs):
		svr_params = self.db_params[self.db_type_var.get()]
		if svr_params == self.SERVER:
			self.fileparamframe.grid_remove()
			self.filepwparamframe.grid_remove()
			self.serverparamframe.grid()
		elif svr_params == self.FILE_PW:
			self.serverparamframe.grid_remove()
			self.fileparamframe.grid_remove()
			self.filepwparamframe.grid()
		else:
			self.serverparamframe.grid_remove()
			self.filepwparamframe.grid_remove()
			self.fileparamframe.grid()
		self.clearstatus()
	def clearstatus(self, *args, **kwargs):
		self.status_msg.set('')
	def connect(self, *args):
		self.exit_status = 1
		self.cancel()
	def cancel(self, *args):
		self.win.destroy()
		self.win.update_idletasks()
	def activate(self):
		self.win.grab_set()
		self.win._root().withdraw()
		self.win.focus_force()
		self.db_choices.focus()
		self.win.wait_window(self.win)


class ConsoleUIError(Exception):
	def __init__(self, msg):
		self.value = msg
	def __repr__(self):
		return "ConsoleUIError(%r)" % self.value

class ConsoleUI(object):
	def __init__(self, monitor_callback, unset_callback, kill_event, stop_update_event, msg_queue, return_queue, title=None):
		import Tkinter as tk
		import ttk
		import tkFileDialog
		self.monitor_callback = monitor_callback
		self.unset_callback = unset_callback
		self.kill_event = kill_event
		self.stop_update_event = stop_update_event
		self.msg_queue = msg_queue
		self.return_queue = return_queue
		self.update_id = None
		self.win = tk.Toplevel()
		self.status_msg = tk.StringVar()
		self.status_msg.set('')
		self.ctrvalue = tk.DoubleVar()
		self.ctrvalue.set(0)
		self.win.title(title if title else "execsql console")
		console_frame = ttk.Frame(master=self.win, padding="2 2 2 2")
		console_frame.grid(column=0, row=0, sticky=tk.NSEW)
		self.textarea = tk.Text(console_frame, width=100, height=25, wrap='none')
		# Status bar and progressbar
		statusframe = ttk.Frame(master=self.win)
		sttextframe = ttk.Frame(master=statusframe)
		stprogframe = ttk.Frame(master=statusframe)
		statusbar = ttk.Label(sttextframe, text='', textvariable=self.status_msg, width=75, relief=tk.RIDGE, anchor=tk.W)
		ctrprogress = ttk.Progressbar(stprogframe, length=125, mode='determinate', maximum=100,
											orient='horizontal', variable=self.ctrvalue)
		statusbar.grid(column=0, row=0, sticky=tk.EW)
		ctrprogress.grid(column=0, row=0, sticky=tk.EW)
		sttextframe.grid(column=0, row=0, sticky=tk.EW)
		stprogframe.grid(column=4, row=0, columnspan=1, sticky=tk.EW)
		statusframe.grid(column=0, row=1, sticky=tk.EW)
		# Scrollbars
		vscroll = tk.Scrollbar(console_frame, orient="vertical", command=self.textarea.yview)
		hscroll = tk.Scrollbar(console_frame, orient="horizontal", command=self.textarea.xview)
		self.textarea.configure(yscrollcommand=vscroll.set)
		self.textarea.configure(xscrollcommand=hscroll.set)
		self.textarea.grid(column=0, row=0, sticky=tk.NSEW)
		vscroll.grid(column=1, row=0, sticky=tk.NS)
		hscroll.grid(column=0, row=2, sticky=tk.EW)
		# Make text area readonly
		self.textarea.configure(state='disabled')
		# Allow resizing
		self.win.columnconfigure(0, weight=1)
		self.win.rowconfigure(0, weight=1)
		console_frame.columnconfigure(0, weight=1)
		console_frame.rowconfigure(0, weight=1)
		statusframe.columnconfigure(0, weight=1)
		sttextframe.columnconfigure(0, weight=3)
		stprogframe.columnconfigure(0, weight=1)
		# Menu bar and functions
		def save_as():
			script, lno = working_script.current_script_line()
			working_dir = os.path.dirname(os.path.abspath(script))
			outfile = tkFileDialog.asksaveasfilename(initialdir=working_dir, parent=self.win, title="File to save", filetypes=[('Text files', '.txt')])
			if outfile:
				alltext = self.textarea.get(1.0, 'end')
				f = open(outfile, "w")
				f.write(alltext)
				f.close()
		mnu = tk.Menu(self.win)
		mnu.add_command(label="Save as...", command=save_as)
		self.win.config(menu=mnu)
		# Kill on window close or Esc
		self.win.protocol("WM_DELETE_WINDOW", self.kill)
		self.win.bind('<Escape>', self.kill)
		self.win.bind("<Return>", self.do_continue)
		# Display and center the window
		self.win.update_idletasks()
		m = re.match(r"(\d+)x(\d+)([-+]\d+)([-+]\d+)", self.win.geometry())
		wwd = int(m.group(1))
		wht = int(m.group(2))
		swd = self.win.winfo_screenwidth()
		sht = self.win.winfo_screenheight()
		xpos = (swd/2) - (wwd/2)
		ypos = (sht/2) - (wht/2)
		self.win.geometry("%dx%d+%d+%d" % (wwd, wht, xpos, ypos))
		self.win.grab_set()
		self.win._root().withdraw()
		self.update_id = self.win.after(100, self.update)
		self.win.wait_window(self.win)
	def kill(self, *args):
		# Close console and push True into return queue
		if self.update_id:
			self.win.after_cancel(self.update_id)
			self.update_id = None
		self.win.destroy()
		self.win.update_idletasks()
		self.unset_callback()
		self.return_queue.put(True)
	def do_continue(self, *args):
		# Push False into return queue to indicate continuation without closing console.
		self.return_queue.put(False)
	def update(self):
		self.update_id = None
		while not self.msg_queue.empty():
			msg = self.msg_queue.get(False)
			# msg is a 2-tuple of type (string) and value (any).
			msgtype, msgval = msg
			if msgtype == 'write':
				self.textarea.configure(state='normal')
				self.textarea.insert('end', msgval)
				self.textarea.see('end')
				self.textarea.configure(state='disabled')
			elif msgtype == 'status':
				self.status_msg.set(msgval)
			elif msgtype == 'progress':
				msgval = msgval if msgval <=100 else 100
				self.ctrvalue.set(msgval)
			elif msgtype == 'hide':
				self.win.withdraw()
			elif msgtype == 'show':
				self.win.deiconify()
			elif msgtype == 'save_all':
				alltext = self.textarea.get(1.0, 'end')
				fmode = "a" if msgval["append"] else "w"
				f = open(msgval["filename"], fmode)
				f.write(alltext)
				f.close()
			self.msg_queue.task_done()
		if self.kill_event.is_set():
			self.kill()
		else:
			if self.monitor_callback():
				self.update_id = self.win.after(100, self.update)
			else:
				self.kill()

class GuiConsole(object):
	# This is the main-thread interface to the GUI console that runs in a separate thread.
	def __init__(self, title=None):
		self.title = title
		self.msg_queue = Queue.Queue()
		self.resp_queue = Queue.Queue()
		self.kill_event = threading.Event()
		self.stop_update_event = threading.Event()
		#self.console_killed_event = threading.Event()
		gui_manager_queue.put(GuiSpec(gui_type=GUI_CONSOLE,
							gui_args={"kill_event": self.kill_event,
									   "stop_update_event": self.stop_update_event,
									   "msg_queue": self.msg_queue,
									   "return_queue": self.resp_queue,
									   "title": self.title},
							return_queue=None,
							return_event=None
							))
	def write(self, msg):
		self.msg_queue.put(('write', msg))
	def write_status(self, msg):
		self.msg_queue.put(('status', msg))
	def set_progress(self, progress_value):
		self.msg_queue.put(('progress', progress_value))
	def save_as(self, filename, append):
		self.msg_queue.put(('save_all', {"filename": filename, "append": append}))
	def deactivate(self):
		self.kill_event.set()
	def hide(self):
		self.msg_queue.put(('hide', None))
	def show(self):
		self.msg_queue.put(('show', None))
	def wait_for_user(self):
		self.stop_update_event.set()
		while self.resp_queue.empty():
			time.sleep(0)
		exit_status = self.resp_queue.get(False)
		self.resp_queue.task_done()
		return exit_status


class PauseUI(object):
	def __init__(self, title, message, countdown=None):
		# Countdown must be an integer indicating the maximum number of seconds
		# that the UI will be displayed.
		#global tk, ttk
		import Tkinter as tk
		import ttk
		self.countdown = countdown
		self.button_value = None
		self.timed_out = False
		self.start_time = None
		self.elapsed_time = None
		self.after_id = None
		self.win = tk.Toplevel()
		self.win.title(title if title else "Pausing...")
		self.msg_label = None
		# Message frame and control.
		msgframe = ttk.Frame(master=self.win, padding="3 3 3 3")
		self.msg_label = ttk.Label(msgframe, text=message, wraplength=400)
		self.msg_label.grid(column=0, row=0, sticky=tk.EW)
		msgframe.grid(column=0, row=0, sticky=tk.EW)
		if countdown:
			ctrframe = ttk.Frame(master=self.win, padding="3 3 3 3")
			self.ctrvalue = tk.DoubleVar()
			self.ctrvaluestr = tk.StringVar()
			self.ctrlabel = ttk.Label(ctrframe, textvariable=self.ctrvaluestr, width=6,
										anchor=tk.NE, justify=tk.RIGHT)
			self.ctrprogress = ttk.Progressbar(ctrframe, length=300, mode='determinate',
												orient=tk.HORIZONTAL, variable=self.ctrvalue)
			self.after_id = self.win.after(100, self.count)
			self.ctrlabel.grid(column=0, row=0, sticky=tk.E)
			self.ctrprogress.grid(column=1, row=0, sticky=tk.W, padx=3)
			ctrframe.grid(column=0, row=1, sticky=tk.EW)
		# Button frame
		btnframe = ttk.Frame(master=self.win, padding="3 3 3 3")
		cancel_btn = ttk.Button(btnframe, text="Cancel", command=self.cancel)
		cancel_btn.grid(column=1, row=0, sticky=tk.E, padx=3)
		self.win.bind("<Escape>", self.cancel)
		continue_btn = ttk.Button(btnframe, text="Continue", command=self.do_continue)
		continue_btn.grid(column=0, row=0, sticky=tk.E, padx=3)
		self.win.bind("<Return>", self.do_continue)
		btnframe.grid(column=0, row=2, sticky=tk.E)
		# Other bindings
		self.win.protocol("WM_DELETE_WINDOW", self.cancel)
		# Position window.
		self.win.update_idletasks()
		m = re.match(r"(\d+)x(\d+)([-+]\d+)([-+]\d+)", self.win.geometry())
		wwd = int(m.group(1))
		wht = int(m.group(2))
		swd = self.win.winfo_screenwidth()
		sht = self.win.winfo_screenheight()
		xpos = (swd/2) - (wwd/2)
		ypos = (sht/2) - (wht/2)
		self.win.geometry("%dx%d+%d+%d" % (wwd, wht, xpos, ypos))
		# Limit resizing
		self.win.resizable(width=0, height=0)
	def cancel(self, *args):
		self.win.destroy()
		self.win.update_idletasks()
	def do_continue(self, *args):
		self.button_value = 1
		self.win.destroy()
		self.win.update_idletasks()
	def count(self):
		self.elapsed_time = time.time() - self.start_time
		self.ctrvalue.set(100 * (1 - self.elapsed_time/self.countdown))
		self.ctrvaluestr.set(round(self.countdown - self.elapsed_time, 1))
		if self.elapsed_time > self.countdown:
			#self.ctrprogress.stop()
			self.ctrprogress.after_cancel(self.after_id)
			self.timed_out = True
			self.win.destroy()
			self.win.update_idletasks()
		else:
			self.after_id = self.win.after(100, self.count)
	def activate(self):
		# Window control
		self.win.grab_set()
		self.win._root().withdraw()
		self.win.focus_force()
		if self.countdown:
			self.start_time = time.time()
			self.ctrvalue.set(100.0)
			#self.ctrprogress.start()
		self.win.wait_window(self.win)
		return self.button_value, self.timed_out


class EntrySpec(object):
	def __init__(self, name, prompt, required=False, initial_value=None, default_width=None, 
					lookup_list=None, validation_regex=None, validation_key_regex=None, entry_type=None):
		# The only recognized value for entry_type is "checkbox".
		self.name = name
		self.prompt = prompt
		self.required = required
		self.value = initial_value
		self.width = default_width
		self.lookup_list = lookup_list
		if validation_regex:
			if validation_regex[0] != '^':
				validation_regex = '^' + validation_regex
			if validation_regex[-1] != '$':
				validation_regex = validation_regex + '$'
			self.validation_rx = re.compile(validation_regex, re.I)
		else:
			self.validation_rx = None
		if validation_key_regex:
			if validation_key_regex[0] != '^':
				validation_key_regex = '^' + validation_key_regex
			if validation_key_regex[-1] != '$':
				validation_key_regex = validation_key_regex + '$'
			self.validation_key_rx = re.compile(validation_key_regex, re.I)
		else:
			self.validation_key_rx = None
		self.entry_type = entry_type
		if not self.width and self.lookup_list:
			self.width = max([len(unicode(x)) for x in self.lookup_list])
	def __repr__(self):
		return "EntrySpec(%s, %s, %s, %s, %s, %s, %s, %s)" % (self.name, self.prompt, self.required, self.value,
				self.width, self.lookup_list, self.validation_rx.pattern if self.validation_rx else None, self.entry_type)


class EntryFormUI(object):
	def __init__(self, title, message, entry_specs, column_headers=None, rowset=None):
		# entry_specs is a list of EntrySpec objects
		import Tkinter as tk
		import ttk
		import tkFont
		import tkFileDialog
		self.button_value = 0
		self.entries = entry_specs
		self.column_headers = column_headers
		self.rowset = rowset
		self.return_value = None
		self.win = tk.Toplevel()
		self.win.title(title)
		self.msg_label = None
		self.tbl = None			# The ttk.Treeview widget that may display data.
		self.buttons = []		# A list of ttk.Button objects, with an extra attribute "command_func"
		#							(because the Button callback function is not queryable)
		self.button_clicked_value = None
		def validate_entry(value_rx, key_rx, required):
			def checker(reason, new_val):
				# Don't allow a keystroke that would produce an invalid value.
				# Don't allow leaving if the value is invalid.
				#if required and not new_val:
				#	return False
				if reason == 'key' and key_rx:
					return key_rx.match(new_val) is not None
				elif reason == 'focusout':
					if new_val is not None:
						if value_rx:
							return value_rx.match(new_val) is not None
					else:
						if required:
							return False
				return True
			return checker
		def validate_item(item_list, required):
			def checker(new_val):
				if required and not new_val:
					return False
				if new_val:
					return new_val in item_list
			return checker
		def setfocus(entry):
			def focuser():
				entry.entryctrl.focus()
			return focuser
		def wrap_msg(event):
			self.msg_label.configure(wraplength=event.width - 5)
		# Message frame and control.
		msgframe = ttk.Frame(master=self.win, padding="3 3 3 3")
		self.msg_label = ttk.Label(msgframe, text=message)
		self.msg_label.bind("<Configure>", wrap_msg)
		self.msg_label.grid(column=0, row=0, sticky=tk.EW)
		# Data entry frame
		entryframe = ttk.Frame(master=self.win, padding="3 3 3 3")
		for i, e in enumerate(self.entries):
			self.entries[i].entrylabel = ttk.Label(entryframe, text=e.prompt)
			self.entries[i].entryvar = tk.StringVar()
			if e.value is not None:
				self.entries[i].entryvar.set(e.value)
			if e.lookup_list:
				self.entries[i].entryctrl = ttk.Combobox(entryframe, textvariable=self.entries[i].entryvar, width=e.width, values=e.lookup_list)
				if e.required:
					self.entries[i].entryctrl.configure(validate='all')
					self.entries[i].entryctrl.configure(validatecommand=(e.entryctrl.register(validate_item(e.lookup_list, e.required)), '%P'))
			elif self.entries[i].entry_type is not None and self.entries[i].entry_type.lower() == "checkbox":
				self.entries[i].entryctrl = tk.Checkbutton(entryframe, text="", variable=self.entries[i].entryvar, onvalue="1", offvalue="0")
				if e.value is None or str(e.value) == "0":
					self.entries[i].entryvar.set("0")
				else:
					self.entries[i].entryvar.set("1")
			else:
				self.entries[i].entryctrl = ttk.Entry(entryframe, width=e.width if e.width else 20, textvariable=self.entries[i].entryvar)
				if e.validation_rx or e.required:
					self.entries[i].entryctrl.configure(validate='all')
					self.entries[i].entryctrl.configure(validatecommand=(e.entryctrl.register(validate_entry(e.validation_rx, e.validation_key_rx, e.required)), '%V', '%P'))
					self.entries[i].entryctrl.configure(invalidcommand=(e.entryctrl.register(setfocus(e))))
			self.entries[i].entryvar.trace("w", self.validate_all)
			self.entries[i].entrylabel.grid(column=0, row=i, sticky=tk.EW, padx=3)
			self.entries[i].entryctrl.grid(column=1, row=i, sticky=tk.W, padx=3, pady=3)
		# Add data table frame if needed.
		if rowset and column_headers:
			# Get the data to display.
			nrows = range(len(rowset))
			ncols = range(len(column_headers))
			hdrwidths = [len(column_headers[j]) for j in ncols]
			datawidthtbl = [[len(rowset[i][j] if isinstance(rowset[i][j], basestring) else unicode(rowset[i][j])) for i in nrows] for j in ncols]
			datawidths = [max(cwidths) for cwidths in datawidthtbl]
			colwidths = [max(hdrwidths[i], datawidths[i]) for i in ncols]
			# Set the font.
			ff = tkFont.nametofont("TkFixedFont")
			tblstyle = ttk.Style()
			tblstyle.configure('tblstyle', font=ff)
			charpixels = int(1.3 * ff.measure(u"0"))
			pixwidths = [charpixels * col for col in colwidths]
			tableframe = ttk.Frame(master=self.win, padding="3 3 3 3")
			statusframe = ttk.Frame(master=self.win)
			# Create and configure the Treeview table widget
			self.tbl = ttk.Treeview(tableframe, columns=column_headers, selectmode="none", show="headings")
			self.tbl.configure()["style"] = tblstyle
			ysb = ttk.Scrollbar(tableframe, orient='vertical', command=self.tbl.yview)
			xsb = ttk.Scrollbar(tableframe, orient='horizontal', command=self.tbl.xview)
			self.tbl.configure(yscrollcommand=ysb.set, xscrollcommand=xsb.set)
			# Fill the Treeview table widget with data
			for i in range(len(column_headers)):
				self.tbl.column(column_headers[i], width=pixwidths[i])
				self.tbl.heading(column_headers[i], text=column_headers[i])
			for i, row in enumerate(rowset):
				enc_row = [c if c is not None else '' for c in row]
				self.tbl.insert(parent='', index='end', iid=str(i), values=enc_row)
			#tableframe.grid(column=0, row=1, sticky=tk.NSEW )
			self.tbl.grid(column=0, row=0, sticky=tk.NSEW)
			ysb.grid(column=1, row=0, sticky=tk.NS)
			xsb.grid(column=0, row=1, sticky=tk.EW)
			#statusframe.grid(column=0, row=3, sticky=tk.EW)
			tableframe.columnconfigure(0, weight=1)
			tableframe.rowconfigure(0, weight=1)
			# Status bar
			statusmsg = "    %d rows" % len(rowset)
			statusbar = ttk.Label(statusframe, text=statusmsg, relief=tk.RIDGE, anchor=tk.W)
			statusbar.pack(side=tk.BOTTOM, fill=tk.X)
			# Allow resizing of the table
			tableframe.columnconfigure(0, weight=1)
			tableframe.rowconfigure(0, weight=1)
			# Menu bar and functions
			def save_as():
				script, lno = working_script.current_script_line()
				working_dir = os.path.dirname(os.path.abspath(script))
				outfile = tkFileDialog.asksaveasfilename(initialdir=working_dir, parent=self.win, title="File to save", filetypes=[('CSV files', '.csv'), ('ODS files', '.ods'), ('HTML files', '.html')])
				if outfile:
					if outfile[-4:] == 'html':
						export_html(outfile, self.column_headers, self.rowset, append=False)
					elif outfile[-3:].lower() == "csv":
						write_delimited_file(outfile, "csv", self.column_headers, self.rowset)
					else:
						# Don't append because the odf.py library errors when opening--maybe due to a long pathname.
						export_ods(outfile, self.column_headers, self.rowset, append=False, sheetname=title)
			mnu = tk.Menu(self.win)
			mnu.add_command(label="Save as...", command=save_as)
			self.win.config(menu=mnu)
		else:
			# Don't allow user resizing if no data table is displayed.
			self.win.resizable(width=0, height=0)
		# Button frame
		btnframe = ttk.Frame(master=self.win, padding="3 3 3 3")
		cancel_btn = ttk.Button(btnframe, text="Cancel", command=self.cancel)
		cancel_btn.grid(column=1, row=0, sticky=tk.E, padx=3)
		self.win.bind("<Escape>", self.cancel)
		continue_btn = ttk.Button(btnframe, text="Continue", command=self.do_continue)
		self.continue_button = continue_btn
		continue_btn.grid(column=0, row=0, sticky=tk.E, padx=3)
		self.win.bind("<Return>", self.do_continue)
		# Put the frames and other widgets in place.
		msgframe.grid(column=0, row=0, sticky=tk.EW)
		entryframe.grid(column=0, row=1, sticky=tk.EW)
		if rowset and column_headers:
			tableframe.grid(column=0, row=2, sticky=tk.NSEW)
			statusframe.grid(column=0, row=4, sticky=tk.EW)
		btnframe.grid(column=0, row=3, sticky=tk.E)
		# Allow resizing.
		self.win.columnconfigure(0, weight=1)
		self.win.rowconfigure(1, weight=1)
		self.win.rowconfigure(2, weight=4)
		msgframe.columnconfigure(0, weight=1)
		btnframe.columnconfigure(0, weight=1)
		# Other key bindings
		self.win.protocol("WM_DELETE_WINDOW", self.cancel)
		# Position window.
		self.win.update_idletasks()
		m = re.match(r"(\d+)x(\d+)([-+]\d+)([-+]\d+)", self.win.geometry())
		wwd = int(m.group(1))
		wht = int(m.group(2))
		swd = self.win.winfo_screenwidth()
		sht = self.win.winfo_screenheight()
		xpos = (swd/2) - (wwd/2)
		ypos = (sht/2) - (wht/2)
		self.win.geometry("%dx%d+%d+%d" % (wwd, wht, xpos, ypos))
		# Limit resizing
		self.win.minsize(width=400, height=0)
	def validate_all(self, *args):
		valid_errors = []
		for e in self.entries:
			value = e.entryvar.get()
			if value is None:
				if e.required:
					valid_errors.append("%s is required but is missing." % e.name)
				elif e.lookup_list:
					valid_errors.append("%s is not one of the valid items" % e.name)
			else:
				if e.lookup_list and not value in e.lookup_list:
					valid_errors.append("%s is not one of the valid items" % e.name)
				else:
					if e.validation_rx and not e.validation_rx.match(value):
						valid_errors.append("%s does not match the required pattern." % e.name)
		valid = len(valid_errors) == 0
		self.continue_button.configure(state='normal' if valid else 'disabled')
	def cancel(self, *args):
		self.win.destroy()
		self.win.update_idletasks()
	def do_continue(self, *args):
		self.button_value = 1
		self.win.destroy()
		self.win.update_idletasks()
	def activate(self):
		self.validate_all()
		# Window control
		self.win.grab_set()
		self.win._root().withdraw()
		self.win.focus_force()
		self.entries[0].entryctrl.focus()
		self.win.wait_window(self.win)
		if self.button_value:
			for e in self.entries:
				e.value = e.entryvar.get()
		return (self.button_value, self.entries)

class OpenFileUI(object):
	def __init__(self, working_dir, script):
		self.working_dir = working_dir
		self.script = script
	def activate(self):
		import Tkinter as tk
		import tkFileDialog
		self.win = tk.Tk()
		self.win.withdraw()
		fn = tkFileDialog.askopenfilename(initialdir=self.working_dir, parent=self.win, title="Filename for %s" % self.script)
		self.win.destroy()
		return fn

class SaveFileUI(object):
	def __init__(self, working_dir, script):
		self.working_dir = working_dir
		self.script = script
	def activate(self):
		import Tkinter as tk
		import tkFileDialog
		self.win = tk.Tk()
		self.win.withdraw()
		fn = tkFileDialog.asksaveasfilename(initialdir=self.working_dir, parent=self.win, title="Filename for %s" % self.script)
		self.win.destroy()
		return fn

class GetDirectoryUI(object):
	def __init__(self, working_dir, script):
		self.working_dir = working_dir
		self.script = script
	def activate(self):
		import Tkinter as tk
		import tkFileDialog
		self.win = tk.Tk()
		self.win.withdraw()
		fn = tkFileDialog.askdirectory(initialdir=self.working_dir, parent=self.win, mustexist=True, title="Directory for %s" % self.script)
		self.win.destroy()
		return fn



# End of UI classes
#===============================================================================================


#===============================================================================================
#-----  METACOMMAND FUNCTIONS


#****	EXPORT
def x_export(**kwargs):
	schema = kwargs["schema"]
	table = kwargs["table"]
	queryname = dbs.current().schema_qualified_table_name(schema, table)
	select_stmt = "select * from %s;" % queryname
	outfile = kwargs['filename']
	description = kwargs["description"]
	tee = kwargs['tee']
	tee = False if not tee else True
	append = kwargs['append']
	append = True if append else False
	filefmt = kwargs['format'].lower()
	global conf
	if conf.make_export_dirs and outfile.lower() != 'stdout':
		make_export_dirs(outfile)
	if tee and outfile.lower() != 'stdout':
		prettyprint_query(select_stmt, dbs.current(), 'stdout', False, desc=description)
	# Handle special writers first.
	if filefmt == 'txt' or filefmt == 'text':
		prettyprint_query(select_stmt, dbs.current(), outfile, append, desc=description)
		return None
	elif filefmt == 'txt-nd' or filefmt == 'text-nd':
		prettyprint_query(select_stmt, dbs.current(), outfile, append, nd_val=u"ND", desc=description)
		return None
	elif filefmt == 'ods':
		write_query_to_ods(select_stmt, dbs.current(), outfile, append, sheetname=queryname, desc=description)
		return None
	elif filefmt == 'json':
		write_query_to_json(select_stmt, dbs.current(), outfile, append, desc=description)
		return None
	elif filefmt == 'values':
		write_query_to_values(select_stmt, dbs.current(), outfile, append, desc=description)
		return None
	elif filefmt == 'html':
		write_query_to_html(select_stmt, dbs.current(), outfile, append, desc=description)
		return None
	elif filefmt == 'latex':
		write_query_to_latex(select_stmt, dbs.current(), outfile, append, desc=description)
		return None
	# Now handle all delimited-file output formats
	try:
		hdrs, rows = dbs.current().select_rowsource(select_stmt)
	except ErrInfo:
		raise
	except:
		raise ErrInfo("db", select_stmt, exception_msg=exception_desc())
	if filefmt == 'raw':
		write_query_raw(outfile, rows, append)
	else:
		write_delimited_file(outfile, filefmt, hdrs, rows, conf.output_encoding, append)
	return None

metacommands.append(MetaCommand(ins_table_rxs(r'^\s*EXPORT\s+', ins_fn_rxs(r'\s+(?P<tee>TEE\s+)?(?P<append>APPEND\s+)?TO\s+', r'\s+AS\s+(?P<format>CSV|TAB|TSV|TABQ|TSVQ|UNITSEP|US|TXT|TXT-ND|PLAIN|ODS|JSON|VALUES|HTML|LATEX|RAW)(?:\s+DESCRIP(?:TION)?\s+"(?P<description>[^"]*)")?\s*$')),
									x_export, "EXPORT", "Write data from a table or view to a file."))


#****	EXPORT QUERY
def x_export_query(**kwargs):
	select_stmt = kwargs['query']
	outfile = kwargs['filename']
	description = kwargs["description"]
	tee = kwargs['tee']
	tee = False if not tee else True
	append = kwargs['append']
	append = True if append else False
	filefmt = kwargs['format'].lower()
	global conf
	if conf.make_export_dirs and outfile.lower() != 'stdout':
		make_export_dirs(outfile)
	if tee and outfile.lower() != 'stdout':
		prettyprint_query(select_stmt, dbs.current(), 'stdout', False, desc=description)
	# Handle special writers first.
	if filefmt == 'txt' or filefmt == 'text':
		prettyprint_query(select_stmt, dbs.current(), outfile, append, desc=description)
		return None
	elif filefmt == 'txt-nd' or filefmt == 'text-nd':
		prettyprint_query(select_stmt, dbs.current(), outfile, append, nd_val=u"ND", desc=description)
		return None
	elif filefmt == 'ods':
		script_name, lno = working_script.current_script_line()
		write_query_to_ods(select_stmt, dbs.current(), outfile, append, sheetname="Query_%d" % lno, desc=description)
		return None
	elif filefmt == 'json':
		write_query_to_json(select_stmt, dbs.current(), outfile, append, desc=description)
		return None
	elif filefmt == 'values':
		write_query_to_values(select_stmt, dbs.current(), outfile, append, desc=description)
		return None
	elif filefmt == 'html':
		write_query_to_html(select_stmt, dbs.current(), outfile, append, desc=description)
		return None
	elif filefmt == 'latex':
		write_query_to_latex(select_stmt, dbs.current(), outfile, append, desc=description)
		return None
	# Now handle all delimited-file output formats
	try:
		hdrs, rows = dbs.current().select_rowsource(select_stmt)
	except ErrInfo:
		raise
	except:
		raise ErrInfo("db", select_stmt, exception_msg=exception_desc())
	if filefmt == 'raw':
		write_query_raw(outfile, rows, append)
	else:
		write_delimited_file(outfile, filefmt, hdrs, rows, conf.output_encoding, append)
	return None

metacommands.append(MetaCommand(ins_fn_rxs(r'^\s*EXPORT\s+QUERY\s+<<\s*(?P<query>.*;)\s*>>\s+(?P<tee>TEE\s+)?(?P<append>APPEND\s+)?TO\s+', r'\s+AS\s*(?P<format>CSV|TAB|TSV|TABQ|TSVQ|UNITSEP|US|TXT|TXT-ND|PLAIN|ODS|JSON|HTML|VALUES|LATEX|RAW)(?:\s+DESCRIP(?:TION)?\s+"(?P<description>[^"]*)")?\s*$'),
							x_export_query, "EXPORT QUERY", "Write data from a query to a file."))


#****	EXPORT WITH TEMPLATE
def x_export_with_template(**kwargs):
	schema = kwargs["schema"]
	table = kwargs["table"]
	queryname = dbs.current().schema_qualified_table_name(schema, table)
	select_stmt = "select * from %s;" % queryname
	outfile = kwargs['filename']
	template_file = kwargs['template']
	tee = kwargs['tee']
	tee = False if not tee else True
	append = kwargs['append']
	append = True if append else False
	global conf
	if conf.make_export_dirs and outfile.lower() != 'stdout':
		make_export_dirs(outfile)
	if tee and outfile.lower() != 'stdout':
		prettyprint_query(select_stmt, dbs.current(), 'stdout', False)
	report_query(select_stmt, dbs.current(), outfile, template_file, append)
	return None

metacommands.append(MetaCommand(ins_table_rxs(r'^\s*EXPORT\s+', 
						ins_fn_rxs(r'\s+(?P<tee>TEE\s+)?(?P<append>APPEND\s+)?TO\s+', 
						ins_fn_rxs(r'\s+WITH\s+TEMPLATE\s+', r'\s*$', 'template'))),
						x_export_with_template))


#****	EXPORT QUERY WITH TEMPLATE
def x_export_query_with_template(**kwargs):
	select_stmt = kwargs['query']
	outfile = kwargs['filename']
	template_file = kwargs['template']
	tee = kwargs['tee']
	tee = False if not tee else True
	append = kwargs['append']
	append = True if append else False
	global conf
	if conf.make_export_dirs and outfile.lower() != 'stdout':
		make_export_dirs(outfile)
	if tee and outfile.lower() != 'stdout':
		prettyprint_query(select_stmt, dbs.current(), 'stdout', False)
	report_query(select_stmt, dbs.current(), outfile, template_file, append)
	return None

metacommands.append(MetaCommand(ins_fn_rxs(r'^\s*EXPORT\s+QUERY\s+<<\s*(?P<query>.*;)\s*>>\s+(?P<tee>TEE\s+)?(?P<append>APPEND\s+)?TO\s+', 
										   ins_fn_rxs(r'\s+WITH\s+TEMPLATE\s+', r'\s*$', 'template')),
							x_export_query_with_template))



#****	HALT
def x_halt(**kwargs):
	errmsg = kwargs["errmsg"]
	errlevel = kwargs["errorlevel"]
	global conf
	global gui_manager_thread, gui_manager_queue
	use_gui = gui_console_isrunning()
	if errmsg and (use_gui or conf.gui_level > 1):
		x_halt_msg(table=None, schema=None, **kwargs)
		return
	if errlevel:
		errlevel = int(errlevel)
	else:
		errlevel = 2
	if errmsg:
		output.write_err(errmsg)
	if working_script:
		script, lno = working_script.current_script_line()
	else:
		script = lno = None
	exec_log.log_exit_halt(script, lno, msg=errmsg)
	exit_now(errlevel, None)

metacommands.append(MetaCommand(r'^\s*HALT\s*(?:"(?P<errmsg>.+)")?(?:\s+EXIT_STATUS\s+(?P<errorlevel>\d+))?\s*$', x_halt))


#****	HALT MESSAGE
def x_halt_msg(**kwargs):
	errmsg = kwargs["errmsg"]
	errlevel = kwargs["errorlevel"]
	if errlevel:
		errlevel = int(errlevel)
	else:
		errlevel = 2
	schema = kwargs["schema"]
	table = kwargs["table"]
	if table:
		db = dbs.current()
		db_obj = db.schema_qualified_table_name(schema, table)
		sql = u"select * from %s;" % db_obj
		headers, rows = db.select_data(sql)
	else:
		headers, rows = None, None

	enable_gui()
	return_queue = Queue.Queue()
	gui_args = {"title": "HALT",
				 "message": errmsg,
				 "button_list": [("OK", 1, "<Return>")],
				 "no_cancel": True,
				 "column_headers": headers,
				 "rowset": rows}
	gui_manager_queue.put(GuiSpec(GUI_HALT, gui_args, return_queue))
	user_response = return_queue.get(block=True)
	exec_log.log_exit_halt(*working_script.current_script_line(), msg=errmsg)
	exit_now(errlevel, None)

metacommands.append(MetaCommand(ins_table_rxs(r'^\s*HALT\s+MESSAGE\s+"(?P<errmsg>(.|\n)*)"(?:\s+DISPLAY\s+',
				r')?(?:\s+EXIT_STATUS\s+(?P<errorlevel>\d+))?\s*$'), x_halt_msg))


#****	BEGIN BATCH
def x_begin_batch(**kwargs):
	working_script.start_batch()
	return None

metacommands.append(MetaCommand(r'^\s*BEGIN\s+BATCH\s*$', x_begin_batch))


#****	END BATCH
def x_end_batch(**kwargs):
	working_script.end_batch()
	return None

# Set a name so this can be found and evaluated during processing, when all other metacommands are ignored.
metacommands.append(MetaCommand(r'^\s*END\s+BATCH\s*$', x_end_batch, "END BATCH", run_in_batch=True))


#****	ROLLBACK BATCH
def x_rollback(**kwargs):
	working_script.rollback_batch()

metacommands.append(MetaCommand(r'^\s*ROLLBACK(:?\s+BATCH)?\s*$', x_rollback, "ROLLBACK BATCH", run_in_batch=True))


#****	ERROR_HALT
def x_error_halt(**kwargs):
	flag = kwargs['onoff'].lower()
	if not flag in ('on', 'off'):
		raise ErrInfo(type="cmd", command_text=kwargs["metacommandline"], other_msg=u"Unrecognized flag for error handling: %s" % flag)
	status.halt_on_err = flag in ('on', 'yes')
	return None

metacommands.append(MetaCommand(r'\s*ERROR_HALT\s+(?P<onoff>ON|OFF|YES|NO)\s*$', x_error_halt))


#****	METACOMMAND_ERROR_HALT
def x_metacommand_error_halt(**kwargs):
	flag = kwargs['onoff'].lower()
	if not flag in ('on', 'off'):
		raise ErrInfo(type="cmd", command_text=kwargs["metacommandline"], other_msg=u"Unrecognized flag for metacommand error handling: %s" % flag)
	status.halt_on_metacommand_err = flag in ('on', 'yes')
	return None

metacommands.append(MetaCommand(r'\s*METACOMMAND_ERROR_HALT\s+(?P<onoff>ON|OFF|YES|NO)\s*$', x_metacommand_error_halt, set_error_flag=False))


#****	INCLUDE
def x_include(**kwargs):
	filename = kwargs['filename']
	working_script.read_sqlfile(filename)
	return None

metacommands.append(MetaCommand(ins_fn_rxs(r'^\s*INCLUDE\s+', r'\s*$'), x_include))


#****	IMPORT
def x_import(**kwargs):
	# is_new should have values of 0, 1, or 2
	newstr = kwargs['new']
	if newstr:
		is_new = 1 + ['new', 'replacement'].index(newstr.lower())
	else:
		is_new = 0
	schemaname = kwargs['schema']
	tablename = kwargs['table']
	filename = kwargs['filename']
	if not os.path.exists(filename):
		raise ErrInfo(type="cmd", command_text=kwargs['metacommandline'], other_msg='Input file does not exist')
	quotechar = kwargs['quotechar']
	if quotechar:
		quotechar = quotechar.lower()
	delimchar = kwargs['delimchar']
	if delimchar:
		if delimchar.lower() == 'tab':
			delimchar = unicode(chr(9))
		elif delimchar.lower() in ('unitsep', 'us'):
			delimchar = unicode(chr(31))
	enc = kwargs['encoding']
	junk_hdrs = kwargs['skip']
	if not junk_hdrs:
		junk_hdrs = 0
	else:
		junk_hdrs = int(junk_hdrs)
	try:
		importtable(dbs.current(), schemaname, tablename, filename, is_new, skip_header_line=True, quotechar=quotechar, delimchar=delimchar, encoding=enc, junk_header_lines=junk_hdrs)
	except ErrInfo:
		raise
	except:
		raise ErrInfo("exception", exception_msg=exception_desc(), other_msg="Can't import file %s" % filename)
	return None

metacommands.append(MetaCommand(
	ins_table_rxs(r'^\s*IMPORT\s+TO\s+(?:(?P<new>NEW|REPLACEMENT)\s+)?', ins_fn_rxs(r'\s+FROM\s+', r'(?:\s+WITH(?:\s+QUOTE\s+(?P<quotechar>NONE|\'|")\s+DELIMITER\s+(?P<delimchar>TAB|UNITSEP|US|,|;|\|))?(?:\s+ENCODING\s+(?P<encoding>\w+))?)?(?:\s+SKIP\s+(?P<skip>\d+))?\s*$')),
	x_import))


#****	IMPORT ODS
def x_import_ods(**kwargs):
	# is_new should have values of 0, 1, or 2
	newstr = kwargs['new']
	if newstr:
		is_new = 1 + ['new', 'replacement'].index(newstr.lower())
	else:
		is_new = 0
	schemaname = kwargs['schema']
	tablename = kwargs['table']
	filename = kwargs['filename']
	sheetname = kwargs['sheetname']
	hdr_rows = kwargs['skip']
	if not hdr_rows:
		hdr_rows = 0
	else:
		hdr_rows = int(hdr_rows)
	if not os.path.exists(filename):
		raise ErrInfo(type="cmd", command_text=kwargs['metacommandline'], other_msg='Input file does not exist')
	try:
		importods(dbs.current(), schemaname, tablename, is_new, filename, sheetname, hdr_rows)
	except ErrInfo:
		raise
	except:
		raise ErrInfo("exception", exception_msg=exception_desc(), other_msg="Can't import file %s" % filename)
	return None

metacommands.append(MetaCommand(
	ins_table_rxs(r'^\s*IMPORT\s+TO\s+(?:(?P<new>NEW|REPLACEMENT)\s+)?', ins_fn_rxs(r'\s+FROM\s+', r'\s+SHEET\s+"(?P<sheetname>[A-Za-z0-9_\.\/\-\\ ]+)"(?:\s+SKIP\s+(?P<skip>\d+))?\s*$'))
	+ins_table_rxs(r'^\s*IMPORT\s+TO\s+(?:(?P<new>NEW|REPLACEMENT)\s+)?', ins_fn_rxs(r'\s+FROM\s+', r'\s+SHEET\s+(?P<sheetname>[A-Za-z0-9_\.\/\-\\]+)(?:\s+SKIP\s+(?P<skip>\d+))?\s*$')),
	x_import_ods))


#****	IMPORT XLS
def x_import_xls(**kwargs):
	# is_new should have values of 0, 1, or 2
	newstr = kwargs['new']
	if newstr:
		is_new = 1 + ['new', 'replacement'].index(newstr.lower())
	else:
		is_new = 0
	schemaname = kwargs['schema']
	tablename = kwargs['table']
	filename = kwargs['filename']
	sheetname = kwargs['sheetname']
	junk_hdrs = kwargs['skip']
	if not junk_hdrs:
		junk_hdrs = 0
	else:
		junk_hdrs = int(junk_hdrs)
	if not os.path.exists(filename):
		raise ErrInfo(type="cmd", command_text=kwargs['metacommandline'], other_msg='Input file does not exist')
	try:
		importxls(dbs.current(), schemaname, tablename, is_new, filename, sheetname, junk_hdrs)
	except ErrInfo:
		raise
	except:
		raise ErrInfo("exception", exception_msg=exception_desc(), other_msg="Can't import file %s" % filename)
	return None

metacommands.append(MetaCommand(
	ins_table_rxs(r'^\s*IMPORT\s+TO\s+(?:(?P<new>NEW|REPLACEMENT)\s+)?', ins_fn_rxs(r'\s+FROM\s+EXCEL\s+', r'\s+SHEET\s+"(?P<sheetname>[A-Za-z0-9_\.\/\-\\ ]+)"(?:\s+SKIP\s+(?P<skip>\d+))?\s*$'))
	+ins_table_rxs(r'^\s*IMPORT\s+TO\s+(?:(?P<new>NEW|REPLACEMENT)\s+)?', ins_fn_rxs(r'\s+FROM\s+EXCEL\s+', r'\s+SHEET\s+(?P<sheetname>[A-Za-z0-9_\.\/\-\\]+)(?:\s+SKIP\s+(?P<skip>\d+))?\s*$')),
	x_import_xls))



#****	PAUSE
def x_pause(**kwargs):
	quitmsg = "Quit from PAUSE metacommand"
	text = kwargs["text"]
	action = kwargs["action"]
	if action:
		action = action.lower()
	countdown = kwargs["countdown"]
	timeunit = kwargs["timeunit"]
	quitted = False
	timed_out = False
	msg = text
	if countdown:
		countdown = float(countdown)
		msg = "%s\nProcess will %s after %s %s without a response." % (msg, action, countdown, timeunit)
	maxtime_secs = countdown
	if timeunit and timeunit.lower() == "minutes":
		maxtime_secs = maxtime_secs * 60
	global conf
	global gui_manager_thread, gui_manager_queue
	use_gui = False
	if gui_manager_thread:
		return_queue = Queue.Queue()
		gui_manager_queue.put(GuiSpec(QUERY_CONSOLE, {}, return_queue))
		user_response = return_queue.get(block=True)
		use_gui = user_response["console_running"]
	if use_gui or conf.gui_level > 0:
		enable_gui()
		return_queue = Queue.Queue()
		gui_args = {"title": "Script %s" % working_script.current_script_line()[0],
					 "message": msg,
					 "countdown": maxtime_secs}
		gui_manager_queue.put(GuiSpec(GUI_PAUSE, gui_args, return_queue))
		user_response = return_queue.get(block=True)
		quitted = user_response["quitted"]
		return_queue.task_done()
	else:
		timed_out = False
		if os.name == 'posix':
			rv = pause(msg, maxtime_secs)
		else:
			rv = pause_win(msg, maxtime_secs)
		quitted = rv == 1
		timed_out = rv == 2
	if (quitted or (timed_out and action == "halt")) and status.cancel_halt:
		exec_log.log_exit_halt(*working_script.current_script_line(), msg=quitmsg)
		exit_now(2, None)
	return None

metacommands.append(MetaCommand(r'^\s*PAUSE\s+"(?P<text>.+)"(?:\s+(?P<action>HALT|CONTINUE)\s+AFTER\s+(?P<countdown>\d+(?:\.\d*)?)\s+(?P<timeunit>SECONDS|MINUTES))?\s*$', x_pause))


#****	ASK
def x_ask(**kwargs):
	message = kwargs["question"]
	subvar = kwargs["match"]
	if os.name == 'posix':
		resp = get_yn(message)
	else:
		resp = get_yn_win(message)
	script, lno = working_script.current_script_line()
	if resp == chr(27):
		exec_log.log_exit_halt(script, lno, msg="Quit from ASK metacommand")
		exit_now(2, None)
	else:
		respstr = "Yes" if resp == "y" else "No"
		subvars.add_substitution(subvar, respstr)
		exec_log.log_status_info("Question {%s} on line %d answered %s" % (message, lno, respstr))
	return None

metacommands.append(MetaCommand(r'^\s*ASK\s+"(?P<question>.+)"\s+SUB\s+(?P<match>\w+)\s*$', x_ask))



#****	PROMPT ASK
def x_prompt_ask(**kwargs):
	#title, message, button_list, selected_button=0, no_cancel=False, column_headers=None, rowset=None, textentry=None
	quitmsg = "Quit from PROMPT ASK metacommand"
	subvar = kwargs["match"]
	schema = kwargs["schema"]
	table = kwargs["table"]
	script, lno = working_script.current_script_line()
	if table is not None:
		queryname = dbs.current().schema_qualified_table_name(schema, table)
		cmd = u"select * from %s;" % queryname
		colnames, rows = dbs.current().select_data(cmd)
	else:
		colnames, rows = None, None
	enable_gui()
	return_queue = Queue.Queue()
	gui_args = {"title": script,
				 "message": kwargs["question"],
				 "button_list": [('Yes', 1, 'y'), ('No', 0, 'n')],
				 "column_headers": colnames,
				 "rowset": rows}
	gui_manager_queue.put(GuiSpec(GUI_DISPLAY, gui_args, return_queue))
	user_response = return_queue.get(block=True)
	btn = user_response["button"]
	if btn is None:
		if  status.cancel_halt:
			exec_log.log_exit_halt(script, lno, msg=quitmsg)
			exit_now(2, None)
	else:
		respstr = "Yes" if btn == 1 else "No"
		subvars.add_substitution(subvar, respstr)
		exec_log.log_status_info("Question {%s} on line %d answered %s" % (kwargs["question"], lno, respstr))
	return None

metacommands.append(MetaCommand(
		ins_table_rxs(r'^\s*PROMPT\s+ASK\s+"(?P<question>.+)"\s+SUB\s+(?P<match>\w+)(?:\s+DISPLAY\s+', r')?\s*$'),
		x_prompt_ask))


#****	PROMPT ENTER_SUB
def x_prompt_enter(**kwargs):
	sub_var = kwargs["match_str"]
	message = kwargs["message"]
	as_pw = kwargs["password"] is not None
	schema = kwargs["schema"]
	table = kwargs["table"]
	if table is not None:
		db = dbs.current()
		cmd = u"select * from %s;" % db.schema_qualified_table_name(schema, table)
		hdrs, rows = db.select_data(cmd)
	else:
		hdrs, rows = None, None
	enable_gui()
	return_queue = Queue.Queue()
	gui_args = {"title": "Enter a value",
				 "message": message,
				 "button_list": [("OK", 1, "<Return>")],
				 "column_headers": hdrs,
				 "rowset": rows,
				 "textentry": True,
				 "hidetext": as_pw}
	gui_manager_queue.put(GuiSpec(GUI_DISPLAY, gui_args, return_queue))
	user_response = return_queue.get(block=True)
	btnval = user_response["button"]
	txtval = user_response["return_value"]
	if btnval is None:
		if status.cancel_halt:
			exec_log.log_exit_halt(*working_script.current_script_line(), msg="Quit from prompt to enter a SUB value.")
			exit_now(2, None)
	else:
		subvars.add_substitution(sub_var, txtval)
		script_name, lno = working_script.current_script_line()
		if as_pw:
			exec_log.log_status_info("Password assigned to variable {%s} on line %d." % (sub_var, lno))
		else:
			exec_log.log_status_info("Variable {%s} set to {%s} on line %d." % (sub_var, txtval, lno))
	return None

metacommands.append(MetaCommand(
		ins_table_rxs(r'^\s*PROMPT\s+ENTER_SUB\s+(?P<match_str>\w+)\s+(?:(?P<password>PASSWORD)\s+)?MESSAGE\s+"(?P<message>(.|\n)*)"(?:\s+DISPLAY\s+', r')?\s*$'),
		x_prompt_enter))


#****	PROMPT ENTRY FORM
def x_prompt_entryform(**kwargs):
	spec_schema = kwargs["schema"]
	spec_table = kwargs["table"]
	display_schema = kwargs["schemadisp"]
	display_table = kwargs["tabledisp"]
	message = kwargs["message"]
	tbl1 = dbs.current().schema_qualified_table_name(spec_schema, spec_table)
	try:
		if not dbs.current().table_exists(spec_table, spec_schema):
			raise ErrInfo(type="cmd", command_text=kwargs['metacommandline'], other_msg="Table %s does not exist" % spec_table)
	except:
		pass
	curs = dbs.current().cursor()
	cmd = u"select * from %s;" % tbl1
	curs.execute(cmd)
	colhdrs = [d[0].lower() for d in curs.description]
	if 'sequence' in colhdrs:
		cmd = u"select * from %s order by sequence;" % tbl1
		curs.execute(cmd)
	if not ('sub_var' in colhdrs and 'prompt' in colhdrs):
		raise ErrInfo(type="cmd", command_text=kwargs['metacommandline'], other_msg="The variable name and prompt are required, but missing.")
	spec_rows = curs.fetchall()
	entry_list = []
	subvar_rx = re.compile(r'^\w+$', re.I)
	for r in spec_rows:
		lookups = None
		entry_width = None
		v = dict(zip(colhdrs, r))
		subvar = v.get("sub_var")
		if not subvar:
			raise ErrInfo(type="cmd", command_text=kwargs['metacommandline'], other_msg="A substitution variable name must be provided for all of the entry specifications.")
		if not subvar_rx.match(subvar):
			raise ErrInfo(type="cmd", command_text=kwargs['metacommandline'], other_msg="Invalid substitution variable name: %s" % subvar)
		prompt_msg = v.get('prompt')
		if not prompt_msg:
			raise ErrInfo(type="cmd", command_text=kwargs['metacommandline'], other_msg="A prompt must be provided for all of the entry specifications.")
		initial_value = None
		if 'initial_value' in colhdrs and v['initial_value'] is not None:
			try:
				initial_value = unicode(v['initial_value'])
			except:
				raise ErrInfo(type="cmd", command_text=kwargs['metacommandline'], other_msg="The initial value of %s can't be used." % v['initial_value'])
		if 'lookup_table' in colhdrs:
			lt = v['lookup_table']
			if lt:
				curs.execute("select * from %s;" % lt)
				lookups = [lookup_row[0] for lookup_row in curs.fetchall()]
		if 'width' in colhdrs:
			entry_width = v.get('width')
			if entry_width:
				try:
					entry_width = int(entry_width)
				except:
					raise ErrInfo(type="cmd", command_text=kwargs['metacommandline'], other_msg="Entry width %s is not an integer" % entry_width)
		subvars.remove_substitution(subvar)
		entry_list.append(EntrySpec(subvar, prompt_msg, required=bool(v.get('required')), initial_value=initial_value,
							default_width=entry_width, lookup_list=lookups, validation_regex=v.get('validation_regex'),
							validation_key_regex=v.get('validation_key_regex'), entry_type=v.get('entry_type')))
	colnames, rows = None, None
	if display_table:
		db = dbs.current()
		sq_name = db.schema_qualified_table_name(display_schema, display_table)
		colnames, rows = db.select_data(u"select * from %s;" % sq_name)
	enable_gui()
	return_queue = Queue.Queue()
	gui_args = {"title": "Entry",
				 "message": message,
				 "entry_specs": entry_list,
				 "column_headers": colnames,
				 "rowset": rows}
	gui_manager_queue.put(GuiSpec(GUI_ENTRY, gui_args, return_queue))
	user_response = return_queue.get(block=True)
	btn = user_response["button"]
	entries = user_response["return_value"]
	script, line_no = working_script.current_script_line()
	if btn:
		for e in entries:
			if e.value:
				value = unicode(e.value)
				subvars.add_substitution(e.name, value)
				exec_log.log_status_info(u"Substitution variable %s set to {%s} on line %d of %s" % (e.name, value, line_no, script))
			else:
				if working_script.sub_exists(e.name):
					exec_log.log_status_info(u"Substitution variable %s removed on line %d of %s" % (e.name, line_no, script))
	else:
		if status.cancel_halt:
			msg = u"Halted from entry form %s" % tbl1
			exec_log.log_exit_halt(script, line_no, msg)
			exit_now(2, None)


metacommands.append(MetaCommand(
	ins_table_rxs(r'^\s*PROMPT\s+ENTRY_FORM\s+', ins_table_rxs(r'\s+MESSAGE\s+"(?P<message>(.|\n)*)"(?:\s+DISPLAY\s+', r')?\s*$', suffix="disp")),
	x_prompt_entryform))


#****	PROMPT MESSAGE DISPLAY
def x_prompt(**kwargs):
	db = dbs.current()
	schema = kwargs["schema"]
	table = kwargs["table"]
	message = kwargs["message"]
	sq_name = db.schema_qualified_table_name(schema, table)
	script, line_no = working_script.current_script_line()
	cmd = u"select * from %s;" % sq_name
	colnames, rows = db.select_data(cmd)
	#title, message, button_list, selected_button=0, no_cancel=False, column_headers=None, rowset=None, textentry=None
	enable_gui()
	return_queue = Queue.Queue()
	gui_args = {"title": table,
				 "message": message,
				 "button_list": [('Continue', 1, "<Return>")],
				 "column_headers": colnames,
				 "rowset": rows}
	gui_manager_queue.put(GuiSpec(GUI_DISPLAY, gui_args, return_queue))
	user_response = return_queue.get(block=True)
	btn = user_response["button"]
	if not btn:
		if status.cancel_halt:
			msg = u"Halted from display of %s" % sq_name
			exec_log.log_exit_halt(script, line_no, msg)
			exit_now(2, None)
	return None

metacommands.append(MetaCommand(
	ins_table_rxs(r'^\s*PROMPT\s+MESSAGE\s+"(?P<message>(.|\n)*)"\s+DISPLAY\s+', r'\s*$'), x_prompt))


#****	PROMPT OPENFILE SUB
def x_prompt_openfile(**kwargs):
	sub_name = kwargs["match"]
	try:
		subvars.remove_substitution(sub_name)
		script, lno = working_script.current_script_line()
		working_dir = os.path.dirname(os.path.abspath(script))
		enable_gui()
		return_queue = Queue.Queue()
		gui_args = {"working_dir": working_dir, "script": script}
		gui_manager_queue.put(GuiSpec(GUI_OPENFILE, gui_args, return_queue))
		user_response = return_queue.get(block=True)
		fn = user_response["filename"]
		if not fn:
			if status.cancel_halt:
				msg = u"Halted from prompt for name of file to open"
				exec_log.log_exit_halt(script, lno, msg)
				exit_now(2, None)
		else:
			subvars.add_substitution(sub_name, fn)
			exec_log.log_status_info("Substitution string %s set to filename %s at line %d of %s" % (sub_name, fn, lno, script))
	except (ErrInfo, SystemExit):
		raise
	except:
		raise ErrInfo(type="exception", exception_msg=exception_desc())
	return None

metacommands.append(MetaCommand(r'^\s*PROMPT\s+OPENFILE\s+SUB\s+(?P<match>\w+)\s*$', x_prompt_openfile))


#****	PROMPT SAVEFILE SUB
def x_prompt_savefile(**kwargs):
	sub_name = kwargs["match"]
	try:
		subvars.remove_substitution(sub_name)
		script, lno = working_script.current_script_line()
		working_dir = os.path.dirname(os.path.abspath(script))
		enable_gui()
		return_queue = Queue.Queue()
		gui_args = {"working_dir": working_dir, "script": script}
		gui_manager_queue.put(GuiSpec(GUI_SAVEFILE, gui_args, return_queue))
		user_response = return_queue.get(block=True)
		fn = user_response["filename"]
		if not fn:
			if status.cancel_halt:
				msg = u"Halted from prompt for name of file to save"
				exec_log.log_exit_halt(script, lno, msg)
				exit_now(2, None)
		else:
			subvars.add_substitution(sub_name, fn)
			exec_log.log_status_info("Substitution string %s set to filename %s at line %d of %s" % (sub_name, fn, lno, script))
	except (ErrInfo, SystemExit):
		raise
	except:
		raise ErrInfo(type="exception", exception_msg=exception_desc())
	return None

metacommands.append(MetaCommand(r'^\s*PROMPT\s+SAVEFILE\s+SUB\s+(?P<match>\w+)\s*$', x_prompt_savefile))


#****	PROMPT DIRECTORY SUB
def x_prompt_directory(**kwargs):
	sub_name = kwargs["match"]
	try:
		subvars.remove_substitution(sub_name)
		script, lno = working_script.current_script_line()
		working_dir = os.path.dirname(os.path.abspath(script))
		enable_gui()
		return_queue = Queue.Queue()
		gui_args = {"working_dir": working_dir, "script": script}
		gui_manager_queue.put(GuiSpec(GUI_DIRECTORY, gui_args, return_queue))
		user_response = return_queue.get(block=True)
		dirname = user_response["directory"]
		if not dirname:
			if status.cancel_halt:
				msg = u"Halted from prompt for name of directory"
				exec_log.log_exit_halt(script, lno, msg)
				exit_now(2, None)
		else:
			subvars.add_substitution(sub_name, dirname)
			exec_log.log_status_info("Substitution string %s set to directory %s at line %d of %s" % (sub_name, dirname, lno, script))
	except (ErrInfo, SystemExit):
		raise
	except:
		raise ErrInfo(type="exception", exception_msg=exception_desc())
	return None

metacommands.append(MetaCommand(r'^\s*PROMPT\s+DIRECTORY\s+SUB\s+(?P<match>\w+)\s*$', x_prompt_directory))


#****	PROMPT SELECT_SUB
def x_prompt_selectsub(**kwargs):
	#prompt_selectsub(kwargs["schema"], kwargs["tablename"], kwargs["msg"])
	schema = kwargs["schema"]
	table = kwargs["table"]
	msg = kwargs["msg"]
	cont = kwargs["cont"]
	db = dbs.current()
	sq_name = db.schema_qualified_table_name(schema, table)
	sql = u"select * from %s;" % sq_name
	hdrs, rows = db.select_data(sql)
	for subvar in hdrs:
		subvar = u'@'+subvar
		subvars.remove_substitution(subvar)
	btns = [("OK", 1, "O")]
	if cont:
		btns.append(("Continue", 2, "<Return>"))
	enable_gui()
	return_queue = Queue.Queue()
	gui_args = {"title": "Select data",
				 "message": msg,
				 "button_list": btns,
				 "column_headers": hdrs,
				 "rowset": rows}
	gui_manager_queue.put(GuiSpec(GUI_SELECTSUB, gui_args, return_queue))
	user_response = return_queue.get(block=True)
	btn_val = user_response["button"]
	return_val = user_response["return_value"]
	selected_row = None
	if btn_val and btn_val == 1:
		# return_val will be a tuple with a single value corresponding to the item ID,
		# which is assigned so as to be an index into the row source.
		selected_row = rows[int(return_val[0])]
	script, line_no = working_script.current_script_line()
	if btn_val is None or (btn_val == 1 and selected_row is None):
		if status.cancel_halt:
			exec_log.log_exit_halt(script, line_no, msg=u"Halted from prompt for row of %s on line %d of %s" % (sq_name, line_no, script))
			exit_now(2, None)
	else:
		if btn_val == 1:
			for i, item in enumerate(selected_row):
				if item is None:
					item = u''
				item = unicode(item)
				match_str = u"@" + hdrs[i]
				subvars.add_substitution(match_str, item)
				exec_log.log_status_info(u"Substitution string %s set to {%s} on line %d of %s" % (match_str, item, line_no, script))
	return None

metacommands.append(MetaCommand(
	ins_table_rxs(r'^\s*PROMPT\s+SELECT_SUB\s+', r'\s+MESSAGE\s+"(?P<msg>(.|\n)*)"(?:\s+(?P<cont>CONTINUE))?\s*$'), x_prompt_selectsub))


#****	SUB
def x_sub(**kwargs):
	subvars.add_substitution(kwargs['match'], kwargs['repl'])
	return None

sub_metacmd = MetaCommand(r'^\s*SUB\s+(?P<match>\w+)\s+(?P<repl>.+)$', x_sub, "SUB", "Define a string to match and a replacement for it.")
metacommands.append(sub_metacmd)


#****	RM_SUB
def x_rm_sub(**kwargs):
	subvars.remove_substitution(kwargs['match'])
	return None

metacommands.append(MetaCommand(r'^\s*RM_SUB\s+(?P<match>\w+)\s*$', x_rm_sub))


#****	SUBDATA
def x_subdata(**kwargs):
	subvar = kwargs["match"]
	sql = u"select * from %s;" % kwargs["datasource"]
	db = dbs.current()
	script, line_no = working_script.current_script_line()
	errmsg = "There are no data in %s to use with the SUBDATA metacommand (script %s, line %d)." % (kwargs["datasource"], script, line_no)
	# Exceptions should be trapped by the caller, so are re-raised here after settting status
	try:
		hdrs, rec = db.select_rowsource(sql)
	except ErrInfo:
		raise
	except:
		raise ErrInfo(type="exception", exception_msg=exception_desc(), other_msg="Can't get headers and rows from %s." % sql)
	try:
		row1 = rec.next()
	except:
		subvars.remove_substitution(subvar)
		raise ErrInfo(type="exception", exception_msg=exception_desc(), other_msg=errmsg)
	if not row1:
		raise ErrInfo(type="error", other_msg=errmsg)
	dataval = row1[0]
	if dataval is None:
		dataval = u''
	if not isinstance(dataval, basestring):
		dataval = unicode(dataval)
	subvars.add_substitution(subvar, dataval)
	return None

metacommands.append(MetaCommand(r'^\s*SUBDATA\s+(?P<match>\w+)\s+(?P<datasource>.+)\s*$', x_subdata))


#****	SELECT_SUB
def x_selectsub(**kwargs):
	sql = u"select * from %s;" % kwargs["datasource"]
	db = dbs.current()
	script, line_no = working_script.current_script_line()
	nodatamsg = "There are no data in %s to use with the SELECT_SUB metacommand (script %s, line %d)." % (kwargs["datasource"], script, line_no)
	try:
		hdrs, rec = db.select_rowsource(sql)
	except ErrInfo:
		raise
	except:
		raise ErrInfo(type="exception", exception_msg=exception_desc(), other_msg="Can't get headers and rows from %s." % sql)
	# Remove any existing variables with these names
	for subvar in hdrs:
		subvar = u'@'+subvar
		if subvars.sub_exists(subvar):
			subvars.remove_substitution(subvar)
			exec_log.log_status_info(u"Substitution variable %s removed on line %d of %s" % (subvar, line_no, script))
	try:
		row1 = rec.next()
	except StopIteration:
		row1 = None
	except:
		raise ErrInfo(type="exception", exception_msg=exception_desc(), other_msg=nodatamsg)
	if row1:
		for i, item in enumerate(row1):
			if item is None:
				item = u''
			item = unicode(item)
			match_str = u"@" + hdrs[i]
			subvars.add_substitution(match_str, item)
			exec_log.log_status_info(u"Substitution variable %s set to {%s} on line %d of %s" % (match_str, item, line_no, script))
	else:
		exec_log.log_status_info(nodatamsg)
	return None

metacommands.append(MetaCommand(r'^\s*SELECT_SUB\s+(?P<datasource>.+)\s*$', x_selectsub))


#****	SUB_ENCRYPT
def x_sub_encrypt(**kwargs):
	subvars.add_substitution(kwargs['subvar'], Encrypt().encrypt(kwargs['plaintext']))
	return None

metacommands.append(MetaCommand(r'^\s*SUB_ENCRYPT\s+(?P<subvar>\w+)\s+(?P<plaintext>.+)\s*$', x_sub_encrypt))


#****	SUB_DECRYPT
def x_sub_decrypt(**kwargs):
	subvars.add_substitution(kwargs['subvar'], Encrypt().decrypt(kwargs['crypttext']))
	return None

metacommands.append(MetaCommand(r'^\s*SUB_DECRYPT\s+(?P<subvar>\w+)\s+(?P<crypttext>.+)\s*$', x_sub_decrypt))



#****	SYSTEM_CMD
def x_system_cmd(**kwargs):
	syscmd = kwargs['command']
	if os.name != 'posix':
		syscmd = syscmd.replace("\\", "\\\\")
	subprocess.call(shlex.split(unicode(syscmd)))
	return None

metacommands.append(MetaCommand(r'^\s*SYSTEM_CMD\s*\(\s*(?P<command>.+)\s*\)\s*$', x_system_cmd))


#****	WAIT_UNTIL
def x_wait_until(**kwargs):
	countdown = int(kwargs['seconds'])
	while countdown > 0:
		if xcmd_test(kwargs['condition']):
			return
		time.sleep(1)
		countdown -= 1
	if kwargs['end'].lower() == 'halt':
		exec_log.log_exit_halt(*working_script.current_script_line(), msg="Halted at expiration of WAIT_UNTIL metacommand.")
		exit_now(2, None)
	return None

metacommands.append(MetaCommand(r'^\s*WAIT_UNTIL\s+(?P<condition>.+)\s+(?P<end>HALT|CONTINUE)\s+AFTER\s+(?P<seconds>\d+)\s+SECONDS\s*$', x_wait_until))


#****	WRITE
def x_write(**kwargs):
	msg = u'%s\n' % kwargs['text']
	tee = kwargs['tee']
	tee = False if not tee else True
	outf = kwargs['outputname']
	global conf
	if outf:
		EncodedFile(outf, conf.output_encoding).open('a').write(msg)
	if (not outf) or tee:
		try:
			output.write(msg.encode(conf.output_encoding))
		except ConsoleUIError as e:
			output.reset()
			exec_log.log_status_info("Console UI write failed (message {%s}); output reset to stdout." % e.value)
			output.write(msg.encode(conf.output_encoding))
	if conf.tee_write_log:
		exec_log.log_user_msg(msg)
	return None

metacommands.append(MetaCommand(r'^\s*WRITE\s+"(?P<text>(.|\n)*)"(?:(?:\s+(?P<tee>TEE))?\s+TO\s+(?P<outputname>[a-zA-Z0-9:._/\-\\]+))?\s*$', x_write))


#****	EMAIL
def x_email(**kwargs):
	from_addr = kwargs['from']
	to_addr = kwargs['to']
	subject = kwargs['subject']
	msg = kwargs['msg']
	msg_file = kwargs['msg_file']
	att_file = kwargs['att_file']
	m = Mailer()
	m.sendmail(from_addr, to_addr, subject, msg, msg_file, att_file)

# email address rx: r"^[A-Za-z0-9_\-\.!#$%&'*+/=?^`{|}~]+@[A-Za-z0-9]+(-[A-Za-z0-9]+)*(\.[A-Za-z0-9]+)*$"
metacommands.append(MetaCommand(ins_fn_rxs(ins_fn_rxs(r'^\s*EMAIL\s+'
							     r'FROM\s+(?P<from>[A-Za-z0-9_\-\.!#$%&\'*+/=?^`{|}~]+@[A-Za-z0-9]+(-[A-Za-z0-9]+)*(\.[A-Za-z0-9]+)*)\s+'
								 r'TO\s+(?P<to>[A-Za-z0-9_\-\.!#$%&\'*+/=?^`{|}~]+@[A-Za-z0-9]+(-[A-Za-z0-9]+)*(\.[A-Za-z0-9]+)*([;,]\s*[A-Za-z0-9\-\.!#$%&\'*+/=?^`{|}~]+@[A-Za-z0-9]+(-[A-Za-z0-9]+)*(\.[A-Za-z0-9]+)*)*)\s+'
								 r'SUBJECT "(?P<subject>[^"]+)"\s+'
								 r'MESSAGE\s+"(?P<msg>[^"]*)"'
								 r'(\s+MESSAGE_FILE\s+', r')?(\s+ATTACH(MENT)?_FILE\s+', 'msg_file'),
								 r')?\s*$', 'att_file'), x_email))



#****	LOG_WRITE_MESSAGES
def x_logwritemessages(**kwargs):
	global conf
	setting = kwargs['setting'].lower()
	conf.tee_write_log = setting in ('yes', 'on')

metacommands.append(MetaCommand(r'^\s*LOG_WRITE_MESSAGES\s+(?P<setting>Yes|No|On|Off)\s*$', x_logwritemessages))



#****	AUTOCOMMIT
def x_autocommit(**kwargs):
	setting = kwargs['setting'].lower()
	db = dbs.current()
	if setting in ('on', 'yes'):
		db.autocommit_on()
	else:
		db.autocommit_off()

metacommands.append(MetaCommand(r'^\s*AUTOCOMMIT\s+(?P<setting>ON|OFF|YES|NO)\s*$', x_autocommit))


#****	IF
def x_if(**kwargs):
	tf_value = xcmd_test(kwargs['condtest'])
	if tf_value:
		src_line = working_script.current_script_line()
		working_script.insert_commands([SqlCmd(src_line[0], src_line[1], command_type="cmd", sql_text=kwargs['condcmd'])])
	return None

metacommands.append(MetaCommand(r'^\s*IF\s*\(\s*(?P<condtest>.+)\s*\)\s*{\s*(?P<condcmd>.+)\s*}\s*$', x_if))


#****	BLOCK IF
def x_if_block(**kwargs):
	if working_script.all_true():
		working_script.new_if_level(xcmd_test(kwargs['condtest']))
	else:
		# Push any if level
		working_script.new_if_level(False)
	return None

metacommands.append(MetaCommand(r'^\s*IF\s*\(\s*(?P<condtest>.+)\s*\)\s*$', x_if_block, run_when_false=True))


#****	BLOCK ENDIF
def x_if_end(**kwargs):
	working_script.exit_if_level()
	return None

metacommands.append(MetaCommand(r'^\s*ENDIF\s*$', x_if_end, run_when_false=True))


#****	BLOCK ELSE
def x_if_else(**kwargs):
	if working_script.all_true() or working_script.only_current_false():
		working_script.invert_if_level()
	return None

metacommands.append(MetaCommand(r'^\s*ELSE\s*$', x_if_else, run_when_false=True))


#****	BLOCK ELSEIF
def x_if_elseif(**kwargs):
	if working_script.only_current_false():
		working_script.replace_if_level(xcmd_test(kwargs['condtest']))
	else:
		working_script.replace_if_level(False)
	return None

metacommands.append(MetaCommand(r'^\s*ELSEIF\s*\(\s*(?P<condtest>.+)\s*\)\s*$', x_if_elseif, run_when_false=True))


#****	BLOCK ANDIF
def x_if_andif(**kwargs):
	if working_script.all_true():
		working_script.replace_if_level(working_script.current_if_level() and xcmd_test(kwargs['condtest']))
	return None

metacommands.append(MetaCommand(r'^\s*ANDIF\s*\(\s*(?P<condtest>.+)\s*\)\s*$', x_if_andif))


#****	BLOCK ORIF
def x_if_orif(**kwargs):
	if working_script.all_true():
		return None		# Short-circuit evaluation
	if working_script.only_current_false():
		working_script.replace_if_level(xcmd_test(kwargs['condtest']))
	return None

metacommands.append(MetaCommand(r'^\s*ORIF\s*\(\s*(?P<condtest>.+)\s*\)\s*$', x_if_orif, run_when_false=True))


#****	CONNECT to Postgres
def x_connect_pg(**kwargs):
	need_pwd = kwargs['need_pwd']
	if need_pwd:
		need_pwd = need_pwd.lower() == 'true'
	portno = kwargs["port"]
	if portno:
		portno = int(portno)
	mk_new = kwargs['new']
	mk_new = mk_new.lower() == 'new' if mk_new else False
	pw = kwargs['password']
	enc = kwargs['encoding']
	if enc:
		new_db = PostgresDatabase(kwargs['server'], kwargs['db_name'], kwargs['user'], need_passwd=need_pwd,
				port=portno, new_db=mk_new, encoding=enc, password=pw)
	else:
		new_db = PostgresDatabase(kwargs['server'], kwargs['db_name'], kwargs['user'], need_passwd=need_pwd,
				port=portno, new_db=mk_new, password=pw)
	dbs.add(kwargs['db_alias'].lower(), new_db)
	return None

metacommands.append(MetaCommand(r'^CONNECT\s+TO\s+POSTGRESQL\s*\(\s*SERVER\s*=\s*(?P<server>[A-Z0-9][A-Z0-9_\-\.]*)\s*,\s*DB\s*=\s*(?P<db_name>[A-Z][A-Z0-9_\-]*)(?:\s*,\s*USER\s*=\s*(?P<user>[A-Z][A-Z0-9_]*)\s*,\s*NEED_PWD\s*=\s*(?P<need_pwd>TRUE|FALSE))?(?:\s*,\s*PORT\s*=\s*(?P<port>\d+))?(?:\s*,\s+PASSWORD\s*=\s*(?P<password>[^\s]+))?(?:\s*,\s*ENCODING\s*=\s*(?P<encoding>[A-Z][A-Z0-9_-]+))?(?:\s*,\s*(?P<new>NEW))?\s*\)\s+AS\s+(?P<db_alias>[A-Z][A-Z0-9_]*)\s*$', x_connect_pg))


#****	CONNECT to SQLite
def x_connect_sqlite(**kwargs):
	db_file = kwargs['filename']
	mk_new = kwargs['new']
	mk_new = mk_new.lower() == 'new' if mk_new else False
	# The SQLite library will automatically create a new database if the referenced one does not exist.
	# The 'new' keyword in the connect metacommand is to ensure that this is what the user really wants,
	# and for consistency with the connect metacommand for Postgres.
	if not mk_new and not os.path.exists(db_file):
		raise ErrInfo(type="cmd", command_text=kwargs['metacommandline'], other_msg='SQLite file does not exist.')
	if mk_new and os.path.exists(db_file):
		raise ErrInfo(type="cmd", command_text=kwargs['metacommandline'], other_msg='SQLite file already exists, NEW keyword is invalid.')
	new_db = SQLiteDatabase(db_file)
	dbs.add(kwargs['db_alias'].lower(), new_db)
	return None

metacommands.append(MetaCommand(
	ins_fn_rxs(r'^CONNECT\s+TO\s+SQLITE\s*\(\s*FILE\s*=\s*', r'(?:\s*,\s*(?P<new>NEW))?\s*\)\s+AS\s+(?P<db_alias>[A-Z][A-Z0-9_]*)\s*$'), x_connect_sqlite))


#****	CONNECT to Access
def x_connect_access(**kwargs):
	db_file = kwargs['filename']
	enc = kwargs['encoding']
	#user = kwargs['user_name']
	need_pwd = kwargs['need_pwd']
	password = kwargs['password']
	if need_pwd:
		need_pwd = need_pwd.lower() == 'true'
	new_db = AccessDatabase(db_file, need_passwd=need_pwd, encoding=enc, password=password)
	dbs.add(kwargs['db_alias'].lower(), new_db)
	return None

metacommands.append(MetaCommand(
	ins_fn_rxs(r'^CONNECT\s+TO\s+ACCESS\s*\(\s*FILE\s*=\s*', r'(?:\s*,\s*NEED_PWD\s*=\s*(?P<need_pwd>TRUE|FALSE))?(?:\s*,\s+PASSWORD\s*=\s*(?P<password>[^\s]+))?(?:\s*,\s*ENCODING\s*=\s*(?P<encoding>[A-Z][A-Z0-9_-]+))?\s*\)\s+AS\s+(?P<db_alias>[A-Z][A-Z0-9_]*)\s*$'),
	x_connect_access))


#****	CONNECT to SQL Server
def x_connect_ssvr(**kwargs):
	need_pwd = kwargs['need_pwd']
	if need_pwd:
		need_pwd = need_pwd.lower() == 'true'
	portno = kwargs["port"]
	if portno:
		portno = int(portno)
	new_db = SqlServerDatabase(kwargs['server'], kwargs['db_name'], kwargs['user'], need_passwd=need_pwd, port=portno, encoding=kwargs['encoding'])
	dbs.add(kwargs['db_alias'].lower(), new_db)
	return None

metacommands.append(MetaCommand((
	r'^CONNECT\s+TO\s+SQLSERVER\s*\(\s*SERVER\s*=\s*(?P<server>[A-Z0-9][A-Z0-9_\/\\\-\.]*)\s*,\s*DB\s*=\s*(?P<db_name>[A-Z][A-Z0-9_\-]*)(?:\s*,\s*USER\s*=\s*(?P<user>[A-Z][A-Z0-9_~`!@#$%^&\*\+=\/\?\.-]*)\s*,\s*NEED_PWD\s*=\s*(?P<need_pwd>TRUE|FALSE))?(?:\s*,\s*PORT\s*=\s*(?P<port>\d+))?(?:\s*,\s*ENCODING\s*=\s*(?P<encoding>[A-Z][A-Z0-9_-]+))?\s*\)\s+AS\s+(?P<db_alias>[A-Z][A-Z0-9_]*)\s*$',
	r'^CONNECT\s+TO\s+SQLSERVER\s*\(\s*SERVER\s*=\s*"(?P<server>[A-Z0-9][A-Z0-9_\/\\\s\-\.]*)"\s*,\s*DB\s*=\s*"(?P<db_name>[A-Z][A-Z0-9_\-\s]*)"(?:\s*,\s*USER\s*=\s*(?P<user>[A-Z][A-Z0-9_~`!@#$%^&\*\+=\/\?\.-]*)\s*,\s*NEED_PWD\s*=\s*(?P<need_pwd>TRUE|FALSE))?(?:\s*,\s*PORT\s*=\s*(?P<port>\d+))?(?:\s*,\s*ENCODING\s*=\s*(?P<encoding>[A-Z][A-Z0-9_-]+))?\s*\)\s+AS\s+(?P<db_alias>[A-Z][A-Z0-9_]*)\s*$',
	r'^CONNECT\s+TO\s+SQLSERVER\s*\(\s*SERVER\s*=\s*"(?P<server>[A-Z0-9][A-Z0-9_\/\\\s\-\.]*)"\s*,\s*DB\s*=\s*(?P<db_name>[A-Z][A-Z0-9_\-]*)(?:\s*,\s*USER\s*=\s*(?P<user>[A-Z][A-Z0-9_~`!@#$%^&\*\+=\/\?\.-]*)\s*,\s*NEED_PWD\s*=\s*(?P<need_pwd>TRUE|FALSE))?(?:\s*,\s*PORT\s*=\s*(?P<port>\d+))?(?:\s*,\s*ENCODING\s*=\s*(?P<encoding>[A-Z][A-Z0-9_-]+))?\s*\)\s+AS\s+(?P<db_alias>[A-Z][A-Z0-9_]*)\s*$',
	r'^CONNECT\s+TO\s+SQLSERVER\s*\(\s*SERVER\s*=\s*(?P<server>[A-Z0-9][A-Z0-9_\/\\\-\.]*)\s*,\s*DB\s*=\s*"(?P<db_name>[A-Z][A-Z0-9_\- ]*)"(?:\s*,\s*USER\s*=\s*(?P<user>[A-Z][A-Z0-9_~`!@#$%^&\*\+=\/\?\.-]*)\s*,\s*NEED_PWD\s*=\s*(?P<need_pwd>TRUE|FALSE))?(?:\s*,\s*PORT\s*=\s*(?P<port>\d+))?(?:\s*,\s*ENCODING\s*=\s*(?P<encoding>[A-Z][A-Z0-9_-]+))?\s*\)\s+AS\s+(?P<db_alias>[A-Z][A-Z0-9_]*)\s*$'
	), x_connect_ssvr))


#****	CONNECT to MySQL
def x_connect_mysql(**kwargs):
	need_pwd = kwargs['need_pwd']
	if need_pwd:
		need_pwd = need_pwd.lower() == 'true'
	portno = kwargs["port"]
	if portno:
		portno = int(portno)
	pw = kwargs['password']
	enc = kwargs['encoding']
	if enc:
		new_db = MySQLDatabase(kwargs['server'], kwargs['db_name'], kwargs['user'], need_passwd=need_pwd,
				port=portno, encoding=enc, password=pw)
	else:
		new_db = MySQLDatabase(kwargs['server'], kwargs['db_name'], kwargs['user'], need_passwd=need_pwd,
				port=portno, password=pw)
	dbs.add(kwargs['db_alias'].lower(), new_db)
	return None

metacommands.append(MetaCommand((
	r'^CONNECT\s+TO\s+MYSQL\s*\(\s*SERVER\s*=\s*(?P<server>[A-Z0-9][A-Z0-9_\-\.]*)\s*,\s*DB\s*=\s*(?P<db_name>[A-Z][A-Z0-9_\-]*)(?:\s*,\s*USER\s*=\s*(?P<user>[A-Z][A-Z0-9_]*)\s*,\s*NEED_PWD\s*=\s*(?P<need_pwd>TRUE|FALSE))?(?:\s*,\s*PORT\s*=\s*(?P<port>\d+))?(?:\s*,\s+PASSWORD\s*=\s*(?P<password>[^\s]+))?(?:\s*,\s*ENCODING\s*=\s*(?P<encoding>[A-Z][A-Z0-9_-]+))?\s*\)\s+AS\s+(?P<db_alias>[A-Z][A-Z0-9_]*)\s*$',
	r'^CONNECT\s+TO\s+MARIADB\s*\(\s*SERVER\s*=\s*(?P<server>[A-Z0-9][A-Z0-9_\-\.]*)\s*,\s*DB\s*=\s*(?P<db_name>[A-Z][A-Z0-9_\-]*)(?:\s*,\s*USER\s*=\s*(?P<user>[A-Z][A-Z0-9_]*)\s*,\s*NEED_PWD\s*=\s*(?P<need_pwd>TRUE|FALSE))?(?:\s*,\s*PORT\s*=\s*(?P<port>\d+))?(?:\s*,\s+PASSWORD\s*=\s*(?P<password>[^\s]+))?(?:\s*,\s*ENCODING\s*=\s*(?P<encoding>[A-Z][A-Z0-9_-]+))?\s*\)\s+AS\s+(?P<db_alias>[A-Z][A-Z0-9_]*)\s*$',
	), x_connect_mysql))


#****	CONNECT to Firebird
def x_connect_fb(**kwargs):
	need_pwd = kwargs['need_pwd']
	if need_pwd:
		need_pwd = need_pwd.lower() == 'true'
	portno = kwargs["port"]
	if portno:
		portno = int(portno)
	enc = kwargs['encoding']
	if enc:
		new_db = FirebirdDatabase(kwargs['server'], kwargs['db_name'], kwargs['user'], need_passwd=need_pwd,
				port=portno, encoding=enc)
	else:
		new_db = FirebirdDatabase(kwargs['server'], kwargs['db_name'], kwargs['user'], need_passwd=need_pwd,
				port=portno)
	dbs.add(kwargs['db_alias'].lower(), new_db)
	return None

metacommands.append(MetaCommand(r'^CONNECT\s+TO\s+FIREBIRD\s*\(\s*SERVER\s*=\s*(?P<server>[A-Z0-9][A-Z0-9_\-\.]*)\s*,\s*DB\s*=\s*(?P<db_name>[A-Z][A-Z0-9_\-]*)(?:\s*,\s*USER\s*=\s*(?P<user>[A-Z][A-Z0-9_]*)\s*,\s*NEED_PWD\s*=\s*(?P<need_pwd>TRUE|FALSE))?(?:\s*,\s*PORT\s*=\s*(?P<port>\d+))?(?:\s*,\s*ENCODING\s*=\s*(?P<encoding>[A-Z][A-Z0-9_-]+))?\s*\)\s+AS\s+(?P<db_alias>[A-Z][A-Z0-9_]*)\s*$', x_connect_fb))


#****	CONNECT to a DSN
def x_connect_dsn(**kwargs):
	need_pwd = kwargs['need_pwd']
	if need_pwd:
		need_pwd = need_pwd.lower() == 'true'
	pw = kwargs['password']
	enc = kwargs['encoding']
	if enc:
		new_db = DsnDatabase(kwargs['dsn'], kwargs['user'], need_passwd=need_pwd, encoding=enc, password=pw)
	else:
		new_db = DsnDatabase(kwargs['dsn'], kwargs['user'], need_passwd=need_pwd, password=pw)
	dbs.add(kwargs['db_alias'].lower(), new_db)
	return None

metacommands.append(MetaCommand(r'^CONNECT\s+TO\s+DSN\s*\(\s*DSN\s*=\s*(?P<dsn>[A-Z0-9][A-Z0-9_\-\.]*)\s*(?:\s*,\s*USER\s*=\s*(?P<user>[A-Z][A-Z0-9_]*)\s*,\s*NEED_PWD\s*=\s*(?P<need_pwd>TRUE|FALSE))?(?:\s*,\s+PASSWORD\s*=\s*(?P<password>[^\s]+))?(?:\s*,\s*ENCODING\s*=\s*(?P<encoding>[A-Z][A-Z0-9_-]+))?\s*\)\s+AS\s+(?P<db_alias>[A-Z][A-Z0-9_]*)\s*$', x_connect_dsn))


#****	USE
def x_use(**kwargs):
	db_alias = kwargs['db_alias'].lower()
	if not db_alias in dbs.aliases():
		raise ErrInfo(type="cmd", command_text=kwargs['metacommandline'], other_msg="Unrecognized database alias: %s." % db_alias)
	dbs.make_current(db_alias)
	exec_log.log_db_connect(dbs.current())
	subvars.add_substitution("$CURRENT_DBMS", dbs.aliased_as(db_alias).type.dbms_id)
	subvars.add_substitution("$CURRENT_DATABASE", dbs.aliased_as(db_alias).name())
	return None

metacommands.append(MetaCommand(r'^USE\s+(?P<db_alias>[A-Z][A-Z0-9_]*)\s*$', x_use))


#****	COPY
def x_copy(**kwargs):
	alias1 = kwargs['alias1'].lower()
	schema1 = kwargs['schema1']
	table1 = kwargs['table1']
	new = kwargs['new']
	new_tbl2 = new.lower() if new else None
	alias2 = kwargs['alias2'].lower()
	schema2 = kwargs['schema2']
	table2 = kwargs['table2']
	if alias1 not in dbs.aliases():
		raise ErrInfo(type="cmd", command_text=kwargs['metacommandline'], other_msg="Unrecognized database alias: %s." % alias1)
	if alias2 not in dbs.aliases():
		raise ErrInfo(type="cmd", command_text=kwargs['metacommandline'], other_msg="Unrecognized database alias: %s." % alias2)
	db1 = dbs.aliased_as(alias1)
	db2 = dbs.aliased_as(alias2)
	tbl1 = db1.schema_qualified_table_name(schema1, table1)
	tbl2 = db2.schema_qualified_table_name(schema2, table2)
	# Check to see if the source table exists, and raise an exception if it does not.
	# Ignore exceptions that occur during this check because the user may not have
	# permission to read the system tables used by the 'table_exists()' method, but
	# may have permission to read the data.
	try:
		if not db1.table_exists(table1, schema1):
			raise ErrInfo(type="cmd", command_text=kwargs['metacommandline'], other_msg="Table %s does not exist" % tbl1)
	except:
		pass
	if new_tbl2 and new_tbl2 == "new" and db2.table_exists(table2, schema2):
		raise ErrInfo(type="cmd", command_text=kwargs['metacommandline'], other_msg="Table %s already exists" % tbl2)
	# Get the data from the 'FROM' database
	select_stmt = "select * from %s;" % tbl1
	try:
		hdrs, rows = db1.select_rowsource(select_stmt)
	except ErrInfo:
		raise
	except:
		raise ErrInfo("db", select_stmt, exception_msg=exception_desc())
	def get_ts():
		if not get_ts.tablespec:
			hdrs, rows = db1.select_rowsource(select_stmt)
			get_ts.tablespec = DataTable(hdrs, rows)
		return get_ts.tablespec
	get_ts.tablespec = None
	# Evaluate data types in tbl1.
	#tbl_desc = DataTable(hdrs, rows)
	# Get the rowsource again.
	#hdrs, rows = db1.select_rowsource(select_stmt)
	# Create the new table if necessary.
	if new_tbl2:
		# Generate a CREATE TABLE statement.
		tbl_desc = get_ts()
		create_tbl = tbl_desc.create_table(db2.type, schema2, table2)
		if new_tbl2 == 'replacement':
			try:
				db2.drop_table(tbl2)
			except:
				exec_log.log_status_info("Could not drop existing table (%s) for COPY metacommand" % tbl2)
		db2.execute(create_tbl)
		if db2.type == dbt_firebird:
			db2.execute(u"COMMIT;")
	try:
		db2.populate_table(schema2, table2, rows, hdrs, get_ts)
		db2.commit()
	except ErrInfo:
		raise
	except:
		raise ErrInfo("db", select_stmt, exception_msg=exception_desc())

# "COPY [<schema1>.]<table1> FROM <alias1> TO [NEW] [<schema2>.]<table2> IN <alias2>"
metacommands.append(MetaCommand((
	r'^COPY\s+(?:(?P<schema1>[A-Z][A-Z0-9_\-\:]*)\.)?(?P<table1>[A-Z][A-Z0-9_\-\:]*)\s+FROM\s+(?P<alias1>[A-Z][A-Z0-9_]*)\s+TO\s+(?:(?P<new>NEW|REPLACEMENT)\s+)?(?:(?P<schema2>[A-Z][A-Z0-9_\-\:]*)\.)?(?P<table2>[A-Z][A-Z0-9_\-\:]*)\s+IN\s+(?P<alias2>[A-Z][A-Z0-9_]*)\s*$',
	r'^COPY\s+(?:"(?P<schema1>[A-Z][A-Z0-9_\-\: ]*)"\.)?"(?P<table1>[A-Z][A-Z0-9_\-\:]*)"\s+FROM\s+(?P<alias1>[A-Z][A-Z0-9_]*)\s+TO\s+(?:(?P<new>NEW|REPLACEMENT)\s+)?(?:"(?P<schema2>[A-Z][A-Z0-9_\-\:]*)"\.)?"(?P<table2>[A-Z][A-Z0-9_\-\:]*)"\s+IN\s+(?P<alias2>[A-Z][A-Z0-9_]*)\s*$',
	r'^COPY\s+(?:\[(?P<schema1>[A-Z][A-Z0-9_\-\: ]*)\]\.)?\[(?P<table1>[A-Z][A-Z0-9_\-\:]*)\]\s+FROM\s+(?P<alias1>[A-Z][A-Z0-9_]*)\s+TO\s+(?:(?P<new>NEW|REPLACEMENT)\s+)?(?:\[(?P<schema2>[A-Z][A-Z0-9_\-\:]*)\]\.)?\[(?P<table2>[A-Z][A-Z0-9_\-\:]*)\]\s+IN\s+(?P<alias2>[A-Z][A-Z0-9_]*)\s*$'
	), x_copy))


#****	COPY QUERY
def x_copy_query(**kwargs):
	alias1 = kwargs['alias1'].lower()
	select_stmt = kwargs['query']
	new = kwargs['new']
	new_tbl2 = new.lower() if new else None
	alias2 = kwargs['alias2'].lower()
	schema2 = kwargs['schema']
	table2 = kwargs['table']
	if alias1 not in dbs.aliases():
		raise ErrInfo(type="cmd", command_text=kwargs['metacommandline'], other_msg="Unrecognized database alias: %s." % alias1)
	if alias2 not in dbs.aliases():
		raise ErrInfo(type="cmd", command_text=kwargs['metacommandline'], other_msg="Unrecognized database alias: %s." % alias2)
	db1 = dbs.aliased_as(alias1)
	db2 = dbs.aliased_as(alias2)
	tbl2 = db2.schema_qualified_table_name(schema2, table2)
	if new_tbl2 and new_tbl2 == "new" and db2.table_exists(table2, schema2):
		raise ErrInfo(type="cmd", command_text=kwargs['metacommandline'], other_msg="Table %s already exists" % tbl2)
	# Get the data.
	try:
		hdrs, rows = db1.select_rowsource(select_stmt)
	except ErrInfo:
		raise
	except:
		raise ErrInfo("db", select_stmt, exception_msg=exception_desc())
	def get_ts():
		if not get_ts.tablespec:
			hdrs, rows = db1.select_rowsource(select_stmt)
			get_ts.tablespec = DataTable(hdrs, rows)
		return get_ts.tablespec
	get_ts.tablespec = None
	# Evaluate data types in source data.
	#tbl_desc = DataTable(hdrs, rows)
	# Get the rowsource again.
	#hdrs, rows = db1.select_rowsource(select_stmt)
	# Create the new table if necessary.
	if new_tbl2:
		# Generate a CREATE TABLE statement.
		tbl_desc = get_ts()
		create_tbl = tbl_desc.create_table(db2.type, schema2, table2)
		if new_tbl2 == 'replacement':
			try:
				db2.drop_table(tbl2)
			except:
				exec_log.log_status_info("Could not drop existing table (%s) for COPY metacommand" % tbl2)
		db2.execute(create_tbl)
		if db2.type == dbt_firebird:
			db2.execute(u"COMMIT;")
	try:
		db2.populate_table(schema2, table2, rows, hdrs, get_ts)
		db2.commit()
	except ErrInfo:
		raise
	except:
		raise ErrInfo("db", select_stmt, exception_msg=exception_desc())

# "COPY QUERY <query> FROM <alias1> TO [NEW] [<schema2>.]<table2> IN <alias2>"
metacommands.append(MetaCommand(
	ins_table_rxs(r'^COPY QUERY\s+<<\s*(?P<query>.*;)\s*>>\s+FROM\s+(?P<alias1>[A-Z][A-Z0-9_]*)\s+TO\s+(?:(?P<new>NEW|REPLACEMENT)\s+)?', r' IN\s+(?P<alias2>[A-Z][A-Z0-9_]*)\s*$'),
	x_copy_query))


#****	EXECUTE SCRIPT
def x_executescript(**kwargs):
	script_id = kwargs["script_id"]
	working_script.insert_sub_script(script_id)

metacommands.append(MetaCommand(r'^\s*EXEC(?:UTE)?\s+SCRIPT\s+(?P<script_id>\w+)\s*$', x_executescript))


# RUN|EXECUTE  --  Execute a SQL query.
def x_execute(**kwargs):
	# Note that the action of the db.exec_cmd method varies depending on the capabilities
	# of the DBMS in use.
	# Returns None.
	sql = kwargs['queryname']
	db = dbs.current()
	try:
		db.exec_cmd(sql)
		db.commit()
	except ErrInfo:
		raise
	except:
		raise ErrInfo("db", command_text=sql, exception_msg=exception_desc())
	return None

metacommands.append(MetaCommand(r'^\s*(?P<cmd>RUN|EXECUTE)\s+(?P<queryname>\#?\w+)\s*$', x_execute, "RUN|EXECUTE", "Run a database function, view, or action query (DBMS-dependent)"))


#****	ON ERROR_HALT WRITE
def x_error_halt_write_clear(**kwargs):
	global err_halt_writespec
	err_halt_writespec = None

metacommands.append(MetaCommand(r'^\s*ON\s+ERROR_HALT\s+WRITE\s+CLEAR\s*$', x_error_halt_write_clear))


def x_error_halt_write(**kwargs):
	msg = u'%s\n' % kwargs['text']
	tee = kwargs['tee']
	tee = False if not tee else True
	outf = kwargs['outputname']
	global err_halt_writespec
	err_halt_writespec = WriteSpec(message=msg, dest=outf, tee=tee)

metacommands.append(MetaCommand(r'^\s*ON\s+ERROR_HALT\s+WRITE\s+"(?P<text>(.|\n)*)"(?:(?:\s+(?P<tee>TEE))?\s+TO\s+(?P<outputname>[a-zA-Z0-9:._/\-\\]+))?\s*$', x_error_halt_write))



#****	ON ERROR_HALT EMAIL
def x_error_halt_email_clear(**kwargs):
	global err_halt_email
	err_halt_email = None

metacommands.append(MetaCommand(r'^\s*ON\s+ERROR_HALT\s+EMAIL\s+CLEAR\s*$', x_error_halt_email_clear))


def x_error_halt_email(**kwargs):
	from_addr = kwargs['from']
	to_addr = kwargs['to']
	subject = kwargs['subject']
	msg = kwargs['msg']
	msg_file = kwargs['msg_file']
	att_file = kwargs['att_file']
	global err_halt_email
	err_halt_email = MailSpec(from_addr, to_addr, subject, msg, msg_file, att_file)

# email address rx: r"^[A-Za-z0-9_\-\.!#$%&'*+/=?^`{|}~]+@[A-Za-z0-9]+(-[A-Za-z0-9]+)*(\.[A-Za-z0-9]+)*$"
metacommands.append(MetaCommand(ins_fn_rxs(ins_fn_rxs(r'^\s*ON\s+ERROR_HALT\s+EMAIL\s+'
							     r'FROM\s+(?P<from>[A-Za-z0-9_\-\.!#$%&\'*+/=?^`{|}~]+@[A-Za-z0-9]+(-[A-Za-z0-9]+)*(\.[A-Za-z0-9]+)*)\s+'
								 r'TO\s+(?P<to>[A-Za-z0-9_\-\.!#$%&\'*+/=?^`{|}~]+@[A-Za-z0-9]+(-[A-Za-z0-9]+)*(\.[A-Za-z0-9]+)*([;,]\s*[A-Za-z0-9\-\.!#$%&\'*+/=?^`{|}~]+@[A-Za-z0-9]+(-[A-Za-z0-9]+)*(\.[A-Za-z0-9]+)*)*)\s+'
								 r'SUBJECT "(?P<subject>[^"]+)"\s+'
								 r'MESSAGE\s+"(?P<msg>[^"]*)"'
								 r'(\s+MESSAGE_FILE\s+', r')?(\s+ATTACH(MENT)?_FILE\s+', 'msg_file'),
								 r')?\s*$', 'att_file'), x_error_halt_email))




#****	RM_FILE
def x_rm_file(**kwargs):
	fn = kwargs["filename"].strip()
	if os.path.isfile(fn):
		os.unlink(fn)

metacommands.append(MetaCommand((
	r'^RM_FILE\s+(?P<filename>.+)\s*$',
	r'^RM_FILE\s+"(?P<filename>.+)"\s*$'
	), x_rm_file))


#****	SUB_TEMPFILE
def x_sub_tempfile(**kwargs):
	subvars.add_substitution(kwargs["match_string"], tempfiles.new_temp_fn())

metacommands.append(MetaCommand(r'^\s*SUB_TEMPFILE\s+(?P<match_string>\w+)\s*$', x_sub_tempfile))


#****	WRITE CREATE_TABLE
def x_write_create_table(**kwargs):
	filename = kwargs['filename']
	if not os.path.exists(filename):
		raise ErrInfo(type="cmd", command_text=kwargs['metacommandline'], other_msg='Input file does not exist')
	quotechar = kwargs['quotechar']
	delimchar = kwargs['delimchar']
	global conf
	if delimchar:
		if delimchar.lower() == 'tab':
			delimchar = unicode(chr(9))
		elif delimchar.lower() in ('unitsep', 'us'):
			delimchar = unicode(chr(31))
	junk_hdrs = kwargs["skip"]
	if not junk_hdrs:
		junk_hdrs = 0
	else:
		junk_hdrs = int(junk_hdrs)
	inf = CsvFile(filename, conf.import_encoding, junk_header_lines=junk_hdrs)
	if quotechar and delimchar:
		inf.lineformat(delimchar, quotechar, None)
	inf.evaluate_column_types()
	sql = inf.create_table(dbs.current().type, kwargs["schema"], kwargs["table"], pretty=True)
	comment = kwargs["comment"]
	outfile = kwargs["outfile"]
	if outfile:
		o = EncodedFile(outfile, conf.output_encoding).open('a')
	else:
		o = output
	if comment:
		o.write(u"-- %s\n" % comment)
	o.write(u"%s\n" % sql)

metacommands.append(MetaCommand(
	ins_table_rxs(r'^\s*WRITE\s+CREATE_TABLE\s+',
					ins_fn_rxs(r'\s+FROM\s+',
								ins_fn_rxs(r'(?:\s+WITH\s+QUOTE\s+(?P<quotechar>NONE|\'|")\s+DELIMITER\s+(?P<delimchar>TAB|UNITSEP|US|,|;|\|))?(?:\s+SKIP\s+(?P<skip>\d+))?(?:\s+COMMENT\s+"(?P<comment>[^"]+)")?(?:\s+TO\s+',
											r')?\s*$', "outfile"))),
	x_write_create_table))


#****	WRITE CREATE_TABLE ODS
def x_write_create_table_ods(**kwargs):
	schemaname = kwargs['schema']
	tablename = kwargs['table']
	filename = kwargs['filename']
	sheetname = kwargs['sheet']
	hdr_rows = kwargs['skip']
	if not hdr_rows:
		hdr_rows = 0
	else:
		hdr_rows = int(hdr_rows)
	comment = kwargs['comment']
	outfile = kwargs['outfile']
	global conf
	if not os.path.exists(filename):
		raise ErrInfo(type="cmd", command_text=kwargs['metacommandline'], other_msg='Input file does not exist')
	hdrs, data = ods_data(filename, sheetname, hdr_rows)
	tablespec = DataTable(hdrs, data)
	sql = tablespec.create_table(dbs.current().type, schemaname, tablename, pretty=True)
	if outfile:
		o = EncodedFile(outfile, conf.output_encoding).open('a')
	else:
		o = output
	if comment:
		o.write(u"-- %s\n" % comment)
	o.write(u"%s\n" % sql)

metacommands.append(MetaCommand(
	ins_table_rxs(r'^\s*WRITE\s+CREATE_TABLE\s+',
				ins_fn_rxs(r'\s+FROM\s+',
							ins_rxs(( r'"(?P<sheet>[A-Za-z0-9_\.\/\-\\ ]+)"', r'(?P<sheet>[A-Za-z0-9_\.\/\-\\]+)'),
									r'\s+SHEET\s+',
									ins_fn_rxs(r'(?:\s+SKIP\s+(?P<skip>\d+))?(?:\s+COMMENT\s+"(?P<comment>[^"]+)")?(?:\s+TO\s+',
											r')?\s*$', "outfile")
									)
							)
					),
	x_write_create_table_ods))



#****	WRITE CREATE_TABLE XLS
def x_write_create_table_xls(**kwargs):
	schemaname = kwargs['schema']
	tablename = kwargs['table']
	filename = kwargs['filename']
	sheetname = kwargs['sheet']
	junk_hdrs = kwargs['skip']
	if not junk_hdrs:
		junk_hdrs = 0
	else:
		junk_hdrs = int(junk_hdrs)
	comment = kwargs['comment']
	outfile = kwargs['outfile']
	global conf
	if not os.path.exists(filename):
		raise ErrInfo(type="cmd", command_text=kwargs['metacommandline'], other_msg='Input file does not exist')
	hdrs, data = xls_data(filename, sheetname, junk_hdrs)
	tablespec = DataTable(hdrs, data)
	sql = tablespec.create_table(dbs.current().type, schemaname, tablename, pretty=True)
	if outfile:
		o = EncodedFile(outfile, conf.output_encoding).open('a')
	else:
		o = output
	if comment:
		o.write(u"-- %s\n" % comment)
	o.write(u"%s\n" % sql)

metacommands.append(MetaCommand(
	ins_table_rxs(r'^\s*WRITE\s+CREATE_TABLE\s+',
				ins_fn_rxs(r'\s+FROM\s+EXCEL\s+',
							ins_rxs(( r'"(?P<sheet>[A-Za-z0-9_\.\/\-\\ ]+)"', r'(?P<sheet>[A-Za-z0-9_\.\/\-\\]+)'),
									r'\s+SHEET\s+',
									ins_fn_rxs(r'(?:\s+SKIP\s+(?P<skip>\d+))?(?:\s+COMMENT\s+"(?P<comment>[^"]+)")?(?:\s+TO\s+',
											r')?\s*$', "outfile")
									)
							)
					),
	x_write_create_table_xls))



#****	WRITE CREATE_TABLE ALIAS
def x_write_create_table_alias(**kwargs):
	alias = kwargs['alias'].lower()
	schema = kwargs['schema']
	table = kwargs['table']
	comment = kwargs['comment']
	outfile = kwargs['filename']
	if alias not in dbs.aliases():
		raise ErrInfo(type="cmd", command_text=kwargs['metacommandline'], other_msg="Unrecognized database alias: %s." % alias)
	db = dbs.aliased_as(alias)
	tbl = db.schema_qualified_table_name(schema, table)
	# Check for existence of the table, but ignore exceptions on the check, because
	# the user may have permission to read from the table but not to read the system
	# tables to verify that the table exists.
	try:
		if not db.table_exists(table, schema):
			raise ErrInfo(type="cmd", command_text=kwargs['metacommandline'], other_msg="Table %s does not exist" % tbl)
	except:
		pass
	select_stmt = "select * from %s;" % tbl
	try:
		hdrs, rows = db.select_rowsource(select_stmt)
	except ErrInfo:
		raise
	except:
		raise ErrInfo("db", select_stmt, exception_msg=exception_desc())
	tablespec = DataTable(hdrs, rows)
	sql = tablespec.create_table(dbs.current().type, kwargs["schema1"], kwargs["table1"], pretty=True)
	if outfile:
		o = EncodedFile(outfile, conf.output_encoding).open('a')
	else:
		o = output
	if comment:
		o.write(u"-- %s\n" % comment)
	o.write(u"%s\n" % sql)

metacommands.append(MetaCommand(
	ins_table_rxs(r'^\s*WRITE\s+CREATE_TABLE\s+',
					ins_table_rxs(r'\s+FROM\s+',
									ins_fn_rxs(r'\s+IN\s+(?P<alias>[A-Z][A-Z0-9_]*)(?:\s+COMMENT\s+"(?P<comment>[^"]+)")?(?:\s+TO\s+',
												r')?\s*$')
									), 
					"1"),
	x_write_create_table_alias))


#****	CANCEL_HALT
def x_cancel_halt(**kwargs):
	flag = kwargs['onoff'].lower()
	if not flag in ('on', 'off'):
		raise ErrInfo(type="cmd", command_text=kwargs["metacommandline"], other_msg=u"Unrecognized flag for handling GUI cancellations: %s" % flag)
	status.cancel_halt = flag in ('on', 'yes')
	return None

metacommands.append(MetaCommand(r'^\s*CANCEL_HALT\s+(?P<onoff>ON|OFF|YES|NO)\s*$', x_cancel_halt))


#****	RESET COUNTER
def x_reset_counter(**kwargs):
	ctr_no = int(kwargs["counter_no"])
	working_script.remove_counter(ctr_no)

metacommands.append(MetaCommand(r'^\s*RESET\s+COUNTER\s+(?P<counter_no>\d+)\s*$', x_reset_counter))


#****	RESET COUNTERS
def x_reset_counters(**kwargs):
	working_script.remove_all_counters()

metacommands.append(MetaCommand(r'^\s*RESET\s+COUNTERS\s*$', x_reset_counters))


#****	SET COUNTER
def x_set_counter(**kwargs):
	ctr_no = int(kwargs["counter_no"])
	ctr_val = int(kwargs["value"])
	working_script.set_counter(ctr_no, ctr_val)

metacommands.append(MetaCommand(r'^\s*SET\s+COUNTER\s+(?P<counter_no>\d+)\s+TO\s+(?P<value>\d+)\s*$', x_set_counter))



#****	PROMPT CONNECT
def x_prompt_connect(**kwargs):
	alias = kwargs["alias"]
	message = kwargs["message"]
	gui_connect(alias, message, cmd=kwargs["metacommandline"])
	return None

metacommands.append(MetaCommand((
		r'^\s*PROMPT(?:\s+MESSAGE\s+"(?P<message>(.|\n)*)")?\s+CONNECT\s+AS\s+(?P<alias>\w+)\s*$',
		r'^\s*CONNECT\s+PROMPT(?:\s+MESSAGE\s+"(?P<message>(.|\n)*)")?\s+AS\s+(?P<alias>\w+)\s*$',
		r'^\s*PROMPT(?:\s+"(?P<message>(.|\n)*)")?\s+CONNECT\s+AS\s+(?P<alias>\w+)\s*$',
		r'^\s*CONNECT\s+PROMPT(?:\s+"(?P<message>(.|\n)*)")?\s+AS\s+(?P<alias>\w+)\s*$',
		), x_prompt_connect))


#****	TIMER
def x_timer(**kwargs):
	onoff = kwargs["onoff"].lower()
	if onoff == 'on':
		timer.start()
	else:
		timer.stop()

metacommands.append(MetaCommand(r'^\s*TIMER\s+(?P<onoff>ON|OFF)\s*$', x_timer))


#****	EMPTY_STRINGS
def x_empty_strings(**kwargs):
	flag = kwargs['yesno'].lower()
	if not flag in ('yes', 'no'):
		raise ErrInfo(type="cmd", command_text=kwargs["metacommandline"], other_msg=u"Unrecognized value for EMPTY_STRINGS metacommand: %s" % flag)
	conf.empty_strings = flag == 'yes'
	return None

metacommands.append(MetaCommand(r'^\s*EMPTY_STRINGS\s+(?P<yesno>YES|NO)\s*$', x_empty_strings))


#****	BOOLEAN_INT
def x_boolean_int(**kwargs):
	flag = kwargs['yesno'].lower()
	if not flag in ('yes', 'no'):
		raise ErrInfo(type="cmd", command_text=kwargs["metacommandline"], other_msg=u"Unrecognized value for BOOLEAN_INT metacommand: %s" % flag)
	conf.boolean_int = flag == 'yes'
	return None

metacommands.append(MetaCommand(r'^\s*BOOLEAN_INT\s+(?P<yesno>YES|NO)\s*$', x_boolean_int))


#****	BOOLEAN_WORDS
def x_boolean_words(**kwargs):
	flag = kwargs['yesno'].lower()
	if not flag in ('yes', 'no'):
		raise ErrInfo(type="cmd", command_text=kwargs["metacommandline"], other_msg=u"Unrecognized value for BOOLEAN_WORDS metacommand: %s" % flag)
	conf.boolean_int = flag == 'yes'
	return None

metacommands.append(MetaCommand(r'^\s*BOOLEAN_WORDS\s+(?P<yesno>YES|NO)\s*$', x_boolean_words))


#****	IMPORT_COMMON_COLUMNS_ONLY
def x_import_common_cols_only(**kwargs):
	flag = kwargs['yesno'].lower()
	if not flag in ('yes', 'no'):
		raise ErrInfo(type="cmd", command_text=kwargs["metacommandline"], other_msg=u"Unrecognized value for IMPORT_COMMON_COLUMNS_ONLY metacommand: %s" % flag)
	conf.import_common_cols_only = flag == 'yes'
	return None

metacommands.append(MetaCommand(r'^\s*IMPORT_COMMON_COLUMNS_ONLY\s+(?P<yesno>YES|NO)\s*$', x_import_common_cols_only))


#****	LOG
def x_log(**kwargs):
	message = kwargs["message"]
	exec_log.log_user_msg(message)

metacommands.append(MetaCommand(r'^\s*LOG\s+"(?P<message>.+)"\s*$', x_log))


#****	CONSOLE ON|OFF
def x_console(**kwargs):
	onoff = kwargs["onoff"].lower()
	if onoff == 'on':
		gui_console_on()
	else:
		gui_console_off()

metacommands.append(MetaCommand(r'^\s*CONSOLE\s+(?P<onoff>ON|OFF)\s*$', x_console))


#****	CONSOLE HIDE|SHOW
def x_console_hideshow(**kwargs):
	hideshow = kwargs["hideshow"].lower()
	if hideshow == 'hide':
		gui_console_hide()
	else:
		gui_console_show()

metacommands.append(MetaCommand(r'^\s*CONSOLE\s+(?P<hideshow>HIDE|SHOW)\s*$', x_console_hideshow))


#****	CONSOLE STATUS
def x_consolestatus(**kwargs):
	message = kwargs["message"]
	gui_console_status(message)

metacommands.append(MetaCommand(r'^\s*CONSOLE\s+STATUS\s+"(?P<message>.+)"\s*$', x_consolestatus))


#****	CONSOLE PROGRESS
def x_consoleprogress(**kwargs):
	num = float(kwargs["num"])
	total = kwargs["total"]
	if total:
		num = 100 * num / float(total)
	gui_console_progress(num)

metacommands.append(MetaCommand(r'^\s*CONSOLE\s+PROGRESS\s+(?P<num>[0-9]+(?:\.[0-9]+)?)(?:\s*/\s*(?P<total>[0-9]+(?:\.[0-9]+)?))?\s*$', x_consoleprogress))


#****	CONSOLE SAVE
def x_consolesave(**kwargs):
	fn = kwargs["filename"]
	ap = kwargs["append"]
	append = ap is not None
	gui_console_save(fn, append)

metacommands.append(MetaCommand(ins_fn_rxs(r'^\s*CONSOLE\s+SAVE(?:\s+(?P<append>APPEND))?\s+TO\s+', r'\s*$'), x_consolesave))


#****	CONSOLE WAIT
def x_consolewait(**kwargs):
	message = kwargs["message"]
	gui_console_wait_user(message)

metacommands.append(MetaCommand(r'^\s*CONSOLE\s+WAIT(?:\s+"(?P<message>.+)")?\s*$', x_consolewait))


#****	CONSOLE WAIT_WHEN_ERROR
def x_consolewait_onerror(**kwargs):
	flag = kwargs["onoff"].lower()
	conf.gui_wait_on_error_halt = flag in ('on', 'yes')

metacommands.append(MetaCommand(r'^\s*CONSOLE\s+WAIT_WHEN_ERROR\s+(?P<onoff>ON|OFF|YES|NO)\s*$', x_consolewait_onerror))


#****	CONSOLE WAIT_WHEN_DONE
def x_consolewait_whendone(**kwargs):
	flag = kwargs["onoff"].lower()
	conf.gui_wait_on_exit = flag in ('on', 'yes')

metacommands.append(MetaCommand(r'^\s*CONSOLE\s+WAIT_WHEN_DONE\s+(?P<onoff>ON|OFF|YES|NO)\s*$', x_consolewait_whendone))


#****	SUB_APPEND
def x_sub_append(**kwargs):
	working_script.append_substitution(kwargs['match'], kwargs['repl'])
	return None

metacommands.append(MetaCommand(r'^\s*SUB_APPEND\s+(?P<match>\w+)\s+(?P<repl>(.|\n)*)$', x_sub_append))


#****	WRITE SCRIPT
def x_writescript(**kwargs):
	script_id = kwargs["script_id"]
	output_dest = kwargs['filename']
	append = kwargs['append']
	if output_dest is None or output_dest == 'stdout':
		ofile = output
	else:
		if append:
			ofile = EncodedFile(output_dest, conf.output_encoding).open("a")
		else:
			ofile = EncodedFile(output_dest, conf.output_encoding).open("w")
	lines = working_script.script_lines(script_id)
	for line in lines:
		ofile.write(u"%s\n" % line)

metacommands.append(MetaCommand(ins_fn_rxs(r'^\s*WRITE\s+SCRIPT\s+(?P<script_id>\w+)(?:\s+(?P<append>APPEND\s+)?TO\s+', r')?\s*$'), x_writescript))


#****	MAX_INT
def x_max_int(**kwargs):
	global conf
	maxint = kwargs['maxint']
	conf.max_int = long(maxint)
	return None

metacommands.append(MetaCommand(r'^\s*MAX_INT\s+(?P<maxint>[0-9]+)\s*$', x_max_int))


#****	PG_VACUUM
def x_pg_vacuum(**kwargs):
	db = dbs.current()
	if db.type == dbt_postgres:
		args = kwargs["vacuum_args"]
		db.vacuum(args)

metacommands.append(MetaCommand(r'^\s*PG_VACUUM(?P<vacuum_args>.*)\s*$', x_pg_vacuum))


#****	DEBUG LOG SUBVARS
def x_debug_log_subvars(**kwargs):
	for s in subvars.substitutions:
		exec_log.log_status_info("Substitution [%s] = [%s]" % s)
	
metacommands.append(MetaCommand(r'^\s*DEBUG\s+LOG\s+SUBVARS\s*$', x_debug_log_subvars))


#****	DEBUG LOG CONFIG
def x_debug_log_config(**kwargs):
	exec_log.log_status_info("Config; Script encoding = %s" % conf.script_encoding)
	exec_log.log_status_info("Config; Output encoding = %s" % conf.output_encoding)
	exec_log.log_status_info("Config; Import encoding = %s" % conf.import_encoding)
	exec_log.log_status_info("Config; Import common columns only = %s" % conf.import_common_cols_only)
	exec_log.log_status_info("Config; Max int = %d" % conf.max_int)
	exec_log.log_status_info("Config; Boolean int = %s" % conf.boolean_int)
	exec_log.log_status_info("Config; Boolean words = %s" % conf.boolean_words)
	exec_log.log_status_info("Config; Empty_strings = %s" % conf.empty_strings)
	exec_log.log_status_info("Config; GUI level = %s" % conf.gui_level)
	exec_log.log_status_info("Config; GUI wait when done = %s" % conf.gui_wait_on_exit)
	exec_log.log_status_info("Config; GUI wait when error halt = %s" % conf.gui_wait_on_error_halt)
	exec_log.log_status_info("Config; CSS file for HTML export = %s" % conf.css_file)
	exec_log.log_status_info("Config; CSS styles for HTML export = %s" % conf.css_styles)
	exec_log.log_status_info("Config; Make export directories = %s" % conf.make_export_dirs)
	exec_log.log_status_info("Config; Template processor = %s" % conf.template_processor)
	exec_log.log_status_info("Config; Tee writes to log = %s" % conf.tee_write_log)
	exec_log.log_status_info("Config; SMTP host = %s" % conf.smtp_host)
	exec_log.log_status_info("Config; SMTP port = %s" % conf.smtp_port)
	exec_log.log_status_info("Config; SMTP username = %s" % conf.smtp_username)
	exec_log.log_status_info("Config; SMTP use SSL = %s" % conf.smtp_ssl)
	exec_log.log_status_info("Config; SMTP use TLS = %s" % conf.smtp_tls)
	exec_log.log_status_info("Config; Email format = %s" % conf.email_format)
	exec_log.log_status_info("Config; Email CSS = %s" % conf.email_css)

metacommands.append(MetaCommand(r'^\s*DEBUG\s+LOG\s+CONFIG\s*$', x_debug_log_config))


#****	DEBUG WRITE SUBVARS
def x_debug_write_subvars(**kwargs):
	output_dest = kwargs['filename']
	append = kwargs['append']
	if output_dest is None or output_dest == 'stdout':
		ofile = output
	else:
		if append:
			ofile = EncodedFile(output_dest, conf.output_encoding).open("a")
		else:
			ofile = EncodedFile(output_dest, conf.output_encoding).open("w")
	for s in subvars.substitutions:
		ofile.write(u"Substitution [%s] = [%s]\n" % s)

metacommands.append(MetaCommand(ins_fn_rxs(r'^\s*DEBUG\s+WRITE\s+SUBVARS(?:\s+(?P<append>APPEND\s+)?TO\s+', r')?\s*$'), x_debug_write_subvars))


#****	DEBUG WRITE CONFIG
def x_debug_write_config(**kwargs):
	output_dest = kwargs['filename']
	append = kwargs['append']
	if output_dest is None or output_dest == 'stdout':
		ofile = output
	else:
		if append:
			ofile = EncodedFile(output_dest, conf.output_encoding).open("a")
		else:
			ofile = EncodedFile(output_dest, conf.output_encoding).open("w")
	ofile.write(u"Config; Script encoding = %s\n" % conf.script_encoding)
	ofile.write(u"Config; Output encoding = %s\n" % conf.output_encoding)
	ofile.write(u"Config; Import encoding = %s\n" % conf.import_encoding)
	ofile.write(u"Config; Import common columns only = %s\n" % conf.import_common_cols_only)
	ofile.write(u"Config; Max int = %d\n" % conf.max_int)
	ofile.write(u"Config; Boolean int = %s\n" % conf.boolean_int)
	ofile.write(u"Config; Boolean words = %s\n" % conf.boolean_words)
	ofile.write(u"Config; Empty_strings = %s\n" % conf.empty_strings)
	ofile.write(u"Config; GUI level = %s\n" % conf.gui_level)
	ofile.write(u"Config; GUI wait when done = %s\n" % conf.gui_wait_on_exit)
	ofile.write(u"Config; GUI wait when error halt = %s\n" % conf.gui_wait_on_error_halt)
	ofile.write(u"Config; CSS file for HTML export = %s\n" % conf.css_file)
	ofile.write(u"Config; CSS styles for HTML export = %s\n" % conf.css_styles)
	ofile.write(u"Config; Make export directories = %s\n" % conf.make_export_dirs)
	ofile.write(u"Config; Template processor = %s\n" % conf.template_processor)
	ofile.write(u"Config; Tee writes to log = %s\n" % conf.tee_write_log)
	ofile.write(u"Config; SMTP host = %s\n" % conf.smtp_host)
	ofile.write(u"Config; SMTP port = %s\n" % conf.smtp_port)
	ofile.write(u"Config; SMTP username = %s\n" % conf.smtp_username)
	ofile.write(u"Config; SMTP use SSL = %s\n" % conf.smtp_ssl)
	ofile.write(u"Config; SMTP use TLS = %s\n" % conf.smtp_tls)
	ofile.write(u"Config; Email format = %s\n" % conf.email_format)
	ofile.write(u"Config; Email CSS = %s\n" % conf.email_css)

metacommands.append(MetaCommand(ins_fn_rxs(r'^\s*DEBUG\s+WRITE\s+CONFIG(?:\s+(?P<append>APPEND\s+)?TO\s+', r')?\s*$'), x_debug_write_config))


#****	DEBUG WRITE ODBC_DRIVERS
def x_debug_write_odbc_drivers(**kwargs):
	try:
		import pyodbc
	except:
		fatal_error(u"The pyodbc module is required.  See http://github.com/mkleehammer/pyodbc")
	output_dest = kwargs['filename']
	append = kwargs['append']
	if output_dest is None or output_dest == 'stdout':
		ofile = output
	else:
		if append:
			ofile = EncodedFile(output_dest, conf.output_encoding).open("a")
		else:
			ofile = EncodedFile(output_dest, conf.output_encoding).open("w")
	for d in pyodbc.drivers():
		ofile.write(u"%s\n" % d)

metacommands.append(MetaCommand(ins_fn_rxs(r'^\s*DEBUG\s+WRITE\s+ODBC_DRIVERS(?:\s+(?P<append>APPEND\s+)?TO\s+', r')?\s*$'), x_debug_write_odbc_drivers))




#	End of metacommand definitions.
#===============================================================================================


#===============================================================================================
#-----  CONDITIONAL TESTS FOR METACOMMANDS

def xf_hasrows(**kwargs):
	queryname = kwargs["queryname"]
	invert = kwargs["invert"]
	invert = False if invert is None else True
	sql = u"select count(*) from %s;" % queryname
	# Exceptions should be trapped by the caller, so are re-raised here after settting status
	try:
		hdrs, rec = dbs.current().select_data(sql)
	except ErrInfo:
		raise
	except:
		raise ErrInfo("db", sql, exception_msg=exception_desc())
	nrows = rec[0][0]
	#rs.Close()
	if invert:
		return nrows == 0
	return nrows > 0

conditionals.append(MetaCommand(r'^\s*(?P<invert>NOT\s+)?HASROWS\((?P<queryname>.+)\)\s*$', xf_hasrows))

def xf_sqlerror(**kwargs):
	invert = kwargs["invert"]
	if invert:
		return not status.sql_error
	return status.sql_error

conditionals.append(MetaCommand(r'^\s*(?P<invert>NOT\s+)?sql_error\(\s*\)\s*$', xf_sqlerror))

def xf_fileexists(**kwargs):
	filename = kwargs["filename"]
	invert = kwargs["invert"]
	invert = False if invert is None else True
	f_exists = os.path.isfile(filename.strip())
	if invert:
		f_exists = not f_exists
	return f_exists

conditionals.append(MetaCommand(r'^(?P<invert>NOT\s+)?FILE_EXISTS\(\s*("?)(?P<filename>[^")]+)\2\)\s*$', xf_fileexists))


def xf_direxists(**kwargs):
	dirname = kwargs["dirname"]
	invert = kwargs["invert"]
	invert = False if invert is None else True
	f_exists = os.path.isdir(dirname.strip())
	if invert:
		f_exists = not f_exists
	return f_exists

conditionals.append(MetaCommand(r'^(?P<invert>NOT\s+)?DIRECTORY_EXISTS\(\s*("?)(?P<dirname>[^")]+)\2\)\s*$', xf_direxists))


def xf_schemaexists(**kwargs):
	schemaname = kwargs["schema"]
	invert = kwargs["invert"]
	invert = False if invert is None else True
	t_exists = dbs.current().schema_exists(schemaname)
	if invert:
		t_exists = not t_exists
	return t_exists

conditionals.append(MetaCommand((
	r'^(?P<invert>NOT\s+)?SCHEMA_EXISTS\(\s*"(?P<schema>[A-Za-z0-9_\-\: ]+)"\s*\)\s*$',
	r'^(?P<invert>NOT\s+)?SCHEMA_EXISTS\(\s*(?P<schema>[A-Za-z0-9_\-\: ]+)\s*\)\s*$'
	), xf_schemaexists))


def xf_tableexists(**kwargs):
	schemaname = kwargs["schema"]
	tablename = kwargs["tablename"]
	invert = kwargs["invert"]
	invert = False if invert is None else True
	t_exists = dbs.current().table_exists(tablename.strip(), schemaname)
	if invert:
		t_exists = not t_exists
	return t_exists

conditionals.append(MetaCommand((
	r'^(?P<invert>NOT\s+)?TABLE_EXISTS\(\s*(?:"(?P<schema>[A-Za-z0-9_\-\: ]+)"\.)?"(?P<tablename>[A-Za-z0-9_\-\: ]+)"\)\s*$',
	r'^(?P<invert>NOT\s+)?TABLE_EXISTS\(\s*(?:\[(?P<schema>[A-Za-z0-9_\-\: ]+)\]\.)?\[(?P<tablename>[A-Za-z0-9_\-\: ]+)\]\)\s*$',
	r'^(?P<invert>NOT\s+)?TABLE_EXISTS\(\s*(?:(?P<schema>[A-Za-z0-9_\-\: ]+)\.)?(?P<tablename>[A-Za-z0-9_\-\: ]+)\)\s*$'
	), xf_tableexists))

def xf_sub_defined(**kwargs):
	invert = kwargs["invert"]
	invert = False if invert is None else True
	s_exists = working_script.sub_exists(kwargs["match_str"])
	if invert:
		s_exists = not s_exists
	return s_exists


conditionals.append(MetaCommand(r'^(?:(?P<invert>NOT)\s+)?SUB_DEFINED\s*\(\s*(?P<match_str>[\$@]?\w+)\s*\)\s*$', xf_sub_defined))

def xf_equals(**kwargs):
	import unicodedata
	invert = kwargs["invert"]
	invert = False if invert is None else True
	s1 = unicodedata.normalize('NFC', kwargs["string1"]).lower()
	s2 = unicodedata.normalize('NFC', kwargs["string2"]).lower()
	converters = (int, float, DT_Timestamp().from_data, DT_TimestampTZ().from_data, DT_Date().from_data, DT_Boolean().from_data)
	for convf in converters:
		try:
			v1 = convf(s1)
			v2 = convf(s2)
		except:
			continue
		are_eq = v1 == v2
		if are_eq:
			break
	else:
		are_eq = s1 == s2
	return are_eq if not invert else not are_eq

conditionals.append(MetaCommand(r'^\s*(?:(?P<invert>NOT)\s+)?EQUAL(S)?\s*\(\s*"(?P<string1>.+)"\s*,\s*"(?P<string2>.+)"\s*\)\s*$', xf_equals))

def xf_identical(**kwargs):
	invert = kwargs["invert"]
	invert = False if invert is None else True
	s1 = kwargs["string1"]
	s2 = kwargs["string2"]
	are_eq = s1 == s2
	return are_eq if not invert else not are_eq

conditionals.append(MetaCommand(r'^\s*(?:(?P<invert>NOT)\s+)?IDENTICAL\s*\(\s*"(?P<string1>.+)"\s*,\s*"(?P<string2>.+)"\s*\)\s*$', xf_identical))

def xf_isnull(**kwargs):
	invert = kwargs["invert"]
	item = kwargs["item"].strip()
	invert = False if invert is None else True
	isnull = item == u""
	return isnull if not invert else not isnull

conditionals.append(MetaCommand(r'^\s*(?:(?P<invert>NOT)\s+)?IS_NULL\(\s*(?P<item>".*")\s*\)\s*$', xf_isnull))

def xf_iszero(**kwargs):
	invert = kwargs["invert"]
	val = kwargs["value"].strip()
	invert = False if invert is None else True
	try:
		v = float(val)
	except:
		raise ErrInfo(type="cmd", command_text=kwargs["metacommandline"], other_msg="The value {%s} is not numeric." % val)
	rv = v == 0
	return rv if not invert else not rv

conditionals.append(MetaCommand(r'^\s*(?:(?P<invert>NOT)\s+)?IS_ZERO\(\s*(?P<value>.*)\s*\)\s*$', xf_iszero))

def xf_isgt(**kwargs):
	invert = kwargs["invert"]
	invert = False if invert is None else True
	val1 = kwargs["value1"].strip()
	val2 = kwargs["value2"].strip()
	try:
		v1 = float(val1)
		v2 = float(val2)
	except:
		raise ErrInfo(type="cmd", command_text=kwargs["metacommandline"], other_msg="Values {%s} and {%s} are not both numeric." % (val1, val2))
	rv = v1 > v2
	return rv if not invert else not rv

conditionals.append(MetaCommand(r'^\s*(?:(?P<invert>NOT)\s+)?IS_GT\(\s*(?P<value1>.*)\s*,\s*(?P<value2>.*)\s*\)\s*$', xf_isgt))

def xf_isgte(**kwargs):
	invert = kwargs["invert"]
	invert = False if invert is None else True
	val1 = kwargs["value1"].strip()
	val2 = kwargs["value2"].strip()
	try:
		v1 = float(val1)
		v2 = float(val2)
	except:
		raise ErrInfo(type="cmd", command_text=kwargs["metacommandline"], other_msg="Values {%s} and {%s} are not both numeric." % (val1, val2))
	rv = v1 >= v2
	return rv if not invert else not rv

conditionals.append(MetaCommand(r'^\s*(?:(?P<invert>NOT)\s+)?IS_GTE\(\s*(?P<value1>.*)\s*,\s*(?P<value2>.*)\s*\)\s*$', xf_isgte))

def xf_dbms(**kwargs):
	dbms = kwargs["dbms"]
	invert = kwargs["invert"]
	invert = False if invert is None else True
	name_matches = dbs.current().type.dbms_id.lower() == dbms.strip().lower()
	if invert:
		name_matches = not name_matches
	return name_matches

conditionals.append(MetaCommand(r'^\s*(?:(?P<invert>NOT)\s+)?DBMS\(\s*"(?P<dbms>[A-Z0-9_\-\(\)\/\\\. ]+)"\s*\)\s*$', xf_dbms))

def xf_dbname(**kwargs):
	dbname = kwargs["dbname"]
	invert = kwargs["invert"]
	invert = False if invert is None else True
	name_matches = dbs.current().name().lower() == dbname.strip().lower()
	if invert:
		name_matches = not name_matches
	return name_matches

conditionals.append(MetaCommand(r'^\s*(?:(?P<invert>NOT)\s+)?DATABASE_NAME\(\s*(?P<dbname>[A-Z0-9_\-\(\)\/\\\. ]+)\s*\)\s*$', xf_dbname))

def xf_viewexists(**kwargs):
	viewname = kwargs["viewname"]
	invert = kwargs["invert"]
	invert = False if invert is None else True
	v_exists = dbs.current().view_exists(viewname.strip())
	if invert:
		v_exists = not v_exists
	return v_exists

conditionals.append(MetaCommand(r'^\s*(?:(?P<invert>NOT)\s+)?VIEW_EXISTS\(\s*("?)(?P<viewname>[^")]+)\2\)\s*$', xf_viewexists))

def xf_columnexists(**kwargs):
	tablename = kwargs["tablename"]
	schemaname = kwargs["schema"]
	columnname = kwargs["columnname"]
	invert = kwargs["invert"]
	invert = False if invert is None else True
	v_exists = dbs.current().column_exists(tablename.strip(), columnname.strip(), schemaname)
	if invert:
		v_exists = not v_exists
	return v_exists

conditionals.append(MetaCommand((
	r'^(?P<invert>NOT\s+)?COLUMN_EXISTS\(\s*"(?P<columnname>[A-Za-z0-9_\-\: ]+)"\s+IN\s+(?:"(?P<schema>[A-Za-z0-9_\-\: ]+)"\.)?"(?P<tablename>[A-Za-z0-9_\-\: ]+)"\)\s*$',
	r'^(?P<invert>NOT\s+)?COLUMN_EXISTS\(\s*"(?P<columnname>[A-Za-z0-9_\-\: ]+)"\s+IN\s+(?:\[(?P<schema>[A-Za-z0-9_\-\: ]+)\]\.)?\[(?P<tablename>[A-Za-z0-9_\-\: ]+)\]\)\s*$',
	r'^(?P<invert>NOT\s+)?COLUMN_EXISTS\(\s*"(?P<columnname>[A-Za-z0-9_\-\: ]+)"\s+IN\s+(?:(?P<schema>[A-Za-z0-9_\-\: ]+)\.)?(?P<tablename>[A-Za-z0-9_\-\: ]+)\)\s*$',
	r'^(?P<invert>NOT\s+)?COLUMN_EXISTS\(\s*(?P<columnname>[A-Za-z0-9_\-\:]+)\s+IN\s+(?:"(?P<schema>[A-Za-z0-9_\-\: ]+)"\.)?"(?P<tablename>[A-Za-z0-9_\-\: ]+)"\)\s*$',
	r'^(?P<invert>NOT\s+)?COLUMN_EXISTS\(\s*(?P<columnname>[A-Za-z0-9_\-\:]+)\s+IN\s+(?:\[(?P<schema>[A-Za-z0-9_\-\: ]+)\]\.)?\[(?P<tablename>[A-Za-z0-9_\-\: ]+)\]\)\s*$',
	r'^(?P<invert>NOT\s+)?COLUMN_EXISTS\(\s*(?P<columnname>[A-Za-z0-9_\-\:]+)\s+IN\s+(?:(?P<schema>[A-Za-z0-9_\-\: ]+)\.)?(?P<tablename>[A-Za-z0-9_\-\: ]+)\)\s*$'
	), xf_columnexists))

def xf_aliasdefined(**kwargs):
	invert = kwargs["invert"]
	alias = kwargs["alias"]
	a_exists = alias in dbs.aliases()
	if invert:
		a_exists = not a_exists
	return a_exists

conditionals.append(MetaCommand(r'^\s*(?:(?P<invert>NOT)\s+)?ALIAS_DEFINED\s*\(\s*(?P<alias>\w+)\s*\)\s*$', xf_aliasdefined))

def xf_sqlerror(**kwargs):
	invert = kwargs["invert"]
	if invert:
		return not status.sql_error
	return status.sql_error

conditionals.append(MetaCommand(r'^\s*(?P<invert>NOT\s+)?sql_error\(\s*\)\s*$', xf_sqlerror))

def xf_metacommanderror(**kwargs):
	invert = kwargs["invert"]
	if invert:
		return not status.metacommand_error
	return status.metacommand_error

conditionals.append(MetaCommand(r'^\s*(?P<invert>NOT\s+)?metacommand_error\(\s*\)\s*$', xf_metacommanderror))

def xf_console(**kwargs):
	invert = kwargs["invert"]
	console_on = gui_console_isrunning()
	if invert:
		console_on = not console_on
	return console_on

conditionals.append(MetaCommand(r'^\s*(?:(?P<invert>NOT)\s+)?CONSOLE\s*$', xf_console))

def xf_newer_file(**kwargs):
	invert = kwargs["invert"]
	file1 = kwargs["file1"]
	file2 = kwargs["file2"]
	if not os.path.exists(file1):
		raise ErrInfo(type="cmd", other_msg="File %s does not exist." % file1)
	if not os.path.exists(file2):
		raise ErrInfo(type="cmd", other_msg="File %s does not exist." % file2)
	newer = os.stat(file1).st_mtime > os.stat(file2).st_mtime
	if invert:
		newer = not newer
	return newer

conditionals.append(MetaCommand(ins_fn_rxs(r'^\s*(?:(?P<invert>NOT)\s+)?NEWER_FILE\s*\(\s*',
									ins_fn_rxs(r'\s*,\s*', r'\s*\)\s*$', symbolicname='file2'), symbolicname='file1'), xf_newer_file))

def xf_newer_date(**kwargs):
	invert = kwargs["invert"]
	file1 = kwargs["file1"]
	datestr = kwargs["datestr"]
	if not os.path.exists(file1):
		raise ErrInfo(type="cmd", other_msg="File %s does not exist." % file1)
	dt_value = parse_datetime(datestr)
	if not dt_value:
		raise ErrInfo(type="cmd", other_msg="%s can't be interpreted as a date/time." % datestr)
	newer = os.stat(file1).st_mtime > time.mktime(dt_value.timetuple())
	if invert:
		newer = not newer
	return newer

conditionals.append(MetaCommand(ins_fn_rxs(r'^\s*(?:(?P<invert>NOT)\s+)?NEWER_DATE\s*\(\s*',
									r'\s*,\s*(?P<datestr>.+)\s*\)\s*$', symbolicname='file1'), xf_newer_date))


def xcmd_test(teststr):
	for test in conditionals:
		applies, result = test.run(teststr)
		if applies:
			return result
	else:
		raise ErrInfo(type="cmd", command_text=teststr, other_msg="Unrecognized conditional")


#	End of conditional tests for metacommands.
#===============================================================================================


#===============================================================================================
#-----  SUPPORT FUNCTIONS (2)

def file_size_date(filename):
	# Returns the file size and date (as string) of the given file.
	s_file = os.path.abspath(filename)
	f_stat = os.stat(s_file)
	return f_stat.st_size, time.strftime(u"%Y-%m-%d %H:%M", time.gmtime(f_stat.st_mtime))

def chainfuncs(*funcs):
	funclist = funcs
	def execchain(*args):
		for f in funclist:
			f()
	return execchain

def as_none(item):
	if isinstance(item, basestring) and len(item) == 0:
		return None
	elif isinstance(item, int) and item == 0:
		return None
	return item

def parse_datetime(datestr):
	dt_fmts = (
				"%c",
				"%x %X",
				"%m/%d/%y %H%M",
				"%m/%d/%y %H:%M",
				"%m/%d/%y %H:%M:%S",
				"%m/%d/%y %I:%M%p",
				"%m/%d/%y %I:%M %p",
				"%m/%d/%y %I:%M:%S%p",
				"%m/%d/%y %I:%M:%S %p",
				"%m/%d/%Y %H%M",
				"%m/%d/%Y %H:%M",
				"%m/%d/%Y %H:%M:%S",
				"%m/%d/%Y %I:%M%p",
				"%m/%d/%Y %I:%M %p",
				"%m/%d/%Y %I:%M:%S%p",
				"%m/%d/%Y %I:%M:%S %p",
				"%Y-%m-%d %H%M",
				"%Y-%m-%d %H:%M",
				"%Y-%m-%d %H:%M:%S",
				"%Y-%m-%d %I:%M%p",
				"%Y-%m-%d %I:%M %p",
				"%Y-%m-%d %I:%M:%S%p",
				"%Y-%m-%d %I:%M:%S %p",
				"%Y/%m/%d %H%M",
				"%Y/%m/%d %H:%M",
				"%Y/%m/%d %H:%M:%S",
				"%Y/%m/%d %I:%M%p",
				"%Y/%m/%d %I:%M %p",
				"%Y/%m/%d %I:%M:%S%p",
				"%Y/%m/%d %I:%M:%S %p",
				"%Y/%m/%d %X",
				"%b %d, %Y %X",
				"%b %d, %Y %I:%M %p",
				"%b %d %Y %X",
				"%b %d %Y %I:%M %p",
				"%d %b, %Y %X",
				"%d %b, %Y %I:%M %p",
				"%d %b %Y %X",
				"%d %b %Y %I:%M %p",
				"%b. %d, %Y %X",
				"%b. %d, %Y %I:%M %p",
				"%b. %d %Y %X",
				"%b. %d %Y %I:%M %p",
				"%d %b., %Y %X",
				"%d %b., %Y %I:%M %p",
				"%d %b. %Y %X",
				"%d %b. %Y %I:%M %p",
				"%B %d, %Y %X",
				"%B %d, %Y %I:%M %p",
				"%B %d %Y %X",
				"%B %d %Y %I:%M %p",
				"%d %B, %Y %X",
				"%d %B, %Y %I:%M %p",
				"%d %B %Y %X",
				"%d %B %Y %I:%M %p",
				"%x",
				"%m/%d/%Y",
				"%m/%d/%y",
				"%Y-%m-%d",
				"%Y/%m/%d",
				"%b %d, %Y",
				"%b %d %Y",
				"%d %b, %Y",
				"%d %b %Y",
				"%b. %d, %Y",
				"%b. %d %Y",
				"%d %b., %Y",
				"%d %b. %Y",
				"%B %d, %Y",
				"%B %d %Y",
				"%d %B, %Y",
				"%d %B %Y"
				)
	if type(datestr) == datetime.datetime:
		return datestr
	if not isinstance(datestr, basestring):
		datestr = unicode(datestr)
	dt = None
	for f in dt_fmts:
		try:
			dt = datetime.datetime.strptime(datestr, f)
		except:
			continue
		break
	return dt

def parse_datetimetz(data):
	timestamptz_fmts = (
		"%c%Z", "%c %Z",
		"%x %X%Z", "%x %X %Z",
		"%m/%d/%Y%Z", "%m/%d/%Y %Z",
		"%m/%d/%y%Z", "%m/%d/%y %Z",
		"%m/%d/%y %H%M%Z", "%m/%d/%y %H%M %Z",
		"%m/%d/%y %H:%M%Z", "%m/%d/%y %H:%M %Z",
		"%m/%d/%y %H:%M:%S%Z", "%m/%d/%y %H:%M:%S %Z",
		"%m/%d/%y %I:%M%p%Z", "%m/%d/%y %I:%M%p %Z",
		"%m/%d/%y %I:%M %p%Z", "%m/%d/%y %I:%M %p %Z",
		"%m/%d/%y %I:%M:%S%p%Z", "%m/%d/%y %I:%M:%S%p %Z",
		"%m/%d/%y %I:%M:%S %p%Z", "%m/%d/%y %I:%M:%S %p %Z",
		"%m/%d/%Y %H%M%Z", "%m/%d/%Y %H%M %Z",
		"%m/%d/%Y %H:%M%Z", "%m/%d/%Y %H:%M %Z",
		"%m/%d/%Y %H:%M:%S%Z", "%m/%d/%Y %H:%M:%S %Z",
		"%m/%d/%Y %I:%M%p%Z", "%m/%d/%Y %I:%M%p %Z",
		"%m/%d/%Y %I:%M %p%Z", "%m/%d/%Y %I:%M %p %Z",
		"%m/%d/%Y %I:%M:%S%p%Z", "%m/%d/%Y %I:%M:%S%p %Z",
		"%m/%d/%Y %I:%M:%S %p%Z", "%m/%d/%Y %I:%M:%S %p %Z",
		"%Y-%m-%d %H%M%Z", "%Y-%m-%d %H%M %Z",
		"%Y-%m-%d %H:%M%Z", "%Y-%m-%d %H:%M %Z",
		"%Y-%m-%d %H:%M:%S%Z", "%Y-%m-%d %H:%M:%S %Z",
		"%Y-%m-%d %I:%M%p%Z", "%Y-%m-%d %I:%M%p %Z",
		"%Y-%m-%d %I:%M %p%Z", "%Y-%m-%d %I:%M %p %Z",
		"%Y-%m-%d %I:%M:%S%p%Z", "%Y-%m-%d %I:%M:%S%p %Z",
		"%Y-%m-%d %I:%M:%S %p%Z", "%Y-%m-%d %I:%M:%S %p %Z",
		"%Y/%m/%d %H%M%Z", "%Y/%m/%d %H%M %Z",
		"%Y/%m/%d %H:%M%Z", "%Y/%m/%d %H:%M %Z",
		"%Y/%m/%d %H:%M:%S%Z", "%Y/%m/%d %H:%M:%S %Z",
		"%Y/%m/%d %I:%M%p%Z", "%Y/%m/%d %I:%M%p %Z",
		"%Y/%m/%d %I:%M %p%Z", "%Y/%m/%d %I:%M %p %Z",
		"%Y/%m/%d %I:%M:%S%p%Z", "%Y/%m/%d %I:%M:%S%p %Z",
		"%Y/%m/%d %I:%M:%S %p%Z", "%Y/%m/%d %I:%M:%S %p %Z",
		"%Y/%m/%d %X%Z", "%Y/%m/%d %X %Z",
		"%b %d, %Y %X%Z", "%b %d, %Y %X %Z",
		"%b %d, %Y %I:%M %p%Z", "%b %d, %Y %I:%M %p %Z",
		"%b %d %Y %X%Z", "%b %d %Y %X %Z",
		"%b %d %Y %I:%M %p%Z", "%b %d %Y %I:%M %p %Z",
		"%d %b, %Y %X%Z", "%d %b, %Y %X %Z",
		"%d %b, %Y %I:%M %p%Z", "%d %b, %Y %I:%M %p %Z",
		"%d %b %Y %X%Z", "%d %b %Y %X %Z",
		"%d %b %Y %I:%M %p%Z", "%d %b %Y %I:%M %p %Z",
		"%b. %d, %Y %X%Z", "%b. %d, %Y %X %Z",
		"%b. %d, %Y %I:%M %%Z", "%b. %d, %Y %I:%M %p %Z",
		"%b. %d %Y %X%Z", "%b. %d %Y %X %Z",
		"%b. %d %Y %I:%M %p%Z", "%b. %d %Y %I:%M %p %Z",
		"%d %b., %Y %X%Z", "%d %b., %Y %X %Z",
		"%d %b., %Y %I:%M %p%Z", "%d %b., %Y %I:%M %p %Z",
		"%d %b. %Y %X%Z", "%d %b. %Y %X %Z",
		"%d %b. %Y %I:%M %p%Z", "%d %b. %Y %I:%M %p %Z",
		"%B %d, %Y %X%Z", "%B %d, %Y %X %Z",
		"%B %d, %Y %I:%M %p%Z", "%B %d, %Y %I:%M %p %Z",
		"%B %d %Y %X%Z", "%B %d %Y %X %Z",
		"%B %d %Y %I:%M %p%Z", "%B %d %Y %I:%M %p %Z",
		"%d %B, %Y %X%Z", "%d %B, %Y %X %Z",
		"%d %B, %Y %I:%M %p%Z", "%d %B, %Y %I:%M %p %Z",
		"%d %B %Y %X%Z", "%d %B %Y %X %Z",
		"%d %B %Y %I:%M %p%Z", "%d %B %Y %I:%M %p %Z"
		)
	if type(data) == type(datetime.datetime.now()):
		if data.tzinfo is None or data.tzinfo.utcoffset(data) is None:
			return None
		return data
	if not isinstance(data, basestring):
		return None
	dt = None
	# Check for numeric timezone
	dtzrx = re.compile(u"(.+)\s*([+-])(\d{1,2}):?(\d{2})$")
	try:
		datestr, sign, hr, min = dtzrx.match(data).groups()
		dt = parse_datetime(datestr)
		if not dt:
			return None
		sign = -1 if sign=='-' else 1
		return datetime.datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, tzinfo=Tz(sign, int(hr), int(min)))
	except:
		# Check for alphabetic timezone
		for f in timestamptz_fmts:
			try:
				dt = datetime.datetime.strptime(data, f)
			except:
				continue
			break
		return dt


def read_sqlscript(scriptfile_obj, script_dict, script_id):
	# Read lines from the given script file object and create a list of SqlCmd objects in the
	# script_dict with the given script_id.  The filename (fn) and line number
	# are stored with each command.
	# Function parameters
	#    scriptfile_obj: A ScriptFile object that identifies the file to be read.
	#	 script_dict:    A dictionary of named lists of SqlCmd objects.
	#    script_id:      The name (key) to be used for the script_dict.
	# Lines containing execsql command statements must begin with "-- !x!"
	# Currently this routine knows only three things about SQL:
	#	1. Lines that start with "--" are comments.
	#	2. Lines that end with ";" terminate a SQL statement.'
	#	3. Lines that start with "/*" begin a block comment, and lines that
	#		end with "*/" end a block comment.
	# The following metacommands are executed IMMEDIATELY during this process:
	#	* BEGIN SCRIPT <scriptname>
	#	* END SCRIPT
	beginscript = re.compile(r'^--\s*!x!\s*BEGIN\s+SCRIPT\s+(?P<scriptname>\w+)\s*$', re.I)
	endscript = re.compile(r'^--\s*!x!\s*END\s+SCRIPT\s*$', re.I)
	execline = re.compile(r'^--\s*!x!\s*(?P<cmd>.+)$', re.I)
	cmtline = re.compile(r'^--')
	in_block_cmt = False
	is_comment_line = False
	sqllist = []
	if not script_id in script_dict.keys():
		script_dict[script_id] = []
	ended = False
	currcmd = ''
	while not ended:
		try:
			line = scriptfile_obj.next()
		except StopIteration:
			ended = True
		except:
			raise
		if not ended:
			line = line.strip()
			is_comment_line = False
			if len(line) > 0:
				if in_block_cmt:
					is_comment_line = True
					if line[-2:] == u"*/":
						in_block_cmt = False
				else:
					# Not in block comment
					if line[0:2] == u"/*":
						in_block_cmt = True
						is_comment_line = True
						if line[-2:] == u"*/":
							in_block_cmt = False
					else:
						if cmtline.match(line):
							is_comment_line = not execline.match(line)
				if not is_comment_line:
					m = execline.match(line)
					if m:
						begs = beginscript.match(line)
						if not begs:
							ends = endscript.match(line)
						if begs:
							# This is a BEGIN SCRIPT metacommand
							scriptname = begs.group('scriptname').lower()
							read_sqlscript(scriptfile_obj, script_dict, scriptname)
						elif ends:
							# This is an END SCRIPT metacommand
							ended = True
						else:
							# This is a non-IMMEDIATE metacommand
							sqllist.append(SqlCmd(scriptfile_obj.filename, scriptfile_obj.lno, 'cmd', m.group('cmd').strip()))
					else:
						# This line is not a comment and not a metacommand, therefore should be
						# part of a SQL statement.
						cmd_end = True if line[-1] == ';' else False
						if line[-1] == '\\':
							line = line[:-1].strip()
						if currcmd == '':
							sqlline = scriptfile_obj.lno
							currcmd = line
						else:
							currcmd = u"%s \n%s" % (currcmd, line)
						if cmd_end:
							sqllist.append(SqlCmd(scriptfile_obj.filename, sqlline, 'sql', currcmd.strip()))
							currcmd = ''
	script_dict[script_id].extend(sqllist)


def read_sqlscriptfile(fn, script_dict, script_id):
	# Open the text file with the specified name (fn), read it, and return a list of
	# SqlCmd objects representing either SQL statements or execsql command statements.
	f = ScriptFile(fn, conf.script_encoding)
	read_sqlscript(f, script_dict, script_id)


def write_delimited_file(outfile, filefmt, column_headers, rowsource, file_encoding='utf8', append=False):
	o_file = CsvFile(outfile, file_encoding)
	if filefmt.lower() == 'csv':
		o_file.lineformat(',', '"', None)
	elif filefmt.lower() in ('tab', 'tsv'):
		o_file.lineformat('\t', None, None)
	elif filefmt.lower() in ('tabq', 'tsvq'):
		o_file.lineformat('\t', '"', None)
	elif filefmt.lower() in ('unitsep', 'us'):
		o_file.lineformat(chr(31), None, None)
	elif filefmt.lower() == 'plain':
		o_file.lineformat(' ', '', None)
	ofile = o_file.writer(append)
	if not (filefmt.lower() == 'plain' or append):
		ofile.writerow(column_headers)
	for rec in rowsource:
		try:
			ofile.writerow(rec)
		except ErrInfo:
			raise
		except:
			raise ErrInfo("exception", exception_msg=exception_desc(), other_msg=u"Can't write output to file %s." % outfile)

def write_query_raw(outfile, rowsource, append=False):
	mode = "wb" if not append else "ab"
	of = open(outfile, mode)
	for row in rowsource:
		for col in row:
			of.write(col)
	of.close()


def pause(message=None, max_time=None):
	if message:
		output.write(message+"\n")
	output.write("Press <Enter> to continue, <Esc> to quit. ")
	if max_time:
		th = TimerHandler(max_time)
		output.write("\n")
		old_alarm_handler = signal.signal(signal.SIGALRM, th.alarm_handler)
		signal.setitimer(signal.ITIMER_REAL, 0.01, 0.01)
	gc = GetChar()
	timed_out = False
	c = None
	while True:
		try:
			c = gc.getch()
		except TimeoutError:
			timed_out = True
			del gc
			break
		if c == chr(13) or c == chr(27):
			if max_time:
				signal.setitimer(signal.ITIMER_REAL, 0)
			break
		c = None
	if max_time:
		signal.signal(signal.SIGALRM, old_alarm_handler)
	output.write("\n")
	if c and c == chr(27):
		return 1
	elif timed_out:
		return 2
	return 0

def pause_win(message=None, max_time=None):
	if message:
		output.write(message+"\n")
	output.write("Press <Enter> to continue, <Esc> to quit. ")
	if max_time:
		output.write("\n")
		start_time = time.time()
	timed_out = False
	while True:
		if msvcrt.kbhit():
			c = msvcrt.getch()
			if c == chr(13) or c == chr(27):
				break
		c = None
		if max_time:
			elapsed_time = time.time() - start_time
			if elapsed_time > max_time:
				timed_out = True
				break
			time_left = max_time - elapsed_time
			barlength = 30
			bar_left = int(round(barlength * time_left/max_time, 0))
			sys.stdout.write("%s  |%s%s|\r" % ("{:8.1f}".format(time_left), "+"*bar_left, "-"*(barlength-bar_left)))
		time.sleep(0.01)
	output.write("\n")
	if c and c == chr(27):
		return 1
	elif timed_out:
		return 2
	return 0


def get_yn(message):
	output.write(message + " [y, n, <Esc> to quit]: ")
	gc = GetChar()
	c = None
	while not c in ('y', 'n', 'Y', 'N', chr(27)):
		c = gc.getch()
	if c.lower() in ('y', 'n'):
		output.write(c)
	output.write("\n")
	return c.lower()


def get_yn_win(message):
	output.write(message + " [y, n, <Esc> to quit]: ")
	c = None
	while not c in ('y', 'n', 'Y', 'N', chr(27)):
		if msvcrt.kbhit():
			c = msvcrt.getch()
	if c.lower() in ('y', 'n'):
		output.write(c)
	output.write("\n")
	return c.lower()




def make_export_dirs(outfile):
	if outfile.lower() != 'stdout':
		output_dir = os.path.dirname(outfile)
		if output_dir != '':
			output_dir = os.path.normpath(output_dir)
			emsg = "Can't create, or can't access, the directory %s to use for EXPORTed data." % output_dir
			try:
				os.makedirs(output_dir)
			except OSError as e:
				if e.errno != errno.EEXIST:
					raise ErrInfo("exception", exception_msg=emsg)
			except:
				raise ErrInfo("exception", exception_msg=emsg)

def get_password(dbms_name, database_name, user_name, server_name=None, other_msg=None):
	global conf
	global gui_manager_thread, gui_manager_queue
	use_gui = False
	if working_script:
		script_name, line_no = working_script.current_script_line()
	else:
		script_name = ""
		line_no = 0
	prompt = "The execsql script %s wants the %s password for" % (script_name, dbms_name)
	if server_name is not None:
		prompt = "%s\nServer: %s" % (prompt, server_name)
	prompt = "%s\nDatabase: %s\nUser: %s" % (prompt, database_name, user_name)
	if other_msg is not None:
		prompt = "%s\n%s" % (prompt, other_msg)
	if gui_manager_thread:
		return_queue = Queue.Queue()
		gui_manager_queue.put(GuiSpec(QUERY_CONSOLE, {}, return_queue))
		user_response = return_queue.get(block=True)
		use_gui = user_response["console_running"]
	if use_gui or conf.gui_level > 0:
		enable_gui()
		return_queue = Queue.Queue()
		gui_args = {"title": "Password for %s database %s" % (dbms_name, database_name),
					 "message": prompt,
					 "button_list": [("Continue", 1, "<Return>")],
					 "textentry": True,
					 "hidetext": True}
		gui_manager_queue.put(GuiSpec(GUI_DISPLAY, gui_args, return_queue))
		user_response = return_queue.get(block=True)
		btn = user_response["button"]
		passwd = user_response["return_value"]
		if not btn:
			if status.cancel_halt:
				exec_log.log_exit_halt(script_name, line_no, "Canceled on password prompt for %s database %s, user %s" % (dbms_name, database_name, user_name))
				exit_now(2, None)
	else:
		prompt = prompt.replace('\n', ' ', 1).replace('\n', ', ') + " >"
		passwd = getpass.getpass(str(prompt.encode('ascii', 'ignore')))
	return passwd

def prettyprint_rowset(colhdrs, rows, output_dest, append=False, nd_val=u'', desc=None):
	# Adapted from the pp() function by Aaron Watters,
	# posted to gadfly-rdbms@egroups.com 1999-01-18.
	def as_ucode(s):
		if s is None:
			return nd_val
		if isinstance(s, unicode):
			return s
		if isinstance(s, str):
			return s.decode(dbs.current().encoding)
		return unicode(s)
	if type(rows) <> 'list':
		try:
			rows = list(rows)
		except:
			raise ErrInfo("exception", exception_msg=exception_desc(), other_msg="Can't create a list in memory of the data to be displayed as formatted text.")
	rcols = range(len(colhdrs))
	rrows = range(len(rows))
	colwidths = [max(0, len(colhdrs[j]), *(len(as_ucode(rows[i][j])) for i in rrows)) for j in rcols]
	names = u' '+u' | '.join([colhdrs[j].ljust(colwidths[j]) for j in rcols])
	sep = u'|'.join([u'-'*(colwidths[j]+2) for j in rcols])
	rows = [names, sep] + [u' '+u' | '.join(
			[as_ucode(rows[i][j]).ljust(colwidths[j])
			for j in rcols]) for i in rrows]
	if output_dest == 'stdout':
		ofile = output
		margin = u'    '
	else:
		margin = u' '
		if append:
			ofile = EncodedFile(output_dest, conf.output_encoding).open("a")
		else:
			ofile = EncodedFile(output_dest, conf.output_encoding).open("w")
	if desc is not None:
		ofile.write(u"%s\n" % desc)
	for row in rows:
		ln = u"%s%s\n" % (margin, row)
		ofile.write(ln)
	return None

def prettyprint_query(select_stmt, db, outfile, append=False, nd_val=u'', desc=None):
	status.sql_error = False
	names, rows = db.select_data(select_stmt)
	prettyprint_rowset(names, rows, outfile, append, nd_val, desc)

def report_query(select_stmt, db, outfile, template_file, append=False):
	# Write (export) a template-based report.
	status.sql_error = False
	#names, rows = db.select_rowsource(select_stmt)
	headers, ddict = db.select_rowdict(select_stmt)
	if conf.template_processor == 'jinja':
		t = JinjaTemplateReport(template_file)
	elif conf.template_processor == 'airspeed':
		t = AirspeedTemplateReport(template_file)
	else:
		t = StrTemplateReport(template_file)
	t.write_report(headers, ddict, outfile, append)

def write_query_to_ods(select_stmt, db, outfile, append=False, sheetname=None, desc=None):
	try:
		hdrs, rows = db.select_rowsource(select_stmt)
	except ErrInfo:
		raise
	except:
		raise ErrInfo("db", select_stmt, exception_msg=exception_desc())
	export_ods(outfile, hdrs, rows, append, select_stmt, sheetname, desc)

def export_ods(outfile, hdrs, rows, append=False, querytext=None, sheetname=None, desc=None):
	# If not given, determine the worksheet name to use.  The pattern is "Sheetx", where x is
	# the first integer for which there is not already a sheet name.
	if append and os.path.isfile(outfile):
		wbk = OdsFile()
		wbk.open(unicode(outfile))
		sheet_names = wbk.sheetnames()
		name = sheetname or u"Sheet"
		sheet_name = name
		sheet_no = 1
		while True:
			if sheet_name not in sheet_names:
				break
			sheet_no += 1
			sheet_name = u"%s%d" % (name, sheet_no)
		wbk.close()
	else:
		sheet_name = sheetname or u"Sheet1"
		if os.path.isfile(outfile):
			os.unlink(outfile)
	wbk = OdsFile()
	wbk.open(unicode(outfile))
	# Add a "Datasheets" inventory sheet if it doesn't exist.
	datasheet_name = u"Datasheets"
	if not datasheet_name in wbk.sheetnames():
		inventory_sheet = wbk.new_sheet(datasheet_name)
		wbk.add_row_to_sheet(('datasheet_name', 'created_on', 'created_by', 'description', 'source'), inventory_sheet)
		wbk.add_sheet(inventory_sheet)
	# Add the data to a new sheet.
	tbl = wbk.new_sheet(sheet_name)
	wbk.add_row_to_sheet(hdrs, tbl)
	for row in rows:
		wbk.add_row_to_sheet(row, tbl)
	# Add sheet to workbook
	wbk.add_sheet(tbl)
	# Add information to the "Datasheets" sheet.
	datasheetlist = wbk.sheet_named(datasheet_name)
	if datasheetlist:
		script, lno = working_script.current_script_line()
		if querytext:
			src = "%s with database %s, with script %s, line %d" % (querytext, dbs.current().name(), os.path.abspath(script), lno)
		else:
			src = "From database %s, with script %s, line %d" % (dbs.current().name(), os.path.abspath(script), lno)
		wbk.add_row_to_sheet((sheet_name,
						datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
						getpass.getuser(),
						desc,
						src), datasheetlist)
	# Save and close the workbook.
	wbk.save_close()

def write_query_to_json(select_stmt, db, outfile, append=False, desc=None):
	global json
	import json
	global conf
	try:
		hdrs, rows = db.select_rowsource(select_stmt)
	except ErrInfo:
		raise
	except:
		raise ErrInfo("db", select_stmt, exception_msg=exception_desc())
	ef = EncodedFile(outfile, conf.output_encoding)
	if append:
		f = ef.open("at")
		f.write(u",\n")
	else:
		f = ef.open("wt")
	f.write(u"[")
	uhdrs = [unicode(h) for h in hdrs]
	first = True
	for row in rows:
		if first:
			f.write(u"\n")
		else:
			f.write(u",\n")
		first = False
		dictdata = dict(zip(uhdrs, [unicode(v) if isinstance(v, basestring) else v for v in row]))
		jsondata = json.dumps(dictdata, separators=(u',', u':'))
		f.write(unicode(jsondata))
	f.write(u"\n]\n")
	f.close()

def export_values(outfile, hdrs, rows, append=False, desc=None):
	global conf
	if outfile.lower() == 'stdout':
		f = output
	else:
		ef = EncodedFile(outfile, conf.output_encoding)
		if append:
			f = ef.open("at")
		else:
			f = ef.open("wt")
	if desc is not None:
		f.write(u"-- %s\n" % desc)
	f.write(u"INSERT INTO !!target_table!!\n    (%s)\n" % u", ".join(hdrs))
	f.write(u"VALUES\n")
	firstrow = True
	for r in rows:
		if firstrow:
			firstrow = False
		else:
			f.write(u",\n")
		quoted_row = ["'%s'" % v.replace("'", "''") if isinstance(v, basestring) else unicode(v) for v in r]
		f.write(u"    (%s)" % u", ".join(quoted_row))
	f.write(u"\n    ;\n")

def write_query_to_values(select_stmt, db, outfile, append=False, desc=None):
	try:
		hdrs, rows = db.select_rowsource(select_stmt)
	except ErrInfo:
		raise
	except:
		raise ErrInfo("db", select_stmt, exception_msg=exception_desc())
	export_values(outfile, hdrs, rows, append, desc)


def export_html(outfile, hdrs, rows, append=False, querytext=None, desc=None):
	global conf
	def write_table(f):
		f.write(u'<table>\n')
		if desc is not None:
			f.write(u'<caption>%s</caption>\n' % desc)
		f.write(u'<thead><tr>')
		for h in hdrs:
			f.write(u'<th>%s</th>' % h)
		f.write(u'</tr></thead>\n<tbody>\n')
		for r in rows:
			f.write(u'<tr>')
			for v in r:
				f.write(u'<td>%s</td>' % (v if v else u''))
			f.write(u'</tr>\n')
		f.write(u'</tbody>\n</table>\n')
	script, lno = working_script.current_script_line()
	# If not append, write a complete HTML document with header and table.
	# If append and the file does not exist, write just the table.
	# If append and the file exists, R/W up to the </body> tag, write the table, write the remainder of the input.
	if not append:
		ef = EncodedFile(outfile, conf.output_encoding)
		f = ef.open("wt")
		f.write(u'<!DOCTYPE html>\n<html>\n<head>\n<meta charset="utf-8" />\n')
		if querytext:
			descrip = "Source: [%s] with database %s in script %s, line %d" % (querytext, dbs.current().name(), os.path.abspath(script), lno)
		else:
			descrip = "From database %s in script %s, line %d" % (dbs.current().name(), os.path.abspath(script), lno)
		f.write(u'<meta name="description" content="%s" />\n' % descrip)
		datecontent = datetime.datetime.now().strftime("%Y-%m-%d")
		f.write(u'<meta name="created" content="%s" />\n' % datecontent)
		f.write(u'<meta name="revised" content="%s" />\n' % datecontent)
		f.write(u'<meta name="author" content="%s" />\n' % getpass.getuser())
		f.write(u'<title>Data Table</title>\n')
		if conf.css_file or conf.css_styles:
			if conf.css_file:
				f.write(u'<link rel="stylesheet" type="text/css" href="%s">' % conf.css_file)
			if conf.css_styles:
				f.write(u'<style type="text/css">\n%s\n</style>' % conf.css_styles)
		else:
			f.write(u'<style type="text/css">\n')
			f.write(u'table {font-family: "Liberation Mono", "DejaVu Sans Mono", "Bitstream Vera Sans Mono", "Lucida Console", "Courier New", Courier, fixed; '+
					u'border-top: 3px solid #814324; border-bottom: 3px solid #814324; '+
					u'border-left: 2px solid #814324; border-right: 2px solid #814324; '+
					u'border-collapse: collapse; }\n')
			f.write(u'td {text-align: left; padding 0 10px; border-right: 1px dotted #814324; }\n')
			f.write(u'th {padding: 2px 10px; text-align: center; border-bottom: 1px solid #814324; border-right: 1px dotted #814324;}\n')
			f.write(u'tr.hdr {font-weight: bold;}\n')
			f.write(u'thead tr {border-bottom: 1px solid #814324; background-color: #F3F1E2; }\n')
			f.write(u'tbody tr { border-bottom: 1px dotted #814324; }\n')
			f.write(u'</style>')
		f.write(u'\n</head>\n<body>\n')
		write_table(f)
		f.write(u'</body>\n</html>\n')
	else:
		if not os.path.isfile(outfile):
			ef = EncodedFile(outfile, conf.output_encoding)
			f = ef.open("wt")
			write_table(f)
		else:
			ef = EncodedFile(outfile, conf.output_encoding)
			f = ef.open("rt")
			tempf, tempfname = tempfile.mkstemp(text=True)
			tf = EncodedFile(tempfname, conf.output_encoding)
			t = tf.open("wt")
			remainder = u''
			for line in f:
				bodypos = line.lower().find("</body>")
				if bodypos > -1:
					t.write(line[0:bodypos])
					t.write(u"\n")
					remainder = line[bodypos:]
					break
				else:
					t.write(line)
			t.write(u"\n")
			write_table(t)
			t.write(remainder)
			for line in f:
				t.write(line)
			t.close()
			f.close()
			os.unlink(outfile)
			os.rename(tempfname, outfile)


def write_query_to_html(select_stmt, db, outfile, append=False, desc=None):
	try:
		hdrs, rows = db.select_rowsource(select_stmt)
	except ErrInfo:
		raise
	except:
		raise ErrInfo("db", select_stmt, exception_msg=exception_desc())
	export_html(outfile, hdrs, rows, append, select_stmt, desc)


def export_latex(outfile, hdrs, rows, append=False, querytext=None, desc=None):
	global conf
	def write_table(f):
		f.write(u'\\begin{center}\n')
		f.write(u'  \\begin{table}[h]\n')
		if desc is not None:
			f.write(u'  \\caption{%s}\n' % desc)
		f.write(u'  \\begin{tabular} {%s }\n' % (u' l'*len(hdrs)))
		f.write(u'  \\hline\n')
		f.write(u'  ' + u' & '.join([h.replace(u'_', u'\_') for h in hdrs]) + u' \\\\\n')
		f.write(u'  \\hline\n')
		for r in rows:
			f.write(u'  ' + u' & '.join([unicode(c).replace(u'_', u'\_') for c in r]) + u' \\\\\n')
		f.write(u'  \\hline\n')
		f.write(u'  \\end{tabular}\n')
		f.write(u'  \\end{table}\n')
		f.write(u'\\end{center}\n')
	script, lno = working_script.current_script_line()
	# If not append, write a complete LaTeX document with header and table.
	# If append and the file does not exist, write just the table.
	# If append and the file exists, R/W up to the \end{document} tag, write the table, write the remainder of the input.
	if not append:
		if outfile.lower() == 'stdout':
			f = output
		else:
			ef = EncodedFile(outfile, conf.output_encoding)
			f = ef.open("wt")
		f.write(u'\\documentclass{article}\n')
		f.write(u'\\begin{document}\n')
		write_table(f)
		f.write(u'\\end{document}\n')
	else:
		if outfile.lower() == 'stdout' or not os.path.isfile(outfile):
			if outfile.lower() == 'stdout':
				f = output
			else:
				ef = EncodedFile(outfile, conf.output_encoding)
				f = ef.open("wt")
			write_table(f)
		else:
			ef = EncodedFile(outfile, conf.output_encoding)
			f = ef.open("rt")
			tempf, tempfname = tempfile.mkstemp(text=True)
			tf = EncodedFile(tempfname, conf.output_encoding)
			t = tf.open("wt")
			remainder = u''
			for line in f:
				bodypos = line.lower().find(u"\\end{document}")
				if bodypos > -1:
					t.write(line[0:bodypos])
					t.write(u"\n")
					remainder = line[bodypos:]
					break
				else:
					t.write(line)
			t.write(u"\n")
			write_table(t)
			t.write(remainder)
			for line in f:
				t.write(line)
			t.close()
			f.close()
			os.unlink(outfile)
			os.rename(tempfname, outfile)


def write_query_to_latex(select_stmt, db, outfile, append=False, desc=None):
	try:
		hdrs, rows = db.select_rowsource(select_stmt)
	except ErrInfo:
		raise
	except:
		raise ErrInfo("db", select_stmt, exception_msg=exception_desc())
	export_latex(outfile, hdrs, rows, append, select_stmt, desc)


def ods_data(filename, sheetname, junk_header_rows=0):
	# Returns the data from the specified worksheet as a list of headers and a list of lists of rows.
	wbk = OdsFile()
	try:
		wbk.open(filename)
	except:
		raise ErrInfo(type="cmd", other_msg="%s is not a valid OpenDocument spreadsheet." % filename)
	try:
		alldata = wbk.sheet_data(sheetname, junk_header_rows)
	except:
		raise ErrInfo(type="cmd", other_msg="%s is not a worksheet in %s." % (sheetname, filename))
	return alldata[0], alldata[1:]

def xls_data(filename, sheetname, junk_header_rows):
	# Returns the data from the specified worksheet as a list of headers and a list of lists of rows.
	wbk = XlsFile()
	try:
		wbk.open(filename)
	except:
		raise ErrInfo(type="cmd", other_msg="%s is not a valid Excel spreadsheet." % filename)
	try:
		alldata = wbk.sheet_data(sheetname, junk_header_rows)
	except:
		raise ErrInfo(type="cmd", other_msg="Error reading worksheet %s from %s." % (sheetname, filename))
	if len(alldata) == 0:
		raise ErrInfo(type="cmd", other_msg="There are no data on worksheet %s of file %s." % (sheetname, filename))
	if len(alldata) == 1:
		return alldata[0], []
	return alldata[0], alldata[1:]


def import_data_table(db, schemaname, tablename, is_new, hdrs, data):
	def get_ts():
		if not get_ts.tablespec:
			get_ts.tablespec = DataTable(hdrs, data)
		return get_ts.tablespec
	get_ts.tablespec = None
	#tablespec = DataTable(hdrs, data)
	if is_new:
		if is_new == 2:
			tblspec = db.schema_qualified_table_name(schemaname, tablename)
			try:
				db.drop_table(tblspec)
			except:
				exec_log.log_status_info("Could not drop existing table (%s) for IMPORT metacommand" % tblspec)
		sql = get_ts().create_table(db.type, schemaname, tablename)
		try:
			db.execute(sql)
			# Don't commit here; commit will be done after populating the table
			# ...except for Firebird.
			if db.type == dbt_firebird:
				db.conn.commit()
		except:
			raise ErrInfo(type="db", command_text=sql, exception_msg=exception_desc(), other_msg=u"Could not create new table (%s) for IMPORT metacommand" % tablename)
	try:
		db.populate_table(schemaname, tablename, data, hdrs, get_ts)
		db.commit()
	except ErrInfo:
		raise
	except:
		raise ErrInfo("db", "Call to populate_table when importing data", exception_msg=exception_desc())

def importods(db, schemaname, tablename, is_new, filename, sheetname, junk_header_rows):
	hdrs, data = ods_data(filename, sheetname, junk_header_rows)
	import_data_table(db, schemaname, tablename, is_new, hdrs, data)

def importxls(db, schemaname, tablename, is_new, filename, sheetname, junk_header_rows):
	hdrs, data = xls_data(filename, sheetname, junk_header_rows)
	import_data_table(db, schemaname, tablename, is_new, hdrs, data)


def importtable(db, schemaname, tablename, filename, is_new, skip_header_line=True, quotechar=None, delimchar=None, encoding=None, junk_header_lines=0):
	global conf
	if not os.path.isfile(filename):
		raise ErrInfo(type="error", other_msg=u"Non-existent file (%s) used with the IMPORT metacommand" % filename)
	enc = conf.import_encoding if not encoding else encoding
	inf = CsvFile(filename, enc, junk_header_lines=junk_header_lines)
	if quotechar and delimchar:
		if quotechar == u'none':
			quotechar = None
		inf.lineformat(delimchar, quotechar, None)
	if is_new in (1, 2):
		inf.evaluate_column_types()
		sql = inf.create_table(db.type, schemaname, tablename)
		if is_new == 2:
			try:
				db.drop_table(db.schema_qualified_table_name(schemaname, tablename))
			except:
				exec_log.log_status_info("Could not drop existing table (%s) for IMPORT metacommand" % tablename)
				# Don't raise an exception; this may not be a problem because the table may not already exist.
		try:
			db.execute(sql)
			# Don't commit table creation here; the commit will be done after data import
			# ...except for Firebird.  Execute the commit directly via the connection so it is always done.
			if db.type == dbt_firebird:
				db.conn.commit()
		except:
			raise ErrInfo(type="db", command_text=sql, exception_msg=exception_desc(), other_msg=u"Could not create new table (%s) for IMPORT metacommand" % tablename)
	else:
		if not db.table_exists(tablename):
			raise ErrInfo("error", other_msg=u"Non-existent table name (%s) used with the IMPORT metacommand" % tablename)
	try:
		db.import_file(schemaname, tablename, inf, skipheader=True)
		db.commit()
	except ErrInfo:
		raise
	except:
		raise ErrInfo("exception", exception_msg=exception_desc(), other_msg="Can't import file (%s) to table (%s)" % (filename, tablename))

def gui_connect(alias, message, cmd=None):
	dbs.disconnect(alias)
	def connection_pg():
		return PostgresDatabase(server, db, user,
							need_passwd=pw is not None,
							port=port, new_db=False,
							encoding=encoding, password=pw)
	def connection_access():
		return AccessDatabase(db_file, need_passwd=pw is not None,
							encoding=encoding, password=pw)
	def connection_sqlite():
		return SQLiteDatabase(db_file)
	def connection_ssvr():
		return SqlServerDatabase(server, db, user, need_passwd=pw is not None,
							port=port, encoding=encoding,
							password=pw)
	def connection_mysql():
		return MySQLDatabase(server, db, user, need_passwd=pw is not None,
							port=port, encoding=encoding,
							password=pw)
	def connection_fb():
		return FirebirdDatabase(server, db, user, need_passwd=pw is not None,
							port=port, 	encoding=encoding,
							password=pw)
	connectors = {u"PostgreSQL": connection_pg,
					u"MS-Access": connection_access,
					u"SQLite": connection_sqlite,
					u"SQL Server": connection_ssvr,
					u"MySQL": connection_mysql,
					u"Firebird": connection_fb}
	enable_gui()
	return_queue = Queue.Queue()
	gui_args = {"title": "Connect to database",
				 "message": message}
	gui_manager_queue.put(GuiSpec(GUI_CONNECT, gui_args, return_queue))
	user_response = return_queue.get(block=True)
	exit_status = user_response["exit_status"]
	db_type = user_response["db_type"]
	server = user_response["server"]
	port = user_response["port"]
	db = user_response["db"]
	db_file = user_response["db_file"]
	user = user_response["user"]
	pw = user_response["pw"]
	encoding = user_response["encoding"]
	if exit_status == 1:
		try:
			db = connectors[db_type]()
		except:
			if cmd:
				raise ErrInfo(type="cmd", command_text=cmd, other_msg=u"Could not connect to %s" % db)
			else:
				raise ErrInfo(type="error", other_msg=u"Could not connect to %s" % db)
		else:
			dbs.add(alias, db)
	else:
		msg = u"Halted from prompt for database connection"
		global working_script
		if working_script:
			script, lno = working_script.current_script_line()
			exec_log.log_exit_halt(script, lno, msg)
		else:
			exec_log.log_status_info(msg)
		exit_now(2, None)


def gui_console_on(title=None):
	global gui_console
	if not gui_console:
		enable_gui()
		gui_console = GuiConsole(title)
		output.redir_stdout(gui_console.write)
		output.redir_stderr(gui_console.write)

def gui_console_hide():
	global gui_console
	if gui_console:
		gui_console.hide()

def gui_console_show():
	global gui_console
	if gui_console:
		gui_console.show()

def gui_console_status(statusmsg):
	global gui_console
	if gui_console:
		gui_console.write_status(statusmsg)

def gui_console_progress(progress_value):
	global gui_console
	if gui_console:
		gui_console.set_progress(progress_value)

def gui_console_save(filename, append):
	global gui_console
	if gui_console:
		gui_console.save_as(filename, append)

def gui_console_wait_user(statusmsg=None):
	global gui_console
	if gui_console:
		if statusmsg:
			gui_console.write_status(statusmsg)
		console_closed = gui_console.wait_for_user()
		if console_closed:
			output.reset()
			gui_console = None

def gui_console_isrunning():
	if gui_manager_thread:
		return_queue = Queue.Queue()
		gui_manager_queue.put(GuiSpec(QUERY_CONSOLE, {}, return_queue))
		user_response = return_queue.get(block=True)
		return user_response["console_running"]
	else:
		return False

def gui_console_off():
	global gui_console
	if gui_console:
		gui_console.deactivate()
		while not gui_console.console_killed_event.is_set():
			time.sleep(0)
		output.reset()
		gui_console = None


# End of support functions (2).
#===============================================================================================


#===============================================================================================
#----- DATABASE CONNECTION INITIALIZERS
# These provide additional argument checking as appropriate.

def db_Access(Access_fn, pw_needed=False, user=None, encoding=None):
	if not os.path.exists(Access_fn):
		raise ErrInfo(type="error", other_msg=u'Access database file "%s" does not exist.' % unicode(Access_fn))
	return AccessDatabase(Access_fn, need_passwd=pw_needed, user_name=user, encoding=encoding)

def db_Postgres(server_name, database_name, user=None, pw_needed=True, port=None, encoding=None, new_db=False):
	return PostgresDatabase(server_name, database_name, user, pw_needed, port, new_db=new_db)

def db_SQLite(sqlite_fn, new_db=False, encoding=None):
	if not new_db and not os.path.exists(sqlite_fn):
		raise ErrInfo(type="error", other_msg=u'SQLite database file "%s" does not exist.' % unicode(sqlite_fn))
	return SQLiteDatabase(sqlite_fn)

def db_SqlServer(server_name, database_name, user=None, pw_needed=True, port=None, encoding=None):
	return SqlServerDatabase(server_name, database_name, user, pw_needed, port, encoding)

def db_MySQL(server_name, database_name, user=None, pw_needed=True, port=None, encoding=None):
	return MySQLDatabase(server_name, database_name, user, pw_needed, port, encoding)

def db_Firebird(server_name, database_name, user=None, pw_needed=True, port=None, encoding=None):
	return FirebirdDatabase(server_name, database_name, user, pw_needed, port, encoding)

def db_Dsn(dsn_name, user=None, pw_needed=True, encoding=None):
	return DsnDatabase(dsn_name=dsn_name, user_name=user, need_passwd=pw_needed, encoding=encoding)

# End of database connection initializers.
#===============================================================================================


#===============================================================================================
#-----  COMMAND-LINE HANDLING

def list_metacommands():
	__METACOMMANDS = """
Metacommands are embedded in SQL comment lines following the !x! token.
See the documentation for more complete descriptions of the metacommands.
   ASK "<question>" SUB <match_string>
   AUTOCOMMIT ON|OFF
   BEGIN BATCH / END BATCH / ROLLBACK BATCH
   BEGIN SCRIPT / END SCRIPT
   BOOLEAN_INT YES|NO
   BOOLEAN_WORDS YES|NO
   CANCEL_HALT ON|OFF
   CONNECT TO <DBMS>(SERVER=<server_name> DB=<database_name>
         [, USER=<user>, NEED_PWD=TRUE|FALSE] [, ENCODING=<encoding>]
         [, NEW]) AS <alias_name>
   CONNECT TO <DBMS>(FILE=<database_file> [, ENCODING=<encoding>])
         AS <alias_name>
   CONNECT TO DSN(DSN=<dsn_name>, [, USER=<user>, NEED_PWD=TRUE|FALSE] 
         [, ENCODING=<encoding>]) AS <alias_name>
   CONSOLE ON|OFF|HIDE|SHOW|STATUS|PROGRESS|SAVE|WAIT
   COPY <table1> FROM <alias1> TO [NEW|REPLACEMENT] <table2> IN <alias2>
   COPY QUERY <<query>> FROM <alias1> TO [NEW|REPLACEMENT] <table2> IN <alias2>
   EMAIL FROM <from_addr> TO <to_addr> SUBJECT "<subject>" MESSAGE "<message>" [MESSAGE_FILE "<filename>"] [ATTACH_FILE "<attachment_filename>"]
   EMPTY_STRINGS YES|NO
   ERROR_HALT ON|OFF
   EXECUTE <proc_name>
   EXECUTE SCRIPT <script_name>
   EXPORT <table_or_view> [APPEND] TO <filename> | stdout AS <format> 
   EXPORT QUERY <<query>> [APPEND] TO <filename> | stdout AS <format> 
   HALT ["<error_message>"]
   HALT MESSAGE "<error_message>" [DISPLAY <table_or_view>]
   IF( [NOT] <conditional> ) { <metacommand> }
   IF() / ANDIF() / ORIF() / ELSEIF() / ELSE / ENDIF
   IMPORT TO [NEW|REPLACEMENT] <table_name> FROM <file_name>
         WITH QUOTE <quote_char> DELIMITER <delim_char>
   IMPORT TO [NEW|REPLACEMENT] <table_name> FROM <odf_file_name>
         SHEET <sheet_name>
   IMPORT TO [NEW|REPLACEMENT] <table_name> FROM EXCEL <excel_file_name>
         SHEET <sheet_name>
   IMPORT_COMMON_COLUMNS_ONLY YES|NO
   INCLUDE <sql_script_file>
   LOG "<text>"
   LOG_WRITE_MESSAGES ON|OFF
   MAX_INT <integer_value>
   METACOMMAND_ERROR_HALT ON|OFF
   ON ERROR_HALT EMAIL FROM <from_address> TO <to_addresses> SUBJECT "<subject>" MESSAGE "<message_text>"
   ON ERROR_HALT WRITE "<text>" [[TEE] TO <output>]
   PAUSE "<text>"
   PG_VACUUM <vacuum_arguments>
   PROMPT ASK "<question>" SUB <match_string> [DISPLAY <table_or_view>]
   PROMPT [MESSAGE "<text>"] CONNECT AS <alias>
   PROMPT DIRECTORY SUB <match_string>
   PROMPT ENTER_SUB <match_string> MESSAGE <text> [DISPLAY <table_or_view>]
   PROMPT ENTRY_FORM <specification table> MESSAGE <text> [DISPLAY <table or view>]
   PROMPT MESSAGE "<text>" DISPLAY <table_or_view>
   PROMPT OPENFILE SUB <match_string>
   PROMPT SAVEFILE SUB <match_string>
   PROMPT SELECT_SUB <table_or_view> MESSAGE <text>
   RESET COUNTER[S]
   RM_FILE <file_name>
   SELECT_SUB <table_or_view>
   SET COUNTER <counter_no> TO <value>
   SUB <match_string> <replacement_str>
   SUB_APPEND <match_string> <replacement_str>
   SUB_DECRYPT <sub_var_name> <encrypted_text>
   SUB_ENCRYPT <sub_var_name> <plaintext>
   SUB_TEMPFILE <match_string>
   SUBDATA <match_string> <table_or_view>
   SYSTEM_CMD (<operating system command line>)
   TIMER ON|OFF
   USE <alias_name>
   WAIT_UNTIL <Boolean_expression> <HALT|CONTINUE> AFTER <n> SECONDS
   WRITE "<text>" [[TEE] TO <output>]
   WRITE CREATE_TABLE FROM <filename> [TO <output>]
   WRITE SCRIPT <script_name> [[APPEND] TO <output_file>]"""
	print(__METACOMMANDS)

def list_encodings():
	enc = codec_dict.keys()
	enc.sort()
	msg = u"Encodings: %s\n" % ", ".join(enc)
	print(msg)

def clparser():
	usage_msg = """Usage: %prog [options] <SQL_script_file> <Server_name> <Database_name>
  or
       %prog [options] <SQL_script_file> <Database_file>
The first form is used with PostgreSQL, Microsoft SQL Server, MySQL, MariaDB, and Firebird; 
the second form is used with Microsoft Access and SQLite.
Arguments:
  SQL_script_file      A text file of SQL statements and/or metacommands to run
  Database_file        An existing Microsoft Access or SQLite database file
  Server_name          The name of the server (host) containing the database to use
  Database_name        The name of the database to use."""
	vers_msg = "%prog " + "%s %s" % (__version__, __vdate)
	desc_msg = "Runs a set of SQL statements and metacommands against the specified database, and optionally captures the output of the last command."
	parser = OptionParser(usage=usage_msg, version=vers_msg, description=desc_msg)
	parser.add_option("-a", "--assign-arg", action="append", dest="sub_vars",
						help="Define the replacement string for a substitution variable $ARG_x.")
	parser.add_option("-b", "--boolean-int", dest="boolean_int", type="choice", 
						choices=['0', '1', 't', 'f', 'T', 'F', 'y', 'n', 'Y', 'N'], default=None,
						help="Treat integers 0 and 1 as boolean values when parsing data.")
	parser.add_option("-d", "--directories", type="choice", choices=['0', '1', 't', 'f', 'T', 'F', 'y', 'n', 'Y', 'N'], dest="make_dirs",
						default=None,
						help="Make directories used by the EXPORT metacommand: n: no (default); y: yes.")
	parser.add_option("-e", "--database_encoding", action="store", dest="database_encoding",
						default=None,
						help="Character encoding used in the database.  Only used for some database types.")
	parser.add_option("-f", "--script_encoding", action="store", dest="script_encoding",
						default=None,
						help="Character encoding of the script file.  The default is UTF-8.")
	parser.add_option("-g", "--output_encoding", action="store", dest="output_encoding",
						default=None,
						help="Character encoding to use for output of the WRITE and EXPORT metacommands.")
	parser.add_option("-i", "--import_encoding", action="store", dest="import_encoding",
						default=None,
						help="Character encoding to use for data files imported with the IMPORT metacommands.")
	parser.add_option("-m", "--metacommands", action="store_true", dest="metacommands",
						default=False,
						help="List metacommands and exit.")
	parser.add_option("-p", "--port", action="store", type="int", dest="port",
						default=None,
						help="Database server port")
	parser.add_option("-n", "--new-db", action="store_true", dest="new_db",
						default=None,
						help="Create a new SQLite or Postgres database if the named database does not exist.")
	parser.add_option("-s", "--scan-lines", action="store", type="int", dest="scanlines",
						default=None,
						help="Number of input file lines to scan to determine the format for the IMPORT metacommand.  Use 0 to scan the entire file.")
	parser.add_option("-t", "--type", type="choice", choices=['a', 'd', 'p', 's', 'l', 'm', 'f'], dest="db_type",
						default=None,
						help="Database type: 'a'-MS-Access; 'p'-PostgreSQL; 's'-SQL Server; 'l'-SQLite, 'm'-MySQL, 'f'-Firebird, 'd'-DSN.  Default (without this option) is 'a'.")
	parser.add_option("-u", "--user", action="store", type="string", dest="user",
						default=None,
						help="Database user name.")
	parser.add_option("-v", "--visible_prompts", type="choice", choices=['0', '1', '2', '3'], dest="use_gui",
						default=None,
						help="GUI use: 0-None (default); 1-password and prompt; 2-halt and initial database selection")
	parser.add_option("-w", "--no-passwd", action="store_true", dest="no_passwd",
						default=None,
						help="Do not prompt for the password when the user is specified")
	parser.add_option("-y", "--encodings", action="store_true", dest="encodings",
						default=False,
						help="List encoding names and exit.")
	parser.add_option("-z", "--import_buffer", type="int", action="store", dest="import_buffer",
						default=None,
						help="Buffer size, in kb, to use with the IMPORT metacommand.  The default is 32.")
	return parser


# End of command-line handling.
#===============================================================================================


#===============================================================================================
#-----  GLOBAL OBJECTS

# Logging object, initialized in main()
exec_log = None

# Status object with status-related attributes.
status = StatObj()

# Substitution variables
subvars = SubVarSet()
for k in os.environ.keys():
	subvars.add_substitution(u"&"+k, os.environ[k])

# Timer for the $TIMER system variable
timer = Timer()

# Redirectable output.
output = WriteHooks()
gui_console = None

# Storage for all the (named) databases that are opened.  Databases are added in 'main()'
# and by the CONNECT metacommand.
dbs = DatabasePool()

# Dynamically modifiable and executable list of SQL statements and metacommands,
# initialized in main()
working_script = None

# A WriteSpec object for messages to be written when the program halts due to an error.
# This is initially None, but may be set and re-set by metacommands.
err_halt_writespec = None

# A MailSpec object for email to be sent when the program halts due to an error.
# This is intially None, but may be set and re-set by metacommands.
err_halt_email = None

# Temporary files created by the SUB_TEMPFILE metacommand.
tempfiles = TempFileMgr()

#	End of global objects.
#===============================================================================================


#===============================================================================================
#----- MAIN

def main():
	global subvars
	dt_now = datetime.datetime.now()
	subvars.add_substitution("$SCRIPT_START_TIME", dt_now.strftime("%Y-%m-%d %H:%M"))
	subvars.add_substitution("$DATE_TAG", dt_now.strftime("%Y%m%d"))
	subvars.add_substitution("$DATETIME_TAG", dt_now.strftime("%Y%m%d_%H%M"))
	subvars.add_substitution("$LAST_SQL", "")
	subvars.add_substitution("$LAST_ERROR", "")
	subvars.add_substitution("$ERROR_MESSAGE", "")
	subvars.add_substitution("$USER", getpass.getuser())
	osys = sys.platform
	if osys.startswith('linux'):
		osys = 'linux'
	elif osys.startswith('win'):
		osys = 'windows'
	subvars.add_substitution("$OS", osys)
	# Get command-line options and arguments
	parser = clparser()
	opts, args = parser.parse_args()
	helpexit = False
	if opts.metacommands:
		list_metacommands()
		helpexit = True
	if opts.encodings:
		list_encodings()
		helpexit = True
	if helpexit:
		sys.exit(0)
	if args is None:
		parser.print_help()
		sys.exit(0)
	if len(args) == 0:
		parser.print_help()
		sys.exit(0)
	script_name = args[0]
	if not os.path.exists(script_name):
		# Don't use fatal_error() because conf is not initialized yet.
		sys.exit(u'SQL script file "%s" does not exist.' % unicode(script_name))
	subvars.add_substitution("$STARTING_SCRIPT", script_name)
	# Read configuration data
	global conf
	conf = ConfigData(os.path.dirname(os.path.abspath(script_name)), subvars)
	# Modify configuration based on command-line options
	if opts.user:
		conf.username = opts.user
	if opts.no_passwd:
		conf.passwd_prompt = False
	if opts.database_encoding:
		conf.db_encoding = opts.database_encoding
	if opts.script_encoding:
		conf.script_encoding = opts.script_encoding
	if not conf.script_encoding:
		conf.script_encoding = 'utf8'
	if opts.output_encoding:
		conf.output_encoding = opts.output_encoding
	if not conf.output_encoding:
		conf.output_encoding = 'utf8'
	if opts.import_encoding:
		conf.import_encoding = opts.import_encoding
	if not conf.import_encoding:
		conf.import_encoding = 'utf8'
	if opts.import_buffer:
		conf.import_buffer = opts.import_buffer * 1024
	if opts.make_dirs:
		conf.make_export_dirs = opts.make_dirs in ('1', 't', 'T', 'y', 'Y')
	if opts.boolean_int:
		conf.boolean_int = opts.boolean_int in ('1', 't', 'T', 'y', 'Y')
	if opts.scanlines:
		conf.scan_lines = opts.scanlines
	if conf.scan_lines is None:
		conf.scan_lines = 100
	if opts.use_gui:
		conf.gui_level = int(opts.use_gui)
	if conf.gui_level is None:
		conf.gui_level = 0
	else:
		if conf.gui_level not in range(4):
			raise ConfigError("Invalid GUI level specification: %s" % conf.gui_level)
	if opts.db_type:
		conf.db_type = opts.db_type
	if conf.db_type is None:
		conf.db_type = 'a'
	# Interpret the command-line-specified user name as an Access user name only if Access is used
	if conf.db_type == 'a' and opts.user:
		conf.access_username = opts.user
	# Modify configuration based on command-line arguments
	if args and (len(args) == 2):
		if conf.db_type in ('a', 'l', 'd'):
			if conf.db_type == 'd':
				conf.db = args[1]
			else:
				conf.db_file = args[1]
		else:
			if conf.server and not conf.db:
				conf.db = args[1]
			else:
				conf.server = args[1]
	elif args and (len(args) == 3):
		conf.server = args[1]
		conf.db = args[2]
	elif args and (len(args) > 3):
		fatal_error(u'Incorrect number of command-line arguments.')
	# Change defaults based on configuration options
	if conf.access_use_numeric:
		if DT_Decimal in dbt_access.dt_xlate.keys():
			del dbt_access.dt_xlate[DT_Decimal]
	# Initiate logging
	opt_dict = vars(opts)
	opts_used = {o: opt_dict[o] for o in opt_dict.keys() if opt_dict[o]}
	global exec_log
	exec_log = Logger(script_name, conf.db, conf.server, opts_used)
	for configfile in conf.files_read:
		exec_log.log_status_info("Read configuration file %s." % configfile)
	subvars.add_substitution("$RUN_ID", exec_log.run_id)
	if opts.sub_vars:
		for n, repl in enumerate(opts.sub_vars):
			var = "$ARG_%s" % str(n+1)
			subvars.add_substitution(var, repl)
			exec_log.log_status_info(u"Command-line substitution variable assignment: %s set to {%s}" % (var, repl))
	# Initialize the script
	global working_script
	working_script = ScriptCommands(conf.include_req + conf.include_opt + [script_name])
	working_script.register_sub_cmd(sub_metacmd)
	# Start the GUI console if necessary.
	if conf.gui_level > 2:
		gui_console_on()
	# Establish the database connection.
	global dbs						# List of databases, including the default/initial/current one to use
	if conf.server is None and conf.db is None and conf.db_file is None:
		if conf.gui_level > 1:
			# Regardless of user, db type, and port specifications
			gui_connect("initial", "Select the database to user with %s." % script_name)
			db = dbs.current()
		else:
			fatal_error(u'Database not specified in configuration files or command-line arguments, and prompt not requested.')
	else:
		# Use Access
		if conf.db_type == "a":
			if conf.db_file is None:
				fatal_error(u"Configured to run with MS-Access, but no Access file name is provided.")
			db = db_Access(conf.db_file, pw_needed=conf.passwd_prompt and conf.access_username is not None, user=conf.access_username, encoding=conf.db_encoding)
		# Use Postgres
		elif conf.db_type == "p":
			db = db_Postgres(conf.server, conf.db, user=conf.username, pw_needed=conf.passwd_prompt, port=conf.port, encoding=conf.db_encoding, new_db=conf.new_db)
		# Use SQL Server
		elif conf.db_type == "s":
			db = db_SqlServer(conf.server, conf.db, user=conf.username, pw_needed=conf.passwd_prompt, port=conf.port, encoding=conf.db_encoding)
		# Use SQLite
		elif conf.db_type == 'l':
			db = db_SQLite(conf.db_file, new_db=conf.new_db, encoding=conf.db_encoding)
		# Use MySQL
		elif conf.db_type == 'm':
			db = db_MySQL(conf.server, conf.db, user=conf.username, pw_needed=conf.passwd_prompt, port=conf.port, encoding=conf.db_encoding)
		# Use Firebird
		elif conf.db_type == 'f':
			db = db_Firebird(conf.server, conf.db, user=conf.username, pw_needed=conf.passwd_prompt, port=conf.port, encoding=conf.db_encoding)
		elif conf.db_type == "d":
		# Use DSN
			db = db_Dsn(conf.db, user=conf.username, pw_needed=conf.passwd_prompt, encoding=conf.db_encoding)
		dbs.add('initial', db)
	exec_log.log_db_connect(db)
	subvars.add_substitution("$CURRENT_DBMS", db.type.dbms_id)
	subvars.add_substitution("$CURRENT_DATABASE", db.name())
	# Run the script.
	# Roll back any uncommitted changes if the script executor does not complete normally.
	atexit.register(dbs.closeall)
	dbs.do_rollback = True
	try:
		working_script.run()
	except SystemExit:
		# A user-triggered (not error/exception) exit before the end of the script.
		# Rollback will be done.
		if gui_console_isrunning() and conf.gui_wait_on_exit:
			gui_console_wait_user("Script complete; close the console window to exit execsql.")
		disable_gui()
		exec_log.log_status_info("%d commands run" % working_script.commands_run())
		raise SystemExit
	except ConfigError as e:
		raise
	except ErrInfo as e:
		exit_now(1, e)
	except Exception as e:
		strace = traceback.extract_tb(sys.exc_info()[2])[-1:]
		lno = strace[0][1]
		msg1 = u"%s: Uncaught exception %s (%s) on line %s" % (unicode(os.path.basename(sys.argv[0])), unicode(sys.exc_info()[0]), unicode(sys.exc_info()[1]), lno)
		if working_script:
			msg1 = msg1 + " in script %s, line %d" % working_script.current_script_line()
		exit_now(1, ErrInfo("exception", exception_msg=msg1))
	dbs.d_rollback = False
	if gui_console_isrunning() and conf.gui_wait_on_exit:
		gui_console_wait_user("Script complete; close the console window to exit execsql.")
	disable_gui()
	exec_log.log_status_info("%d commands run" % working_script.commands_run())
	exec_log.log_exit_end()


if __name__ == "__main__":
	try:
		main()
	except SystemExit:
		raise
	except ErrInfo as e:
		exit_now(1, e)
	except ConfigError as e:
		strace = traceback.extract_tb(sys.exc_info()[2])[-1:]
		lno = strace[0][1]
		sys.exit(u"Configuration error on line %d of execsql.py: %s" % (lno, e.value))
	except Exception:
		strace = traceback.extract_tb(sys.exc_info()[2])[-1:]
		lno = strace[0][1]
		msg1 = u"%s: Uncaught exception %s (%s) on line %s" % (unicode(os.path.basename(sys.argv[0])), unicode(sys.exc_info()[0]), unicode(sys.exc_info()[1]), lno)
		if working_script:
			msg1 = msg1 + " in script %s, line %d" % working_script.current_script_line()
		exit_now(1, ErrInfo("exception", exception_msg=msg1))
