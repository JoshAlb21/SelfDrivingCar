
import gymnasium as gym
from gymnasium import spaces

import pygame
import numpy as np
from typing import Tuple
import time
from statistics import mean

from rl_sd_car.envs.car_game import game


class SdCarEnv(gym.Env):

    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 10}

    def __init__(self, render_mode=None):

        super().__init__()

        self.environment = game.create_game()
        self.environment.init_game()

        action_shape = 3
        self.action_space = spaces.Discrete(action_shape,)

        obs_shape = 9
        high: np.array = np.array([20.0, 360.0, 300.0, 300.0, 300.0, 300.0, 300.0, 300.0, 300.0])
        observation_hist: list = []
        # assumption: no negative velocity
        low: np.array = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        self.observation_space = spaces.Box(low, high, dtype=np.float32)

        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode
        self.reward = 0
        self.step_count = 0

        # For human rendering
        self.window = None
        self.clock = None

    def _get_obs(self):
        '''
        Return current observation of the simulation. Used as input to the agent.
        Can be later processed to state representation.
        '''
        return self.environment.get_rl_observation()

    def step(self, action) -> Tuple[np.array, float, bool, dict]:

        self.step_count += 1
        
        # 1. Execute action
        self.environment.set_rl_action(action)
        self.render()

        # 2. Get observation (important: get observation after action was executed)
        observation = self._get_obs()

        # 3. Calculate reward
        reward = self.calculate_reward()
        
        info = {}

        # Check for termination (new in gymnasium)
        terminated = False

        # Check for done
        done = self.check_done()

        if self.render_mode == "human":
            self.render()

        return observation, reward, terminated, done, info

    def calculate_reward(self) -> float:
        reward = self.environment.reward_account.get_latest_rewards()
        return reward
    
    def _get_info(self):
        'Return more info about the current state of the simulation. NOT used as input to the agent.'
        return {"info1": "foo",
                "info2": "bar"}

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

    def reset(self, seed=None, options=None):
        '''
        Will be called whenever a done signal has been issued by the environment.
        '''

        super().reset(seed=seed)

        print('********************RESET********************')
        self.environment.action_handler.reset_to_start(self.environment.car, random_vel=True)
        observation = self.environment.get_rl_observation(disable_dist=True)
        self.environment.car.update_velocity_norm_history(reset_list=True)
        self.environment.car.update_on_track(on_track=False, reset_list=True)

        info = self._get_info()

        return observation, info

    def close(self):
        pass
    
    def render(self):
        if self.render_mode == "human":
            return self._render_frame_human()
        elif self.render_mode == "rgb_array":
            return self._render_frame_rgb_array()

    def _render_frame_human(self):

        if self.window is None and self.render_mode == "human":
            self.window = self.environment.screen

            #override default pygame fps
            self.environment.ticks = self.metadata["render_fps"]

        self.environment.game_loop_function()

    def _render_frame_rgb_array(self):
        raise NotImplementedError()
        '''
        return np.transpose(
            np.array(pygame.surfarray.pixels3d(canvas)), axes=(1, 0, 2)
        )
        '''