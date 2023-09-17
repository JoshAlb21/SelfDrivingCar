import os
from rl_sd_car.envs.sd_car_env import SdCarEnv
from stable_baselines3 import DQN

import numpy as np

env = SdCarEnv(render_mode="human")

model_name = "dqn_rl_car1"
model_dir = os.path.join(os.path.dirname(__file__), 'model', model_name)
model = DQN.load(model_dir)

obs, info = env.reset()
n_episodes = 300_000
current_episode = 0

for i in range(n_episodes):
    while True:

        action, _states = model.predict(obs, deterministic=True)
        obs, rewards, terminated, done, info = env.step(action)
        print(f"Action_test: {action}")
        print(obs)
        print(rewards)
        if done:
            obs, info = env.reset()