from numpy import array, float64, zeros, dot, transpose


class Neuron:
    """
    Neuron primitive.
    Attributes:
        weights_ : list of floats
            Weight coefficients for each input of sensor layer. Should be initialized
            * default : None

        bias_ : float
            Neuron bias value. Should be initialized
            * default : None

        input_size : int
            Size of input data vector

        function : method (float)
            Activation function. One from tools.activation can be used

        *params : tuple
            Activation function parameters
    """

    def __init__(self, input_size, function, *func_params, weights=None, bias=None):
        self.input_size = input_size
        self.function = function
        self.weights = array(weights)
        self.bias = float64(bias)
        self.func_params = func_params
        if weights is None or bias is None:
            self.initialize_net()

    def initialize_net(self):
        """
        Assigns zero weights and bias
        """
        self.weights = zeros(self.input_size)
        self.bias = 0

    def _calc(self, x):
        """ Unit's calculation method
        :param x : np.array
            Input signal
        :return: net(x)
            Network answer
        """

        return self.function(self._inducted_field(x), *self.func_params)

    def _inducted_field(self, x):
        """ Inducted field counting method
        :param x: np.array(float)
            Input signal
        :return: float64
            Field inducted by perceptron
        """

        return dot(self.weights, transpose(x)) + self.bias
