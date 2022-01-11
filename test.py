# 1. It renders instances for 500 timesteps, performing random actions.
from gym import envs
import gym
env = gym.make('Acrobot-v1')
env.reset()
for _ in range(500):
    env.render()
    env.step(env.action_space.sample())
# 2. To check all env available, uninstalled ones are also shown.
print(envs.registry.all())
