"""system.user.find module"""
from sys import \
    stderr as stderr
__puke = stderr.write

def userfind(pattern='1000', mode='user'):
	"""find any type of entry a user has in passwd by a given pattern"""
	idmap = {
        'user': 0, 'x': 1, 'uid': 2,
        'gid': 3, 'comment': 4, 'home': 5, 'shell': 6}
	mode = int(idmap[mode])
	pstr = str(pattern)
	try:
		with open('/etc/passwd', 'r') as pwd:
			try:
				hits = [f.split(':') for f in [l for l in pwd.readlines() if pstr in l] if pstr in f][0]
			except IndexError as err:
				__puke(str(err))
				hits = []
	except PermissionError as err:
		__puke(str(err))
		return err
	if hits:
		return list(hits)[mode]
