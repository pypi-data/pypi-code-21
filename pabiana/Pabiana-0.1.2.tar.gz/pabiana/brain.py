import importlib
import logging
import multiprocessing as mp
import os
import signal
from os import path

import pip

from . import repo
from .templates import create_director, create_clock
from .utils import read_interfaces, setup_logging


def main(*args):
	args = list(args)
	stop_pip = False
	if '-X' in args:
		stop_pip = True
		args.remove('-X')
	if '-C' in args:
		args.append('def_clock:clock')
		args.remove('-C')
	elif '-D' in args:
		args.append('def_director:clock')
		args.remove('-C')
	if len(args) > 1:
		setup_logging()
		logging.info('Starting %s processes', len(args))
		signal.signal(signal.SIGINT, lambda *args, **kwargs: None)
		mp.set_start_method('spawn')
		for module_area_name in args:
			process = mp.Process(target=run, args=(module_area_name, stop_pip))
			process.start()
	else:
		run(*args, stop_pip=stop_pip)


def run(module_area_name, stop_pip=False):
	module_name, area_name = module_area_name.split(':')
	repo['base-path'] = os.getcwd()
	repo['module-name'] = module_name
	repo['area-name'] = area_name
	
	intf_path = path.join(repo['base-path'], 'interfaces.json')
	repo['interfaces'] = read_interfaces(intf_path)
	
	req_path = path.join(repo['base-path'], module_name, 'requirements.txt')
	if not stop_pip and path.isfile(req_path):
		pip.main(['install', '--upgrade', '-r', req_path])
	
	try:
		mod = importlib.import_module(module_name)
	except ImportError:
		setup_logging()
		if module_name == 'def_director' and area_name == 'clock':
			area = create_director(name=area_name, interfaces=repo['interfaces'])
			area.run()
			return
		if module_name == 'def_clock' and area_name == 'clock':
			area = create_clock(name=area_name, interfaces=repo['interfaces'])
			area.run()
			return
		else:
			raise
	
	if hasattr(mod, 'premise'):
		mod.premise()
	
	if hasattr(mod, 'area'):
		if hasattr(mod, 'config'):
			params = {
				'clock_name': mod.config['clock-name'],
				'clock_slots': mod.config.get('clock-slots')
			}
			if mod.config.get('subscriptions') is not None:
				params['subscriptions'] = mod.config['subscriptions']
			mod.area.subscribe(**params)
			if 'context-values' in mod.config:
				mod.area.context.update(mod.config['context-values'])
		mod.area.run()
	
	elif hasattr(mod, 'runner'):
		if hasattr(mod.runner, 'setup'):
			params = {}
			if hasattr(mod, 'config'):
				params.update(mod.config)
			mod.runner.setup(**params)
		mod.runner.run()

