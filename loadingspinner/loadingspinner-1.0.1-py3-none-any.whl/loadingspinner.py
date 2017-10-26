import spinner
try:
        from colorama import Fore
        spinner.reset = Fore.RESET
except:
        pass
def setText(text):
	spinner.text = text
def setFrames(frames):
	spinner.spinnerFrames = frames
def start():
	spinner.stopcheck = False
	spinner.start()
def stop():
	spinner.stopcheck = True
def resolveColor(color):
	#return None
	color = color.lower()
	if color == "red":
		return Fore.RED
	if color == "green":
		return Fore.GREEN
	if color == "black":
		return Fore.BLACK
	if color == "yellow":
		return Fore.YELLOW
	if color == "blue":
		return Fore.BLUE
	if color == "magenta":
		return Fore.MAGENTA
	if color == "cyan":
		return Fore.CYAN
	if color == "white":
		return Fore.WHITE
	raise Exception("Invalid color: " + color)
def setTextColor(color):
	color = color.lower()
	if not Fore:
		raise ImportException("This function is unavailable unless the module 'Colorama' is installed")
        #raise Exception("This function is not defined yet!")
	spinner.textColor = resolveColor(color)
def setSpinnerColor(color):
	color = color.lower()
	if not Fore:
                raise ImportException("This function is unavailable unless the module 'Colorama' is installed")
	spinner.spinnerColor = resolveColor(color)
def spinnerFail(message):
	return None
