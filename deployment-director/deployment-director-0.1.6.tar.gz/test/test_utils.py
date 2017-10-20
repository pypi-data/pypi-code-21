from DeploymentDirector.utils import interpolate, create_action
from DeploymentDirector.rules import ActionDef
from DeploymentDirector.actions.base import BaseAction

import pytest

def test_interpolate(context):
  def f(string):
    return interpolate(string, context)

  assert(
    f("the ${repo} has the ${branch} and the committer is ${ci[committer_name]}") ==
      "the {0.repo} has the {0.branch} and the committer is {0.ci[committer_name]}".format(context))
  assert(
    f("the ${repo} has the ${branch} and the {committer} is ${ci[committer_name]}") ==
      "the {0.repo} has the {0.branch} and the {{committer}} is {0.ci[committer_name]}".format(context))
  assert(
    f("the ${repo} has the ${branch} and the $${committer} is ${ci[committer_name]}") ==
      "the {0.repo} has the {0.branch} and the ${{committer}} is {0.ci[committer_name]}".format(context))

_action_defs = [
  ActionDef(
    class_name='CommandAction',
    arguments={ 'command': 'true' }),
  ActionDef(
    class_name='CommandAction',
    arguments={ 'command': 'ls /', 'env': { 'ENV1': 'val1'} } ),
  ]

@pytest.mark.parametrize('action_def', _action_defs)
def test_create_action(action_def):
  assert(isinstance(create_action(action_def), BaseAction))
