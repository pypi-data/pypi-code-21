#!/usr/bin/env python
import numpy as np
import glfw
from gym import Env
from gym.spaces import Box
from mujoco_py import MjSim, MjViewer, const

from gym_morph import SPECIES, TASK
from gym_morph.model import build_robot


class MorphEnv(Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, species='ant', task='run'):
        assert species in SPECIES, 'Invalid species "{}"'.format(species)
        assert task in TASK, 'Invalid task "{}"'.format(task)
        self.species = species
        self.task = task
        self.current_seed = 0  # Used to generate random initial states
        self.sim = MjSim(build_robot(species))
        ctrlrange = self.sim.model.actuator_ctrlrange
        self.action_space = Box(ctrlrange[:, 0], ctrlrange[:, 1])
        self.viewer = None

    def _reset(self):
        self.current_seed += 1
        rs = np.random.RandomState(self.current_seed)

        for i, q in enumerate(self.sim.model.jnt_qposadr):
            if self.sim.model.jnt_type[i] != const.JNT_FREE:
                jnt_range = self.sim.model.jnt_range[i]
                self.sim.data.qpos[q] = rs.uniform(jnt_range[0], jnt_range[1])
            else:  # Free joint, only set angle, not position
                quat = rs.uniform(0, 1, size=4)  # Random quaternion
                quat /= np.sqrt(np.sum(np.square(quat)))  # Normalize
                self.sim.data.qpos[q + 3:q + 7] = quat

        # TODO: Use seed to generate random goal
        self.last_torso_xpos = self.sim.data.get_body_xpos('torso').copy()
        return self._get_obs()

    def _get_obs(self):
        # TODO: input goal locations relative to body pose
        return np.concatenate([self.sim.data.qpos, self.sim.data.qvel])

    def _get_reward(self):
        if self.task == 'run':
            # Reward is velocity in the x direction
            xpos = self.sim.data.get_body_xpos('torso')
            reward = xpos[0] - self.last_torso_xpos[0]
            self.last_torso_xpos = xpos.copy()
            return reward
        return 0.

    def _set_action(self, action):
        action = np.asarray(action)
        assert self.action_space.contains(action), '{}'.format(action)
        self.sim.data.ctrl[:] = action

    def _step(self, action):
        self._set_action(action)
        self.sim.step()
        obs = self._get_obs()
        reward = self._get_reward()
        done = False  # TODO
        info = {}  # TODO
        return obs, reward, done, info

    def _render(self, mode='human', close=False):
        assert mode == 'human'  # TODO: rgb_array rendering
        if close and self.viewer is not None:
            glfw.destroy_window(self.viewer.window)
        else:
            if self.viewer is None:
                self.viewer = MjViewer(self.sim)
            self.viewer.render()

    def _seed(self, seed=None):
        if seed is not None:
            self.seed = seed
        return [self.seed]
