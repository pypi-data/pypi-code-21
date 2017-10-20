from mixpanel import Mixpanel
from pysc2.agents.base_agent import BaseAgent


class SC2Agent(BaseAgent):
    def __init__(self, token=None, team='anonymous'):
        super(SC2Agent, self).__init__()

        self._analytics = None
        if token is not None:
            self._analytics = Mixpanel(token)

        self.team = team

        if self._analytics is not None:
            self._analytics.track(self.team, 'Sent Message')

    def reset(self):
        super(SC2Agent, self).reset()
        if self._analytics is not None:
            self._analytics.track(self.team, 'reset', {
                'episodes': self.episodes,
                'steps': self.steps,
                'reward': self.reward
            })

    def step(self, obs):
        ret = super(SC2Agent, self).step(obs)
        if self._analytics is not None:
            self._analytics.track(self.team, 'step', {
                'episodes': self.episodes,
                'steps': self.steps,
                'reward': self.reward
            })
        return ret
