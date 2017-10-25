from cliff.lister import Lister
from cliff.command import Command
from pynvml import *
import docker
import os
import collections
import pprint

def get_nvidia_major():
    info = os.lstat('/dev/nvidia0')
    major, minor = divmod(info.st_rdev, 256)
    return major
	
def get_max_gpu_devices():
	nvmlInit()
        deviceCount = nvmlDeviceGetCount()
	nvmlShutdown()
	
	return deviceCount

def has_gpu_devices():
	nvmlInit()
        deviceCount = nvmlDeviceGetCount()
	nvmlShutdown()

	if deviceCount == 0:
		return False

	return True

def has_no_gpu_devices():
	return not has_gpu_devices()

class GpuRemove(Command):
    """Remove Gpus."""

    def get_parser(self, prog_name):
	""" gpu ids"""
	if has_no_gpu_devices():
		raise RuntimeError('No Gpu Devices to Remove')

	
        parser = super(GpuRemove, self).get_parser(prog_name)
        parser.add_argument('--gpu', nargs='+', required=True, help='specify the gpu ids', type=int, choices=range(0, get_max_gpu_devices()))
        parser.add_argument('--container', required=True, help='specify the container name', type=str)
        return parser

    def take_action(self, args):
        #docker_obj = docker.APIClient(base_url='unix://var/run/docker.sock', version='auto')
        docker_obj = docker.from_env()

	container_obj = docker_obj.inspect_container(args.container)
	container_id = container_obj['Id']	
	sys_file_path = '/sys/fs/cgroup/devices/docker/' + container_id + '/devices.deny'
	
	
	major = get_nvidia_major()
	for gpu_index in args.gpu:
		add_str = 'c '+ str(major) + ':' + str(gpu_index) + ' rwm'	
		with open(sys_file_path, 'w') as file_obj:
			file_obj.write(add_str)

	self.app.stdout.write('OK\n')

class GpuAdd(Command):
    """Add Gpus."""

    def get_parser(self, prog_name):
	""" gpu ids"""
	if has_no_gpu_devices():
		raise RuntimeError('No Gpu Devices to add')

	
        parser = super(GpuAdd, self).get_parser(prog_name)
        parser.add_argument('--gpu', nargs='+', required=True, help='specify the gpu ids', type=int, choices=range(0, get_max_gpu_devices()))
        parser.add_argument('--container', required=True, help='specify the container name', type=str)
        return parser

    def take_action(self, args):
        #docker_obj = docker.APIClient(base_url='unix://var/run/docker.sock', version='auto')
        docker_obj = docker.from_env()
	container_obj = docker_obj.inspect_container(args.container)
	container_id = container_obj['Id']	
	sys_file_path = '/sys/fs/cgroup/devices/docker/' + container_id + '/devices.allow'
	
	
	major = get_nvidia_major()
	for gpu_index in args.gpu:
		add_str = 'c '+ str(major) + ':' + str(gpu_index) + ' rwm'	
		with open(sys_file_path, 'w') as file_obj:
			file_obj.write(add_str)
	self.app.stdout.write('OK\n')
	
class GpuList(Lister):
    """List Gpus."""

    def take_action(self, args):
	nvmlInit()
	deviceCount = nvmlDeviceGetCount()
	dict_gpu = {}

	for i in range(deviceCount):
        	handle = nvmlDeviceGetHandleByIndex(i)
		dict_gpu[i] =  nvmlDeviceGetUUID(handle)

	nvmlShutdown()


        #docker_obj = docker.APIClient(base_url='unix://var/run/docker.sock', version='auto')
        docker_obj = docker.from_env()
	containers = docker_obj.containers(all=True)
	major =get_nvidia_major()
	dict_containers = collections.defaultdict(list)
	for container in containers:
       		container_id = container['Id']
	        container_name = container['Names'][0]
       		container_name = container_name[1:]

	        sys_file_path = '/sys/fs/cgroup/devices/docker/' + container_id + '/devices.list'
		if os.path.isfile(sys_file_path) == False:
			# this is not a nvidia docker container
			continue

       		with  open(sys_file_path, 'r') as file_obj:
       			file_data =  file_obj.read().splitlines()
	        for line in file_data:
 			if str(major) not in line:
				continue
              		index = line.split()[1].split(':')[1]
			if index == '255':
                       		 continue
	                dict_containers[index].append(container_name)

	return (('Index', 'UUID', 'Attached-container' ), ((item, dict_gpu[item], ','.join(dict_containers[str(item)])) for item in dict_gpu ))
