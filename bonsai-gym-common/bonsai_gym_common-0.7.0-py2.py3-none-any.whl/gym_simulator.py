import argparse
import logging
import numpy
import os
import time
from collections import deque
from functools import reduce

import bonsai

log = logging.getLogger(__name__)

INFINITY = -1
RECORDING_TIME = 40*60*60
MAX_SECONDS_WITHOUT_LOG = 10


class GymSimulator(bonsai.Simulator):

    CLASSIFIER = 0
    ESTIMATOR = 1

    def _parse_sim_arguments(self):
        """ Parses only the command line arguments specific to GymSimulator.
        """
        parser = argparse.ArgumentParser(
            description="Command line parser for only the subset of arguments "
                        "specific to GymSimulator")

        headless_help = (
            "The simulator can be run with or without the graphical "
            "environment. By default the graphical environment is shown. "
            "Using --headless will run the simulator without graphical "
            "output. This may be set as BONSAI_HEADLESS in the environment.")

        parser.add_argument("--headless", help=headless_help,
                            action="store_true",
                            default=os.environ.get('BONSAI_HEADLESS', False))

        try:
            args, unknown = parser.parse_known_args()
        except SystemExit:
            # --help specified by user. Continue, so as to print rest of help
            # from (brain_server_connection).
            print("")
            return None
        return args

    def __init__(self, env, skip_frame=1, record_path=None,
                 random_seed=None, interface=None, episode_limit=INFINITY):
        """The constructor: Initialize the simulator parameters.
        """
        sim_args = self._parse_sim_arguments()
        if sim_args is None:
            return

        bonsai.Simulator.__init__(self)
        # Simulator parameters.all.
        self.env = env
        self.DEQUE_SIZE = 1
        # TODO: Make this into a dictionary to conform to the new API
        self._state_deque = deque(maxlen=self.DEQUE_SIZE)
        self._terminal = False
        self._episode_number = 0
        self._frame_count = 0
        self._episode_start_frame = 0
        self._reward = 0
        self.EPISODE_LENGTH = episode_limit
        self._start_time = time.time()
        self._last_log_time = time.time()
        self._is_recording = True if record_path else False
        self._skip_frame = skip_frame
        self.interface = self.CLASSIFIER if interface is None else interface
        self.gym_total_reward = 0.0
        self._render_env = not sim_args.headless
        # TODO: Support multiple actuators by setting the size of
        # the ndarray with the inkling/server message
        self._action = (0 if self.interface == self.CLASSIFIER else
                        numpy.asarray([0]))
        self.env.seed(random_seed)

        self.reset()
        if self._is_recording:
            self.env.monitor.start(record_path)

    def _append_state(self, current_state):
        """This method appends the current state to the state deque.
        """
        self._state_deque.append(current_state)
        # Append the same frames into the deque if the real data size
        # in deque is less than the capacity of deque.
        while len(self._state_deque) < self._state_deque.maxlen:
            self._state_deque.append(current_state)

    def reset(self):
        """This method resets all state related parameters and adds
        the first observation.
        """
        if self._terminal:
            log.info("Episode %s reward is %s",
                     self._episode_number, self.gym_total_reward)
            self._last_log_time = time.time()
            self._episode_number += 1
            self._reward = 0.0

        self.gym_total_reward = 0.0
        self._state_deque.clear()
        first_state = self.process_observation(self.env.reset())
        self._append_state(first_state)
        self._episode_start_frame = self._frame_count
        self._terminal = False

    def set_properties(self, **kwargs):
        """Set the properties of gym simulation.
        """
        if "episode_length" in kwargs:
            self.EPISODE_LENGTH = kwargs["episode_length"]
            log.debug("Gym episode length set to: %s", self.EPISODE_LENGTH)
        if "deque_size" in kwargs:
            self.set_deque_size(kwargs["deque_size"])
            log.debug("Gym deque size set to: %s", self.DEQUE_SIZE)
        return True

    def set_deque_size(self, size):
        """
        Sets the active memory length of the observer.
        """
        self.DEQUE_SIZE = size
        old_deque = self._state_deque
        self._state_deque = deque(maxlen=self.DEQUE_SIZE)

        states = []
        while len(old_deque) > 0:
            states.append(old_deque.popleft())

        for state in states:
            self._append_state(state)

    def _check_terminal(self, done):
        """
        Checks if a Gym episode has completed.
        """
        if (done or
            ((self._frame_count > self.EPISODE_LENGTH +
                self._episode_start_frame)
             and self.EPISODE_LENGTH != INFINITY)):
            self._terminal = True
            self._episode_start_frame = self._frame_count
        else:
            self._terminal = False

    def process_observation(self, obvs):
        """
        Calculates the luminance of the values for the image and
        performs nice preprocessing.
        """

        return obvs

    def get_state_schema(self, state):
        # This is tied with T214
        return state

    def get_gym_action(self, actions):
        if self.interface == self.CLASSIFIER:
            return actions['command']
        else:
            return numpy.asarray([actions['command']])

    def advance(self, actions):
        """
        This method should apply the input action to advance the game
        to the next state, and then it should return that state and the
        reward from advancing to that state. It should also return a
        boolean is_terminal, indicating if the game ended (this could happen
        if all the bricks are broken, or if we run out of lives, or if
        should_stop was specfiied as true).

        If the input should_stop is true, the game should stop, and it
        should re-initialize itself to the starting state based on the
        hardcoded properties.

        If the game itself is terminal (for example you ran out of lives,
        or you broke all the bricks), reset the game as well as ai settings.
        """
        # Step 0: Check if we need to reset or move forward the episode.
        if self._terminal:
            self.reset()
            return

        # Step 1: Perform the action and update the game along with
        # the reward.
        average_reward = 0
        for i in range(self._skip_frame):
            action = self.get_gym_action(actions)
            observation, reward, done, info = self.env.step(action)
            self._frame_count += 1
            average_reward += reward
            self.gym_total_reward += reward

            # Step 2: Render the game.
            if self._render_env:
                self.env.render()

            if done:
                break
        self._reward = average_reward / (i + 1)

        time_from_start = time.time() - self._start_time
        if self._is_recording and (time_from_start > RECORDING_TIME):
            self.env.monitor.close()

        # Step 3: Get the current frames, and append it to deque to get current
        # state.
        current_frame = self.process_observation(observation)
        self._append_state(current_frame)

        # Step 4: Check if we should reset
        self._check_terminal(done)

        # Log a message if this episode has been running for a while
        if self._last_log_time + MAX_SECONDS_WITHOUT_LOG < time.time():
            log.info("Episode %s is still running, reward so far is %s",
                     self._episode_number, self.gym_total_reward)
            self._last_log_time = time.time()

    def get_state(self):
        # We append all of the states in the deque by adding the rows.
        current_state = reduce(
            lambda accum, state: accum + state, self._state_deque)

        # Convert the observation to an inkling schema.
        return bonsai.simulator.SimState(self.get_state_schema(current_state),
                                         self._terminal)

    def open_ai_gym_default_objective(self):
        return self._reward
