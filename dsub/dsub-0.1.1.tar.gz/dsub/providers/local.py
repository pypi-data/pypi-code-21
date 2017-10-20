# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Local Docker provider.

# Local provider

The intent of the local backend provider is to enable rapid testing of user task
scripts and easy extension to running at scale on a compute cluster or a cloud
environment. The local provider should simulate the runtime environment such
that going from local development to scaled-up execution only involves changing
`dsub` command-line parameters.

The local provider is not intended for submitting large numbers of concurrent
tasks to a local queue for execution.

## Execution environment

The local provider runs `dsub` tasks locally, in a Docker container.

Input files are staged on your local machine at
${TMPDIR}/dsub-local/job-id/task-id/input_mnt/.

Output files are copied on your local machine at
${TMPDIR}/dsub-local/job-id/task-id/output_mnt/.

Task status files are staged to ${TMPDIR}/tmp/dsub-local/job-id/task-id/.
The task status files include logs and scripts to drive the task.

task-id is the task index, or "task" for a job that didn't specify a list
of tasks.

Thus using the local runner requires:

* Docker Engine to be installed.
* Sufficient disk space required by submitted tasks.
* Sufficient memory required by submitted tasks.

Note that the local runner supports the `--tasks` parameter. All tasks
submitted will run concurrently.
"""

from collections import namedtuple
from datetime import datetime
from datetime import timedelta
import os
import signal
import string
import subprocess
import tempfile
import textwrap
import time
from . import base
from .._dsub_version import DSUB_VERSION
from ..lib import dsub_util
from ..lib import param_util
from ..lib import providers_util
import yaml

# The local runner allocates space on the host under
#   ${TMPDIR}/dsub-local/
#
# For each task, the on-host directory is
#  ${TMPDIR}/dsub-local/<job-id>/<task-id>
#
# Within the task directory, we create:
#    data: Mount point for user's data
#    docker.env: File of environment variables passed to the Docker container
#    runner.sh: Local runner script
#    status.txt: File for the runner script to record task status (RUNNING,
#    FAILURE, etc.)
#    log.txt: File for the runner script to write log messages
#    task.pid: Process ID file for task runner
#
# From task directory, the data directory is made available to the Docker
# container as /mnt/data. Inside the data directory, the local provider sets up:
#
#   input: files localized from object storage
#   output: files to de-localize to object storage
#
#   script: any code that dsub writes (like the user script)
#   tmp: set TMPDIR in the environment to point here
#
#   workingdir: A workspace directory for user code.
#               This is also the explicit working directory set before the
#               user script runs.

_PROVIDER_NAME = 'local'

DATA_SUBDIR = 'data'

SCRIPT_DIR = 'script'
WORKING_DIR = 'workingdir'

DATA_MOUNT_POINT = '/mnt/data'

# Set file provider whitelist.
_SUPPORTED_FILE_PROVIDERS = frozenset([param_util.P_GCS, param_util.P_LOCAL])
_SUPPORTED_LOGGING_PROVIDERS = _SUPPORTED_FILE_PROVIDERS
_SUPPORTED_INPUT_PROVIDERS = _SUPPORTED_FILE_PROVIDERS
_SUPPORTED_OUTPUT_PROVIDERS = _SUPPORTED_FILE_PROVIDERS


def _format_task_name(job_id, task_id):
  """Create a task name from a job-id and a task-id.

  Task names are used internally by dsub as well as by the docker task runner.
  The name is formatted as either "<job-id>.<task-id>" or jobs with multple
  tasks, or just "<job-id>" for jobs with a single task. Task names follow
  formatting conventions allowing them to be safely used as a docker name.

  Args:
    job_id: (str) the job ID.
    task_id: (str) the task ID.

  Returns:
    a task name string.
  """
  if task_id is None:
    docker_name = job_id
  else:
    docker_name = '%s.%s' % (job_id, task_id)

  # Docker container names must match: [a-zA-Z0-9][a-zA-Z0-9_.-]
  # So 1) prefix it with "dsub-" and 2) change all invalid characters to "-".
  return 'dsub-{}'.format(_convert_suffix_to_docker_chars(docker_name))


def _convert_suffix_to_docker_chars(suffix):
  """Rewrite string so that all characters are valid in a docker name suffix."""
  # Docker container names must match: [a-zA-Z0-9][a-zA-Z0-9_.-]
  accepted_characters = string.ascii_letters + string.digits + '_.-'

  def label_char_transform(char):
    if char in accepted_characters:
      return char
    return '-'

  return ''.join(label_char_transform(c) for c in suffix)


class LocalJobProvider(base.JobProvider):
  """Docker jobs running locally (i.e. on the caller's computer)."""

  def __init__(self):
    self._operations = []

  def prepare_job_metadata(self, script, job_name, user_id):
    job_name_value = job_name or os.path.basename(script)
    if user_id != dsub_util.get_os_user():
      raise ValueError('If specified, the local provider\'s "--user" flag must '
                       'match the current logged-in user.')
    return {
        'job-id': self._make_job_id(job_name_value, user_id),
        'job-name': job_name_value,
        'user-id': user_id,
        'dsub-version': DSUB_VERSION,
    }

  def submit_job(self, job_resources, job_metadata, job_data, all_task_data):
    create_time = datetime.now()

    # Validate inputs.
    param_util.validate_submit_args_or_fail(
        job_resources,
        job_data,
        all_task_data,
        provider_name=_PROVIDER_NAME,
        input_providers=_SUPPORTED_FILE_PROVIDERS,
        output_providers=_SUPPORTED_FILE_PROVIDERS,
        logging_providers=_SUPPORTED_LOGGING_PROVIDERS)

    # Launch tasks!
    launched_tasks = []
    for task_data in all_task_data:
      task_metadata = providers_util.get_task_metadata(job_metadata,
                                                       task_data.get('task-id'))

      # Format the logging path and set it into the task metadata
      task_metadata['logging'] = providers_util.format_logging_uri(
          job_resources.logging.uri, task_metadata)

      # Set up directories
      task_dir = self._task_directory(
          task_metadata.get('job-id'), task_metadata.get('task-id'))
      self._mkdir_outputs(task_dir, job_data['outputs'] + task_data['outputs'])

      script = task_metadata.get('script')
      self._stage_script(task_dir, script.name, script.value)

      # Start the task
      env = self._make_environment(job_data['inputs'] + task_data['inputs'],
                                   job_data['outputs'] + task_data['outputs'])
      self._write_task_metadata(task_metadata, job_data, task_data, create_time)
      self._run_docker_via_script(task_dir, env, job_resources, task_metadata,
                                  job_data, task_data)
      if task_metadata.get('task-id') is not None:
        launched_tasks.append(str(task_metadata.get('task-id')))

    return {
        'job-id': job_metadata.get('job-id'),
        'user-id': job_metadata.get('user-id'),
        'task-id': launched_tasks
    }

  def _run_docker_via_script(self, task_dir, env, job_resources, task_metadata,
                             job_data, task_data):
    script_header = textwrap.dedent("""\
      #!/bin/bash

      # dsub-generated script to start the local Docker container
      # and keep a running status.

      set -o nounset

      readonly VOLUMES=({volumes})
      readonly NAME='{name}'
      readonly IMAGE='{image}'
      # Absolute path to the user's script file inside Docker.
      readonly SCRIPT_FILE='{script}'
      # Mount point for the volume on Docker.
      readonly DATA_MOUNT_POINT='{data_mount_point}'
      # Absolute path to the data.
      readonly DATA_DIR='{data_dir}'
      # Absolute path to the CWD inside Docker.
      readonly WORKING_DIR='{workingdir}'
      # Absolute path to the env config file
      readonly ENV_FILE='{env_file}'
      # Date format used in the logging message prefix.
      readonly DATE_FORMAT='{date_format}'
      # Absolute path to this script's directory.
      readonly TASK_DIR="$(dirname $0)"
      # User to run as (by default)
      readonly MY_UID='{uid}'
      # Set environment variables for recursive input directories
      {export_input_dirs}
      # Set environment variables for recursive output directories
      {export_output_dirs}

      recursive_localize_data() {{
        true # ensure body is not empty, to avoid error.
        {recursive_localize_command}
      }}

      localize_data() {{
        {localize_command}
        recursive_localize_data
      }}

      recursive_delocalize_data() {{
        true # ensure body is not empty, to avoid error.
        {recursive_delocalize_command}
      }}

      delocalize_data() {{
        {delocalize_command}
        recursive_delocalize_data
      }}

      delocalize_logs() {{
        {delocalize_logs_command}

        delocalize_logs_function "${{cp_cmd}}" "${{prefix}}"
      }}
      """)
    script_body = textwrap.dedent("""\
      # Delete local files
      function cleanup() {
        local rm_data_dir="${1:-true}"

        log_info "Copying the logs before cleanup"
        delocalize_logs

        # Clean up files staged from outside Docker
        if [[ "${rm_data_dir}" == "true" ]]; then
          echo "cleaning up ${DATA_DIR}"

          # Clean up files written from inside Docker
          2>&1 docker run \\
            --name "${NAME}-cleanup" \\
            --workdir "${DATA_MOUNT_POINT}/${WORKING_DIR}" \\
            "${VOLUMES[@]}" \\
            --env-file "${ENV_FILE}" \\
            "${IMAGE}" \\
            rm -rf "${DATA_MOUNT_POINT}/*" | tee -a "${TASK_DIR}/log.txt"

          rm -rf "${DATA_DIR}" || echo "sorry, unable to delete ${DATA_DIR}."
        fi
      }
      readonly -f cleanup

      function delocalize_logs_function() {
        local cp_cmd="${1}"
        local prefix="${2}"

        if [[ -f "${TASK_DIR}/stdout.txt" ]]; then
          ${cp_cmd} "${TASK_DIR}/stdout.txt" "${prefix}-stdout.log"
        fi
        if [[ -f "${TASK_DIR}/stderr.txt" ]]; then
          ${cp_cmd} "${TASK_DIR}/stderr.txt" "${prefix}-stderr.log"
        fi
        if [[ -f "${TASK_DIR}/log.txt" ]]; then
          ${cp_cmd} "${TASK_DIR}/log.txt" "${prefix}.log"
        fi
      }
      readonly -f delocalize_logs_function

      function get_datestamp() {
        date "${DATE_FORMAT}"
      }
      readonly -f get_datestamp

      function write_status() {
        local status="${1}"
        echo "${status}" > "${TASK_DIR}/status.txt"
        case "${status}" in
          SUCCESS|FAILURE|CANCELED)
            # Record the finish time (with microseconds)
            # Prepend "10#" so numbers like 0999... are not treated as octal
            local nanos=$(echo "10#"$(date "+%N"))
            echo $(date "+%Y-%m-%d %H:%M:%S").$((nanos/1000)) \
              > "${TASK_DIR}/end-time.txt"
            ;;
          RUNNING)
            ;;
          *)
            echo 2>&1 "Unexpected status: ${status}"
            exit 1
            ;;
        esac
      }
      readonly -f write_status

      function log_info() {
        echo "$(get_datestamp) I: $@" | tee -a "${TASK_DIR}/log.txt"
      }
      readonly -f log_info

      function log_error() {
        echo "$(get_datestamp) E: $@" | tee -a "${TASK_DIR}/log.txt"
      }
      readonly -f log_error

      # Correctly log failures and nounset exits
      function error() {
        local parent_lineno="$1"
        local code="$2"
        local message="${3:-Error}"

        # Disable further traps
        trap EXIT
        trap ERR

        if [[ $code != "0" ]]; then
          write_status "FAILURE"
          log_error "${message} on or near line ${parent_lineno}; exiting with status ${code}"
        fi
        cleanup "false"
        exit "${code}"
      }
      readonly -f error

      function fetch_image() {
        local image="$1"

        for ((attempt=0; attempt < 3; attempt++)); do
          log_info "Using gcloud to fetch ${image}."
          if gcloud docker -- pull "${image}"; then
            return
          fi
          log_info "Sleeping 30s before the next attempt."
          sleep 30s
        done

        log_error "FAILED to fetch ${image}"
        exit 1
      }
      readonly -f fetch_image

      function fetch_image_if_necessary() {
        local image="$1"

        # Remove everything from the first / on
        local prefix="${image%%/*}"

        # Check that the prefix is gcr.io or <location>.gcr.io
        if [[ "${prefix}" == "gcr.io" ]] ||
           [[ "${prefix}" == *.gcr.io ]]; then
          fetch_image "${image}"
        fi
      }
      readonly -f fetch_image_if_necessary

      function get_docker_user() {
        # Get the userid and groupid the Docker image is set to run as.
        docker run \\
          --name "${NAME}-get-docker-userid" \\
          "${IMAGE}" \\
          bash -c 'echo "$(id -u):$(id -g)"' 2>> "${TASK_DIR}/stderr.txt"
      }
      readonly -f get_docker_user

      function docker_recursive_chown() {
        # Calls, in Docker: chown -R $1 $2
        local usergroup="$1"
        local docker_directory="$2"
        # Not specifying a name because Docker refuses to run if two containers
        # have the same name, and it keeps them around for a little bit
        # after they return.
        docker run \\
          --user 0 \\
          "${VOLUMES[@]}" \\
          "${IMAGE}" \\
          chown -R "${usergroup}" "${docker_directory}" \\
          >> "${TASK_DIR}/stdout.txt" 2>> "${TASK_DIR}/stderr.txt"
      }
      readonly -f docker_recursive_chown

      function exit_if_canceled() {
        if [[ -f die ]]; then
          log_info "Job is canceled, stopping Docker container ${NAME}."
          docker stop "${NAME}"
          write_status "CANCELED"
          log_info "Delocalize logs and cleanup"
          cleanup "false"
          trap EXIT
          log_info "Canceled, exiting."
          exit 1
        fi
      }
      readonly -f exit_if_canceled


      # This will trigger whenever a command returns an error code
      # (exactly like set -e)
      trap 'error ${LINENO} $? Error' ERR

      # This will trigger on all other exits. We disable it before normal
      # exit so we know if it fires it means there's a problem.
      trap 'error ${LINENO} $? "Exit (undefined variable or kill?)"' EXIT

      # Make sure that ERR traps are inherited by shell functions
      set -o errtrace

      # Beginning main execution

      # Copy inputs
      cd "${TASK_DIR}"
      write_status "RUNNING"
      log_info "Localizing inputs."
      localize_data

      # Handle gcr.io images
      fetch_image_if_necessary "${IMAGE}"

      log_info "Checking image userid."
      DOCKER_USERGROUP="$(get_docker_user)"
      if [[ "${DOCKER_USERGROUP}" != "0:0" ]]; then
        log_info "Ensuring docker user (${DOCKER_USERGROUP} can access ${DATA_MOUNT_POINT}."
        docker_recursive_chown "${DOCKER_USERGROUP}" "${DATA_MOUNT_POINT}"
      fi

      # Begin execution of user script
      FAILURE_MESSAGE=''
      # Disable ERR trap, we want to copy the logs even if Docker fails.
      trap ERR
      log_info "Running Docker image."
      docker run \\
         --detach \\
         --name "${NAME}" \\
         --workdir "${DATA_MOUNT_POINT}/${WORKING_DIR}" \\
         "${VOLUMES[@]}" \\
         --env-file "${ENV_FILE}" \\
         "${IMAGE}" \\
         "${SCRIPT_FILE}"

      # Start a log writer in the background
      docker logs --follow "${NAME}" \
        >> "${TASK_DIR}/stdout.txt" 2>> "${TASK_DIR}/stderr.txt" &

      # Wait for completion
      DOCKER_EXITCODE=$(docker wait "${NAME}")
      log_info "Docker exit code ${DOCKER_EXITCODE}."
      if [[ "${DOCKER_EXITCODE}" != 0 ]]; then
        FAILURE_MESSAGE="Docker exit code ${DOCKER_EXITCODE} (check stderr)."
      fi

      # If we were canceled during execution, be sure to process as such
      exit_if_canceled

      # Re-enable trap
      trap 'error ${LINENO} $? Error' ERR

      # Prepare data for delocalization.
      HOST_USERGROUP="$(id -u):$(id -g)"
      log_info "Ensure host user (${HOST_USERGROUP}) owns Docker-written data"
      # Disable ERR trap, we want to copy the logs even if Docker fails.
      trap ERR
      docker_recursive_chown "${HOST_USERGROUP}" "${DATA_MOUNT_POINT}"
      DOCKER_EXITCODE_2=$?
      # Re-enable trap
      trap 'error ${LINENO} $? Error' ERR
      if [[ "${DOCKER_EXITCODE_2}" != 0 ]]; then
        # Ensure we report failure at the end of the execution
        FAILURE_MESSAGE="chown failed, Docker returned ${DOCKER_EXITCODE_2}."
        log_error "${FAILURE_MESSAGE}"
      fi

      log_info "Copying outputs."
      delocalize_data

      # Delocalize logs & cleanup
      #
      # Disable further traps (if cleanup fails we don't want to call it
      # recursively)
      trap EXIT
      log_info "Delocalize logs and cleanup."
      cleanup "true"
      if [[ -z "${FAILURE_MESSAGE}" ]]; then
        write_status "SUCCESS"
        log_info "Done"
      else
        write_status "FAILURE"
        # we want this to be the last line in the log, for dstat to work right.
        log_error "${FAILURE_MESSAGE}"
        exit 1
      fi
      """)

    # Build the local runner script
    volumes = ('-v ' + task_dir + '/' + DATA_SUBDIR + '/'
               ':' + DATA_MOUNT_POINT)

    script = script_header.format(
        volumes=volumes,
        name=_format_task_name(
            task_metadata.get('job-id'), task_metadata.get('task-id')),
        image=job_resources.image,
        script=DATA_MOUNT_POINT + '/' + SCRIPT_DIR + '/' +
        task_metadata['script'].name,
        env_file=task_dir + '/' + 'docker.env',
        uid=os.getuid(),
        data_mount_point=DATA_MOUNT_POINT,
        data_dir=task_dir + '/' + DATA_SUBDIR,
        date_format='+%Y-%m-%d %H:%M:%S',
        workingdir=WORKING_DIR,
        export_input_dirs=providers_util.build_recursive_localize_env(
            task_dir, job_data['inputs'] + task_data['inputs']),
        recursive_localize_command=self._localize_inputs_recursive_command(
            task_dir, job_data['inputs'] + task_data['inputs']),
        localize_command=self._localize_inputs_command(
            task_dir, job_data['inputs'] + task_data['inputs']),
        export_output_dirs=providers_util.build_recursive_gcs_delocalize_env(
            task_dir, job_data['outputs'] + task_data['outputs']),
        recursive_delocalize_command=self._delocalize_outputs_recursive_command(
            task_dir, job_data['outputs'] + task_data['outputs']),
        delocalize_command=self._delocalize_outputs_commands(
            task_dir, job_data['outputs'] + task_data['outputs']),
        delocalize_logs_command=self._delocalize_logging_command(
            job_resources.logging.file_provider, task_metadata),
    ) + script_body

    # Write the local runner script
    script_fname = task_dir + '/runner.sh'
    f = open(script_fname, 'wt')
    f.write(script)
    f.close()
    os.chmod(script_fname, 0500)

    # Write the environment variables
    env_vars = env.items() + job_data['envs'] + task_data['envs'] + [
        param_util.EnvParam('DATA_ROOT', DATA_MOUNT_POINT),
        param_util.EnvParam('TMPDIR', DATA_MOUNT_POINT + '/tmp')
    ]
    env_fname = task_dir + '/docker.env'
    with open(env_fname, 'wt') as f:
      for e in env_vars:
        f.write(e[0] + '=' + e[1] + '\n')

    # Execute the local runner script.
    # Redirecting the output to a file ensures that
    # JOBID=$(dsub ...) doesn't block until docker returns.
    runner_log = open(task_dir + '/runner-log.txt', 'wt')
    runner = subprocess.Popen(
        [script_fname], stderr=runner_log, stdout=runner_log)
    pid = runner.pid
    f = open(task_dir + '/task.pid', 'wt')
    f.write(str(pid) + '\n')
    f.close()
    return pid

  def delete_jobs(self,
                  user_list,
                  job_list,
                  task_list,
                  labels,
                  create_time=None):
    # As per the spec, we ignore anything not running.
    tasks = self.lookup_job_tasks(
        status_list=['RUNNING'],
        user_list=user_list,
        job_list=job_list,
        job_name_list=None,
        task_list=task_list,
        labels=labels,
        create_time=create_time)

    canceled = []
    cancel_errors = []
    for task in tasks:
      # Try to cancel it for real.
      # First, tell the runner script to skip delocalization
      task_dir = self._task_directory(
          task.get_field('job-id'),
          task.get_field('task-id'))
      today = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
      with open(os.path.join(task_dir, 'die'), 'wt') as f:
        f.write('Operation canceled at %s\n' % today)

      # Next, kill Docker if it's running.
      docker_name = task.get_docker_name_for_task()

      try:
        subprocess.check_output(['docker', 'kill', docker_name])
      except subprocess.CalledProcessError as cpe:
        cancel_errors += [
            'Unable to cancel %s: docker error %s:\n%s' %
            (docker_name, cpe.returncode, cpe.output)
        ]
        continue

      # The script should have quit in response. If it hasn't, kill it.
      pid = task.get_field('pid', 0)
      if pid <= 0:
        cancel_errors += ['Unable to cancel %s: missing pid.' % docker_name]
        continue
      try:
        os.kill(pid, signal.SIGTERM)
      except OSError as err:
        cancel_errors += [
            'Error while canceling %s: kill(%s) failed (%s).' % (docker_name,
                                                                 pid, str(err))
        ]
      canceled += [task]

      # Mark the job as 'CANCELED' for the benefit of dstat
      today = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
      with open(os.path.join(task_dir, 'status.txt'), 'wt') as f:
        f.write('CANCELED\n')
      with open(os.path.join(task_dir, 'end-time.txt'), 'wt') as f:
        f.write(today)
      msg = 'Operation canceled at %s\n' % today
      with open(os.path.join(task_dir, 'log.txt'), 'a') as f:
        f.write(msg)

    return (canceled, cancel_errors)

  @classmethod
  def _utc_int_to_local_datetime(cls, utc_int):
    """Convert the integer UTC time value into a local datetime."""
    if utc_int is None:
      return None

    # Convert from a UTC integer (seconds since the epoch) to a UTC datetime
    datetime_utc = datetime.utcfromtimestamp(0) + timedelta(seconds=utc_int)
    # Get the offset from UTC to local
    timestamp = time.mktime(datetime_utc.timetuple())
    offset = datetime.fromtimestamp(timestamp) - datetime.utcfromtimestamp(
        timestamp)

    # Convert from a UTC datetime to a local datetime
    return datetime_utc + offset

  def lookup_job_tasks(self,
                       status_list,
                       user_list=None,
                       job_list=None,
                       job_name_list=None,
                       task_list=None,
                       labels=None,
                       create_time=None,
                       max_tasks=0):
    # 'OR' filtering arguments.
    status_list = None if status_list == ['*'] else status_list
    user_list = None if user_list == ['*'] else user_list
    job_list = None if job_list == ['*'] else job_list
    job_name_list = None if job_name_list == ['*'] else job_name_list
    task_list = None if task_list == ['*'] else task_list
    # 'AND' filtering arguments.
    labels = labels if labels else []

    create_time_local = self._utc_int_to_local_datetime(create_time)

    # The local provider is intended for local, single-user development. There
    # is no shared queue (jobs run immediately) and hence it makes no sense
    # to look up a job run by someone else (whether for dstat or for ddel).
    # If a user is passed in, we will allow it, so long as it is the current
    # user. Otherwise we explicitly error out.
    approved_users = [dsub_util.get_os_user()]
    if user_list:
      if user_list != approved_users:
        raise NotImplementedError(
            'Filtering by user is not implemented for the local provider'
            ' (%s)' % str(user_list))
    else:
      user_list = approved_users

    ret = []
    if not job_list:
      # Default to every job we know about.
      job_list = os.listdir(self._provider_root())
    for j in job_list:
      for u in user_list:
        path = self._provider_root() + '/' + j
        if not os.path.isdir(path):
          continue
        for task_id in os.listdir(path):
          if task_id == 'task':
            task_id = None
          if task_list and task_id not in task_list:
            continue

          task = self._get_task_from_task_dir(j, u, task_id)
          if not task:
            continue

          status = task.get_field('status')
          if status_list and status not in status_list:
            continue

          job_name = task.get_field('job-name')
          if job_name_list and job_name not in job_name_list:
            continue

          # If labels are defined, all labels must match.
          task_labels = task.get_field('labels')
          labels_match = all(
              [k in task_labels and task_labels[k] == v for k, v in labels])
          if labels and not labels_match:
            continue
          # Check that the job is not too old.
          if create_time_local:
            task_create_time = task.get_field('create-time')
            if task_create_time < create_time_local:
              continue

          ret.append(task)

          if max_tasks > 0 and len(ret) > max_tasks:
            break

    return ret

  def get_tasks_completion_messages(self, tasks):
    return [task.get_field('status-message') for task in tasks]

  # Private methods

  def _write_task_metadata(self, task_metadata, job_data, task_data,
                           create_time):
    """Write a file with the data needed for dstat."""

    # Build up a dict to dump a YAML file with relevant task details:
    #   job-id: <id>
    #   task-id: <id>
    #   job-name: <name>
    #   inputs:
    #     name: value
    #   outputs:
    #     name: value
    #   envs:
    #     name: value
    #   labels:
    #     name: value
    data = {
        'job-id': task_metadata.get('job-id'),
        'task-id': task_metadata.get('task-id'),
        'job-name': task_metadata.get('job-name'),
        'create-time': create_time.strftime('%Y-%m-%d %H:%M:%S.%f'),
        'logging': task_metadata.get('logging'),
        'labels': {
            'dsub-version': task_metadata.get('dsub-version', '0')
        },
    }
    for key in ['inputs', 'outputs', 'envs', 'labels']:
      data_field = data.get(key, {})

      for param in job_data[key] + task_data[key]:
        data_field[param.name] = param.value
      data[key] = data_field

    task_dir = self._task_directory(
        task_metadata.get('job-id'), task_metadata.get('task-id'))
    with open(os.path.join(task_dir, 'meta.yaml'), 'wt') as f:
      f.write(yaml.dump(data))

  def _read_task_metadata(self, task_dir):
    """Read the meta file containing core fields for dstat."""

    try:
      with open(os.path.join(task_dir, 'meta.yaml'), 'r') as f:
        meta = yaml.load('\n'.join(f.readlines()))

      # Make sure that create-time string is turned into a datetime
      meta['create-time'] = datetime.strptime(meta['create-time'],
                                              '%Y-%m-%d %H:%M:%S.%f')

      return meta
    except (IOError, OSError):
      # lookup_job_tasks may try to read the task metadata as a task is being
      # created. In that case, just catch the exception and return None.
      return None

  def _get_end_time_from_task_dir(self, task_dir):
    try:
      with open(os.path.join(task_dir, 'end-time.txt'), 'r') as f:
        return datetime.strptime(f.readline().strip(), '%Y-%m-%d %H:%M:%S.%f')
    except (IOError, OSError):
      return None

  def _get_last_update_time_from_task_dir(self, task_dir):
    last_update = 0
    for filename in ['status.txt', 'log.txt', 'meta.yaml']:
      try:
        mtime = os.path.getmtime(os.path.join(task_dir, filename))
        last_update = max(last_update, mtime)
      except (IOError, OSError):
        pass

    return last_update

  def _get_status_from_task_dir(self, task_dir):
    try:
      with open(os.path.join(task_dir, 'status.txt'), 'r') as f:
        return f.readline().strip()
    except (IOError, OSError):
      return None

  def _get_log_detail_from_task_dir(self, task_dir):
    try:
      with open(os.path.join(task_dir, 'log.txt'), 'r') as f:
        return f.read().splitlines()
    except (IOError, OSError):
      return None

  def _get_task_from_task_dir(self, job_id, user_id, task_id):
    """Return a Task object with this task's info."""

    # We need to be very careful about how we read and interpret the contents
    # of the task directory. The directory could be changing because a new
    # task is being created. The directory could be changing because a task
    # is ending.

    # If the meta.yaml exists, it means the task is scheduled. It does not mean
    # it is yet running.
    # If the task.pid file exists, it means that the runner.sh was started.
    task_dir = self._task_directory(job_id, task_id)

    # If the metadata does not exist, the task does not yet exist.
    meta = self._read_task_metadata(task_dir)
    if not meta:
      return None

    # Get the pid of the runner
    pid = -1
    try:
      with open(os.path.join(task_dir, 'task.pid'), 'r') as f:
        pid = int(f.readline().strip())
    except (IOError, OSError):
      pass

    # Read the files written by the runner.sh.
    # For new tasks, these may not have been written yet.
    end_time = self._get_end_time_from_task_dir(task_dir)
    last_update = self._get_last_update_time_from_task_dir(task_dir)
    status = self._get_status_from_task_dir(task_dir)
    log_detail = self._get_log_detail_from_task_dir(task_dir)

    # If the status file is not yet written, then mark the task as pending
    if not status:
      status = 'RUNNING'
      log_detail = ['Pending']

    return LocalTask(
        job_id=job_id,
        task_id=task_id,
        task_status=status,
        log_detail=log_detail,
        job_name=meta.get('job-name'),
        create_time=meta.get('create-time'),
        end_time=end_time,
        last_update=datetime.fromtimestamp(last_update)
        if last_update > 0 else None,
        logging=meta.get('logging'),
        envs=meta.get('envs'),
        labels=meta.get('labels'),
        inputs=meta.get('inputs'),
        outputs=meta.get('outputs'),
        user_id=user_id,
        pid=pid)

  def _provider_root(self):
    return tempfile.gettempdir() + '/dsub-local'

  def _delocalize_logging_command(self, file_provider, task_metadata):
    """Returns a command to delocalize logs.

    Args:
      file_provider: a file provider from param_util.
      task_metadata: dictionary of values such as job-id and task-id.

    Returns:
      eg. 'gs://bucket/path/myfile' or 'gs://bucket/script-foobar-12'
    """

    # Get the logging prefix (everything up to ".log")
    logging_prefix = os.path.splitext(task_metadata.get('logging'))[0]

    # Set the provider-specific mkdir and file copy commands
    if file_provider == param_util.P_LOCAL:
      mkdir_cmd = 'mkdir -p "%s"\n' % os.path.dirname(logging_prefix)
      cp_cmd = 'cp'
    elif file_provider == param_util.P_GCS:
      mkdir_cmd = ''
      cp_cmd = 'gsutil -q cp'
    else:
      assert False

    # Construct the copy command
    copy_logs_cmd = textwrap.dedent("""\
      local cp_cmd="{cp_cmd}"
      local prefix="{prefix}"
    """).format(
        cp_cmd=cp_cmd, prefix=logging_prefix)

    # Build up the command
    body = textwrap.dedent("""\
      {mkdir_cmd}
      {copy_logs_cmd}
    """).format(
        mkdir_cmd=mkdir_cmd, copy_logs_cmd=copy_logs_cmd)

    return body

  def _make_job_id(self, job_name_value, user_id):
    """Return a job-id string."""

    # We want the job-id to be expressive while also
    # having a low-likelihood of collisions.
    #
    # For expressiveness, we:
    # * use the job name (truncated at 10 characters).
    # * insert the user-id
    # * add a datetime value
    # To have a high likelihood of uniqueness, the datetime value is out to
    # hundredths of a second.
    #
    # The full job-id is:
    #   <job-name>--<user-id>--<timestamp>
    return '%s--%s--%s' % (job_name_value[:10], user_id,
                           datetime.now().strftime('%y%m%d-%H%M%S-%f'))

  def _task_directory(self, job_id, task_id):
    """The local dir for staging files for that particular task."""
    dir_name = 'task' if task_id is None else str(task_id)
    return self._provider_root() + '/' + job_id + '/' + dir_name

  def _make_environment(self, inputs, outputs):
    """Return a dictionary of environment variables for the VM."""
    ret = {}
    for i in inputs:
      ret[i.name] = DATA_MOUNT_POINT + '/' + i.docker_path
    for o in outputs:
      ret[o.name] = DATA_MOUNT_POINT + '/' + o.docker_path
    return ret

  def _localize_inputs_recursive_command(self, task_dir, inputs):
    """Returns a command that will stage recursive inputs."""
    data_dir = os.path.join(task_dir, DATA_SUBDIR)
    provider_commands = [
        providers_util.build_recursive_localize_command(data_dir, inputs,
                                                        file_provider)
        for file_provider in _SUPPORTED_INPUT_PROVIDERS
    ]
    return '\n'.join(provider_commands)

  def _get_input_target_path(self, local_file_path):
    """Returns a directory or file path to be the target for "gsutil cp".

    If the filename contains a wildcard, then the target path must
    be a directory in order to ensure consistency whether the source pattern
    contains one or multiple files.


    Args:
      local_file_path: A full path terminating in a file or a file wildcard.

    Returns:
      The path to use as the "gsutil cp" target.
    """

    path, filename = os.path.split(local_file_path)
    if '*' in filename:
      return path + '/'
    else:
      return local_file_path

  def _localize_inputs_command(self, task_dir, inputs):
    """Returns a command that will stage inputs."""
    commands = []
    for i in inputs:
      if i.recursive:
        continue

      source_file_path = i.uri
      local_file_path = task_dir + '/' + DATA_SUBDIR + '/' + i.docker_path
      dest_file_path = self._get_input_target_path(local_file_path)

      commands.append('mkdir -p "%s"' % os.path.dirname(local_file_path))

      if i.file_provider in [param_util.P_LOCAL, param_util.P_GCS]:
        # The semantics that we expect here are implemented consistently in
        # "gsutil cp", and are a bit different than "cp" when it comes to
        # wildcard handling, so use it for both local and GCS:
        #
        # - `cp path/* dest/` will error if "path" has subdirectories.
        # - `cp "path/*" "dest/"` will fail (it expects wildcard expansion
        #   to come from shell).
        commands.append('gsutil -q cp "%s" "%s"' % (source_file_path,
                                                    dest_file_path))

    return '\n'.join(commands)

  def _mkdir_outputs(self, task_dir, outputs):
    os.makedirs(task_dir + '/' + DATA_SUBDIR + '/' + WORKING_DIR)
    os.makedirs(task_dir + '/' + DATA_SUBDIR + '/tmp')
    for o in outputs:
      local_file_path = task_dir + '/' + DATA_SUBDIR + '/' + o.docker_path
      # makedirs errors out if the folder already exists, so check.
      if not os.path.isdir(os.path.dirname(local_file_path)):
        os.makedirs(os.path.dirname(local_file_path))

  def _delocalize_outputs_recursive_command(self, task_dir, outputs):
    cmd_lines = []
    # Generate commands to create any required local output directories.
    for var in outputs:
      if var.recursive and var.file_provider == param_util.P_LOCAL:
        cmd_lines.append('  mkdir -p "%s"' % var.uri.path)
    # Generate local and GCS delocalize commands.
    cmd_lines.append(
        providers_util.build_recursive_delocalize_command(
            os.path.join(task_dir, DATA_SUBDIR), outputs, param_util.P_GCS))
    cmd_lines.append(
        providers_util.build_recursive_delocalize_command(
            os.path.join(task_dir, DATA_SUBDIR), outputs, param_util.P_LOCAL))
    return '\n'.join(cmd_lines)

  def _delocalize_outputs_commands(self, task_dir, outputs):
    """Copy outputs from local disk to GCS."""
    commands = []
    for o in outputs:
      if o.recursive:
        continue

      # The destination path is o.uri.path, which is the target directory
      # (rather than o.uri, which includes the filename or wildcard).
      dest_path = o.uri.path
      local_path = task_dir + '/' + DATA_SUBDIR + '/' + o.docker_path

      if o.file_provider == param_util.P_LOCAL:
        commands.append('mkdir -p "%s"' % dest_path)

      # Use gsutil even for local files (explained in _localize_inputs_command).
      if o.file_provider in [param_util.P_LOCAL, param_util.P_GCS]:
        commands.append('gsutil -q cp "%s" "%s"' % (local_path, dest_path))

    return '\n'.join(commands)

  def _stage_script(self, task_dir, script_name, script_text):
    path = (task_dir + '/' + DATA_SUBDIR + '/' + SCRIPT_DIR + '/' + script_name)
    os.makedirs(os.path.dirname(path))
    f = open(path, 'w')
    f.write(script_text)
    f.write('\n')
    f.close()
    st = os.stat(path)
    # Ensure the user script is executable.
    os.chmod(path, st.st_mode | 0100)


# The task object for this provider.
_RawTask = namedtuple('_RawTask', [
    'job_id',
    'task_id',
    'task_status',
    'log_detail',
    'job_name',
    'create_time',
    'end_time',
    'last_update',
    'logging',
    'envs',
    'labels',
    'inputs',
    'outputs',
    'user_id',
    'pid',
])


class LocalTask(base.Task):
  """Basic container for task metadata."""

  def __init__(self, *args, **kwargs):
    self._raw = _RawTask(*args, **kwargs)

  def raw_task_data(self):
    """Return a provider-specific representation of task data.

    Returns:
      string of task data from the provider.
    """
    return self._raw._asdict()

  def get_field(self, field, default=None):
    # Convert the incoming Task object to a dict.
    # With the exception of "status', the dsub "field" names map directly to the
    # Task members where "-" in the field name is "_" in the Task member name.
    tad = {
        key.replace('_', '-'): value
        for key, value in self._raw._asdict().iteritems()
    }

    value = None
    if field == 'status':
      value = tad.get('task-status')
    elif field == 'status-message':
      if tad.get('task-status') == 'SUCCESS':
        value = 'Success'
      else:
        # Return the last line of output
        value = self._last_lines(tad.get('log-detail'), 1)
    elif field == 'status-detail':
      # Return the last three lines of output
      value = self._last_lines(tad.get('log-detail'), 3)
    elif field == 'start-time':
      # There's no delay between creation and start since we launch docker
      # immediately for local runs.
      value = tad.get('create-time')
    else:
      value = tad.get(field)

    return value if value else default

  def get_docker_name_for_task(self):
    return _format_task_name(
        self.get_field('job-id'), self.get_field('task-id'))

  @staticmethod
  def _last_lines(value, count):
    """Return the last line(s) as a single (newline delimited) string."""
    if not value:
      return ''

    return '\n'.join(value[-count:])


if __name__ == '__main__':
  pass
