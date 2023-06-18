import sys
import gymnasium
sys.modules["gym"] = gymnasium

from rl_sd_car.envs.sd_car_env import SdCarEnv
import numpy as np
import time
import os

from stable_baselines3 import DQN
from stable_baselines3.dqn.policies import DQNPolicy
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.results_plotter import plot_results
from stable_baselines3.common import results_plotter
from stable_baselines3.common.noise import NormalActionNoise
from stable_baselines3.common.evaluation import evaluate_policy

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

retrain = False

n_actions = env.action_space.n
action_noise = NormalActionNoise(mean=np.zeros(n_actions), sigma=0.1 * np.ones(n_actions))
model = DQN(DQNPolicy, env, verbose=4)
model.action_noise = action_noise #Somehow does not work with init
time_steps = 50_000_000
model_name = "dqn_rl_car1"
model_dir = os.path.join(os.path.dirname(__file__), 'model', model_name)
callback = SaveOnBestTrainingRewardCallback(check_freq=100, log_dir=log_dir)
# Train the agent

start_train = time.time()

if retrain:
    model = DQN.load(model_dir)
    model.set_env(env)

obs = env.reset()
model.learn(total_timesteps= time_steps, callback=callback)
    
model.save(model_dir)

end_train = time.time()
print(f'Time to train: {end_train-start_train}')