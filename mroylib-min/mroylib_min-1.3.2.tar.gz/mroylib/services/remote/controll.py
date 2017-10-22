from qlib.io import GeneratorApi
from .fablibs import ex_cmd, env, shadowsocks_apt, shadowsocks_yum
from qlib.log import show
from termcolor import colored
from getpass import getpass

import re

# env.roledefs = {str(i):['root@'+v] for i,v in enumerate(
    # [i.strip() for i in open(os.path.join(ROOT_PATH,"server.list")).readlines() if i.strip() ])}



def load(config):
	if not env.roledefs:
		env.roledefs = {str(i):['root@'+v] for i,v in enumerate(
    [i.strip() for i in open(os.path.join(config,"server.list")).readlines() if i.strip() ])}
	
	if not env.hosts:
		for i in env.roledefs:
			show(i,env.roledefs)
		host = input(colored(">>", "green", attrs=['underline']))
		if len(host) < 8:
			host_id = int(host)
			env.hosts = env.roledefs[str(host_id)]
		elif re.match(r'^(\d{1,3}\.){3}\d{1,3}$', host):
			env.host = host
		else:
			show("not match!! , just save as domain host", color='yellow')

	if not env.password:
		env.password = getpass()


def sub_find(file, root="."):
	for r,d ,fs in os.walk(root):
		for f in fs:
			if f.endswith(file):
				return os.path.join(r, f)



def load_conf(path, root):
	with open(path) as fp:
		for l in fp:
			if l.startswith("[") and l.endswith("]"):
				contents = re.findall(r'\[(.+?)\]',  l)[0].split()
				if contents[0] == 'put':
					f = sub_find(contents[1], root)
					if f:
						put(f, "/tmp/")
					else:
						show(f, colored('is not right', 'green'), color='red')
						break

			else:
				ex_cmd(l.strip())

def main():
	args = GeneratorApi({
			'file': "file to run",
			"root": "default is .",
		},"some control part ")

	if not args.root:
		args.root = '.'

	load(args.root)
	load_conf(args.file, args.root)

