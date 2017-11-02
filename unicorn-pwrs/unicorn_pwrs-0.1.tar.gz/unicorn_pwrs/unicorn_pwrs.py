#!/usr/local/bin/python3 
import os
import time
import textwrap
import simpleaudio as sa

from sys import prefix
print(prefix)

# -------------- FILES -------------- #
data_folder = os.path.join(os.path.dirname(__file__), 'data/')

txt_files = {
	'cover'     : os.path.join(data_folder, 'cover.txt'),
	'cv'        : os.path.join(data_folder, 'cv.txt'),
	'reference' : os.path.join(data_folder, 'reference.txt')
}

click_wav = os.path.join(data_folder, 'unicorn_click.wav')
click_wav_obj = sa.WaveObject.from_wave_file(click_wav)

bleed_wav = os.path.join(data_folder, 'unicorn_bleep.wav')
bleed_wav_obj = sa.WaveObject.from_wave_file(bleed_wav)

# -------------- 2/3 SUPPORT -------------- #
try:
    input = raw_input
except NameError:
    pass


# -------------- FUNCTIONS -------------- #
def main():

	u_c = get_user_choice()
	
	while u_c != 'x':
		if u_c == 'c':
			display_cv()
			u_c = get_user_choice()
		elif u_c == 'o':
			display_cvrlttr()
			u_c = get_user_choice()
		elif u_c == 'l':
			display_links()
			u_c = get_user_choice()
		elif u_c == 'r':
			display_reference()
			u_c = get_user_choice()
		else:
			# u_c = u_c.strip()
			bleed_wav_obj.play()
			print()
			print('    hey, maybe try again...? ')
			print('    e.g. like: type \'c\' for cv')
			u_c = get_user_choice()

	goodbye()


def get_user_choice():
	print('\n')
	
	user_choice = input(''' 
    [c]v
   c[o]ver letter
    [l]inks
    [r]eference
    
   e[x]it
   \n\n\n 
>  ''')

	u_c = user_choice.lower()
	return u_c


# def file_len(file):
#     with open(file) as f:
#         for i, l in enumerate(f):
#             pass
#     return i + 1


def print_a_file(file):
	with open(file, 'r') as fin:
		lines = [l.strip() for l in fin.readlines()]
		for l in lines:
			print(textwrap.fill(l, 68))


def print_header(header_name):
	click_wav_obj.play()

	print()
	print('-' * 60)
	print(header_name.center(60, '-'))
	print('-' * 60, '\n')


def display_cv():
	print_header('CV')
	print_a_file(txt_files['cv'])
	# time.sleep(2)
	

def display_cvrlttr():
	print_header('COVER LETTER')
	print_a_file(txt_files['cover'])
	# time.sleep(2)


def display_reference():
	print_header('REFERENCE')
	print_a_file(txt_files['reference'])
	# time.sleep(2)


def display_links():
	links_dict = {
		1 : 'https://github.com/thomasoflight',
		2 : 'https://twitter.com/thomasoflight',
		3 : 'https://cargocollective.com/ariemarie'
	}

	print_header('LINKS')

	print('[1] --> GITHUB')
	print('[2] --> TWITTER')
	print('[3] --> ARIEMARIE.COM (artist website)')

	# time.sleep(2)
	# event loops launches various links


def goodbye():
	print()
	print('Goodbye!')


if __name__ == '__main__':
	main()
