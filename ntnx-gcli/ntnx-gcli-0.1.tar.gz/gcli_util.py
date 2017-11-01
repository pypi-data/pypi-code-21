#!/usr/bin/env python

import click
import json
import sys
import time
from acro_gos_utility import AcroGOSUtil
from gcli_logging import DEBUG, ERROR

class GcliUtil(object):

  def __init__(self, context, vm_ip):
    self.context = context
    self.vm_ip = vm_ip
    self.ip_list = []
    if self.vm_ip == "work_list":
      self.single_mode = False
      for uvm in self.context.persistent_context["uvms"]:
        self.ip_list.append(uvm["ip"])
    else:
      self.single_mode = True
      self.ip_list.append(vm_ip)
    DEBUG("GcliUtil: single_mode=%s, vm_ip=%s" % (self.single_mode, vm_ip))

  def upgrade_guest_agent(self, path):
    for ii in range(len(self.ip_list)):
      util = AcroGOSUtil(self.ip_list[ii])
      try:
        succeed = util.upgrade_test_agent(path)
        result = "Success" if succeed else "Failed"
      except Exception, e:
        result = str(e)
      self._output_result(ii, result)

  def get_gos_info(self):
    for ii in range(len(self.ip_list)):
      util = AcroGOSUtil(self.ip_list[ii])
      try:
        info = util.get_guest_os_info()
      except Exception, e:
        info = str(e)
      self._output_result(ii, info)

  def get_scsi_disk_dev_file(self, device_index):
    for ii in range(len(self.ip_list)):
      util = AcroGOSUtil(self.ip_list[ii])
      try:
        ret = util.get_scsi_disk_dev_file(device_index)
      except Exception, e:
        ret = str(e)
      self._output_result(ii, ret)

  def get_vg_scsi_disk_dev_file(self, index_tuple):
    for ii in range(len(self.ip_list)):
      util = AcroGOSUtil(self.ip_list[ii])
      try:
        ret = util.get_vg_scsi_disk_dev_file(index_tuple)
      except Exception, e:
        ret = str(e)
      self._output_result(ii, ret)

  def transfer_file_to_guest(self, src_path, remote_path):
    for ii in range(len(self.ip_list)):
      util = AcroGOSUtil(self.ip_list[ii])
      try:
        succeed = util.transfer_file_to_guest(src_path, remote_path)
        result = "Success" if succeed else "Failed"
      except Exception, e:
        result = str(e)
      self._output_result(ii, result)

  def transfer_file_from_guest(self, local_path, remote_path):
    for ii in range(len(self.ip_list)):
      util = AcroGOSUtil(self.ip_list[ii])
      try:
        succeed = util.transfer_file_from_guest(local_path, remote_path)
        result = "Success" if succeed else "Failed"
      except Exception, e:
        result = str(e)
      self._output_result(ii, result)

  def _run_commands_sync(self, cmd):
    for ii in range(len(self.ip_list)):
      util = AcroGOSUtil(self.ip_list[ii])
      try:
        result, stdout, stderr = util.run_shell_command_sync(cmd)
        if result == 0:
          if self.single_mode and stdout != "No stdout":
            out_str = stdout
          else:
            out_str = "Success"
        else:
          if self.single_mode:
            out_str = "Failed return=%d, stderr=%s" % (result, stderr)
          else:
            out_str = "Failed return=%d" % result
      except Exception, e:
        out_str = str(e)
      self._output_result(ii, out_str)

  def _run_commands_async(self, cmd):
    for ii in range(len(self.ip_list)):
      util = AcroGOSUtil(self.ip_list[ii])
      try:
        obj = util.run_shell_command_async(cmd)
        tid = self.context.async_task_add(self.ip_list[ii], "run_command", obj)
        out_str = "Task id: %d" % tid
      except Exception, e:
        out_str = str(e)
      self._output_result(ii, out_str)

  def _run_commands_handsoff(self, cmd):
    for ii in range(len(self.ip_list)):
      util = AcroGOSUtil(self.ip_list[ii])
      try:
        task_id = util.run_shell_command_handsoff(cmd)
        self.context.handsoff_task_add(self.ip_list[ii], "run_command", task_id)
        out_str = "Task id: %d" % task_id
      except Exception, e:
        out_str = str(e)
      self._output_result(ii, out_str)

  def run_commands(self, execution_mode, cmd):
    if execution_mode == 'sync':
      self._run_commands_sync(cmd)
    elif execution_mode == 'async':
      self._run_commands_async(cmd)
    elif execution_mode == 'handsoff':
      self._run_commands_handsoff(cmd)
    else:
      ERROR("Unsupported execution_mode: %s" % execution_mode)

  def _run_io_integrity_sync(self, vdisk_file, file_size_gb, time_limit_secs):
    for ii in range(len(self.ip_list)):
      util = AcroGOSUtil(self.ip_list[ii])
      try:
        result, stdout, stderr = \
          util.run_io_integrity_test_sync(vdisk_file=vdisk_file,
                                          file_size_gb=file_size_gb,
                                          time_limit_secs=time_limit_secs)
        if result == 0:
          if self.single_mode and stdout != "No stdout":
            out_str = stdout
          else:
            out_str = "Success"
        else:
          if self.single_mode:
            out_str = "Failed return=%d, stderr=%s" % (result, stderr)
          else:
            out_str = "Failed return=%d" % result
      except Exception, e:
        out_str = str(e)
      self._output_result(ii, out_str)

  def _run_io_integrity_async(self, vdisk_file, file_size_gb, time_limit_secs):
    for ii in range(len(self.ip_list)):
      util = AcroGOSUtil(self.ip_list[ii])
      try:
        obj = util.run_io_integrity_test_async(vdisk_file=vdisk_file,
                                               file_size_gb=file_size_gb,
                                               time_limit_secs=time_limit_secs)
        tid = self.context.async_task_add(self.ip_list[ii], "io_integrity", obj)
        out_str = "Task id: %d" % tid
      except Exception, e:
        out_str = str(e)
      self._output_result(ii, out_str)

  def _run_io_integrity_handsoff(self, vdisk_file, file_size_gb,
                                 time_limit_secs):
    for ii in range(len(self.ip_list)):
      util = AcroGOSUtil(self.ip_list[ii])
      try:
        task_id = \
          util.run_io_integrity_test_handsoff(vdisk_file=vdisk_file,
                                              file_size_gb=file_size_gb,
                                              time_limit_secs=time_limit_secs)
        self.context.handsoff_task_add(self.ip_list[ii], "io_integrity",
                                       task_id)
        out_str = "Task id: %d" % task_id
      except Exception, e:
        out_str = str(e)
      self._output_result(ii, out_str)

  def run_io_integrity_test(self,
                            vdisk_file,
                            file_size_gb,
                            time_limit_secs,
                            execution_mode):
    if execution_mode == 'sync':
      self._run_io_integrity_sync(vdisk_file, file_size_gb, time_limit_secs)
    elif execution_mode == 'async':
      self._run_io_integrity_async(vdisk_file, file_size_gb, time_limit_secs)
    elif execution_mode == 'handsoff':
      self._run_io_integrity_handsoff(vdisk_file, file_size_gb, time_limit_secs)
    else:
      ERROR("Unsupported execution_mode: %s" % execution_mode)

  def _run_user_code_sync(self, engine, name, code):
    for ii in range(len(self.ip_list)):
      util = AcroGOSUtil(self.ip_list[ii])
      try:
        result, stdout, stderr = util.run_user_code_sync(engine=engine,
                                                         name=name, code=code)
        if result == 0:
          if self.single_mode and stdout != "No stdout":
            out_str = stdout
          else:
            out_str = "Success"
        else:
          if self.single_mode:
            out_str = "Failed return=%d, stderr=%s" % (result, stderr)
          else:
            out_str = "Failed return=%d" % result
      except Exception, e:
        out_str = str(e)
      self._output_result(ii, out_str)

  def _run_user_code_async(self, engine, name, code):
    for ii in range(len(self.ip_list)):
      util = AcroGOSUtil(self.ip_list[ii])
      try:
        obj = util.run_user_code_async(engine=engine, name=name, code=code)
        tid = self.context.async_task_add(self.ip_list[ii], "user_code", obj)
        out_str = "Task id: %d" % tid
      except Exception, e:
        out_str = str(e)
      self._output_result(ii, out_str)

  def _run_user_code_handsoff(self, engine, name, code):
    for ii in range(len(self.ip_list)):
      util = AcroGOSUtil(self.ip_list[ii])
      try:
        task_id = util.run_user_code_handsoff(engine=engine, name=name,
                                              code=code)
        self.context.handsoff_task_add(self.ip_list[ii], "user_code",
                                       task_id)
        out_str = "Task id: %d" % task_id
      except Exception, e:
        out_str = str(e)
      self._output_result(ii, out_str)

  def run_user_code(self, engine, name, code, execution_mode):
    if execution_mode == 'sync':
      self._run_user_code_sync(engine, name, code)
    elif execution_mode == 'async':
      self._run_user_code_async(engine, name, code)
    elif execution_mode == 'handsoff':
      self._run_user_code_handsoff(engine, name, code)
    else:
      ERROR("Unsupported execution_mode: %s" % execution_mode)

  def query_handsoff_task(self, task_id):
    for ii in range(len(self.ip_list)):
      util = AcroGOSUtil(self.ip_list[ii])
      try:
        status, sec_passed = util.query_handsoff_task_status(task_id=task_id)
        if status == 1:  # Task still running
          out_str = "Running, %d seconds" % sec_passed
        elif status == 2: # Task completed
          ret, out, error = util.query_handsoff_task_result(task_id=task_id)
          self.context.handsoff_task_update(self.ip_list[ii], task_id, ret)
          if ret == 0:
            if self.single_mode and out != "No stdout":
              out_str = out
            else:
              out_str = "Success, %d seconds" % sec_passed
          else:
            if self.single_mode:
              out_str = "Failed return=%d, %d seconds, stderr=%s" %\
                        (ret, sec_passed, error)
            else:
              out_str = "Failed return=%d, %d seconds" % (ret, sec_passed)
        else: # Wrong task status, mostly doesn't exist
          out_str = "Error, wrong status %d" % status
      except Exception, e:
        out_str = str(e)
      self._output_result(ii, out_str)

  def query_async_task(self, task_id):
    if task_id == 0:
      id_list = self.context.runtime_context["task_map"].keys()
    else:
      id_list = [task_id]
    num = len(id_list)
    for ii in range(num):
      conn = self.context.runtime_context["task_map"][id_list[ii]]
      if conn.is_closed():
        continue
      try:
        status = conn.query_running_status()
        sec_passed = conn.query_running_time()
        if status == 1:  # Task still running
          click.echo("Running, %d seconds" % sec_passed)
        elif status == 2: # Task completed
          ret = conn.query_result_status()
          out = conn.query_result_stdout()
          error = conn.query_result_stderr()
          conn.close_connection()
          self.context.async_task_update(id_list[ii], ret)
          if ret == 0:
            if task_id != 0 and out != "No stdout":
              click.echo(out)
            else:
              click.echo("Success, %d seconds" % sec_passed)
          else:
            if task_id != 0:
              click.echo("Failed return=%d, %d seconds, stderr=%s" %\
                         (ret, sec_passed, error))
            else:
              click.echo("Failed return=%d, %d seconds" % (ret, sec_passed))
        else: # Wrong task status, shouldn't exist
          ERROR("Error, wrong status %d" % status)
      except Exception, e:
        click.echo(str(e))
      if ii < num - 1:
        click.echo("---")

  def _output_result(self, idx, out_str):
      if self.single_mode:
        click.echo(out_str)
        return
      num = len(self.ip_list)
      click.echo("UVM IP: %s, %s" % (self.ip_list[idx], out_str))
      if idx < num - 1:
        click.echo("---")

