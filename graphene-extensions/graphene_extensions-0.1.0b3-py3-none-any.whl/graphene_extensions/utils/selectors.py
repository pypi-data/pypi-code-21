from graphql.execution.base import ResolveInfo
from typing import Dict

from graphql.language.ast import SelectionSet

Selector = Dict[str, Dict]


def get_selectors_from_selection_set(selection_set: SelectionSet) -> Selector:
    return {
        selection.name.value: get_selectors_from_selection_set(selection.selection_set)
        for selection in selection_set.selections
    } if selection_set else None


def get_selectors_from_info(info: ResolveInfo) -> Selector:
    return get_selectors_from_selection_set(info.field_asts[0].selection_set)


def strip_relay_selectors(selector: Selector):
    result_selector = selector.copy()
    for field, selection in result_selector.items():
        if field == 'edges' and isinstance(selection, dict) and 'node' in selection:
            return strip_relay_selectors(selection['node'])
        elif isinstance(selection, dict):
            result_selector[field] = strip_relay_selectors(selection)
    return result_selector
