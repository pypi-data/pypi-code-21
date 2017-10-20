#!/usr/bin/env python

import os
from collections import OrderedDict
from frozendict import frozendict

from .rules import *
from .utils import eprint

# The deployment director compiles a context, consisting of:
# ci:
#  ... information coming from the ci ...
# env:
#  ... environment variables ...
# repo: ... shortcut to ci['repo_name']
# branch: .. shortcut to ci['branch']
class Context(object):

  __slots__ = [ '_ci', '_env' ]

  def __init__(self, options, env={}):
    self._env = frozendict(os.environ) if len(env) == 0 else frozendict(env)
    if options.get('ci_name') == 'codeship':
      self._load_civars_codeship()
    else:
      self._ci = frozendict({})

  def getstr(self, key):
    return ("{self.%s}" % key).format(self=self)

  def _load_civars_codeship(self):
    self._ci = frozendict(
      branch= self.env.get('CI_BRANCH'),
      build_id= self.env.get('CI_BUILD_ID'),
      committer_email= self.env.get('CI_COMMITTER_EMAIL'),
      committer_name= self.env.get('CI_COMMITTER_NAME'),
      committer_username= self.env.get('CI_COMMITTER_USERNAME'),
      commit_description= self.env.get('CI_COMMIT_DESCRIPTION'),
      commit_id= self.env.get('CI_COMMIT_ID'),
      commit_message= self.env.get('CI_COMMIT_MESSAGE'),
      name= self.env.get('CI_NAME'),
      project_id= self.env.get('CI_PROJECT_ID'),
      repo_name= self.env.get('CI_REPO_NAME'),
      string_time= self.env.get('CI_STRING_TIME'),
      timestamp= self.env.get('CI_TIMESTAMP')
    )

  @property
  def ci(self):
    return self._ci

  @property
  def env(self):
    return self._env

  # shortcuts
  @property
  def repo(self):
    return self.ci.get('repo_name')

  @property
  def branch(self):
    return self.ci.get('branch')

  def __repr__(self):
    return 'Context(ci=%s,env=%s)' % (repr(self.ci), repr(self.env))


class DeploymentDirector(object):
  """
  """
  def __init__(self, rules, options={}, env={}, env_overwrite={}):
    from copy import copy
    self.options = options
    self.actions = OrderedDict()
    self.context = Context(options, env)
    #
    if (self.options.get('verbose') > 0):
      eprint('* Using context: %s' % repr(self.context))
    #
    self.parse_rules(rules)

  def parse_rules(self, rules):
    # Verify schema
    rules = RulesFile.parse(rules)
    
    # Go through each of the rules
    for rule in rules.rules:
      if (self.options.get('verbose') > 0):
        eprint('* evaluating rule: ')
        eprint('  ' + repr(rule))
      rule.eval(context=self.context, actions=self.actions)
    
    # Print the actions
    if (self.options.get('verbose') > 0):
      eprint('* resulting actions: ')
      for action in self.actions:
        eprint('  - ' + repr(action))
        eprint('    = ' + repr(self.actions[action]))

  def run_deployment(self):
    # If not dry run, execute actions
    if not self.options.get('dry_run'):
      for (name,action) in self.actions.items():
        print('\n\n')
        print('----++++ ACTION: %s ++++----' % name)
        print('\n\n')
        action.execute()

