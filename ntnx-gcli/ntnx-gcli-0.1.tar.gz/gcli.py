import click

from click_shell import shell
from gcli_util import GcliUtil
from gcli_context import GcliContext
from gcli_logging import log_level_set, log_level_get

context = GcliContext()
context.init_context()

INTRO_MSG = 'Welcome to the Guest OS CLI. Type help or ? to list commands.\n'
PROMPT_MSG = "\033[92m(Guest_OS_cli) \033[0m"

@shell(prompt=PROMPT_MSG, intro=INTRO_MSG)
def cli():
  pass

@cli.command()
@click.option('--log_level', required=True, prompt=True, type=click.INT)
def set_log_level(log_level):
  """Set the overall log level."""
  old = log_level_get()
  log_level_set(log_level)
  new = log_level_get()
  click.echo("Changed log level from %d to %d" % (old, new)) 

@cli.command()
@click.option('--vm_ip', required=True, prompt=True)
@click.option('--path', required=True, nargs=1, type=click.Path(),
                prompt=True)
def upgrade_test_agent(vm_ip, path):
  """Upgrade test agent."""
  gcli_util = GcliUtil(context=context, vm_ip=vm_ip)
  gcli_util.upgrade_guest_agent(path)

@cli.command()
@click.option('--vm_ip', required=True, prompt=True)
def get_gos_info(vm_ip):
  """Get guest os information."""
  gcli_util = GcliUtil(context=context, vm_ip=vm_ip)
  gcli_util.get_gos_info()

@cli.command()
@click.option('--vm_ip', required=True, prompt=True)
@click.option('--device_index', required=True, prompt=True, type=click.INT)
def get_gos_scsi_disk_dev(vm_ip, device_index):
  """Get guest os scsi disk device file."""
  gcli_util = GcliUtil(context=context, vm_ip=vm_ip)
  gcli_util.get_scsi_disk_dev_file(device_index)

@cli.command()
@click.option('--vm_ip', required=True, prompt=True)
@click.option('--vg_index', required=True, prompt=True, type=click.INT)
@click.option('--disk_index', required=True, prompt=True, type=click.INT)
def get_gos_vg_scsi_disk_dev(vm_ip, vg_index, disk_index):
  """Get the volume group SCSI disk device file presented by guest OS."""
  gcli_util = GcliUtil(context=context, vm_ip=vm_ip)
  gcli_util.get_vg_scsi_disk_dev_file((vg_index, disk_index))

@cli.command()
@click.option('--vm_ip', required=True, prompt=True)
@click.option('--src_path', required=True, nargs=1, type=click.Path(),
                prompt=True)
@click.option('--remote_path', required=True, nargs=1, type=click.Path(),
                prompt=True)
def transfer_file_to_guest(vm_ip, src_path, remote_path):
  """Transfter file to guest"""
  gcli_util = GcliUtil(context=context, vm_ip=vm_ip)
  gcli_util.transfer_file_to_guest(src_path, remote_path)

@cli.command()
@click.option('--vm_ip', required=True, prompt=True)
@click.option('--local_path', required=True, nargs=1, type=click.Path(),
              prompt=True)
@click.option('--remote_path', required=True, nargs=1, type=click.Path(),
              prompt=True)
def transfer_file_from_guest(vm_ip, local_path, remote_path):
  """Transfter file from guest"""
  gcli_util = GcliUtil(context=context, vm_ip=vm_ip)
  gcli_util.transfer_file_from_guest(local_path, remote_path)

@cli.command()
@click.option('--vm_ip', required=True, prompt=True)
@click.option('--execution_mode', required=True, prompt=True)
@click.option('--cmd', required=True, prompt=True)
def run_shell_command(vm_ip, execution_mode, cmd):
  """Runs a shell command inside UVM."""
  gcli_util = GcliUtil(context=context, vm_ip=vm_ip)
  gcli_util.run_commands(execution_mode, cmd)

@cli.command()
@click.option('--vm_ip', required=True, prompt=True)
@click.option('--vdisk_file', required=True, nargs=1, type=click.Path(),
                prompt=True)
@click.option('--file_size_gb', required=True, prompt=True, type=click.INT)
@click.option('--time_limit_secs', required=True, prompt=True, type=click.INT)
@click.option('--execution_mode', required=True, prompt=True)
def run_io_integrity_test(vm_ip, vdisk_file, file_size_gb,
                          time_limit_secs, execution_mode):
  """Run io integrity test in guest"""
  gcli_util = GcliUtil(context=context, vm_ip=vm_ip)
  gcli_util.run_io_integrity_test(vdisk_file,
                                  file_size_gb,
                                  time_limit_secs,
                                  execution_mode)

@cli.command()
@click.option('--vm_ip', required=True, prompt=True)
@click.option('--engine', required=True, prompt=True)
@click.option('--name', required=True, prompt=True)
@click.option('--code', required=True, nargs=1, type=click.Path(),
                prompt=True)
@click.option('--execution_mode', required=True, prompt=True)
def run_user_code(vm_ip, engine, name, code, execution_mode):
  """Runs user code in VM."""
  execution_mode = execution_mode.replace('execution_mode=', '')
  gcli_util = GcliUtil(context=context, vm_ip=vm_ip)
  gcli_util.run_user_code(engine, name, code, execution_mode)

@cli.command()
@click.option('--vm_ip', required=True, prompt=True)
@click.option('--task_id', required=True, prompt=True, type=click.INT)
def query_handsoff_task(vm_ip, task_id):
  """Query handsoff task running status and result if completed"""
  gcli_util = GcliUtil(context=context, vm_ip=vm_ip)
  gcli_util.query_handsoff_task(task_id)

@cli.command()
@click.option('--task_id', required=True, prompt=True, type=click.INT)
def query_async_task(task_id):
  """Query handsoff task running status and result if completed"""
  gcli_util = GcliUtil(context=context, vm_ip="dummy")
  gcli_util.query_async_task(task_id)

############################################################
# Keep these commands at bottom
############################################################
@cli.command()
@click.option('--clusters', required=True, prompt=True)
@click.option('--pattern', required=True, prompt=True)
def list_uvm(clusters, pattern):
  """List all the UVMs on given clusters with vm name match the given pattern."""
  context.list_uvms(clusters, pattern)
  click.echo("Success")

@cli.command()
def show_buffer():
  """List UVMs in buffer."""
  context.show_buffer()
  click.echo("Success")

@cli.command()
def set_uvms_from_buffer():
  """Set UVM list from buffer."""
  context.set_uvms_from_buffer()
  click.echo("Success")

@cli.command()
@click.option('--vm_ips', required=True, prompt=True)
def set_uvms(vm_ips):
  """Set UVM list from manual input."""
  context.set_uvms(vm_ips)
  click.echo("Success")

@cli.command()
def show_uvms():
  """List UVMs in list."""
  context.show_uvms()

@cli.command()
def show_tasks():
  """List tasks."""
  context.show_tasks()

@cli.command()
def save_context():
  """Save running context to file."""
  context.save_context()
  click.echo("Success")

if __name__ == "__main__":
  cli()
