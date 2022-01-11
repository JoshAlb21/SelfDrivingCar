import gym
from gym import error, spaces, utils
from gym.utils import seeding


class SdCarEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):

        ...

    def step(self, action):
        ...

    def reset(self):
        ...

    def render(self, mode='human'):
        ...

    def close(self):
        ...

    super(ChopperScape, self).__init__()

    # Define a 2-D observation space
    self.observation_shape = (600, 800, 3)
    self.observation_space = spaces.Box(low=np.zeros(self.observation_shape),
                                        high=np.ones(self.observation_shape),
                                        dtype=np.float16)

    # Define an action space ranging from 0 to 4
    self.action_space = spaces.Discrete(6,)

    # Create a canvas to render the environment images upon
    self.canvas = np.ones(self.observation_shape) * 1

    # Define elements present inside the environment
    self.elements = []

    # Maximum fuel chopper can take at once
    self.max_fuel = 1000

    # Permissible area of helicper to be
    self.y_min = int(self.observation_shape[0] * 0.1)
    self.x_min = 0
    self.y_max = int(self.observation_shape[0] * 0.9)
    self.x_max = self.observation_shape[1]
