import gym
from gym import error, spaces, utils
from gym.utils import seeding

import numpy as np
from typing import List


class SdCarEnv(gym.Env):

    metadata = {'render.modes': ['human']}

    def __init__(self):

        super().__init__()

        # Define an action space
        self.action_space = spaces.Discrete(6,)
        '''
        left
        right
        up
        down
        brake
        nothing
        '''

        # Define observation space
        '''
        velocity (euclidian norm)
        angle
        distance1
        distance2
        '''
        high: np.array = np.array([20.0, 360.0, 1.0, 1.0])
        # assumption: no negative velocity
        low: np.array = np.array([0.0, 0.0, 0.0, 0.0])
        self.observation_space = spaces.Box(low, high, dtype=np.float32)

    def step(self, action) -> List[np.array, float, bool, dict]:

        reward: int = 0

        observation = self.get_observation()
        reward = self.calculate_reward()
        done = self.check_done()

        info = {}

        return observation, reward, done, info

    def calculate_reward(self):
        pass

    def get_observation(self):
        #TODO 
        return np.array([5.0, 360.0, 1.0, 1.0])
    
    def check_done(self):
        #TODO check collision or time steps
        pass

    def reset(self):
        #TODO check collision
        reset_state: np.array = np.array([0.0, 0.0, 1.0, 1.0])

        return reset_state

    def render(self, mode='human'):
        pass

    def close(self):
        pass
