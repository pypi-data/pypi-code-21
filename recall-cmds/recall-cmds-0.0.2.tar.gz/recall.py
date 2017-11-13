import curses
import math
from curses.textpad import Textbox
import os

# TODO:
# move cursor to first occurance of <
# hitting tab goes to next part of command
# copy command into clipboard
# if possible, send command text to current terminal prompt
# args for filepath
# warning for too large of file

# commands formatted for forgets.py: cmd {{label|subcmd}} -p {{label|arg}}
# # # prompt user, enter label: . hit enter, go to next label
ESC_KEY = 27





def addLines(screen, lines, curRow, rangey, colors):
	"""
	Adds lines to the view based off the rangey iterator
	"""
	screen.erase()

	numLines = len(lines)
	for i in rangey:
		if i >= numLines:
			break

		linePrefix = (len(str(numLines)) - len(str(i))) * ' '
		linePrefix += str(i) + '  '

		color = colors[0]
		if i == curRow:
			color = colors[1]

		screen.addstr(i - rangey.start, 1, linePrefix + lines[i], color)


	

def fileNavigator(lines):
	"""
	Responsible for basic navigation of the .forgets file contents
	"""

	screen = curses.initscr()
	curses.noecho()
	curses.cbreak()
	curses.start_color()
	screen.keypad(1)
	colors = (curses.A_NORMAL, curses.A_REVERSE) # (norma, highlight)
	curses.curs_set(0)
	rowsPerPage, tx = screen.getmaxyx()
	screen.resize(rowsPerPage + 2, tx)	

	
	totalLines = len(lines)
	totalPages = int(math.ceil(totalLines / rowsPerPage))
	curRow = 0
	page = 0

	x = screen.addch(curses.KEY_UP)

	while x != ESC_KEY:


		# Navigate file by line
		deltaRow = 0
		if x == curses.KEY_UP: deltaRow = -1
		elif x == curses.KEY_DOWN: deltaRow = 1

		if deltaRow != 0 and curRow + deltaRow < totalLines and curRow + deltaRow > -1:

			curRow += deltaRow
			if curRow == rowsPerPage * (page + deltaRow):
				page += deltaRow

			# going up a page
			elif curRow == (page * rowsPerPage) - 1:
				page += deltaRow


		# Navigate file by page
		deltaPage = 0
		if x == curses.KEY_LEFT: deltaPage = -1
		elif x == curses.KEY_RIGHT: deltaPage = 1

		if deltaPage != 0 and deltaPage + page > -1 and deltaPage + page < totalPages:
			page += deltaPage
			curRow = page * rowsPerPage


		# Select current row
		if x == ord('\n') and totalLines != 0:
			tmp = lines[curRow].strip()
			curses.endwin()
			return tmp


		# update
		r = range(page * rowsPerPage, (page + 1) * rowsPerPage)
		addLines(screen, lines, curRow, r, colors)


		screen.refresh()
		x = screen.getch()

	curses.endwin()

	




def main():
	
	fileContents = []
	homeDir = os.path.expanduser('~')
	FORGETS_FILE = os.path.join(homeDir, '.forgets')

	if not os.path.exists(FORGETS_FILE):
		print('File not found: ~/.forgets')
		exit()

	with open(FORGETS_FILE, 'r') as f:
		fileContents = f.readlines()

	forgottenLine = fileNavigator(fileContents)

	if forgottenLine:
		print(forgottenLine)




if __name__ == '__main__':
	try:
		main()
	except Exception as e:
		curses.endwin()
		print(e)
		