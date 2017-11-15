#!/usr/bin/env python
# -*- coding: utf-8 -*-

import Alfons
import traceback

def start(name, description):
	"Start an IoT service"
	Alfons.info["name"] = name
	Alfons.info["description"] = description
	Alfons.Crypt.AlfonsRSA.getKey()
	Alfons.findServer()

	Alfons.IoT.addCommand("list", "List commands on the IoT", _commandList)

	def handler(request):
		if request.command in Alfons.info["iot_commands"]:
			try:
				return Alfons.info["iot_commands"][request.command]["function"](request)
			except:
				return {"success": False, "message": "Command crashed on the IoT device"}

		return {"success": False, "message": "Command not found"}

	while True:
		try:
			Alfons.listen(handler)
		except KeyboardInterrupt:
			Alfons.eradicate()
			break
		except:
			print "Crashed"
			print traceback.format_exc()

def addCommand(command, description, function):
	if not "iot_commands" in Alfons.info:
		Alfons.info["iot_commands"] = {}
	Alfons.info["iot_commands"][command] = {"command": command, "description": description, "function": function}

def _commandList(request):
	commands = []

	for c in Alfons.info["iot_commands"]:
		command = Alfons.info["iot_commands"][c]
		commands.append({"command": command["command"], "description": command["description"]})

	return {"success": True, "items": commands}