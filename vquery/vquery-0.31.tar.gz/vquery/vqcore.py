from pyVmomi import vim
from .pchelper import *

def get_properties(object_type, _properties):
	properties = []
	properties.append("name")
	if object_type == vim.VirtualMachine:
		if _properties["all"]:
			properties.append("runtime.powerState")
			properties.append("runtime.host")
			properties.append("datastore")
			properties.append("network")
			properties.append("summary.config.memorySizeMB")
			properties.append("summary.config.numCpu")
			properties.append("config.version")
			properties.append("guestHeartbeatStatus")
			properties.append("overallStatus")
			properties.append("summary.guest.hostName")
			properties.append("summary.guest.guestFullName")
			properties.append("summary.guest.ipAddress")
			properties.append("summary.guest.toolsRunningStatus")
			properties.append("summary.guest.toolsStatus")
			properties.append("summary.guest.toolsVersionStatus")
			properties.append("summary.guest.toolsVersionStatus2")
			properties.append("summary.quickStats.hostMemoryUsage")
			properties.append("summary.quickStats.guestMemoryUsage")
			properties.append("summary.storage.committed")
			properties.append("summary.storage.uncommitted")
			properties.append("guest.disk")
			properties.append("summary.quickStats.uptimeSeconds")
			properties.append("summary.quickStats.guestMemoryUsage")
			properties.append("summary.config.vmPathName")
			properties.append("config.template")
			properties.append("snapshot")
		if _properties["folder"]:
			properties.append("parent")
		if _properties["datastore"]:
			properties.append("datastore")
		if _properties["network"]:
			properties.append("network")
		if _properties["host"]:
			properties.append("runtime.host")
		if _properties["cluster"]:
			properties.append("runtime.host")
		if _properties["datacenter"]:
			properties.append("runtime.host")
		if _properties["powerstate"]:
			properties.append("runtime.powerState")
		if _properties["guestip"]:
			properties.append("summary.guest.ipAddress")
		if _properties["guestos"]:
			properties.append("summary.guest.guestFullName")
		if _properties["snapshot"]:
			properties.append("snapshot")
	elif object_type == vim.Datastore:
		if _properties["all"]:
			properties.append("vm")
			properties.append("host")
			properties.append("parent")
			properties.append("summary.capacity")
			properties.append("summary.freeSpace")
			properties.append("summary.uncommitted")
			properties.append("summary.type")
			properties.append("info")
		if _properties["vm"]:
			properties.append("vm")
		if _properties["host"]:
			properties.append("host")
		if _properties["datacenter"]:
			properties.append("parent")
	elif object_type == vim.Network:
		if _properties["all"]:
			properties.append("vm")
			properties.append("host")
			properties.append("parent")
		if _properties["vm"]:
			properties.append("vm")
		if _properties["host"]:
			properties.append("host")
		if _properties["datacenter"]:
			properties.append("parent")
	elif object_type == vim.HostSystem:
		if _properties["all"]:
			properties.append("vm")
			properties.append("datastore")
			properties.append("network")
			properties.append("parent")
			properties.append("summary.quickStats.overallCpuUsage")
			properties.append("summary.quickStats.overallMemoryUsage")
			properties.append("summary.hardware.model")
			properties.append("summary.hardware.cpuModel")
			properties.append("summary.hardware.numCpuCores")
			properties.append("summary.hardware.numCpuPkgs")
			properties.append("summary.hardware.memorySize")
			properties.append("summary.hardware.numNics")
			properties.append("summary.hardware.uuid")
			properties.append("summary.quickStats.uptime")
		if _properties["vm"]:
			properties.append("vm")
		if _properties["datastore"]:
			properties.append("datastore")
		if _properties["network"]:
			properties.append("network")
		if _properties["cluster"]:
			properties.append("parent")
		if _properties["datacenter"]:
			properties.append("parent")
	elif object_type == vim.ClusterComputeResource:
		if _properties["all"]:
			properties.append("host")
			properties.append("datastore")
			properties.append("network")
			properties.append("parent")
		if _properties["vm"]:
			properties.append("host")
		if _properties["datastore"]:
			properties.append("datastore")
		if _properties["network"]:
			properties.append("network")
		if _properties["host"]:
			properties.append("host")
		if _properties["datacenter"]:
			properties.append("parent")
	elif object_type == vim.Datacenter:
		if _properties["all"]:
			properties.append("datastore")
			properties.append("network")
		if _properties["datastore"]:
			properties.append("datastore")
		if _properties["network"]:
			properties.append("network")
	elif object_type == vim.Folder:
		if _properties["all"]:
			properties.append("childEntity") 
		if _properties["vm"]:
			properties.append("childEntity")
			
	return properties

def get_items(si, object_type, properties, exact=False, search_keys=None):
	_properties = get_properties(object_type, properties)
	view = get_container_view(si, obj_type=[object_type])
	view_data = collect_properties(si, view_ref=view,
		       		     obj_type=object_type, 
				     path_set=_properties, 
				     include_mors=True)
	view_data.sort(key=lambda x: x["name"].lower(), reverse=False)

	# Filter result if search keys are specified.
	if search_keys:
		# If we passeed in a string, turn it into a list for easier handling.
		if isinstance(search_keys, str):
			search_keys = [search_keys]

		result = []
		for vd in view_data:
			for search_key in search_keys:
				if exact and search_key == vd["name"]:
					result.append(vd)
				elif search_key.lower() in vd["name"].lower() and not exact:
					result.append(vd)
		view_data = result

	return view_data
