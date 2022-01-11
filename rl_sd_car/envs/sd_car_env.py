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
        self.action_space = spaces.Discrete(5,)
        '''
        left
        right
        acc
        brake
        nothing
        '''

        # Define observation space
        '''
        velocity (only x)
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

        # if we took an action, we were in state 1
        observation = np.array([5.0, 360.0, 1.0, 1.0])
        if action == 2:
            reward = 1
        else:
            reward = -1
        # regardless of the action, game is done after a single step
        done = True

        info = {}

        return observation, reward, done, info

    def calculate_reward():
        pass

    def reset(self):

        state: np.array = np.array([0.0, 0.0, 1.0, 1.0])

        return state

    def render(self, mode='human'):
        pass

    def close(self):
        pass
