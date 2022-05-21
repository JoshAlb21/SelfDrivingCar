from rl_sd_car.envs.sd_car_env import SdCarEnv
import numpy as np
import gym
from gym import envs
import time

from stable_baselines3 import DQN
from stable_baselines3.dqn.policies import DQNPolicy

env = SdCarEnv()
action_space_size = env.action_space.n
state_space_shape = env.observation_space.shape
state_space_low = env.observation_space.low
state_space_high = env.observation_space.high
print(action_space_size)
print(state_space_shape, state_space_low, state_space_high)

obs = env.reset()
action = env.action_space.sample()
print("Sampled action:", action)
obs, reward, done, info = env.step(action)
print(obs, reward, done, info)

model = DQN(DQNPolicy, env, verbose=0)
# Train the agent
model.learn(total_timesteps=10)
end = time.time()

obs = env.reset()
while True:
    action, _states = model.predict(obs)
    obs, rewards, done, info = env.step(action)
    env.render()
    # print(action)
    print(obs)
    print(rewards)
