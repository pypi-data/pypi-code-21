""" One layered Rosenblatt's perceptron
"""

from numpy.random import shuffle
from numpy import append, array
from ..tools.loss import get_loss
from ..basics.neuron import Neuron


class Perceptron(Neuron):
    """
        Single-perceptron.

        Parameters:

            input_size : int
                Size of input data vector

            learning_rate : float
                Weights changing rate
                * default : 0.001

            epochs : int
                Maximum count of iterations in learning algorithm. The solver iterates until convergence
                (determined by 'tolerance') or this number of iterations
                * 0 value means having no limit for iterations
                * default : 0

            tol : float
                Required net() accuracy

        Attributes:

            loss_value : float
                Current value of loss function. Should be initialized
                * default : None

            train_input : 2d np_array of float
                Learning data set (list of input data vectors)
                * default : None

            train_output : np_array of float
                Expected net(x_)
                * default : None

            save_w_hist : bool
                Weight saving on/off indicator
                * default : False

            w_hist : 2d list of weight history

    """

    def __init__(self, input_size, function, *func_params, loss_func='mae', learning_rate=0.001,
                 epochs=100, tol=1e-4, weights_=None, bias_=None, save_w_hist=False):
        super().__init__(input_size, function, *func_params, weights=weights_, bias=bias_)
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.train_input = None
        self.train_output = None
        self.n_epoch = 0
        self.tol = tol
        self.loss_func = get_loss(loss_func)
        self.loss_value = None
        self.save_history = save_w_hist
        self.w_hist = []
        self.loss_hist = []
        self.epoch_hist = []

    def put_data(self, train_input, train_output):
        """
        :param train_input: input learning vectors
        :param train_output: expected output vector
        """
        assert len(train_input) == len(train_output), 'Wrong data-set! ERR: Count of learning input vectors'
        self.train_input = train_input.copy()
        self.train_output = train_output.copy()

    def calc(self, x):
        """
        :param x: numpy array(recommended) or list
            input single vector
        :return: float
            perceptron output
        """
        return self._calc(x)

    def feed_fwd(self, vecs):
        """
        :param vecs:
            input dataset
        :return: float
            perceptron output
        """
        return [self._calc(vec) for vec in vecs]

    def learn(self, df):
        """
        Learning procedure. Executes learning methods up to set.
        :param
                df: method
            Derivative of activation function. One from tools.activation can be used

                loss: {'mae', 'mse'}
            Loss function.
                * default 'mae'
        :return final loss value
        """

        self.w_hist.append(append(self.weights, [self.bias]))


        return self._learn_rosenblatt(df)

    def _learn_rosenblatt(self, derivative):
        """Sgn function type convergence learning"""
        assert self.train_input is not None, 'ERR: Define input vectors learning set'
        assert self.train_output is not None, 'ERR: Define output learning set'
        assert self.weights is not None, 'ERR: Weights are not initialized'
        assert self.bias is not None, 'ERR: Bias is not initialized'

        # 1. initialization
        train = list(zip(self.train_input, self.train_output))

        for n_epoch in range(1, self.epochs + 1):

            outs = []
            calcs = []

            for x, out in train:
                x = array(x)
                # 2. loss saving
                outs.append(out)
                calcs.append(self._calc(x))

                loss_ = - calcs[-1] + out

                # 3. weight adapting
                self.weights += self.learning_rate * loss_ * x * \
                                derivative(x, *self.func_params)
                self.bias += self.learning_rate * loss_ * \
                                derivative(x, *self.func_params)

                # 4. history saving
                if self.save_history:
                    self.w_hist.append(append(self.weights, [self.bias]))

            # 5. calculation loss value
            self.loss_value = self.loss_func(array(outs), array(calcs))

            # 6. saving loss and epoch
            self.loss_hist.append(self.loss_value)
            self.epoch_hist.append(n_epoch)

            # 7. checking main end-loop condition
            if self.loss_value < self.tol:
                return self.loss_value

            # 8. shuffling learning set
            shuffle(train)

        return self.loss_value
