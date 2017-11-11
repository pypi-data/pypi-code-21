from __future__ import absolute_import
import logging
import shlex
import subprocess
import os

LOG = logging.getLogger(__name__)


class SubprocessError(Exception):
	"""Copy-pasted from python 3.5"""
	pass


class CalledProcessError(SubprocessError):
	"""Copy-pasted from python 3.5"""
	def __init__(self, returncode, cmd, output=None, stderr=None):
		self.returncode = returncode
		self.cmd = cmd
		self.output = output
		self.stderr = stderr

	def __str__(self):
		return "Command '%s' returned non-zero exit status %d" % (self.cmd, self.returncode)

	@property
	def stdout(self):
		return self.output


class TimeoutExpired(SubprocessError):
	"""Copy-pasted from python 3.5"""
	def __init__(self, cmd, timeout, output=None, stderr=None):
		self.cmd = cmd
		self.timeout = timeout
		self.output = output
		self.stderr = stderr

	def __str__(self):
		return "Command '%s' timed out after %s seconds" % (self.cmd, self.timeout)

	@property
	def stdout(self):
		return self.output


class CompletedProcess(object):
	"""
	This class mirrors python 3.5's subprocess.CompletedProcess, with some
	added properties.
	"""
	def __init__(self, args, returncode, stdout=None, stderr=None):
		self.args = args
		self.returncode = returncode
		self.stdout = stdout
		self.stderr = stderr

	@property
	def success(self):
		return self.returncode == 0

	def __repr__(self):
		args = [
			'args={!r}'.format(self.args),
			'returncode={!r}'.format(self.returncode),
		]
		if self.stdout is not None:
			args.append('stdout={!r}'.format(self.stdout))
		if self.stderr is not None:
			args.append('stderr={!r}'.format(self.stderr))
		return "{}({})".format(type(self).__name__, ', '.join(args))


def popen(command, env=None, copy_env=True, **kwargs):
	"""Wrapper around subprocess.Popen."""
	proc_env = os.environ if copy_env else {}
	if env:
		proc_env.update(env)

	LOG.debug('command = %r, env = %r', command, proc_env)

	return subprocess.Popen(
		command,
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE,
		env=proc_env,
		**kwargs
	)


def get_result(proc, timeout=None, check=False, input=None):
	"""Get a CompletedProcess object from a subprocess.Popen."""
	try:
		stdout, stderr = proc.communicate(input, timeout=timeout)
	# this except is copied from python's subprocess.run, I don't really
	# get the point of it but whatever
	except subprocess.TimeoutExpired: #pylint: disable=no-member
		proc.kill()
		stdout, stderr = proc.communicate()
		raise TimeoutExpired(
			proc.args, timeout, output=stdout, stderr=stderr
		)
	except:
		proc.kill()
		proc.wait()
		raise

	retcode = proc.poll()
	if check and retcode > 0:
		raise CalledProcessError(
			retcode, proc.args, output=stdout, stderr=stderr
		)

	return CompletedProcess(
		args=proc.args,
		returncode=retcode,
		stdout=stdout.decode().strip(),
		stderr=stderr.decode().strip(),
	)


def run(command, timeout=None, check=False, input=None, **kwargs):
	"""This function sort of mirrors python 3.5's subprocess.run."""
	if isinstance(command, str):
		command = shlex.split(command)

	proc = popen(command, **kwargs)

	return get_result(proc, timeout=timeout, check=check, input=input)
