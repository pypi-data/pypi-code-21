from os import getuid
def whoami():
	with open('/etc/passwd', 'r') as pwf:
		pwl = pwf.readlines()
	return [
        u.split(':')[0] for u in pwl if int(u.split(':')[2]) == getuid()][0]
