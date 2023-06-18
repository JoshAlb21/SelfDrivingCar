import sys
import gymnasium
sys.modules["gym"] = gymnasium

from rl_sd_car.envs.sd_car_env import SdCarEnv


if __name__ == '__main__':

    env = SdCarEnv(render_mode="human")
    ob, info = env.reset()

    for _ in range(2000):
        action = env.action_space.sample()
        ob, reward, terminated, truncated, info = env.step(action)
        print(f"action: {action}, reward: {reward}, terminated: {terminated}, truncated: {truncated}")
        print(f"observation: {ob}")
        print(f"action: {action}")
        #print(f"info: {info}")

        if terminated or truncated:
            processes_observation, info = env.reset()