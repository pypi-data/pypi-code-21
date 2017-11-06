import os
import unittest

import numpy as np

from .sc2_agent import SC2Agent, MODE_EXPLORATION, MODE_EXPLOITATION


class TestSC2Agent(unittest.TestCase):
    def setUp(self):
        self.token = os.getenv('METRICS_TOKEN', None)
        self.team = 'test'

    def test_init_with_token(self):
        agent = SC2Agent(token=self.token, team='test')
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
        agent = SC2Agent(token=self.token, team=self.team)
        agent.setup(None, None)
        self.assertIsNotNone(agent)
        self.assertEqual(agent.episodes, 0)
        agent.reset()
        self.assertEqual(agent.episodes, 1)
        agent.reset()
        self.assertEqual(agent.episodes, 2)

    def test_step(self):
        agent = SC2Agent(token=self.token, team=self.team)
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

    def test_has_sample_collection(self):
        agent = SC2Agent(token=self.token, team=self.team)
        self.assertIsNotNone(agent.samples)

    def test_mode(self):
        agent = SC2Agent(token=self.token, team=self.team)
        agent.setup(None, None)
        self.assertEqual(agent.mode, MODE_EXPLORATION)
        agent.exploration_rate = 0.0
        agent.reset()
        self.assertEqual(agent.mode, MODE_EXPLOITATION)
        agent.exploration_rate = 1.0
        agent.reset()
        self.assertEqual(agent.mode, MODE_EXPLORATION)

    def test_exploration_is_called(self):
        agent = MockAgent(token=self.token, team=self.team, exploration_rate=1.0)
        agent.setup(None, None)
        self.assertEqual(agent.exploration_called, 0)
        obs = DummyObservation()
        agent.mode = MODE_EXPLORATION
        agent.step(obs)
        self.assertEqual(agent.exploration_called, 1)
        self.assertEqual(agent.exploration_called_args['obs'], obs)

    def test_exploitation_is_called(self):
        agent = MockAgent(token=self.token, team=self.team, exploration_rate=0.0)
        agent.setup(None, None)
        self.assertEqual(agent.exploitation_called, 0)
        obs = DummyObservation()
        agent.mode = MODE_EXPLOITATION
        agent._model = DummyModel()
        agent.step(obs)
        self.assertEqual(agent.exploitation_called, 1)
        self.assertEqual(agent.exploitation_called_args['model'], agent._model)
        self.assertEqual(agent.exploitation_called_args['obs'], obs)

    def test_create_model_called_before_first_train(self):
        agent = MockAgent(token=self.token, team=self.team, training_frequency=1)
        agent.setup(None, None)
        self.assertIsNone(agent._model)
        self.assertEqual(agent.create_model_called, 0)
        agent.samples.add(sample_x=[1, 2, 3], sample_y=[4, 5])
        agent.reset()
        self.assertEqual(agent.create_model_called, 1)

    def test_train_is_called_each_X_episodes(self):
        for frequency in range(1, 3):
            agent = MockAgent(token=self.token, team=self.team, training_frequency=frequency)
            agent.setup(None, None)
            agent._model = DummyModel()
            agent.samples.add(sample_x=[1, 2, 3], sample_y=[4, 5])
            agent.samples.add(sample_x=[6, 7, 8], sample_y=[9, 0])

            for passes in range(5):
                for _ in range(frequency - 1):
                    agent.reset()
                    self.assertEqual(agent.train_called, passes)
                agent.reset()
                self.assertEqual(agent.train_called, passes + 1)
                self.assertEqual(agent.train_called_args['model'], agent._model)
                self.assertListEqual(agent.train_called_args['train_x'].tolist(), agent.samples.get_train_x().tolist())
                self.assertListEqual(agent.train_called_args['train_y'].tolist(), agent.samples.get_train_y().tolist())

    def test_train_is_not_called_if_no_samples(self):
        agent = MockAgent(token=self.token, team=self.team, training_frequency=3)
        agent.setup(None, None)
        agent._model = DummyModel()

        for _ in range(10):
            agent.reset()
            self.assertEqual(agent.train_called, 0)

    def test_train_should_return_a_trained_model(self):
        agent = MockAgent(token=self.token, team=self.team, training_frequency=1)
        agent.setup(None, None)
        agent.reset()


class DummyObservation:
    def __init__(self):
        self.reward = np.int64(0)


class DummyModel:
    def __init__(self):
        pass

    def fit(self):
        pass


class MockAgent(SC2Agent):
    def __init__(self, token, team, training_frequency=1, exploration_rate=0.5):
        super().__init__(token=token, team=team, training_frequency=training_frequency,
                         exploration_rate=exploration_rate)
        self.create_model_called = 0
        self.train_called = 0
        self.train_called_args = {}
        self.exploration_called = 0
        self.exploration_called_args = {}
        self.exploitation_called = 0
        self.exploitation_called_args = {}

    def exploration(self, obs):
        self.exploration_called += 1
        self.exploration_called_args['obs'] = obs
        return super().exploration(obs)

    def exploitation(self, model, obs):
        self.exploitation_called += 1
        self.exploitation_called_args['model'] = model
        self.exploitation_called_args['obs'] = obs
        return super().exploitation(model, obs)

    def create_model(self):
        self.create_model_called += 1
        return DummyModel()

    def train(self, model, train_x, train_y):
        self.train_called += 1
        self.train_called_args['model'] = model
        self.train_called_args['train_x'] = train_x
        self.train_called_args['train_y'] = train_y
        return super().train(model, train_x, train_y)
