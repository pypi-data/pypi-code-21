#!/usr/bin/env python
from __future__ import print_function

'''
Copyright (c) 2017 Peach Tech

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

	http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

"""
Peach API Security CLI

This tool is used to control multiple Peach instances at once.
The tool can be used via the command line or as an interactive
tool.

Installation:

  Installation of this tool has two steps.
  
  1. Install Python 2.7
  2. Install dependencies

	pip install -r requirements.txt
  
  3. Start using the tool

Syntax:

  peachcli

"""

try:
	import click
	import peachapisec
except:
	print("Error, missing dependencies.")
	print("Use 'pip install -r requirements.txt'")
	exit(-1)

import os
import json
import csv
import base64
import codecs

try:
	from cStringIO import StringIO
except ImportError:
	from io import StringIO

class UnicodeWriter:
	"""
	A CSV writer which will write rows to CSV file "f",
	which is encoded in the given encoding.
	"""

	def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
		# Redirect output to a queue
		self.queue = StringIO()
		self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
		self.stream = f
		self.encoder = codecs.getincrementalencoder(encoding)()

	def writerow(self, row):
		self.writer.writerow([s.encode("utf-8") for s in row])
		# Fetch UTF-8 output from the queue ...
		data = self.queue.getvalue()
		try:
			# only works in py2
			data = data.decode("utf-8")
		except AttributeError:
			pass
		# ... and reencode it into the target encoding
		data = self.encoder.encode(data)
		# write to the target stream
		self.stream.write(data)
		# empty queue
		self.queue.truncate(0)

	def writerows(self, rows):
		for row in rows:
			self.writerow(row)

@click.group(help="Command line interface for Peach API Security.")
@click.option("--api", help="Peach API Security API URL. Defaults to PEACH_API environ.")
@click.option("--api_token", help="Peach API Security API Token. Defaults to PEACH_API_TOKEN environ.")
@click.pass_context
def cli(ctx, api, api_token, **kwargs):

	if not api:
		print("Error, set PEACH_API or provide --api argument")
		exit(1)

	if not api_token:
		print("Error, set PEACH_API_TOKEN or provide --api argument")
		exit(1)

	ctx.obj['API'] = api
	ctx.obj['API_TOKEN'] = api_token

	os.environ['PEACH_API'] = api
	os.environ['PEACH_API_TOKEN'] = api_token

	peachapisec.set_peach_api(api)
	peachapisec.set_peach_api_token(api_token)

@cli.command(help="List all jobs")
def jobs(**kwargs):
	jobs_list = peachapisec.get_jobs()
	print(json.dumps(jobs_list, sort_keys=True, indent=4, separators=(',', ': ')))

@cli.command(help="Stop all running jobs")
def stopall(**kwargs):
	click.echo("Stoping all running jobs...")

	jobs_list = peachapisec.get_jobs()
	stop_cnt = 0

	for job in jobs_list:
		if not (job['State'] in ['Error', 'Running']):
			continue
		
		try:
			peachapisec.stop_job(job['Id'])
			stop_cnt += 1
		except:
			pass
	else:
		click.echo("Stopped %s jobs." % str(stop_cnt))

@cli.command(help="Stop a running job")
@click.argument('id')
def stop(id, **kwargs):

	if not id:
		print("Syntax error, must provide job id")
		exit(1)
	
	peachapisec.stop_job(id)

@cli.command(help="Generate JUnit XML output")
@click.argument('id')
@click.argument('output', type=click.File('wb'))
def junitxml(id, output, **kwargs):

	if not id:
		print("Syntax error, must provide job id")
		exit(1)
	
	if not output:
		print("Syntax error, must provide valid output filename")
		exit(1)

	peachapisec.set_session_id(id)
	junit = peachapisec.junit_xml()

	output.write(junit.encode('utf-8'))
	output.close()
	print(junit)

@cli.command(help="Mark a point in the job history")
def mark(**kwargs):
	jobs_list = peachapisec.get_jobs()
	
	id = jobs_list[0]["Id"]
	print("Marking at job id '%s'" % id)

	with open("checklastjob.mark", "w") as fd:
		fd.write(id)

@cli.command(help="Verify a new job completed with N failures")
@click.argument('count')
def verify(count, **kwargs):

	if not os.path.isfile("checklastjob.mark"):
		print("Error, no mark file found.  Run the 'mark' command first!")
		exit(1)

	with open("checklastjob.mark", "r") as fd:
		id = fd.read()
		try:
			# only works in py2
			id = id.decode("utf-8")
		except:
			pass

	jobs_list = peachapisec.get_jobs()
	stop_cnt = 0

	job = jobs_list[0]

	if job["Id"] == id:
		print("Error, no new job found")
		exit(1)

	if not (job["State"] == "Finished"):
		print("Error, job state was '%s'" % job["State"])
		exit(1)

	if not(int(job['FaultCount']) == int(count)):
		print("Error, fault count missmatch, got %d, expected %d." % (int(job['FaultCount']), int(count)))
		exit(1)

	print("Pass, found expected %d failures" % int(count))

@cli.command(help="Export job findings as CSV output")
@click.option('--format', type=click.Choice(['csv']), help="Format for export, default is 'csv'.", default="csv")
@click.argument('id')#, help="Job Id or 'last' for last job.")
@click.argument('output', type=click.File('wb'))#, help="File to create")
def export(id, format, output, **kwargs):

	if not id:
		print("Syntax error, must provide job id.  For last job run use 'last'.")
		exit(1)
	
	if not output:
		print("Syntax error, must provide valid output filename")
		exit(1)

	if id == "last":
		all_jobs = peachapisec.get_jobs()
		if len(all_jobs) == 0:
			print(" - No jobs found, exiting")
			return 1

		# Use the most recent job
		id = all_jobs[0]['Id']

	dataFields = [
		'OriginalRequest',
		'ActualRequest',
		'ActualResponse',
		'RecordedRequest',
		'RecordedResponse',
	]

	fields = [
		'Impact',
		'Exploitability',
		'Owasp',
		'Title',
		'Check',
		'Assertion',
		'Description',
		'Detection',
		'EndPoint',
		'Operation',
		'Parameter',
	] + dataFields

	writer = UnicodeWriter(output)
	writer.writerow(fields)

	faults = peachapisec.get_faults(id)
	if len(faults) == 0:
		print(" - No faults found, exiting")
		return 0

	print(" - %d faults found for export" % len(faults))

	for fault in faults:
		if fault['Visibility'] == 'Hidden':
			continue

		print("  - Fault: %s" % fault["Title"])

		fault = peachapisec.get_fault(id, fault['Id'])
		faultData = fault['FaultData']

		values = []

		for field in fields:
			if field in dataFields and faultData and faultData[field]:
				values.append(base64.b64decode(faultData[field]))
			elif fault[field]:
				values.append(fault[field].strip())
			else:
				values.append('')
		
		writer.writerow(values)
	
	output.close()

	print("Export completed!")


def run():
	'''Start Peach CLI
	'''
	cli(obj={}, auto_envvar_prefix='PEACH')

if __name__ == '__main__':
	run()

# end
