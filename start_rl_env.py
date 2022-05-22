from rl_sd_car.envs.sd_car_env import SdCarEnv
import numpy as np
import gym
from gym import envs
import time
import os
import matplotlib.pyplot as plt

from stable_baselines3 import DQN
from stable_baselines3.dqn.policies import DQNPolicy
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.results_plotter import plot_results
from stable_baselines3.common import results_plotter
from stable_baselines3.common.noise import NormalActionNoise

from callback.reward_callback import SaveOnBestTrainingRewardCallback

env = SdCarEnv()
log_dir = os.path.join(os.path.dirname(__file__), 'callback')
env = Monitor(env, log_dir)

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

n_actions = env.action_space.n
action_noise = NormalActionNoise(mean=np.zeros(n_actions), sigma=0.1 * np.ones(n_actions))
model = DQN(DQNPolicy, env, verbose=4)
model.action_noise = action_noise #Somehow does not work with init
time_steps = 100_000
# Train the agent
callback = SaveOnBestTrainingRewardCallback(check_freq=100, log_dir=log_dir)
model.learn(total_timesteps= time_steps, callback=callback)
model_name = "dqn_rl_car1"
model_dir = os.path.join(os.path.dirname(__file__), 'model', model_name)
model.save(model_dir)

#plot_results([log_dir], time_steps, results_plotter.X_TIMESTEPS, "RL Car") #TODO not working yet
#plt.show()

end = time.time()

obs = env.reset()
while True: #TODO update with https://github.com/DLR-RM/stable-baselines3/issues/224
    action, _states = model.predict(obs, deterministic=True)
    obs, rewards, done, info = env.step(action)
    env.render()
    print(f"Action_test: {action}")
    print(obs)
    print(rewards)
