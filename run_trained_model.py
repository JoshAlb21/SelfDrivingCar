import os
from rl_sd_car.envs.sd_car_env import SdCarEnv
from stable_baselines3 import DQN

env = SdCarEnv()

model_name = "dqn_rl_car1"
model_dir = os.path.join(os.path.dirname(__file__), 'model', model_name)
model = DQN.load(model_dir)

obs = env.reset()
n_episodes = 3000
current_episode = 0
while current_episode < n_episodes:
    action, _states = model.predict(obs, deterministic=True)
    obs, rewards, done, info = env.step(action)
    env.render()
    print(f"Action_test: {action}")
    print(obs)
    print(rewards)
    if done:
        current_episode += 1