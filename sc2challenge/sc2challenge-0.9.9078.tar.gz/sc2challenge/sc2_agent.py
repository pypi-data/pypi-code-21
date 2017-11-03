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
        self._send_metrics('reset')

    def step(self, obs):
        ret = super(SC2Agent, self).step(obs)
        self._send_metrics('step')
        return ret

    def _send_metrics(self, stage):
        if self._analytics is not None:
            self._analytics.track(self.team, stage, {
                'episodes': int(self.episodes),
                'steps': int(self.steps),
                'reward': int(self.reward)
            })
