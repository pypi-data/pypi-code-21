"""
Copyright (c) 2017 Nutanix Inc. All rights reserved.

Author: bruce.gao@nutanix.com

Note:
  Protocol between this utility class and test_agent in guest OS is defined by
  the following json structures:
    {"task_type":"start_task", "async":False, "handsoff":False,
     "task_str":"RUN_IO_INTEGRITY", "task_args":""}
    {"task_type":"query_running_status", "handsoff":False, "task_id":0}
    {"task_type":"query_running_time", "handsoff":False, "task_id":0}
    {"task_type":"query_result_status", "handsoff":False, "task_id":0}
    {"task_type":"query_result_stdout", "handsoff":False, "task_id":0}
    {"task_type":"query_result_stderr", "handsoff":False, "task_id":0}
    {"task_type":"query_additional_data", "handsoff":False, "task_id":0}

   "task_str" supported in this agent version:
     "GET_OS_STATS"
     "RUN_IO_INTEGRITY"
     "GET_SCSI_DEV_FILE"
     "GET_VG_SCSI_DEV_FILE"
     "RUN_COMMAND"
     "TRANSFER_FILE_TO_VM"
     "TRANSFER_FILE_FROM_VM"
     "RUN_USER_CODE"

   "task_args" content depends on task_str

   For RUN_IO_INTEGRITY, RUN_COMMAND, RUN_USER_CODE, there are three running
   modes:
     1. sync: Client will bock until task complete. Caller get
              (result, stdout, stderr) after call returned.
     2. async: Client will return a task object(with open socket connection)
               right away. Caller could further call into the task object
               method to query running status and result output.
     3. handsoff: Client will return a task id (socket connection closed).
                  Caller could further call query_handsoff_task.... for task
                  running information.
  Example:
  1. Request guest os to start io integrity test asynchronously.
    {"task_type": "start_task", "async": True, "task_str": "RUN_IO_INTEGRITY",
     "task_args": ""}
  2. Query if the previous started task completed
    {"task_type": "query_running_status"}

"""

import binascii
import json
import socket
import struct
import time
import urllib2

##############################################################################
# This file is copied from nutest/workflows/acropolis/ahv/acro_gos_utility.py
# When it is used as a module in Nutest, use INFO from nulog.
# from framework.lib.nulog import INFO, ERROR
# from framework.lib.utils import wait_for_response
from gcli_logging import DEBUG, ERROR

def wait_for_response(functor, expected, timeout=100, interval=5,
                      suppress=False):
  end_time = timeout + time.time()
  while time.time() < end_time:
    try:
      response = functor()
      if response == expected:
        return response
    except Exception as exp:
      print exp
      if not suppress:
        raise
    time.sleep(interval)
  raise Exception('Execution of functor timedout')

#pylint: disable=no-member
#pylint: disable=invalid-name
#pylint: disable=R0201
#pylint: disable=broad-except

def send_data(sock, data):
  """Common function used in test agent upgrade code. Send data with simple
     protocol on socket.

  Args:
    sock (object): socket object
    data (str): data buffer to send

  Returns:
    None: No returns
  """
  try:
    sock.sendall(struct.pack("I", len(data)))
    sock.sendall(data)
  except Exception, e:
    ERROR("Error sending data: %s" % (e,))
    return False
  return True

def recv_all(sock, bytes_to_recv):
  """Common function used in test agent upgrade code. Receive specified number
     of bytes from socket, or error out.

  Args:
    sock (object): socket object
    bytes_to_recv (int): number of bytes to receive

  Returns:
    str: Data received
  """
  data = ""
  try:
    bytes_received = 0
    while bytes_received != bytes_to_recv:
      data_received = sock.recv(bytes_to_recv - bytes_received)
      if len(data_received) == 0:
        DEBUG("Client closed connection")
        break
      bytes_received += len(data_received)
      data += data_received
  except Exception, e:
    ERROR("Error receiving data (len=%d): %s" % (bytes_to_recv, e))

  assert len(data) == bytes_to_recv, "No enough data to receive"
  return data

def recv_data(sock):
  """Common function used in test agent upgrade code. Receive data with
     a simple protocol.

  Args:
    sock (object): socket object

  Returns:
    str: Data received
  """
  data = ""
  try:
    data_len = recv_all(sock, 4)
    data_len = struct.unpack("I", data_len)[0]
    data = recv_all(sock, data_len)
  except Exception, e:
    ERROR("Error receiving data (len=%d): %s" % (data_len, e))

  return data

class GOSAgentUpgrade(object):
  """Helper class to handle test agent upgrade.

  Sample Usage:
    util = GOSAgentUpgrade(vm_ip)
  """
  def __init__(self, vm_ip):
    """Instance initiator

    Args:
      vm_ip (str): String of vm ip address

    Returns:
      None: No returns
    """
    self.vm_ip = vm_ip
    self.vm_port = 2016
    self.client_socket = None

  def upgrade_agent(self, from_local_file=None, from_url=None):
    """Upgrade test agent from a local file or from a remote url

    Args:
      from_local_file (str): test agent file to be used for upgrade
      from_url (str): http based url location of test agent file

    Returns:
      boolean: successfully upgraded or not
    """
    DEBUG("Start agent upgrade...")
    data = ""
    if from_local_file:
      DEBUG("Upgrade from local file %s" % (from_local_file,))
      with open(from_local_file, "rb") as fd:
        data = fd.read()
    elif from_url:
      DEBUG("Upgrade from url %s" % (from_url,))
      response = urllib2.urlopen(from_url)
      data = response.read()
    else:
      ERROR("Must have from_local_file or from_url")
      return False
    if len(data) <= 0:
      ERROR("Invalid content")
      return False

    DEBUG("Connect to test agent on VM at %s:%d" % (self.vm_ip, self.vm_port))
    self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.client_socket.connect((self.vm_ip, self.vm_port))

    DEBUG("Send test agent body, expect AGENT_RECEIVED_OK")
    success = send_data(self.client_socket, data)
    if not success:
      return False
    ret_str = recv_data(self.client_socket)
    expected_str = "AGENT_RECEIVED_OK"
    if ret_str[:len(expected_str)] != expected_str:
      ERROR("Expect AGENT_RECEIVED_OK, but got %s" % ret_str)
      self.client_socket.close()
      return False

    DEBUG("Waiting for final launching result")
    ret_str = recv_data(self.client_socket)
    expected_str = "LAUNCH_AGENT_OK"
    if ret_str[:len(expected_str)] != expected_str:
      ERROR("Expect LAUNCH_AGENT_OK, but got %s" % ret_str)
      self.client_socket.close()
      return False

    DEBUG("Successfully upgraded test agent.")
    self.client_socket.close()
    return True

class GOSTaskConnection(object):
  """Helper class to handle task connection between test scripts and
     test agent running inside guest os.

  Sample Usage:
    util = GOSTaskConnection(vm_ip)
  """
  VM_PORT = 2017
  PACKET_LIMIT = 256 * 1024 * 1024 * 1024

  TASK_STATUS_INIT = 0
  TASK_STATUS_RUNNING = 1
  TASK_STATUS_DONE = 2

  _STATUS_TO_NAME = {
    TASK_STATUS_INIT: "INIT",
    TASK_STATUS_RUNNING: "RUNNING",
    TASK_STATUS_DONE: "DONE",
  }

  def __init__(self, vm_ip):
    """Instance initiator

    Args:
      vm_ip (str): String of vm ip address

    Returns:
      None: No returns
    """
    self.vm_ip = vm_ip
    self.task_str = ""
    self.task_args = ""
    self.data = ""
    DEBUG("Connect to test agent on VM at %s:%d" % (self.vm_ip, self.VM_PORT))
    self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.client_socket.connect((self.vm_ip, self.VM_PORT))

  @staticmethod
  def task_status_to_name(status_value):
    """
    Obtain the name of the given status value.

    Args:
      status_value(int): Gos task status code.

    Returns:
      str: Name of the given status.
    """
    try:
      return GOSTaskConnection._STATUS_TO_NAME[status_value]
    except KeyError:
      return "Unknown(%s)" % status_value

  def start_task(self, task_str, task_args="", async=False, handsoff=False,
                 payload=None):
    """Start a task remotely in guest OS.

    Args:
      task_str (str): string of what task to start
      task_args (str): additional args for task_str
      async (boolean): Run task async or sync
      handsoff (boolean): If async is true, run task in handsoff mode
      payload (str): Additional data to send along task

    Returns:
      int: The error code of task execution result in guest OS
           0 means success
    """
    self.task_str = task_str
    self.task_args = task_args
    cmd = {"task_type": "start_task",
           "task_str": task_str,
           "async": async,
           "handsoff": handsoff,
           "task_args": task_args
          }
    cmd_str = json.dumps(cmd)
    DEBUG("start_task, json=%s" % cmd_str)
    self._send_data(cmd_str, payload=payload)
    result = self._recv_data()
    return int(result)

  def query_running_status(self, handsoff_task_id=None):
    """Query the task running status

    Args:
      handsoff_task_id (int): If provided, function is querying handsoff task
                              with this given id

    Returns:
      int: 0 - Task is not running yet
           1 - Task is running
           2 - Task run completed
    """
    cmd = {"task_type": "query_running_status"}
    if handsoff_task_id is not None:
      cmd["handsoff"] = True
      cmd["task_id"] = handsoff_task_id
    cmd_str = json.dumps(cmd)
    DEBUG("query_running_status, json=%s" % cmd_str)
    self._send_data(cmd_str)
    result = self._recv_data()
    return int(result)

  def query_running_time(self, handsoff_task_id=None):
    """Query the task running time in seconds

    Args:
      handsoff_task_id (int): If provided, function is querying handsoff task
                              with this given id

    Returns:
      int: How many seconds the task had already run
    """
    cmd = {"task_type": "query_running_time"}
    if handsoff_task_id is not None:
      cmd["handsoff"] = True
      cmd["task_id"] = handsoff_task_id
    cmd_str = json.dumps(cmd)
    DEBUG("query_running_time, json=%s" % cmd_str)
    self._send_data(cmd_str)
    result = self._recv_data()
    return int(result)

  def query_result_status(self, handsoff_task_id=None):
    """Query the task result status code. If task was running synchronously
       This is same as the return value of kicking off the task.

    Args:
      handsoff_task_id (int): If provided, function is querying handsoff task
                              with this given id

    Returns:
      int: 0 - Task completed successfully
           non 0 - Task failed, the value indicated the error
    """
    cmd = {"task_type":"query_result_status"}
    if handsoff_task_id is not None:
      cmd["handsoff"] = True
      cmd["task_id"] = handsoff_task_id
    cmd_str = json.dumps(cmd)
    DEBUG("query_result_status, json=%s" % cmd_str)
    self._send_data(cmd_str)
    result = self._recv_data()
    return int(result)

  def query_result_stdout(self, handsoff_task_id=None):
    """Query the task result stdout.

    Args:
      handsoff_task_id (int): If provided, function is querying handsoff task
                              with this given id

    Returns:
      str: The remote task standard output
    """
    cmd = {"task_type": "query_result_stdout"}
    if handsoff_task_id is not None:
      cmd["handsoff"] = True
      cmd["task_id"] = handsoff_task_id
    cmd_str = json.dumps(cmd)
    DEBUG("query_result_stdout, json=%s" % cmd_str)
    self._send_data(cmd_str)
    stdout = self._recv_data()
    return stdout

  def query_result_stderr(self, handsoff_task_id=None):
    """Query the task result stderr.

    Args:
      handsoff_task_id (int): If provided, function is querying handsoff task
                              with this given id

    Returns:
      str: The remote task standard error message
    """
    cmd = {"task_type": "query_result_stderr"}
    if handsoff_task_id is not None:
      cmd["handsoff"] = True
      cmd["task_id"] = handsoff_task_id
    cmd_str = json.dumps(cmd)
    DEBUG("query_result_stderr, json=%s" % cmd_str)
    self._send_data(cmd_str)
    stderr = self._recv_data()
    return stderr

  def query_additional_data(self, handsoff_task_id=None):
    """Query additional data of the task.

    Args:
      handsoff_task_id (int): If provided, function is querying handsoff task
                              with this given id

    Returns:
      str: The additional data associated with the task completion.
    """
    cmd = {"task_type": "query_additional_data"}
    if handsoff_task_id is not None:
      cmd["handsoff"] = True
      cmd["task_id"] = handsoff_task_id
    cmd_str = json.dumps(cmd)
    DEBUG("query_additional_data, json=%s" % cmd_str)
    self._send_data(cmd_str)
    data = self._recv_data()
    return data

  def is_closed(self):
    """Check if the task connection is closed.

    Returns:
      boolean: True if connection closed, False otherwise
    """
    return self.client_socket is None

  def close_connection(self):
    """Close the socket connection. No further action to be done after this
       call.

    Returns:
      None
    """
    self.client_socket.close()
    self.client_socket = None

  def _send_data(self, data_str, payload=None):
    """Send data with a very simple protocol

    Args:
      data_str (str): data to send
      payload (str): additional data to send

    Returns:
      None: No returns
    """
    data_str = binascii.hexlify(data_str)
    if payload is not None:
      payload = binascii.hexlify(payload)
    data_len = len(data_str)
    payload_len = 0 if payload is None else len(payload)
    assert data_len != 0, "Try to send empty string shouldn't happen."
    if data_len > self.PACKET_LIMIT:
      data_len = self.PACKET_LIMIT
      data_str = data_str[:data_len]
    if payload_len > self.PACKET_LIMIT:
      payload_len = self.PACKET_LIMIT
      payload = payload[:payload_len]
    header = "%12d%12d" % (data_len, payload_len)
    self.client_socket.send(header)
    self.client_socket.send(data_str)
    if payload_len > 0:
      self.client_socket.send(payload)

  def _recv_data(self):
    """Receive data with a very simple protocol

    Returns:
      str: Data received from socket
    """
    header = self.client_socket.recv(24)
    data = ["", ""]
    lens = [int(header[:12]), int(header[12:])]
    # Receiving data blocks
    for ii in range(2):
      total = lens[ii]
      n_received = 0
      while n_received < total:
        remaining = total - n_received
        buf_len = min(remaining, 4096)
        data[ii] += self.client_socket.recv(buf_len)
        n_received = len(data[ii])
    if data[1]:
      self.data = binascii.unhexlify(data[1])
    return binascii.unhexlify(data[0])

class AcroGOSUtil(object):
  """Helper class to handle guest os related tasks.

  Sample Usage:
    util = AcroGOSUtil(vm_ip)
  """

  def __init__(self, vm_ip):
    """Instance initiator

    Args:
      vm_ip (str): String of vm ip address

    Returns:
      None: No returns
    """
    self.vm_ip = vm_ip

  def upgrade_test_agent(self, new_agent):
    """Upgrade the test agent in guest with new_agent.

    Note:
      This call will kill the current running agent in guest, and launch
      the new uploaded agent. So, it should be the first to call after
      guest os up.

    Args:
      new_agent (str): The new agent to be upgraded to guest os. It could be a
                       local file with absolute or relative path, or a url with
                       http access.

    Returns:
      boolean: True if success, False otherwise
    """
    gau = GOSAgentUpgrade(self.vm_ip)

    if new_agent[:7] == "http://":
      return gau.upgrade_agent(from_url=new_agent)

    return gau.upgrade_agent(from_local_file=new_agent)

  def get_guest_os_info(self):
    """Get the basic guest os information. The current implementation will
       return a dict like this:
       {
         "system": "Linux",
         "machine": "x86_64",
         "platform": "Linux-4.8.0-22-generic-x86_64-with-Ubuntu-16.10-yakkety",
         "version": "#24-Ubuntu SMP Sat Oct 8 09:15:00 UTC 2016",
         "memory": "3927MB",
         "num_cpu": "4",
         "processor": "x86_64"
       }

    Note:
      This function must be called when guest os is running

    Returns:
      dict: described above, None if error happens
    """
    guest_os_info = None
    task_conn = GOSTaskConnection(self.vm_ip)
    result = task_conn.start_task("GET_OS_STATS")
    DEBUG("Get guest os info result: %d" % result)
    if result == 0:
      stdout = task_conn.query_result_stdout()
      guest_os_info = json.loads(stdout)
    else:
      stderr = task_conn.query_result_stderr()
      DEBUG("stderr: %d" % stderr)
    task_conn.close_connection()
    return guest_os_info

  def get_scsi_disk_dev_file(self, device_index):
    """Get the SCSI disk device file presented by guest OS in VM
       For example, a SCSI disk at scsi.1 may have device file /dev/sdb in
       CentOS and Ubuntu

    Note:
      This function must be called when guest os is running

    Args:
      device_index (int): the scsi device index. This is returned from
                          add_boot_disk() and add_empty_disk()

    Returns:
      str: the disk device file
    """
    task_conn = GOSTaskConnection(self.vm_ip)
    result = task_conn.start_task("GET_SCSI_DEV_FILE",
                                  task_args=str(device_index))
    # Since this is our own testing code, it doesn't make sense to pass an
    # invalid device_index input. Therefore, result != 0 must be wrong
    assert result == 0, "Error getting scsi disk file."
    disk_file = task_conn.query_result_stdout()
    task_conn.close_connection()
    return disk_file

  def get_vg_scsi_disk_dev_file(self, index_tuple):
    """Get the volume group SCSI disk device file presented by guest OS in VM
       For example, a SCSI disk at volume group is in this format
       0:0:1:1
       0:0:1:2

    Note:
      This function must be called when guest os is running

    Args:
      index_tuple (tuple): VG index and disk index of the vg.

    Raises:
      NuTestEntityError: If index tuple is not a type of tuple.
      TypeError: If a parameter is not from the expected type.

    Returns:
      str: the disk device file
    """
    if not isinstance(index_tuple, tuple):
      raise TypeError(
        "Index tuple must be in this format:(vg_index, disk_index)")

    task_conn = GOSTaskConnection(self.vm_ip)
    result = task_conn.start_task("GET_VG_SCSI_DEV_FILE",
                                  task_args=str(index_tuple))
    # Since this is our own testing code, it doesn't make sense to pass an
    # invalid device_index input. Therefore, result != 0 must be wrong
    assert result == 0, "Error getting scsi disk file."
    disk_file = task_conn.query_result_stdout()
    task_conn.close_connection()
    return disk_file

  def run_io_integrity_test_async(self, vdisk_file=None, file_size_gb=None,
                                  time_limit_secs=None):
    """Run IO integrity test asynchronously.

    Note:
      This function must be called when guest os is running

    Args:
      vdisk_file (str): the vDisk to test against, e.g. /dev/sdb
      file_size_gb (int): vdisk file size in GB
      time_limit_secs (int): how many seconds the integrity test run

    Returns:
      object: the task connection for later query
    """
    task_args = self._create_io_test_args(vdisk_file=vdisk_file,
                                          file_size_gb=file_size_gb,
                                          time_limit_secs=time_limit_secs)
    return self._run_task_async("RUN_IO_INTEGRITY", task_args=task_args)

  def run_io_integrity_test_handsoff(self, vdisk_file=None, file_size_gb=None,
                                     time_limit_secs=None):
    """Run IO integrity test handsoff.

    Note:
      This function must be called when guest os is running

    Args:
      vdisk_file (str): the vDisk to test against, e.g. /dev/sdb
      file_size_gb (int): vdisk file size in GB
      time_limit_secs (int): how many seconds the integrity test run

    Returns:
      int: the task id which can be used later to query
    """
    task_args = self._create_io_test_args(vdisk_file=vdisk_file,
                                          file_size_gb=file_size_gb,
                                          time_limit_secs=time_limit_secs)
    return self._run_task_handsoff("RUN_IO_INTEGRITY", task_args=task_args)

  def run_io_integrity_test_sync(self, vdisk_file=None, file_size_gb=None,
                                 time_limit_secs=None):
    """Run IO integrity test synchronously.

    Note:
      This function must be called when guest os is running

    Args:
      vdisk_file (str): the vDisk to test against, e.g. /dev/sdb
      file_size_gb (int): vdisk file size in GB
      time_limit_secs (int): how many seconds the integrity test run

    Returns:
      tuple: (result, stdout, stderr)
    """
    task_args = self._create_io_test_args(vdisk_file=vdisk_file,
                                          file_size_gb=file_size_gb,
                                          time_limit_secs=time_limit_secs)
    return self._run_task_sync("RUN_IO_INTEGRITY", task_args=task_args)

  def wait_task_complete(self, task_conn, timeout, interval=5):
    """Block caller until the task in task_conn complete.

    Note:
      This function must be called against an async task returned from
      run_io_integrity_test_async()

    Args:
      task_conn (object): object returned form run_io_integrity_test_async()
      timeout (int): how many seconds for wait_for_response to timeout
      interval (int): interval to query running status, default: 5 seconds

    Returns:
      the final result
    """
    if task_conn.is_closed():
      DEBUG("Task connection already closed")
      return 0

    wait_for_response(task_conn.query_running_status,
                      task_conn.TASK_STATUS_DONE,
                      timeout=timeout, interval=interval)
    result = task_conn.query_result_status()
    DEBUG("Task exit status = %d" % result)
    stdout = task_conn.query_result_stdout()
    DEBUG("Task stdout = %s" % stdout)
    stderr = task_conn.query_result_stderr()
    DEBUG("Task stderr = %s" % stderr)
    task_conn.close_connection()
    return result

  def wait_handsoff_task_complete(self, task_id, timeout, interval=5):
    """Block caller until the task specified by task_id complete.

    Note:
      This function must be called against an handsoff task returned from
      run_io_integrity_test_handsoff()

    Args:
      task_id (int): task id returned form run_io_integrity_test_handsoff()
      timeout (int): how many seconds for wait_for_response to timeout
      interval (int): interval to query running status, default: 5 seconds

    Returns:
      the final result
    """
    result = -1
    waited_sec = 0
    while waited_sec < timeout:
      status, run_time = self.query_handsoff_task_status(task_id)
      DEBUG("Waiting task, ip=%s, task_id=%d, status=%d, run_time=%d" %\
           (self.vm_ip, task_id, status, run_time))
      if status == GOSTaskConnection.TASK_STATUS_DONE:
        result, stdout, stderr = self.query_handsoff_task_result(task_id)
        DEBUG("Result = %d, stdout=%s, stderr=%s" % (result, stdout, stderr))
        break
      time.sleep(interval)
      waited_sec += interval
    return result

  def run_shell_command_async(self, cmd_str):
    """Run com_str in a guest OS shell asynchronously.
    Note:
      This function must be called when guest os is running.
      It is using python subprocess.Popen to run cmd_str with shell=True. So
      that it accepts multiple shell commands connected with pipe. It is the
      caller's responsibility to make the cmd_str is really supported in
      guest.
      For Linux guest, you may run command like this:
        "ls -l / | grep myfile"
      For Windows guest, you may run command like this:
        "dir C:\\"

    Args:
      cmd_str (str): the command to run in guest.

    Returns:
      object: the task connection for later query
    """
    return self._run_task_async("RUN_COMMAND", task_args=cmd_str)

  def run_shell_command_handsoff(self, cmd_str):
    """Run cmd_str in a guest OS shell with handsoff mode.
    Note:
      See function run_shell_command_async

    Args:
      cmd_str (str): the command to run in guest.

    Returns:
      int: task id for later query
    """
    return self._run_task_handsoff("RUN_COMMAND", task_args=cmd_str)

  def run_shell_command_sync(self, cmd_str):
    """Run cmd_str in a guest OS shell synchronously.
    Note:
      See function run_shell_command_async

    Args:
      cmd_str (str): the command to run in guest.

    Returns:
      tuple: (result, stdout, stderr)
    """
    return self._run_task_sync("RUN_COMMAND", task_args=cmd_str)

  def transfer_file_to_guest(self, source_path, remote_path):
    """Transfer file into guest.

    Note:
      This function must be called when guest is running.

    Args:
      source_path (str): The source path/url of file to be transferred.
      remote_path (str): path in guest where the transferred file saved to.

    Returns:
      boolean: True if success, False otherwise
    """
    try:
      if source_path[:7] == "http://":
        response = urllib2.urlopen(source_path)
        content = response.read()
      else:
        with open(source_path, 'rb') as ff:
          content = ff.read()
    except Exception, e:
      ERROR("Error read source file, %s" % str(e))
      return False

    task_conn = GOSTaskConnection(self.vm_ip)
    result = task_conn.start_task("TRANSFER_FILE_TO_VM", task_args=remote_path,
                                  payload=content)
    task_conn.close_connection()
    return result == 0

  def transfer_file_from_guest(self, local_path, remote_path):
    """Transfer file from guest.

    Note:
      This function must be called when guest is running.

    Args:
      local_path (str): The local file path where the transferred file saved to
      remote_path (str): path in guest where the file transferred from

    Returns:
      boolean: True if success, False otherwise
    """
    data = ""
    task_conn = GOSTaskConnection(self.vm_ip)
    result = task_conn.start_task("TRANSFER_FILE_FROM_VM",
                                  task_args=remote_path)
    DEBUG("Start task result: %d" % result)
    if result != 0:
      stderr = task_conn.query_result_stderr()
      DEBUG("Task stderr = %s" % stderr)
    else:
      data = task_conn.query_additional_data()
      DEBUG("Additional data, len=%d bytes" % len(data))
    task_conn.close_connection()

    if not data:
      return False

    # Save data into file
    try:
      with open(local_path, 'wb') as ff:
        ff.write(data)
    except Exception, e:
      ERROR("Error write file, %s" % str(e))
      return False

    return True

  def run_user_code_async(self, engine, name, code):
    """Run user defined code in guest shell asynchronously

    Note:
      This function must be called when guest os is running.
      It is using python subprocess.Popen to run cmd_str with shell=True.

    Args:
      engine (str): the code interpreter, such as bash, python, etc
      name (str): the executable file name of code
      code (str): the user defined code

    Example:
      Run a user defined python script synchronously:
        run_user_code("python", "mycode.py", "print 'Hello, world.'")
      Run a windows exe file asynchronously:
        code = read from myprog.exe
        run_user_code("", "myprog.exe", code, async=True)

    Returns:
      object: the task connection
    """
    args_dict = {
      "code_engine" : engine,
      "code_name" : name
    }
    task_args = json.dumps(args_dict)
    return self._run_task_async("RUN_USER_CODE", task_args=task_args,
                                payload=code)

  def run_user_code_handsoff(self, engine, name, code):
    """Run user defined code in guest shell in handsoff mode

    Note:
      See run_user_code_async

    Args:
      engine (str): the code interpreter, such as bash, python, etc
      name (str): the executable file name of code
      code (str): the user defined code

    Example:
      See run_user_code_async

    Returns:
      int: task id for later query
    """
    args_dict = {
      "code_engine" : engine,
      "code_name" : name
    }
    task_args = json.dumps(args_dict)
    return self._run_task_handsoff("RUN_USER_CODE", task_args=task_args,
                                   payload=code)

  def run_user_code_sync(self, engine, name, code):
    """Run user defined code in guest shell synchronously

    Note:
      See run_user_code_async

    Args:
      engine (str): the code interpreter, such as bash, python, etc
      name (str): the executable file name of code
      code (str): the user defined code

    Example:
      See run_user_code_async

    Returns:
      tuple: (result, stdout, stderr)
    """
    args_dict = {
      "code_engine" : engine,
      "code_name" : name
    }
    task_args = json.dumps(args_dict)
    return self._run_task_sync("RUN_USER_CODE", task_args=task_args,
                               payload=code)

  def query_handsoff_task_status(self, task_id):
    """Query handsoff task running status

    Args:
      task_id (int): The task id

    Returns:
      tuple: the running status and time passed since begin
    """
    task_conn = GOSTaskConnection(self.vm_ip)
    run_status = task_conn.query_running_status(handsoff_task_id=task_id)
    run_time = task_conn.query_running_time(handsoff_task_id=task_id)
    task_conn.close_connection()
    return (run_status, run_time)

  def query_handsoff_task_result(self, task_id):
    """Query handsoff task result

    Args:
      task_id (int): The task id

    Returns:
      tuple: the task result (status, stdout, stderr)
    """
    task_conn = GOSTaskConnection(self.vm_ip)
    status = task_conn.query_result_status(handsoff_task_id=task_id)
    stdout = task_conn.query_result_stdout(handsoff_task_id=task_id)
    stderr = task_conn.query_result_stderr(handsoff_task_id=task_id)
    task_conn.close_connection()
    return (status, stdout, stderr)

  def _create_io_test_args(self, vdisk_file=None, file_size_gb=None,
                           time_limit_secs=None):
    """Create test arg string for IO integrity test.

    Args:
      vdisk_file (str): the vDisk to test against, e.g. /dev/sdb
      file_size_gb (int): vdisk file size in GB
      time_limit_secs (int): how many seconds the integrity test run

    Returns:
      str: string dump of a dict with all the provided args.
    """
    task_args_dict = {}
    if vdisk_file:
      task_args_dict["vdisk_file"] = vdisk_file
    if file_size_gb:
      task_args_dict["file_size_gb"] = file_size_gb
    if time_limit_secs:
      task_args_dict["time_limit_secs"] = time_limit_secs
    return json.dumps(task_args_dict)

  def _run_task_async(self, task_str, task_args="", payload=None):
    """Run task with asynchronous mode.

    Args:
      task_str (str): The task string
      task_args (str): task parameters
      payload (str): Additional data to send along task

    Returns:
      object: the task connection for later query
    """
    task_conn = GOSTaskConnection(self.vm_ip)
    task_conn.start_task(task_str, task_args=task_args, async=True,
                         payload=payload)
    return task_conn

  def _run_task_handsoff(self, task_str, task_args="", payload=None):
    """Run task with handsoff mode.

    Args:
      task_str (str): The task string
      task_args (str): task parameters
      payload (str): Additional data to send along task

    Returns:
      int: the task id which for later query
    """
    task_conn = GOSTaskConnection(self.vm_ip)
    task_id = task_conn.start_task(task_str, task_args=task_args, async=True,
                                   handsoff=True, payload=payload)
    task_conn.close_connection()
    return task_id

  def _run_task_sync(self, task_str, task_args="", payload=None):
    """Run task with handsoff mode.

    Args:
      task_str (str): The task string
      task_args (str): task parameters
      payload (str): Additional data to send along task

    Returns:
      tuple: (result, stdout, stderr)
    """
    task_conn = GOSTaskConnection(self.vm_ip)
    result = task_conn.start_task(task_str, task_args=task_args, async=False,
                                  payload=payload)
    DEBUG("Task result = %d" % result)
    stdout = task_conn.query_result_stdout()
    DEBUG("Task stdout = %s" % stdout)
    stderr = task_conn.query_result_stderr()
    DEBUG("Task stderr = %s" % stderr)
    task_conn.close_connection()
    return (result, stdout, stderr)
