import os
import unittest

import numpy as np
from sc2challenge import SC2Agent


class TestSC2Agent(unittest.TestCase):
    def setUp(self):
        self.token = os.getenv('METRICS_TOKEN', None)

    def test_init_with_token(self):
        agent = SC2Agent(token=self.token)
        self.assertIsNotNone(agent)

    def test_init_without_token(self):
        agent = SC2Agent()
        self.assertIsNotNone(agent)

    def test_init_with_team_id(self):
        agent = SC2Agent(team='team1')
        self.assertEqual(agent.team, 'team1')

    def test_init_without_team_id(self):
        agent = SC2Agent()
        self.assertEqual(agent.team, 'anonymous')

    def test_reset(self):
        agent = SC2Agent(token=self.token)
        agent.setup(None, None)
        self.assertIsNotNone(agent)
        self.assertEqual(agent.episodes, 0)
        agent.reset()
        self.assertEqual(agent.episodes, 1)
        agent.reset()
        self.assertEqual(agent.episodes, 2)

    def test_step(self):
        agent = SC2Agent(token=self.token)
        agent.setup(None, None)
        self.assertIsNotNone(agent)
        obs = DummyObservation()
        agent.step(obs)
        self.assertEqual(agent.reward, 0)
        agent.step(obs)
        self.assertEqual(agent.reward, 0)
        obs.reward = 1
        agent.step(obs)
        self.assertEqual(agent.reward, 1)

    def test_no_samples_at_init(self):
        agent = SC2Agent(token=self.token)
        agent.setup(None, None)
        self.assertEqual(len(agent._samples), 0)

    def test_add_sample(self):
        agent = SC2Agent(token=self.token)
        agent.setup(None, None)
        agent.add_sample(sample_input=[0, 1, 2, 3], sample_output=[4, 5])
        self.assertEqual(len(agent._samples), 1)
        self.assertEqual(len(agent._samples[0][0]), 4)
        self.assertEqual(len(agent._samples[0][1]), 2)
        agent.add_sample(sample_input=[6, 7, 8, 9], sample_output=[0, 1])
        agent.add_sample(sample_input=[2, 3, 4, 5], sample_output=[6, 7])
        self.assertEqual(len(agent._samples), 3)
        self.assertEqual(agent._samples.shape[1], 2)


class DummyObservation:
    def __init__(self):
        self.reward = np.int64(0)
