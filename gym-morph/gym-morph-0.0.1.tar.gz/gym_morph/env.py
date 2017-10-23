#!/usr/bin/env python
import os
import numpy as np
import glfw
from gym import Env
from mujoco_py import load_model_from_path, MjSim, MjViewer


# Based on the MuJoCo Ant model
SPECIES = ['longleg',  # morphing - extends first leg joint
           'longfoot',  # morphing - extends second leg joint
           'insect',  # non-morphing - 6 two-joint legs
           'lifter',  # non-morphing - extra lifing joint in hip
           'triple',  # non-morphing - three leg joints
           'ant']  # non-morphing - 4 two-joint legs

TASK = ['run',  # Run as fast as possible in a single direction
        'flagrun',  # Run to a specified 2d location
        'twister']  # Place foot on a specified spot


class MorphEnv(Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, species='ant', task='run'):
        assert species in SPECIES, 'Invalid species'
        self.species = species
        self.task = task
        self.current_seed = 0  # Used to generate random initial states
        # TODO: modify based on species and task
        curdir = os.path.dirname(__file__)
        self.sim = MjSim(load_model_from_path(os.path.join(curdir, 'ant.xml')))
        self.viewer = None

    def _reset(self):
        # Use seed to generate random state
        # Use random state to generate:
        #   init pos, init rotation, init joint position, task goal locations
        self.current_seed += 1
        # random_state = np.random.RandomState(self.current_seed)
        return self._get_obs()

    def _get_obs(self):
        # TODO: input goal locations relative to body pose
        return np.concatenate([self.sim.data.qpos, self.sim.data.qvel])

    def _step(self):
        obs = self._get_obs()
        reward = 0  # TODO
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
