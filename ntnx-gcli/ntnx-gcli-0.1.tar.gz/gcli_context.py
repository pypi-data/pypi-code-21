#!/usr/bin/env python

import click
import json
import os
import paramiko
from gcli_logging import DEBUG, INFO, WARNING

"""
# What the runtime_context looks like
{
  "task_id_counter" : 1,
  "task_map" : {
    1 : <task conn obj>
  },
  "tasks" : [
    {"type" : "async", "id" : "30001", "name" : "run_shell_command", "vm" : "10.5.134.52", "status" : "Running"},
    {"type" : "async", "id" : "30001", "name" : "run_shell_command", "vm" : "10.5.134.46", "status" : "Running"},
    {"type" : "async", "id" : "30001", "name" : "run_shell_command", "vm" : "10.5.134.47", "status" : "Running"}
  ],
  "buffer" : [
    {"name" : "gcli_u01", "ip" : "10.5.134.52", "cluster" : "sturgeon"},
    {"name" : "gcli_u02", "ip" : "10.5.134.46", "cluster" : "sturgeon"},
    {"name" : "gcli_u03", "ip" : "10.5.134.47", "cluster" : "sturgeon"},
    {"name" : "gcli_u04", "ip" : "10.5.134.42", "cluster" : "sturgeon"},
    {"name" : "gcli_u05", "ip" : "10.5.134.31", "cluster" : "sturgeon"},
    {"name" : "gcli_u06", "ip" : "10.5.134.38", "cluster" : "sturgeon"},
    {"name" : "gcli_u07", "ip" : "10.5.134.40", "cluster" : "sturgeon"},
    {"name" : "gcli_u08", "ip" : "10.5.134.43", "cluster" : "sturgeon"},
    {"name" : "gcli_u09", "ip" : "10.5.134.57", "cluster" : "sturgeon"},
    {"name" : "gcli_u10", "ip" : "10.5.134.53", "cluster" : "sturgeon"}
  ]
}

# What the persistent_context looks like
{
  "tasks": [
    {"type" : "Handsoff", "id" : "30001", "name" : "run_shell_command", "vm" : "10.5.134.42", "status" : "Running"},
    {"type" : "Handsoff", "id" : "30001", "name" : "run_shell_command", "vm" : "10.5.134.31", "status" : "Running"},
    {"type" : "Handsoff", "id" : "30001", "name" : "run_shell_command", "vm" : "10.5.134.38", "status" : "Running"},
    {"type" : "Handsoff", "id" : "30001", "name" : "run_shell_command", "vm" : "10.5.134.40", "status" : "Running"}
  ],
  "uvms": [
    {"name" : "gcli_u01", "ip" : "10.5.134.52", "cluster" : "sturgeon"},
    {"name" : "gcli_u03", "ip" : "10.5.134.47", "cluster" : "sturgeon"},
    {"name" : "gcli_u04", "ip" : "10.5.134.42", "cluster" : "sturgeon"},
    {"name" : "gcli_u06", "ip" : "10.5.134.38", "cluster" : "sturgeon"},
    {"name" : "gcli_u08", "ip" : "10.5.134.43", "cluster" : "sturgeon"},
    {"name" : "gcli_u10", "ip" : "10.5.134.53", "cluster" : "sturgeon"}
  ]
}
"""

class GcliContext(object):
  """ Hold and handle all the gcli context data. """
  def __init__(self, context_file="gcli_context.json"):
    self.runtime_context = {}
    self.persistent_context = {}
    self.context_file = context_file

  def init_context(self):
    self.runtime_context = {
      "task_id_counter" : 1,
      "task_map" : {},
      "tasks" : [],
      "buffer" : []
    }
    if os.path.exists(self.context_file):
      with open(self.context_file) as f_context:
        data = f_context.read()
        self.persistent_context = json.loads(data)
    else:
      self.persistent_context = {"tasks" : [], "uvms" : []}
      WARNING("!!!No previous context, starting fresh!!!")

  def save_context(self):
    with open(self.context_file, "w") as f_context:
        json.dump(self.persistent_context, f_context, indent=2)

  def _list_vm_from_cluster(self, cluster, pattern):
    hostname = cluster + "-c1"
    port = 22
    username = "nutanix"
    password = "nutanix/4u"
    ncli_app = "/home/nutanix/prism/cli/ncli"
    out_prefix = "Name                      : "
    command = "%s vm ls | grep -A 1 \"%s%s\"" % (ncli_app, out_prefix, pattern)

    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname, port=port, username=username, password=password)
    stdin, stdout, stderr = client.exec_command(command)
    output = stdout.read()
    client.close()
    return output

  def list_uvms(self, clusters, pattern):
    self.runtime_context["buffer"] = []
    cluster_list = clusters.split(',')
    for cluster in cluster_list:
      #find uvms on this each cluster
      uvm_list = self._list_vm_from_cluster(cluster, pattern)
      uvm_list = uvm_list.split('--\n')
      for uvm_info in uvm_list:
        uvm_info_list = uvm_info.split('\n')
        if len(uvm_info_list) >=2:
          vm_name = uvm_info_list[0].split(':')[1].strip()
          vm_ip = uvm_info_list[1].split(':')[1]
          vm_ip = vm_ip.split(',')[0].strip()
          uvm_dict = {"name" : vm_name, "ip" : vm_ip, "cluster" : cluster}
          self.runtime_context["buffer"].append(uvm_dict)

  def _uvm_format_out(self, uvm=None):
    if uvm is None:
      click.echo(" == Cluster ================ VM Name "
                 "================ VM IP ========")
      return
    out_str = " %-24s %-24s %-18s" % (uvm["cluster"], uvm["name"], uvm["ip"])
    click.echo(out_str)

  def show_buffer(self):
    self._uvm_format_out()
    if "buffer" in self.runtime_context:
      for uvm in self.runtime_context["buffer"]:
        self._uvm_format_out(uvm=uvm)

  def set_uvms_from_buffer(self):
    if "buffer" in self.runtime_context:
      self.persistent_context["uvms"] = self.runtime_context["buffer"][:]
    click.echo("%d UVMs set to working list" % len(self.runtime_context["buffer"]))

  def set_uvms(self, vm_ips):
    self.persistent_context["uvms"] = []
    ips = vm_ips.split(',')
    DEBUG(str(ips))
    for ip in ips:
      uvm = {"name" : "NA", "ip" : ip, "cluster" : "NA"}
      self.persistent_context["uvms"].append(uvm)
    click.echo("%d UVMs set to working list" % len(ips))

  def show_uvms(self):
    self._uvm_format_out()
    if "uvms" in self.persistent_context:
      for uvm in self.persistent_context["uvms"]:
        self._uvm_format_out(uvm=uvm)

  def _task_format_out(self, task=None):
    if task is None:
      click.echo(" == type == == id ==== == vm ip ======="
                 " == task name ======= == status ======")
      return
    out_str = " %-10s %-10s %-16s %-20s %-16s" %\
              (task["type"], task["id"], task["vm"], task["name"],
               task["status"])
    click.echo(out_str)

  def show_tasks(self):
    counter = 0
    self._task_format_out()
    if "tasks" in self.runtime_context:
      for task in self.runtime_context["tasks"]:
        self._task_format_out(task=task)
        counter += 1
    if "tasks" in self.persistent_context:
      for task in self.persistent_context["tasks"]:
        self._task_format_out(task=task)
        counter += 1
    click.echo(" Tatal: %d" % counter)

  def async_task_add(self, vm_ip, task_name, obj):
    task_id = self.runtime_context["task_id_counter"]
    self.runtime_context["task_id_counter"] += 1
    self.runtime_context["task_map"][task_id] = obj
    task = {
      "type" : "async", 
      "id" : task_id, 
      "name" : task_name, 
      "vm" : vm_ip, 
      "status" : "Running"
    }
    self.runtime_context["tasks"].append(task)
    return task_id

  def handsoff_task_add(self, vm_ip, task_name, task_id):
    task = {
      "type" : "handsoff", 
      "id" : task_id, 
      "name" : task_name, 
      "vm" : vm_ip, 
      "status" : "Running"
    }
    self.persistent_context["tasks"].append(task)

  def handsoff_task_update(self, vm_ip, task_id, result):
    for task in self.persistent_context["tasks"]:
      if task["vm"] == vm_ip and task["id"] == task_id:
        task["status"] = "Success" if result == 0 else "Failed"
        break

  def async_task_update(self, task_id, result):
    for task in self.runtime_context["tasks"]:
      if task["id"] == task_id:
        task["status"] = "Success" if result == 0 else "Failed"
        break
