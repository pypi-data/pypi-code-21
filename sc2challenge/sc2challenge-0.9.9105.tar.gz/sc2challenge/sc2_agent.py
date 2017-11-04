from random import random as randfloat

from absl import logging
from mixpanel import Mixpanel
from pysc2.agents.base_agent import BaseAgent
from pysc2.lib import actions

from .training_sample_store import TrainingSampleStore

MODE_EXPLORATION = 0
MODE_EXPLOITATION = 1


class SC2Agent(BaseAgent):
    def __init__(self, token=None, team='anonymous', exploration_rate=0.1, training_frequency=5):
        super(SC2Agent, self).__init__()
        self.team = team
        self.samples = TrainingSampleStore()
        self.mode = MODE_EXPLORATION
        self.exploration_rate = exploration_rate
        self._model = None
        self.training_frequency = training_frequency

        self._analytics = None
        if token is not None:
            self._analytics = Mixpanel(token)

        if self._analytics is not None:
            self._analytics.track(self.team, 'init', {
                'team': self.team
            })

    def reset(self):
        super(SC2Agent, self).reset()
        self.steps = 0
        self.reward = 0
        self.mode = MODE_EXPLORATION if randfloat() < self.exploration_rate else MODE_EXPLOITATION
        self._send_metrics('episode')

        if len(self.samples) > 0 and self.episodes % self.training_frequency == 0:
            self.train(model=self._model, train_x=self.samples.get_train_x(), train_y=self.samples.get_train_y())

    def step(self, obs):
        super(SC2Agent, self).step(obs)

        if (self.steps - 1) % 10 == 0:
            logging.info('-----------------------------------------------')
            logging.info('| Ep. | Step | Reward | Samples | Mode | Rate | (Mode 0:Exploration 1:Exploitation)')
            logging.info('-----------------------------------------------')
        logging.info('| %3d | %4d | %6d | %7d | %4d | %.2f |' %
                     (self.episodes, self.steps, self.reward, len(self.samples), self.mode, self.exploration_rate))

        self._send_metrics('step')

        if self._model is None:
            self._model = self.create_model(obs)

        if self.mode == MODE_EXPLORATION:
            return self.exploration(obs)
        return self.exploitation(model=self._model, obs=obs)

    def _send_metrics(self, stage):
        if self._analytics is not None:
            self._analytics.track(self.team, stage, {
                'team': self.team,
                'episodes': int(self.episodes),
                'steps': int(self.steps),
                'reward': int(self.reward),
            })

    def exploration(self, obs):
        assert self
        if obs is None:
            raise Exception('observation not provided')
        return actions.FunctionCall(0, [])

    def exploitation(self, model, obs):
        assert self
        assert model
        assert obs
        return actions.FunctionCall(0, [])

    def create_model(self, obs):
        assert self
        assert obs
        return None

    def train(self, model, train_x, train_y):
        assert self
        assert model
        assert len(train_x)
        assert len(train_y)
        return
