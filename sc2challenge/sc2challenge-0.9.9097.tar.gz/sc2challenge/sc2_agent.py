import numpy as np
from absl import logging
from mixpanel import Mixpanel
from pysc2.agents.base_agent import BaseAgent


class SC2Agent(BaseAgent):
    def __init__(self, token=None, team='anonymous'):
        super(SC2Agent, self).__init__()
        self.team = team
        self._samples = np.array([])

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
        self._send_metrics('episode')

    def step(self, obs):
        ret = super(SC2Agent, self).step(obs)

        if (self.steps - 1) % 10 == 0:
            logging.info('---------------------------------')
            logging.info('| Ep. | Step | Reward | Samples |')
            logging.info('---------------------------------')
        logging.info('| %3d | %4d | %6d | %7d |' % (self.episodes, self.steps, self.reward, len(self._samples)))

        self._send_metrics('step')
        return ret

    def _send_metrics(self, stage):
        if self._analytics is not None:
            self._analytics.track(self.team, stage, {
                'team': self.team,
                'episodes': int(self.episodes),
                'steps': int(self.steps),
                'reward': int(self.reward),
            })

    def add_sample(self, sample_input, sample_output):
        sample = [np.array(sample_input), np.array(sample_output)]
        if len(self._samples) == 0:
            self._samples = np.array([sample])
        else:
            self._samples = np.vstack((self._samples, sample))
