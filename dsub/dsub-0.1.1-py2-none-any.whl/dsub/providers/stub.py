# Copyright 2016 Google Inc. All Rights Reserved.
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
"""Stub provider, for unit testing. Does not actually run anything."""

from . import base


class StubJobProvider(base.JobProvider):
  """Stub provider, for unit testing. Does not actually run anything."""

  def __init__(self):
    self._operations = []

  # 1) Methods that are supposed to do something. Use mocks
  #    if you need to check that they are called.

  def submit_job(self, job_resources, job_metadata, job_data, all_job_data):
    pass

  def delete_jobs(self,
                  user_list,
                  job_list,
                  task_list,
                  labels,
                  create_time=None):
    pass

  # 2) Methods that manipulate the state of the fictional operations.
  #    Meant to be called by the test code, to set things up.

  def set_operations(self, ops):
    """Set the state of the fictional world.

    Args:
     ops: a list of dict, each representing an operation.

    Operations can have the following fields:
       - status: tuple (string,date)
       - user: string
       - job-id: string
       - job-name: string
       - task-id: string
       - labels: list<dict>
       - status-message: string
       - error-messages : list of string
    """
    self._operations = [StubTask(o) for o in ops]

  def get_operations(self):
    return self._operations

  # 3) Methods that return information.
  #    Meant to be called by the code under test, they rely on the fake
  #    state set via group (2) above.

  def prepare_job_metadata(self, script, job_name, user_id):
    del script, job_name, user_id  # pacify linter
    raise BaseException('Not implemented')

  def lookup_job_tasks(self,
                       status_list,
                       user_list=None,
                       job_list=None,
                       job_name_list=None,
                       task_list=None,
                       labels=None,
                       create_time=None,
                       max_tasks=0):
    """Return a list of operations based on the input criteria.

    If any of the filters are empty or "[*]", then no filtering is performed on
    that field.

    Args:
      status_list: ['*'], or a list of job status strings to return. Valid
        status strings are 'RUNNING', 'SUCCESS', 'FAILURE', or 'CANCELED'.
      user_list: a list of ids for the user(s) who launched the job.
      job_list: a list of job ids to return.
      task_list: a list of specific tasks within the specified job(s) to return.
      create_time: a UTC value for earliest create time for a job.
      max_tasks: the maximum number of job tasks to return or 0 for no limit.

    Returns:
      A list of Genomics API Operations objects.
    """

    if status_list and len(status_list) == 1 and status_list[0] == '*':
      status_list = None
    user_list = None if user_list == '*' else user_list
    job_list = None if job_list == '*' else job_list
    job_name_list = None if job_name_list == '*' else job_name_list
    task_list = None if task_list == '*' else task_list

    if labels or create_time:
      raise NotImplementedError(
          'Lookup by labels and create_time not yet supported by stub.')

    operations = [
        x for x in self._operations
        if ((not status_list or x.get_field('status',
                                            (None, None))[0] in status_list) and
            (not user_list or x.get_field('user', None) in user_list) and
            (not job_list or x.get_field('job-id', None) in job_list) and
            (not job_name_list or x.get_field('job-name', None) in job_name_list
            ) and (not task_list or x.get_field('task-id', None) in task_list))
    ]
    if max_tasks > 0:
      operations = operations[:max_tasks]
    return operations

  def get_tasks_completion_messages(self, tasks):
    error_messages = []
    for task in tasks:
      error_messages += [task.get_field('error-message', '')]

    return error_messages


class StubTask(base.Task):

  def __init__(self, op):
    self.op = op

  def get_field(self, field, default=None):
    if field == 'task-status':
      return self.op['status'][0]
    return self.op.get(field, None)

  def raw_task_data(self):
    return self.op

if __name__ == '__main__':
  pass
