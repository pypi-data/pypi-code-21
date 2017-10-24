import numbers
import re
import semver
import six

from craftai.errors import CraftAiDecisionError, CraftAiNullDecisionError
from craftai.operators import _OPERATORS
from craftai.time import Time
from craftai.timezones import is_timezone

_VALUE_VALIDATORS = {
  "continuous": lambda value: isinstance(value, numbers.Real),
  "enum": lambda value: isinstance(value, six.string_types),
  "timezone": lambda value: isinstance(value, six.string_types) and is_timezone(value),
  "time_of_day": lambda value: isinstance(value, numbers.Real) and value >= 0 and value < 24,
  "day_of_week": lambda value: isinstance(value, six.integer_types) and value >= 0 and value <= 6,
  "day_of_month": lambda value: isinstance(value, six.integer_types) and value >= 1 and value <= 31,
  "month_of_year": lambda value: isinstance(value, six.integer_types) and value >= 1 and value <= 12
}

_DECISION_VERSION = "1.1.0"

class Interpreter(object):

  @staticmethod
  def decide(tree, args):
    errors = []
    bare_tree, configuration, _ = Interpreter._parse_tree(tree)
    if configuration != {}:
      state = args[0]
      time = None if len(args) == 1 else args[1]
      context_result = Interpreter._rebuild_context(configuration, state, time)
      context = context_result["context"]
    else:
      context = Interpreter.join_decide_args(args)

    errors = Interpreter._check_context(configuration, context)

    # deal with missing properties
    if errors:
      message = "Unable to take decision, the given context is not valid: " + errors.pop(0)

      for error in errors:
        message = "".join((message, ", ", error))
      message = message + "."

      raise CraftAiDecisionError(message)

    decision = {}
    decision["output"] = {}
    for output in configuration.get("output"):
      decision["output"][output] = Interpreter._decide_recursion(bare_tree[output], context)
    decision["context"] = context
    decision["_version"] = _DECISION_VERSION

    return decision

  ####################
  # Internal helpers #
  ####################

  @staticmethod
  def _rebuild_context(configuration, state, time=None):
    missings = []
    # Model should come from _parse_tree and is assumed to be checked upon
    # already
    output = configuration["output"]
    context = configuration["context"]

    # We should not use the output key(s) to compare against
    configuration_ctx = {
      key: context[key] for (key, value) in context.items() if (key not in output)
    }

    # Check if we need the time object
    to_generate = []

    for prop in configuration_ctx.items():
      prop_name = prop[0]
      prop_attributes = prop[1]
      if prop_attributes["type"] in ["time_of_day", "day_of_week", "day_of_month",
                                     "month_of_year", "timezone"]:
        # is_generated is at True, we must generate the time for the associated context property
        case_1 = "is_generated" in list(prop_attributes.keys()) and prop[1]["is_generated"]
        # is_generated is not given, by default at True, so we must generate it as well
        case_2 = "is_generated" not in list(prop_attributes.keys())
        if case_1 or case_2:
          to_generate.append(prop_name)

    # Propagate missings properties to next function
    if to_generate:
      # Can't generate from time -> missings properties are errors
      if not isinstance(time, Time):
        # Check for missings properties
        for prop in to_generate:
          if prop not in list(state.keys()):
            missings.append("expected property '{}' is not defined".format(prop))

      # Generate context properties which need to
      else:
        for prop in to_generate:
          state[prop] = time.to_dict()[configuration_ctx[prop]["type"]]

    # Rebuild the context with generated and non-generated values
    context = {
      feature: state.get(feature) for feature, properties in configuration_ctx.items()
    }

    return {
      "context": context,
      "errors": missings
    }

  @staticmethod
  def _decide_recursion(node, context):
    # If we are on a leaf
    if not (node.get("children") is not None and len(node.get("children"))):
      predicted_value = node.get("predicted_value")
      if predicted_value is None:
        raise CraftAiNullDecisionError(
          """Unable to take decision: the decision tree has no valid"""
          """ predicted value for the given context."""
        )

      leaf = {
        "predicted_value": predicted_value,
        "confidence": node.get("confidence") or 0,
        "decision_rules": []
      }

      if node.get("standard_deviation", None) is not None:
        leaf["standard_deviation"] = node.get("standard_deviation")

      return leaf

    # Finding the first element in this node's childrens matching the
    # operator condition with given context
    matching_child = Interpreter._find_matching_child(node, context)

    if not matching_child:
      prop = node.get("children")[0].get("decision_rule").get("property")
      raise CraftAiNullDecisionError(
        """Unable to take decision: value '{}' for property '{}' doesn't"""
        """ validate any of the decision rules.""".format(context.get(prop), prop)
      )

    # If a matching child is found, recurse
    result = Interpreter._decide_recursion(matching_child, context)
    new_predicates = [{
      "property": matching_child["decision_rule"]["property"],
      "operator": matching_child["decision_rule"]["operator"],
      "operand": matching_child["decision_rule"]["operand"]
    }]

    final_result = {
      "predicted_value": result["predicted_value"],
      "confidence": result["confidence"],
      "decision_rules": new_predicates + result["decision_rules"]
    }

    if result.get("standard_deviation", None) is not None:
      final_result["standard_deviation"] = result.get("standard_deviation")

    return final_result

  @staticmethod
  def _check_context(configuration, context):
    # Extract the required properties (i.e. those that are not the output)
    expected_properties = [
      p for p in configuration["context"]
      if not p in configuration["output"]
    ]

    # Retrieve the missing properties
    missing_properties = [
      p for p in expected_properties
      if not p in context or context[p] is None
    ]

    # Validate the values
    bad_properties = [
      p for p in expected_properties
      if p in context and
      not context[p] is None and
      not _VALUE_VALIDATORS[configuration["context"][p]["type"]](context[p])
    ]

    if missing_properties or bad_properties:
      missing_properties = sorted(missing_properties)
      missing_properties_messages = [
        "expected property '{}' is not defined"
        .format(p) for p in missing_properties
      ]
      bad_properties = sorted(bad_properties)
      bad_properties_messages = [
        "'{}' is not a valid value for property '{}' of type '{}'"
        .format(context[p], p, configuration["context"][p]["type"]) for p in bad_properties
      ]

      return missing_properties_messages + bad_properties_messages
    return []

  @staticmethod
  def _find_matching_child(node, context):
    for child in node["children"]:
      property_name = child["decision_rule"]["property"]
      operand = child["decision_rule"]["operand"]
      operator = child["decision_rule"]["operator"]
      context_value = context.get(property_name)
      if context_value is None:
        raise CraftAiDecisionError(
          """Unable to take decision, property '{}' is missing from the given context.""".
          format(property_name)
        )
      if (not isinstance(operator, six.string_types) or
          not operator in _OPERATORS):
        raise CraftAiDecisionError(
          """Invalid decision tree format, {} is not a valid"""
          """decision operator.""".format(operator)
        )

      # To be compared, continuous parameters should not be strings
      if "continuous" in operator:
        context_value = float(context_value)
        operand = float(operand)

      if _OPERATORS[operator](context_value, operand):
        return child
    return {}

  @staticmethod
  def join_decide_args(args):
    joined_args = {}
    for arg in args:
      if isinstance(arg, Time):
        joined_args.update(arg.to_dict())
      try:
        joined_args.update(arg)
      except TypeError:
        raise CraftAiDecisionError(
          """Invalid context args, the given objects aren't dicts"""
          """ or Time instances."""
        )
    return joined_args

  @staticmethod
  def _parse_tree(tree_object):
    # Checking definition of tree_object
    if not isinstance(tree_object, dict):
      raise CraftAiDecisionError("Invalid decision tree format, the given json is not an object.")

    # Checking version existence
    tree_version = tree_object.get("_version")
    if not tree_version:
      raise CraftAiDecisionError(
        """Invalid decision tree format, unable to find the version"""
        """ informations."""
      )

    # Checking version and tree validity according to version
    if re.compile(r"\d+.\d+.\d+").match(tree_version) is None:
      raise CraftAiDecisionError(
        """Invalid decision tree format, "{}" is not a valid version.""".
        format(tree_version)
      )
    elif semver.match(tree_version, ">=1.0.0") and semver.match(tree_version, "<2.0.0"):
      if tree_object.get("configuration") is None:
        raise CraftAiDecisionError(
          """Invalid decision tree format, no configuration found"""
        )
      if tree_object.get("trees") is None:
        raise CraftAiDecisionError(
          """Invalid decision tree format, no tree found."""
        )
      bare_tree = tree_object.get("trees")
      configuration = tree_object.get("configuration")
    else:
      raise CraftAiDecisionError(
        """Invalid decision tree format, {} is not a supported"""
        """ version.""".
        format(tree_version)
      )
    return bare_tree, configuration, tree_version
