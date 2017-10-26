import re
import xml.etree.ElementTree as ET

class Section(object):
	def __init__(self, xml):
		self.repeats = False
		self.key = None
		self.name = ""
		self.ignore = False
		self.current_line = 0
		self.exit_regex = None
		self.contents = []
		self.builder = {}
		self.builder_list = None

		root = ET.fromstring(xml)
		if "ignore" in root.attrib and root.attrib["ignore"].lower() == "true":
			self.ignore = True
		if "name" in root.attrib:
			self.name = root.attrib["name"]
		if "key" in root.attrib:
			self.key = root.attrib["key"]

		for element in root:
			if element.tag == "repeat-until":
				self.repeats = True
				if element.find("regex") is not None:
					self.exit_regex = re.compile(element.find("regex").text)
			if element.tag == "section":
				self.contents.append(Section(ET.tostring(element)))
			if element.tag == "line":
				self.contents.append(Line(ET.tostring(element)))
		
		if self.repeats:
			# These Sections will be stored in either a dictionary or a list,
			# depending on whether a key field has been defined for this section.
			if self.key:
				self.builder_list = {}
			else:
				self.builder_list = []

	def run(self, line, mark_line_for_rerun):
		# Run `line` against self.contents[current_line]
		# If it returns a match, increment current_line. If current_line is greater than contents, set to beginning.
		# Else, check for exit regex. If exists, return complete. 
		# Return partial.

		# Run line
		status, result = self.contents[self.current_line].run(line, mark_line_for_rerun)
		# Update builder
		if result:
			# Add results to builder dict
			if type(self.contents[self.current_line]) is Section:
				# Result object is section: add to `builder[name]`, where `name` is the name of the section
				self.builder[self.contents[self.current_line].name] = result
			elif type(self.contents[self.current_line]) is Line:
				# Result object is line: merge with builder object.
				self.builder.update(result)
			else:
				raise TypeError("Invalid contents")
		
		# if "Mnemonic" in self.builder and self.builder["Mnemonic"] == "102557":
		# 	print("----------------")
		# 	print(line)
		# 	self.contents[self.current_line].debug()
		# 	print(self.builder)
		# 	print(status, result)

		# Update line pointer
		if status == "complete":
			# Go to next Line/Section
			self.current_line = (self.current_line+1) % len(self.contents) # Loop to beginning if at the end

		# Check if section is done
		if self.builder and self.current_line == 0:
			if not self.repeats:
			#	 End of non-repeating section. Return complete.
				to_return = self.get_built()
				self.reset()
				return ("complete", to_return)
			else:
				#print self.key, self.repeats
				# End of repeating section. Add to builder list.
				if self.key is not None:
					# Keyed repeating section. Find the key!
					try:
						key = self.builder
						for k in self.key.split("|"):
							key = key[k]
					except KeyError:
						print(self.builder)
						raise ValueError("Invalid key for {}: ({})".format(self.name, self.key))
					# Key found. Add to list.
					self.builder_list[key] = self.builder.copy()
					# Reset builder
					self.builder = {}
				else:
					# Non-keyed repeating section.
					self.builder_list.append(self.builder.copy())
					# Reset builder
					self.builder = {}
					#print "Adding to list ({})".format(len(self.builder_list))
				return ("partial", self.get_built())

		elif self.exit_regex is not None and self.exit_regex.match(line) is not None:
			# Line matches the exit regex. Tell the main loop to re-run this line.
			#print "Exit regex found"
			mark_line_for_rerun()
			to_return = self.get_built()
			self.reset()
			return ("complete", to_return)
		else:
			return ("partial", self.get_built())
	
	def finalize(self):
		# Parser reached end of file, wrap up any remaining builders
		if self.builder:
			if not self.repeats:
			#	 End of non-repeating section. Return complete.
				to_return = self.get_built()
				self.reset()
				return to_return
			else:
				# End of repeating section. Add to builder list.
				if self.key is not None:
					# Keyed repeating section. Find the key!
					try:
						key = self.builder
						for k in self.key.split("|"):
							key = key[k]
					except KeyError:
						print(self.builder)
						raise ValueError("Invalid key for {}: ({})".format(self.name, self.key))
					# Key found. Add to list.
					self.builder_list[key] = self.builder.copy()
					# Reset builder
					self.builder = {}
					return self.get_built()
				else:
					# Non-keyed repeating section.
					self.builder_list.append(self.builder.copy())
					# Reset builder
					self.builder = {}
					return self.get_built()
		# No builder in progress - return existing data
		return self.get_built()

	def get_built(self):
		if self.ignore:
			return {}
		return self.builder_list if self.repeats else self.builder

	def reset(self):
		self.builder = {}
		self.current_line = 0
		if self.repeats:
			# These Sections will be stored in either a dictionary or a list,
			# depending on whether a key field has been defined for this section.
			if self.key:
				self.builder_list = {}
			else:
				self.builder_list = []

	def debug(self, indent=""):
		print(indent + "--- Section debug ---")
		print(indent + "  name: {}".format(self.name))
		print(indent + "  repeats: {}".format(self.repeats))
		print(indent + "  key: {}".format(self.key))
		print(indent + "  ignore: {}".format(self.ignore))
		print(indent + "  Exit regex: {}".format(self.exit_regex.pattern if self.exit_regex is not None else ""))
		print(indent + "  Contents:\n")
		for c in self.contents:
			c.debug(indent+"\t")
		print(indent + "---")

class Line(object):
	def __init__(self, xml):
		root = ET.fromstring(xml)
		self.ignore = True if "ignore" in root.attrib and root.attrib["ignore"].lower() == "true" else False
		self.regex = re.compile(root.find("regex").text)
		self.fields = [f.text for f in root.findall("fields/field")]
		self.strip_fields = True
		if self.regex.groups != len(self.fields):
			raise ValueError("Number of capture groups in regex ({}) doesn't match the number of fields provided ({}). Regex:\n{}".format(self.regex.groups, len(self.fields), self.regex.pattern))

	def run(self, line, mark_line_for_rerun):
		""" Compares `line` to the stored regex.

		If `line` matches, the groups are mapped to fields in a dict 
		according to the fields definition.

		Returns a tuple of ("complete", result) if a match was found,
		or ("invalid", None) if no match was found.
		"""
		matches = self.regex.match(line)
		if matches:
			if self.ignore:
				return ("complete", {})
			result = {}
			for key, field in enumerate(self.fields):
				result[field] = matches.group(key+1)
				if self.strip_fields:
					result[field] = result[field].strip()
			#print(line)
			#print(result)
			return ("complete", result)
		return ("invalid", None)

	def debug(self, indent=""):
		print(indent + "[[ Line debug ]]")
		print(indent + "  regex: {}".format(self.regex.pattern))
		print(indent + "  fields: ({})".format(", ".join(self.fields)))
		print(indent + "[[]]\n")