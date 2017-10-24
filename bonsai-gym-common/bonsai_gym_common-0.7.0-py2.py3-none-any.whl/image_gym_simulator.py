from bonsai.simulator import SimState
from bonsai.inkling_types import Luminance
from bonsai_gym_common import GymSimulator

IMAGE_DEQUE_SIZE = 4


class ImageGymSimulator(GymSimulator):

    """Handles openAI gyms with raw pixel data."""

    def __init__(self, env, record_path, width, height, downsample):
        self.width = width
        self.height = height
        self.downsample = downsample
        super(ImageGymSimulator, self).__init__(env, skip_frame=4,
                                                record_path=record_path)
        self.set_deque_size(IMAGE_DEQUE_SIZE)

    def process_observation(self, obvs):
        """
        Calculates the luminance of the values for the image and
        performs nice preprocessing.
        """

        R = obvs[:, :, 0]
        G = obvs[:, :, 1]
        B = obvs[:, :, 2]

        # Calculates weighted apparent brightness values
        # according to https://en.wikipedia.org/wiki/Relative_luminance
        obvs = 0.2126 * R + 0.7152 * G + 0.0722 * B

        # Normalize the observations.
        obvs /= 255.0

        # should be replaced with tranformd
        obvs = obvs[::self.downsample, ::self.downsample]

        return obvs.ravel().tolist()

    def get_state(self):
        parent_state = GymSimulator.get_state(self)
        return SimState({"observation": parent_state.state},
                        parent_state.is_terminal)

    def get_state_schema(self, state):
        return Luminance(
            int(self.width / self.downsample),
            int(self.height * self.DEQUE_SIZE / self.downsample), state)
