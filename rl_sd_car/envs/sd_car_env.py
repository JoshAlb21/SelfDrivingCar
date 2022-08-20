import re
import gym
from gym import error, spaces, utils
from gym.utils import seeding

import numpy as np
from typing import Tuple
import time
from statistics import mean

from rl_sd_car.envs.car_game import game


class SdCarEnv(gym.Env):

    metadata = {'render.modes': ['human']}

    def __init__(self):

        super().__init__()
        self.environment = game.create_game()
        self.environment.init_game()
        self.action_space = spaces.Discrete(3,)
        high: np.array = np.array([20.0, 360.0, 300.0, 300.0, 300.0, 300.0, 300.0, 300.0, 300.0])
        observation_hist: list = []
        # assumption: no negative velocity
        low: np.array = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
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
        #TODO add a time buffer in beginning after recent reset to give the agent a chance
        done = False
        n_last_steps = 30
        mean_threshold = 0.1
        vel_history = self.environment.car.get_velocity_norm_history(n_last_steps)
        #print(f'Vel history{mean(vel_history)}')
        vel_cond = len(vel_history)>(n_last_steps-1) and mean(vel_history) < mean_threshold
        track_history = self.environment.car.get_on_track_history(n_last_steps)
        track_cond = sum(track_history)==0 #False is eqal to zero

        if vel_cond or track_cond: done = True
        
        return done

    def reset(self):
        self.environment.action_handler.reset_to_start(self.environment.car, random_vel=True)
        observation = self.environment.get_rl_observation(disable_dist=True)
        self.environment.car.update_velocity_norm_history(reset_list=True)
        self.environment.car.update_on_track(on_track=False, reset_list=True)
        print('********************RESET********************')

        return observation

    def render(self, mode='human'):
        pass

    def close(self):
        pass
