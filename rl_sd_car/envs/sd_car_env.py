import gym
from gym import error, spaces, utils
from gym.utils import seeding

import numpy as np
from typing import Tuple
import time

from rl_sd_car.envs.car_game import game


class SdCarEnv(gym.Env):

    metadata = {'render.modes': ['human']}

    def __init__(self):

        super().__init__()
        self.environment = game.create_game()
        self.environment.init_game()
        self.action_space = spaces.Discrete(6,)
        high: np.array = np.array([20.0, 360.0, 1.0, 1.0])
        observation_hist: list = []
        # assumption: no negative velocity
        low: np.array = np.array([0.0, 0.0, 0.0, 0.0])
        self.observation_space = spaces.Box(low, high, dtype=np.float32)

    def step(self, action) -> Tuple[np.array, float, bool, dict]:

        self.environment.set_rl_action(action)
        self.environment.game_loop_function()
        observation = self.environment.get_rl_observation()
        reward = self.calculate_reward()
        done = self.check_done()

        info = {}

        return observation, reward, done, info

    def calculate_reward(self) -> float:
        reward = self.environment.reward_account.get_latest_rewards()
        return reward

    def check_done(self):
        done = False
        return done

    def reset(self):
        self.environment.action_handler.reset_to_start(self.environment.car)
        observation = self.environment.get_rl_observation(disable_dist=True)

        return observation

    def render(self, mode='human'):
        pass

    def close(self):
        pass
