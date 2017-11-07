from distutils.core import setup

setup(name='execsql',
	version='1.24.0.1',
	description="Runs a SQL script against a PostgreSQL, MS-Access, SQLite, MS-SQL-Server, MySQL, MariaDB, or Firebird database, or an ODBC DSN.  Provides metacommands to import and export data, copy data between databases, conditionally execute SQL and metacommands, and dynamically alter SQL and metacommands with substitution variables.  Data can be exported in 13 different formats, including CSV, TSV, ODS, HTML, JSON, LaTeX, and Markdown tables, and using custom templates.",
	author='Dreas Nielsen',
	author_email='dreas.nielsen@gmail.com',
    url='https://bitbucket.org/rdnielsen/execsql/',
	scripts=['execsql/execsql.py'],
    license='GPL',
	requires=[],
	python_requires = '2.6, 2.7',
	classifiers=[
		'Environment :: Console',
		'Intended Audience :: End Users/Desktop',
		'License :: OSI Approved :: GNU General Public License (GPL)',
		'Programming Language :: SQL',
		'Programming Language :: Python :: 2.7',
		'Topic :: Database',
		'Topic :: Database :: Front-Ends',
		'Topic :: Office/Business'
		],
	keywords=['SQL', 'Postgres', 'PostgreSQL', 'SQLite', 'Firebird', 
		'Access', 'SQL Server', 'MySQL', 'MariaDb', 'ODBC', 'database', 
		'CSV', 'TSV', 'OpenDocument', 'JSON', 'LaTeX', 'table', 'DBMS',
		'query', 'script', 'template', 'Jinja', 'Airspeed'],
	long_description="""``execsql.py`` is a Python program that runs 
a SQL script stored in a text file against a PostgreSQL, MS-Access, SQLite, 
MS-SQL-Server, MySQL, MariaDB, or Firebird database, or to an ODBC 
DSN.  execsql.py also supports a set of special commands (metacommands) 
that can import and export data, copy data between databases, and 
conditionally execute SQL statements and metacommands.  These metacommands 
make up a control language that works the same across all supported DBMSs. 
The metacommands are embedded in SQL comments, so they will be ignored 
by other script processors (e.g., psql for Postgres and sqlcmd for SQL 
Server).  The metacommands make up a toolbox that can be used to create 
both automated and interactive data processing applications.

The program's features and requirements are summarized below.
Complete documentation is available at http://execsql.readthedocs.io/en/latest/.


Capabilities
============

You can use the ``execsql`` program to:

* Import data from text files or OpenDocument spreadsheets into 
  a database.
* Copy data between different databases, even databases using 
  different types of DBMSs.
* Export tables and views as formatted text, comma-separated values (CSV),
  tab-separated values (TSV), OpenDocument spreadsheets, HTML tables,
  JSON, LaTeX tables, or unformatted (e.g., binary) data.
* Export data to non-tabular formats using several different types
  of template processors.
* Display tables and views on the console or in a GUI dialog window.
* Conditionally execute different SQL commands and metacommands based 
  on the DBMS in use, the database in use, data values, user input, 
  and other conditions. Conditional execution can be used with the 
  INCLUDE and SCRIPT metacommands to implement loops.
* Use simple dynamically-created data entry forms to get user input.
* Write messages to the console or to a file during the processing of 
  a SQL script, using metacommands embedded in SQL comments. These 
  messages can be used to display the progress of the script or create 
  a custom log of the operations that have been carried out or results 
  obtained. Status messages and data exported in text format can be 
  combined in a single text file. Data tables can be exported in a text 
  format that is compatible with Markdown pipe tables, so that script 
  output can be converted into a variety of document formats.
* Write more modular and maintainable SQL code by factoring repeated 
  code out into separate scripts, parameterizing the code using 
  substitution variables, and using the INCLUDE or SCRIPT metacommands 
  to merge the modules into a single stream of commands.
* Standardize the SQL scripting language used for different types of 
  database management systems.
* Merge multiple elements of a workflow--e.g., data loading, summarization, 
  and reporting--into a single script for better coupling of related steps 
  and more secure maintenance.

Standard SQL provides no features for interacting with external files or 
with the user, or for controlling the flow of actions to be carried out
based either on data or on user input.  ``execsql`` provides these features
in a way that operates identically across all supported DBMSs on both
Linux and Windows.

``execsql`` is inherently a command-line program that can operate in a completely 
non-interactive mode (except for password prompts). Therefore, it is suitable 
for incorporation into a toolchain controlled by a shell script (on Linux), 
batch file (on Windows), or other system-level scripting application. When 
used in this mode, the only interactive elements will be password prompts. 
However, several metacommands can be used to generate interactive prompts 
and data displays, so execsql scripts can be written to provide some user 
interactivity.

In addition, execsql automatically maintains a log that documents key 
information about each run of the program, including the databases that are 
used, the scripts that are run, and the user's choices in response to 
interactive prompts. Together, the script and the log provide documentation 
of all actions carried out that may have altered data.

The documentation includes more than 20 examples showing the use of
execsql's metacommands, in both simple and complex scripts.


Requirements
============

The ``execsql`` program uses third-party Python libraries to communicate with 
different database and spreadsheet software. These libraries must be 
installed to use those programs with execsql. Only those libraries that 
are needed, based on the command line arguments and metacommands, must 
be installed. The libraries required for each database or spreadsheet 
application are:

* PosgreSQL: psycopg2.
* SQL Server: pydobc.
* MS-Access: pydobc and pywin32.
* MySQL or MariaDB: pymysql.
* Firebird: fdb.
* DSN connections: pyodbc.
* OpenDocument spreadsheets: odfpy.
* Excel spreadsheets (read only): xlrd.

Connections to SQLite databases are made using Python's standard library, 
so no additional software is needed.


Recent Changes
===============

+-----------+------------+------------------------------------------------+
| Version   | Date       | Features                                       |
+===========+============+================================================+
| 1.24.0.0  | 2017-11-04 | Added the 'import_required' and                |
|           |            | 'import_optional' configuration settings.      |
+-----------+------------+------------------------------------------------+
| 1.23.3.0  | 2017-11-03 | Added the CONSOLE_WAIT_WHEN_ERROR_HALT         |
|           |            | setting and associated metacommand and system  |
|           |            | variables.                                     |
+-----------+------------+------------------------------------------------+
| 1.23.2.0  | 2017-11-02 | Added the $ERROR_MESSAGE system variable.      |
+-----------+------------+------------------------------------------------+
| 1.23.1.0  | 2017-10-20 | Added the ASK metacommand.                     |
+-----------+------------+------------------------------------------------+
| 1.23.0.0  | 2017-10-09 | Added the ON ERROR_HALT EMAIL metacommand.     |
+-----------+------------+------------------------------------------------+
| 1.22.0.0  | 2017-10-07 | Added the ON ERROR_HALT WRITE metacommand.     |
+-----------+------------+------------------------------------------------+
| 1.21.13.0 | 2017-09-29 | Added the SUB_APPEND and WRITE SCRIPT          |
|           |            | metacommands.                                  |
+-----------+------------+------------------------------------------------+
| 1.21.12.0 | 2017-09-24 | Added the PG_VACUUM metacommand.               |
+-----------+------------+------------------------------------------------+
| 1.21.11.0 | 2017-09-23 | Modified error message content and format.     |
+-----------+------------+------------------------------------------------+
| 1.21.10.0 | 2017-09-12 | Added the "error_response" setting for         |
|           |            | encoding mismatches.                           |
+-----------+------------+------------------------------------------------+
| 1.21.9.0  | 2017-09-06 | Modified to handle trailing comments on        |
|           |            | SQL script lines.                              |
+-----------+------------+------------------------------------------------+
| 1.21.8.0  | 2017-08-11 | Added a PASSWORD option to the CONNECT         |
|           |            | metacommand for MySQL/MariaDB.                 |
+-----------+------------+------------------------------------------------+
| 1.21.7.0  | 2017-08-05 | Modified to allow import of CSV files with     |
|           |            | more columns than the target table.  Added     |
|           |            | DEBUG metacommands.                            |
+-----------+------------+------------------------------------------------+
| 1.21.1.0  | 2017-07-04 | Passed headers to template processors as a     |
|           |            | separate object.                               |
+-----------+------------+------------------------------------------------+
| 1.21.0.0  | 2017-07-01 | Added the EMAIL, SUB_ENCRYPT, and SUB_DECRYPT  |
|           |            | metacommands, and configuration proerties to   |
|           |            | support emailing.  Added the                   |
|           |            | METACOMMAND_ERROR_HALT metacommand, the        |
|           |            | $METACOMMAND_ERROR_HALT_STATE system variable, |
|           |            | and the METACOMMAND_ERROR() conditional.       |
|           |            | Extended the EXPORT metacommand to allow use   |
|           |            | of different template processors.              |
+-----------+------------+------------------------------------------------+
| 1.18.0.0  | 2017-06-24 | Improved speed of IMPORT metacommand for CSV   |
|           |            | files imported to Postgres and MySQL/MariaDB.  |
|           |            | Modified the EXPORT...APPEND...AS HTML         |
|           |            | metacommand to append tables *inside* the      |
|           |            | (first) </body> tag.                           |
+-----------+------------+------------------------------------------------+
| 1.17.0.0  | 2017-05-28 | Modified the specifications for the            |
|           |            | PROMPT ENTRY_FORM to allow checkboxes to be    |
|           |            | used.                                          |
+-----------+------------+------------------------------------------------+


"""
	)
