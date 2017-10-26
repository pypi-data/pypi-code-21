#----------Python Spinner----------#
#      Made by creepersbane        #
# Made for use in conjunction with #
#     the "spin_mod.py" file       #
# To use this module please import #
#        spin_mod instead          #
#----------------------------------#
from time import sleep
import threading
########################################################
# Variables defined here
spinnerFrames = ["\u005F","\u23B8","\u203E","\u23B9"]
stopcheck = False
threadRunning = False
text = "Dummy Text. Please replace."
textColor = ""
spinnerColor = ""
reset = ""
########################################################
# This __init__ does nothing :P
def __init__(self):
	return self
# The following functions are for use within the thread
def stopCheck():
	return stopcheck
def getFrames():
	return spinnerFrames
def setFrames(frames):
	spinnerFrames = frames
def stop(): # This is broken
	stopcheck = True
def getText():
	return text
def setText(newText):
	text = newText
def getTextColor():
        return textColor
def getSpinnerColor():
        return spinnerColor
# The actual spinner
def spinner():
	text = getText()
	spinnerFrames = getFrames()
	textColor = getTextColor()
	spinnerColor = getSpinnerColor()
	frame = 1
	while not stopCheck():
		print("\r \u001b[2K" + spinnerColor + spinnerFrames[(frame - 1) % len(spinnerFrames)] + " " + reset + textColor + text + reset,end="",flush=True)
		frame = frame + 1
		sleep(0.1)
		text = getText()
		textColor = getTextColor()
		spinnerColor = getTextColor()
		if (frame - 1) % len(spinnerFrames) == 0:
			spinnerFrames = getFrames()
			frame = 1
	print("")
def start():
	if threadRunning:
		return None
	spinObj = threading.Thread(target=spinner)
	spinObj.start()
def demo():
	try:
		start()
	except KeyboardInterrupt:
		print("")
if __name__ == "__main__":
	demo()
