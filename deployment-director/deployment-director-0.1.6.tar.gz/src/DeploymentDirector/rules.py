#!/usr/bin/env python

from .utils import interpolate, create_action

from voluptuous import Schema, All, Any, Coerce, Required
import re

# useful coercers to normalise the schema output and open some shortcuts
# for the user when writing the yaml
def CoerceArray(x):
  """
  Coerces x -> [x]
  """
  return [x] if type(x) not in (list, tuple) else x

def CoerceToDict(key):
  """
  Coerces x -> { key: x }
  """
  def f(x):
    return { key: x } if type(x) != dict else x
  return f


# Base class that binds a schema to a python class
class SchemaBinder(object):
  @classmethod
  def schema(cls):
    raise Exception("Abstract method!")

  @classmethod
  def schema_source(cls):
    return cls.schema().schema

  @classmethod
  def factory(cls, x):
    raise Exception("Abstract method!")

  @classmethod
  def binding(cls):
    # Returns a schema bound to an object of the invoked class, 
    return Schema(All(cls.schema(), lambda x: cls.factory(x)))

  def __repr__(self):
    return "%s(%s)" % (self.__class__.__name__, repr(self.__dict__))


# Class that represents a successful match
class Match(object):
  def __init__(self, matcher_clause, context, matched_as={}):
    self.matcher_clause = matcher_clause
    self.context = context
    self.matched_as = matched_as

  def map_lookup(self, mapp, key):
    # 1. attempt retrieving the key from the context
    map_key = self.context.getstr(key)
    if mapp.has_key(map_key):
      return mapp.get(map_key)
    # 2. attempt key generated during matching (matched_as feature)
    if self.matched_as.has_key(key):
      return mapp.get(self.matched_as[key])
    else:
      return None


class MatchSpec(SchemaBinder):
  """
  an operator provided string / object to do matching against, i.e.:
    master
  or:
    /some-regex-.*/
  or:
    match: master
  or:
    match: /some-regex-.*/
    as: regex-MATCH   # to be used later on in mapping
  """
  @classmethod
  def schema(cls):
    return Schema(Any(
      All(str, CoerceToDict('match')),
      {
        Required('match'): str,
        'as': str 
      }
      ))

  @classmethod
  def factory(cls, x):
    return cls(**x)

  def __init__(self, match, **kwargs):
    self.match = match
    self.as_alias = kwargs['as'] if kwargs.has_key('as') else None
    # if the match spec is a regular expression, compile it
    if re.match('/.*/', self.match):
      self.match_re = re.compile(self.match[1:-1] + '$')  # added '$' forces whole string match

  def test_match(self, value):
    def is_a_match(value):
      if hasattr(self, 'match_re'):
        return self.match_re.match(value)
      else:
        return self.match == value
    #
    if is_a_match(value):
      if self.as_alias:
        return { 'as': self.as_alias }
      else:
        return True
    else:
      return False


# available matchers against the deployment job context
matching_criteria = Any('branch', 'repo')

class MatcherClause(SchemaBinder):
  """
  the matcher clause, a dictionary with all the criteria that should match
  against the job context, i.e:
    repo: my_repo
    branch: [ my_branch, or_my_branch ]
  """
  @classmethod
  def schema(cls):
    return Schema({ matching_criteria: All( Any(MatchSpec.binding(), [MatchSpec.binding()]), CoerceArray) })

  @classmethod
  def factory(cls, x):
    return cls(x)   # passes criteria dictionary to constructor

  def __init__(self, criteria):
    # criteria looks like { branch: [ branch1, branch2 ], repo: [ repo1 ] }
    self.criteria = criteria

  def test(self, context):
    # all criterions must match (i.e. branch and repo), any failure to match aborts the loop
    matched_as = {}
    for (k, match_specs) in self.criteria.items():
      value = context.getstr(k)
      match = self._any_match(match_specs, value)
      if not match:   # shortcut: no match in a criterion is a failure
        return False
      if type(match) == dict:       # matched as something else
        matched_as[k] = match['as']
    return Match(matcher_clause=self, context=context, matched_as=matched_as)

  def _any_match(self, match_specs, value):
    for match_spec in match_specs:
      match = match_spec.test_match(value)
      if match:       # stops at the first match
        return match  # may be True or { 'as': ... }
    return False

  def __repr__(self):
    return "MatcherClause(%s)" % repr(self.criteria)


class ActionDef(SchemaBinder):
  """
  Action definitions. Takes the form of either
    action: (class name)
  or
    action:
      class_name: (class name)
      arguments:  # constructor arguments
        arg1: val1

  behind the scenes
    action: (class name)
  is normalised to
    action:
      class_name: (class name)
  """
  @classmethod
  def schema(cls):
    action_def_full = Schema({
      Required('class_name'): str,
      'arguments': {str: object}
      })
    return Schema(All(Any(str, action_def_full), CoerceToDict('class_name')))

  @classmethod
  def factory(cls, x):
    return cls(**x)

  def __init__(self, class_name, arguments={}):
    self.__dict__.update(class_name=class_name, arguments=arguments)


class ParamValueAssignation(SchemaBinder):
  """
  specifies assignation of a value to an action parameter. The canonical form is
    value: (some value)
  or
    map:
      key1: val1
      ...
    key: keyvar

  if just a scalar or an array, then that's transformed to
    value: (provided scalar or array)

  note that in order to assign a dictionary it's mandatory to use the canonical form
    value:
      k1: v1
      k2: v2
  """
  @classmethod
  def schema(cls):
    return Schema(
      All(
        Any(
            str, int, bool,       # could be one of these primitive objects
            [object],             # or an array of anything
            Any(                  # if a dictionary ...
              {                   # ... it could be just a value (anything)
                Required('value'): object
              }, {                # ... or a map (based on a matching key)
                Required('map'): Schema({ Required(str): object }),
                Required('key'): matching_criteria  # key (matching)
                })
          ),
        CoerceToDict('value')
        )
      )

  @classmethod
  def factory(cls, x):
    return cls(**x)

  def __init__(self, **kwargs):
    self.__dict__.update(kwargs)

  def interpolate(self, obj, context):
    if type(obj) == str:
      # Actually do interpolation
      return interpolate(obj, context)
    elif type(obj) == list:
      return [ self.interpolate(x, context) for x in obj ]
    elif type(obj) == dict:
      return dict([ (k, self.interpolate(v, context)) for (k,v) in obj.items() ])
    else:
      return obj

  def resolve(self, match):
    context = match.context
    if hasattr(self, 'value'):
      return self.interpolate(self.value, context)
    elif hasattr(self, 'map'):
      value = match.map_lookup(self.map, self.key)
      return self.interpolate(value, context)
    else:
      return None


class ActionSettings(SchemaBinder):
  """
  settings that can be adjusted in an action
  """
  @classmethod
  def schema(cls):
    return Schema({
      'enabled': bool,
      'labels': { str: str },
      'parameters': {
        str: ParamValueAssignation.binding()
        }
      })

  @classmethod
  def factory(cls, x):
    return cls(**x)

  def __init__(self, **kwargs):
    self.__dict__.update(kwargs)

  def resolve(self, match):
    def param_resolve(obj):
      return obj.resolve(match) if isinstance(obj, ParamValueAssignation) else obj

    settings = dict(
      reduce(
        lambda x,y: x + y,
        [
          [('enabled', self.enabled)] if hasattr(self, 'enabled') else [],
          [('labels', self.labels)] if hasattr(self, 'labels') else [],
          [('parameters', dict([(k,param_resolve(v)) for (k,v) in self.parameters.items()]))] if hasattr(self, 'parameters') else []
        ])
    )
    return ActionSettings(**settings)


class AddAction(SchemaBinder):
  """
  The Add Action consequence

  add_action:
    name: (name of the action)
    action: (action class / definition as above)
    enabled: ...
    labels: { ... }
    parameters:
      ..: ...
  """
  @classmethod
  def schema(cls):
    return Schema({
      'add_action': Schema({
          Required('name'): str,
          Required('action'): ActionDef.binding(),
          }).extend(ActionSettings.schema_source())
      })

  @classmethod
  def factory(cls, x):
    return cls(**x['add_action'])

  def __init__(self, name, action, **kwargs):
    self.__dict__.update(name=name, action=action)
    if len(kwargs) > 0:
      self.__dict__.update({ 'settings': ActionSettings(**kwargs) })

  def apply(self, match, actions):
    if actions.has_key(self.name):
      raise Exception("An action named %s already exists")
    new_action = create_action(self.action)
    if hasattr(self, 'settings'):
      new_action.update_settings(self.settings.resolve(match))
    actions[self.name] = new_action


class ActionMatcher(SchemaBinder):
  @classmethod
  def schema(cls):
    return Schema(
      All(
        Any(
          str,                                    # match by action name
          { 'name': str, 'labels': { str: str } } # and/or match by labels
        ),
        CoerceToDict('name')
        )
      )

  @classmethod
  def factory(cls, x):
    return cls(**x)

  def __init__(self, **kwargs):
    self.__dict__.update(kwargs)

  def match(self, actions):
    return actions.get(self.name)


class ConfigureAction(SchemaBinder):
  @classmethod
  def schema(cls):
    return Schema({
      'configure_action': {
        Required('action'): ActionMatcher.binding(),
        Required('settings'): ActionSettings.binding()
      }})

  @classmethod
  def factory(cls, x):
    return cls(**x['configure_action'])

  def __init__(self, action, settings):
    self.__dict__.update(action=action, settings=settings)

  def apply(self, match, actions):
    action = self.action.match(actions)
    if action:
      action.update_settings(self.settings.resolve(match))


class Rule(SchemaBinder):
  """
  allow rule recursivity in consequences, a consequence can be evaluating another rule
  i.e..
    when:
      ...
    then:
    - add_action
      ...
    - configure_action
      ...
    - when:
      ...
      then:
      - ...
      - ...
  """
  @classmethod
  def schema(cls):
    def consequence(v):
        # implements recursivity
      return Schema(Any(AddAction.binding(), ConfigureAction.binding(), Rule.binding()))(v)

    # multiple matcher clause present alternatives for matching (read as a logic OR)
    #   - repo: my_repo
    #     branch: my_branch
    #   - repo: my_other_repo
    #     branch: my_other_branch
    matcher = All(Any(MatcherClause.binding(), [MatcherClause.binding()]), CoerceArray)

    return Schema({
      Required('when'): matcher,
      Required('then'): [consequence]
      })

  @classmethod
  def factory(cls, x):
    return cls(**x)

  def __init__(self, when, then):
    self.__dict__.update(when=when, then=then)

  def eval(self, context, actions):
    for clause in self.when:
      match = clause.test(context)
      if match:   # one match is enough (by now)
        for consequence in self.then:
          consequence.apply(match, actions)

  def apply(self, match, actions):
    self.eval(match.context, actions)

class RulesFile(SchemaBinder):
  @classmethod
  def schema(cls):
    return Schema({
      Required('version'): All(Any(str, int), Coerce(int)),
      Required('rules'): [Rule.binding()]
      })

  @classmethod
  def factory(cls, x):
    return cls(**x)

  @classmethod
  def parse(cls, data):
    return cls.binding()(data)

  def __init__(self, version, rules):
    self.__dict__.update(version=version, rules=rules)
    self.validate()

  def validate(self):
    if self.version != 1:
      raise Exception("Invalid version of rules file")
