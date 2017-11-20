import click

from globus_cli.parsing import common_options, task_id_arg
from globus_cli.safeio import formatted_print

from globus_cli.services.transfer import get_client, assemble_generic_doc


@click.command('update', short_help='Update a task',
               help='Update label and/or deadline on an active task')
@common_options
@task_id_arg
@click.option('--label', help='New Label for the task')
@click.option('--deadline', help='New Deadline for the task')
def update_task(deadline, label, task_id):
    """
    Executor for `globus task update`
    """
    client = get_client()

    task_doc = assemble_generic_doc(
        'task', label=label, deadline=deadline)

    res = client.update_task(task_id, task_doc)
    formatted_print(res, simple_text='Success')
