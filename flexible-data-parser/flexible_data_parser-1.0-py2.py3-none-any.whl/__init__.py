from .Sections import Section, Line

class FileParser(object):
	def __init__(self, pattern):
		self.pattern = pattern
		self._rerun = True

	def initialize(self):
		# load pattern into objects
		with open(self.pattern, "r") as inp:
			self.root = Section(inp.read())

	def parse(self, filename):
		self.initialize()
		with open(filename, "r") as inp:
			for line_num, line in enumerate(inp):
				while self._rerun:
					self._rerun = False
					try:
						status, result = self.root.run(line, self._rerun_line)
					except ValueError:
						print(line_num)
						print(line)
						raise
					#print "{}\n\n(Status, Result, Rerun) = ({}, {}, {})".format(line, status, result, self._rerun)
				if status == "complete":
					break
				self._rerun = True
		result = self.root.finalize()
		return result

	def _rerun_line(self):
		#print "Told to rerun"
		self._rerun = True