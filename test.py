# 1. It renders instances for 500 timesteps, performing random actions.
from gym import envs
import gym
import numpy as np
from rl_sd_car.envs.sd_car_env import SdCarEnv

#env = gym.make('sd-v0')
env = SdCarEnv()
action_space_size = env.action_space.n
state_space_size = env.observation_space.n

q_table = np.zeros((state_space_size, action_space_size))

print(q_table)