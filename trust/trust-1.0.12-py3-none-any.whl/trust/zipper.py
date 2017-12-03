class Zipper():
    def __init__(self, child, parent, logger=None):
        self._child = child
        self._parent = parent
        self._logger = logger or logging.getLogger(__name__)

    def zip(self):
        actions = ["merge"]

        if type(self._child) is not dict:
            self._logger.debug("Child is not a dict. Returning.")
            return self._child
        else:
            self._logger.debug("Child as keys %s.", self._child.keys())
            if ".special:actions" in self._child.keys():
                actions = self._child[".special:actions"]
                self._logger.debug("Using custom actions %s.", actions)
                if type(self._parent) is list:
                    return self._combine_with_parent_list(actions)

        if type(self._parent) is not dict:
            return self._parent

        return self._combine_element(
            actions,
            self._combine_on_both,
            self._combine_on_child,
            self._combine_on_parent
        )

    def _combine_with_parent_list(self, actions):
        """
        Combines a child and a parent when the parent is a list.
        """
        if "add" in actions:
            return self._add_array()

        if "merge" in actions:
            return self._merge_array()

    def _add_array(self):
        values_to_add = self._child[".special:values"]
        return self._parent + values_to_add

    def _merge_array(self):
        return list(set(self._add_array()))

    def _combine_on_both(self, actions, child_element, parent_element):
        if "replace" in actions or "merge" in actions:
            return Zipper(child_element, parent_element, self._logger).zip()

    def _combine_on_child(self, actions, child_element):
        if "replace" in actions or "merge" in actions:
            return child_element

    def _combine_on_parent(self, actions, parent_element):
        if "replace" in actions:
            # Do nothing, since child is replacing the parent.
            return None

        if "merge" in actions:
            return parent_element

    def _combine_element(self, actions, on_both, on_child, on_parent):
        child_keys = (self._child.keys()
                      if type(self._child) is dict
                      else [])

        parent_keys = (self._parent.keys()
                       if type(self._parent) is dict
                       else [])

        parent_items = (self._parent.items()
                        if type(self._parent) is dict
                        else [])

        result = {}

        for parent_key, parent_value in parent_items:
            if parent_key in child_keys:
                # The element exists both in child and parent.
                self._logger.debug(
                    "Combining parent and child %s using actions %s.",
                    parent_key, actions
                )

                new = on_both(actions, self._child[parent_key], parent_value)
                if new:
                    result[parent_key] = new

            elif parent_key != ".special:actions":
                # The element exists only in parent.
                self._logger.debug(
                    "Combining parent %s using actions %s.",
                    parent_key, actions
                )

                new = on_parent(actions, parent_value)
                if new:
                    result[parent_key] = new

        for child_key, child_value in self._child.items():
            if child_key != ".special:actions":
                if child_key not in parent_keys:
                    # The element exists only in child.
                    self._logger.debug(
                        "Combining child %s using actions %s.",
                        child_key, actions
                    )

                    new = on_child(actions, child_value)
                    if new:
                        result[child_key] = new

        return result
