import numpy as np
from copy import deepcopy

from ..errors import InvalidConfigError

class Variable(object):
    def __init__(self, name, var_type, domain, dimensionality):
        self.name = name
        self.domain = domain
        self.type = var_type
        self.dimensionality = dimensionality

    def is_continuous(self):
        return False

    def expand(self):
        """
        Builds a list of single dimensional variables representing current variable.

        Examples:
        For single dimensional variable, it is returned as is
        discrete of (0,2,4) -> discrete of (0,2,4)
        For multi dimensional variable, a list of variables is returned, each representing a single dimension
        continuous {0<=x<=1, 2<=y<=3} -> continuous {0<=x<=1}, continuous {2<=y<=3}
        """
        expanded_variables = []
        for i in range(self.dimensionality):
            one_d_variable = deepcopy(self)
            one_d_variable.dimensionality = 1
            if self.dimensionality > 1:
                one_d_variable.name = '{}_{}'.format(self.name, i+1)
            else:
                one_d_variable.name = self.name
            one_d_variable.dimensionality_in_model = 1
            expanded_variables.append(one_d_variable)
        return expanded_variables

    def objective_to_model(self, x_objective):
        """
        Translates objective input to model input
        with respect to current variable
        """
        return [x_objective]

    def model_to_objective(self, x_model, index_in_model):
        """
        Translates model input to objective input
        with respect to current variable
        """
        return [x_model[0, index_in_model]]

    def get_bounds(self):
        """
        Returns a list of tuples representing bounds of the variable
        """
        pass

    def get_possible_values(self):
        """
        Returns a list of possible variable values
        """
        pass

    def set_index_in_objective(self,index):
        """
        Allows to set the index of this variable in the objective space
        """
        self.index_in_objective = index

    def set_index_in_model(self,index):
        """
        Allows to set the index of this variable in the model space
        """
        self.index_in_model = index


class ContinuousVariable(Variable):
    def __init__(self, name, domain, dimensionality=1):
        super(ContinuousVariable, self).__init__(name, 'continuous', domain, dimensionality)

    def get_bounds(self):
        return [self.domain] * self.dimensionality

    def is_continuous(self):
        return True

    def is_bandit(self):
        return False

    def get_possible_values(self):
        raise AttributeError("Impossible to produce a list of values for continuous variable " + self.name)


class BanditVariable(Variable):
    def __init__(self, name, domain, dimensionality=None):
        dims = np.array([len(d) for d in domain])
        if not np.all(dims == dims[0]):
            raise InvalidConfigError('The dimensionalities of the bandit variable ' + name + ' have to be the same!')

        if dimensionality is None:
            dimensionality = len(domain[0])

        super(BanditVariable, self).__init__(name, 'bandit', domain, dimensionality)

    def objective_to_model(self, x_objective):
        return x_objective

    def is_bandit(self):
        return True

    def model_to_objective(self, x_model):
        return x_model

    def expand(self):
        one_d_variable = BanditVariable(self.name, self.domain, None)
        one_d_variable.dimensionality_in_model = self.domain.shape[1]

        return [one_d_variable]

    def get_bounds(self):
        return [(min(self.domain[:,d]), max(self.domain[:,d])) for d in range(self.domain.shape[1])]

    def get_possible_values(self):
        return self.domain


class DiscreteVariable(Variable):
    def __init__(self, name, domain, dimensionality = 1):
        super(DiscreteVariable, self).__init__(name, 'discrete', domain, dimensionality)

    def get_bounds(self):
        return [(min(self.domain), max(self.domain))]

    def get_possible_values(self):
        return self.domain

    def is_bandit(self):
        return False

class CategoricalVariable(Variable):
    def __init__(self, name, domain, dimensionality = 1):
        super(CategoricalVariable, self).__init__(name, 'categorical', domain, dimensionality)

    def expand(self):
        expanded_variables = super(CategoricalVariable, self).expand()
        for v in expanded_variables:
            v.dimensionality_in_model = len(self.domain)
        return expanded_variables

    def objective_to_model(self, x_objective):
        entry = [0] * self.dimensionality_in_model
        entry[int(x_objective)] = 1
        return entry

    def model_to_objective(self, x_model, index_in_model):
        vardim = self.dimensionality_in_model
        original_entry = x_model[0, index_in_model:(index_in_model+vardim)]
        entry = sum(x * y for x, y in zip(range(vardim), original_entry))
        return [entry]

    def get_bounds(self):
        return [(0,1)] * self.dimensionality_in_model

    def get_possible_values(self):
        return np.eye(len(self.domain))

    def is_bandit(self):
        return False


def create_variable(descriptor):
    """
    Creates a variable from a dictionary descriptor
    """
    if descriptor['type'] == 'continuous':
        return ContinuousVariable(descriptor['name'], descriptor['domain'], descriptor.get('dimensionality', 1))
    elif descriptor['type'] == 'bandit':
        return BanditVariable(descriptor['name'], descriptor['domain'], descriptor.get('dimensionality', None))  # bandits variables cannot be repeated
    elif descriptor['type'] == 'discrete':
        return DiscreteVariable(descriptor['name'], descriptor['domain'], descriptor.get('dimensionality', 1))
    elif descriptor['type'] == 'categorical':
        return CategoricalVariable(descriptor['name'], descriptor['domain'], descriptor.get('dimensionality', 1))
    else:
        raise InvalidConfigError('Unknown variable type ' + descriptor['type'])
